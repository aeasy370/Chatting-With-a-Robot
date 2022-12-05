import whisper
import numpy

model = whisper.load_model('base.en')
result = model.transcribe('audio1389724773.m4a')
print(result['text'])