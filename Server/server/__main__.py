import os
import logging
from flask import Flask
import multiprocessing as mp
from dotenv import load_dotenv
from manager import AudioManager
import blueprints
from robocomm import RoboComm


load_dotenv()
# if PLC_HOST is unset, then the server will not attempt to communicate with any robots/plcs
PLC_HOST = os.getenv("PLC_HOST")
PLC_PORT = os.getenv("PLC_PORT", "9999")
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "servaudiofiles")
ALLOWED_EXTENSIONS = os.getenv("ALLOWED_EXTENSIONS", "mp3,3gp,mov,m4a")
MODEL = os.getenv("MODEL", "base.en")
WORKERS = os.getenv("WORKERS", "1")
USE_CPU = os.getenv("USE_CPU", "True")
PORT = os.getenv("PORT", "5000")
DEMO_MODE = os.getenv("DEMO_MODE", "False")


log = logging.getLogger("server.main")


def _setup_logging(debug=False):
    """sets up the server logger"""
    level = logging.DEBUG if debug else logging.INFO
    ch = logging.StreamHandler()
    formatter = logging.Formatter("[%(asctime)s %(levelname)s %(name)s] %(message)s")
    ch.setFormatter(formatter)
    log = logging.getLogger("server")
    log.setLevel(level)
    log.addHandler(ch)

    mplog = mp.get_logger()
    mplog.setLevel(level)
    mplog.addHandler(ch)


def main():
    app = Flask(__name__)
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
    app.config["ALLOWED_EXTENSIONS"] = set(ALLOWED_EXTENSIONS.split(","))
    app.config["MODEL"] = MODEL
    app.config["WORKERS"] = int(WORKERS)
    app.config["USE_CPU"] = USE_CPU.lower() in ["true", "yes"]
    app.config["DEMO_MODE"] = DEMO_MODE.lower() in ["true", "yes"]
    app.config["MANAGER"] = AudioManager(
        app.config["MODEL"],
        app.config["UPLOAD_FOLDER"],
        app.config["WORKERS"],
        app.config["USE_CPU"],
    )
    app.config["PORT"] = PORT
    app.config["PLC_HOST"] = PLC_HOST
    app.config["PLC_PORT"] = PLC_PORT
    if PLC_HOST is not None:
        app.config["CONNECTION"] = RoboComm(PLC_HOST, PLC_PORT, app.config["DEMO_MODE"])
    else:
        app.config["CONNECTION"] = None
    app.register_blueprint(blueprints.main)

    app.run(host="0.0.0.0", port=app.config["PORT"])


if __name__ == "__main__":
    _setup_logging(debug=True)
    main()
