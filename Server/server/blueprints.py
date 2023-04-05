import logging
from flask import Blueprint, request, current_app
from manager import AudioManager


log = logging.getLogger(f"server.handler")
main = Blueprint("main", __name__)
main.add_url_rule("/<filename>", endpoint="return_text", build_only=True)


@main.route("/", methods=["POST", "GET"])
def upload_audio():
    if request.method == "POST":
        if "file" not in request.files:
            return "no file"
        file = request.files["file"]
        if file.filename == "":
            return ""
        if file:
            mgr: AudioManager = current_app.config["MANAGER"]
            mgr.save_audio_file(file.filename, file)
            mgr.request_transcription(file.filename)
            return ""
    if request.method == "GET":
        return ""


@main.route("/<filename>", methods=["GET"])
def return_text(filename):
    if not any(
        map(lambda ext: ext in filename, current_app.config["ALLOWED_EXTENSIONS"])
    ):
        return ""

    mgr: AudioManager = current_app.config["MANAGER"]
    log.debug(f"getting transcription for {filename}")
    return mgr.get_transcription(filename, timeout=30)
