import logging
from flask import Blueprint, request, current_app
from manager import AudioManager
from processing import read_keyword_file, get_diagnostic_from_transcription
from robocomm import RoboComm


log = logging.getLogger(f"server.handler")
keywords = read_keyword_file("diagnostic.json")
main = Blueprint("main", __name__)
main.add_url_rule("/<filename>", endpoint="return_text", build_only=True)


@main.route("/", methods=["POST", "GET"])
def upload_audio():
    if request.method == "POST":
        if "file" in request.files:
            file = request.files["file"]
        elif len(request.form) > 0 and "file" == request.form[0][0]:
            file = request.form[0][1]
        else:
            return "no file"
    
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
        log.debug(f"eliding recording for {filename}")
        return ""

    mgr: AudioManager = current_app.config["MANAGER"]
    log.debug(f"getting transcription for {filename}")
    transcript = mgr.get_transcription(filename, timeout=30)
    if transcript is None:
        return "failure to transcribe", 500

    diagnostic = get_diagnostic_from_transcription(keywords, transcript["text"])
    if diagnostic is None:
        return "failure to get diagnostic", 500
        
    # at this point, we know that transcript and diagnostic are valid
    # so let's check if we have a CONNECTION in the app and if so, attempt to get some data from the robot!
    conn: RoboComm = current_app.config["CONNECTION"]
    if conn is None:
        return diagnostic, 200
    
    # now we know we have a connection, so send the data to the robot
    conn.send(diagnostic)
    # and receive
    return str(conn.receive()), 200
