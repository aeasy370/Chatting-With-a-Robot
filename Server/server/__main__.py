import os
import logging
from quart import Quart
import asyncio
from dotenv import load_dotenv
from manager import AudioManager
import blueprints
from robocomm import handle_plc_connection


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


def main():
    _setup_logging(debug=True)
    
    app = Quart(__name__)
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
    app.config["DIAGNOSTIC_QUEUE"] = asyncio.Queue()
    app.config["RESPONSE_QUEUE"] = asyncio.Queue()
    app.config["PORT"] = PORT
    app.config["PLC_HOST"] = PLC_HOST
    app.config["PLC_PORT"] = int(PLC_PORT)
    app.register_blueprint(blueprints.main)
    
    @app.before_serving
    async def startup():
        if app.config["PLC_HOST"] is not None:
            loop = asyncio.get_event_loop()
            log.debug(f"creating server for PLC on port {PLC_PORT}")
            app.config["CONNECTION"] = await asyncio.start_server(
                lambda r, w: handle_plc_connection(app.config["DIAGNOSTIC_QUEUE"], app.config["RESPONSE_QUEUE"], r, w),
                host="127.0.0.1",
                port=app.config["PLC_PORT"]
            )
            # loop.create_task(app.config["CONNECTION"])
        else:
            app.config["CONNECTION"] = None
    
    app.run()


if __name__ == "__main__":
    main()
