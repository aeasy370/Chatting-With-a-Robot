import logging
from quart import Blueprint, request, current_app
from manager import AudioManager
from processing import read_keyword_file, get_diagnostic_from_transcription


log = logging.getLogger(f"server.handler")
keywords = read_keyword_file("diagnostic.json")
main = Blueprint("main", __name__)
main.add_url_rule("/<filename>", endpoint="return_text")


@main.route("/", methods=["POST", "GET"])
async def upload_audio():
    if request.method == "POST":
        files = await request.files
        form = await request.form
        if "file" in files:
            file = files["file"]
        elif len(request.form) > 0 and "file" == form[0][0]:
            file = form[0][1]
        else:
            return "no file"

        if file.filename == "":
            return ""
        if file:
            mgr: AudioManager = current_app.config["MANAGER"]
            await mgr.save_audio_file(file.filename, file)
            mgr.request_transcription(file.filename)
            return ""
        if request.method == "GET":
            return ""


@main.route("/<filename>", methods=["GET"])
async def return_text(filename):
    if not any(
        map(lambda ext: ext in filename, current_app.config["ALLOWED_EXTENSIONS"])
    ):
        log.debug(f"eliding recording for {filename}")
        return "", 200

    mgr: AudioManager = current_app.config["MANAGER"]
    log.debug(f"getting transcription for {filename}")
    transcript = mgr.get_transcription(filename, timeout=500)
    if transcript is None:
        return "failure to transcribe", 500

    diagnostic = get_diagnostic_from_transcription(keywords, transcript["text"])
    if diagnostic is None:
        return "failure to get diagnostic", 500

    # at this point, we know that transcript and diagnostic are valid
    # so let's check if we have a queue for diagnostics in the app
    squeue = current_app.config["DIAGNOSTIC_QUEUE"]
    rqueue = current_app.config["RESPONSE_QUEUE"]
    if (squeue is None) or (rqueue is None):
        return diagnostic, 200
    
    # queue must take bytes
    await squeue.put(bytes(diagnostic, "utf-8"))
    log.debug("notified plc handler to send diagnostic")
    
    return await rqueue.get()
