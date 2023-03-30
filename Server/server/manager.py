import os
import time
import multiprocessing as mp
import logging
import warnings
from typing import Dict, Tuple
from enum import Enum
from queue import Empty
from pathlib import Path
import whisper
from werkzeug.datastructures import FileStorage
import noisereduce as nr


log = logging.getLogger(f'server.manager')


class MessageType(Enum):
    STOP = 1
    TRANSCRIBE = 2
    DONE_PROCESSING = 3


class Message:
    def __init__(self, mtype: MessageType, data: Dict[str, str]):
        self.mtype = mtype
        self.data = data

    def stop() -> "Message":
        return Message(MessageType.STOP, {})

    def transcribe(filename: str) -> "Message":
        data = {
            "name": filename
        }
        return Message(MessageType.TRANSCRIBE, data)
    
    def done_processing(filename: str, result: Dict[str, str]) -> "Message":
        data = {
            "name": filename,
            "result": result
        }
        return Message(MessageType.DONE_PROCESSING, data)


class State:
    def __init__(self, model: str, audio_folder: str, mgr: mp.Manager, use_cpu: bool):
        self.model = model
        self.audio_folder = audio_folder
        self.job_queue: mp.Queue = mgr.Queue()
        self.result_queue: mp.Queue = mgr.Queue()
        self.use_cpu = use_cpu


class AudioManager:
    def _worker(args: Tuple[int, State]):
        rank = args[0]
        state = args[1]
        # load model on worker first
        #
        # each worker gets their own model since we can't share
        # a single loaded model across a Pool. this is because shared memory
        # for Sparse Tensors is literally not implemented
        #
        # TODO: check the memory usage on this
        log.debug(f"worker {rank} loading model '{state.model}'...")
        if state.use_cpu:
            model = whisper.load_model(state.model, "cpu")
        else:
            model = whisper.load_model(state.model)
        log.debug(f"worker {rank} done loading model")

        # launch into an infinite loop where we take
        # messages from a queue, process them, and then report back
        while True:
            job: Message = state.job_queue.get()

            if job.mtype == MessageType.STOP:
                # quit the worker if we receive a stop message
                break
            elif job.mtype == MessageType.TRANSCRIBE:
                # if we receive a transcribe message, transcribe it and put the result in the result queue
                name = job.data["name"]
                log.info(f"worker transcribing {name}")

                # load file, reduce noise
                filepath = Path(state.audio_folder).joinpath(name)
                a = whisper.load_audio(filepath)
                a = whisper.pad_or_trim(a)
                a = nr.reduce_noise(a, whisper.audio.SAMPLE_RATE)

                # there are a few dumb warnings that can happen while transcribing an audio file,
                # so we catch those here and ignore the ones that don't matter
                with warnings.catch_warnings():
                    # we ignore the warn against using CPU because sometimes we want to run this on CPU
                    warnings.filterwarnings("ignore", message="Performing inference on CPU when CUDA is available")
                    # this particular warning is a known issue and is safe to completely disregard
                    warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")
                    transcription = whisper.transcribe(model, a)
                
                msg = Message.done_processing(name, transcription)
                state.result_queue.put(msg)
                log.info(f"worker transcribed {name}")
            else:
                log.warn(f"invalid message received in worker {rank}")
            

    def __init__(self, model: str, audio_folder: str = "servaudiofiles", workers=1, use_cpu=False):
        self.workers = workers
        self.pool = mp.Pool(self.workers)
        log.debug(f"manager initialized pool with {self.workers} workers")
        self.mgr = mp.Manager()
        self.state = State(model, audio_folder, self.mgr, use_cpu)
        self.results = {}

        os.makedirs(audio_folder, exist_ok=True)
        args = [(i, self.state) for i in range(0, self.workers)]
        self.pool.map_async(AudioManager._worker, args)

    def save_audio_file(self, name: str, f: FileStorage):
        f.save(os.path.join(self.state.audio_folder, name))

    def request_transcription(self, filename):
        if self.results.get(filename):
            return
        
        self.state.job_queue.put(Message.transcribe(filename))
    
    def get_transcription(self, name: str, timeout=1):
        self.request_transcription(name)
        while True:
            # empty the queue every time we call get_transcription and store the result
            try:
                res: Message = self.state.result_queue.get_nowait()
                if res.mtype == MessageType.DONE_PROCESSING:
                    self.results[res.data["name"]] = res.data["result"]
            except Empty:
                break
        
        # if we happen to already have the result we want, return it
        if self.results.get(name):
            return self.results.get(name)
        
        start_time = time.time()
        while True:
            if timeout != None and time.time() - start_time > timeout:
                return None
            
            try:
                # poll the queue every second for the item we're looking for
                res: Message = self.state.result_queue.get(block=True, timeout=1)
                if res.mtype != MessageType.DONE_PROCESSING:
                    log.warn("invalid message received while handling queue")
                else:
                    self.results[res.data["name"]] = res.data["result"]
                    if res.data["name"] == name:
                        return res.data["result"]
            except Empty:
                continue
    
    def stop_workers(self):
        for _ in range(0, self.workers):
            # put a stop message for every single worker
            self.state.job_queue.put(Message.stop())
