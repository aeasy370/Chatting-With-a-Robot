Server software for our UTK 2022-2023 Senior Design project - Chatting with a Robot

# setup
The server provides both a `requirements.txt` file as well as a `pyproject.toml` ([pyproject.toml](https://pip.pypa.io/en/stable/reference/build-system/pyproject-toml/)) for multiple build workflows. The recommended build workflow is either plain python `venv`s or to use [Poetry](https://python-poetry.org). Additionally, the server requires `ffmpeg` to be installed and in the PATH. Instructions on how to do this are in the [ffmpeg](#ffmpeg) section. 

## requirements.txt and venv
1. Create a virtual environment by running `py -m venv venv` (Windows) or `python3 -m venv venv` (MacOS/Linux).
2. Activate the virtual environment by running `.\venv\Scripts\activate` (Windows) or `source ./venv/bin/activate` (MacOS/Linux).
3. Install all dependencies via `pip install -r requirements.txt`.

To run the server, just execute the `server` module via Python.

## pyproject.toml and Poetry
If you do not have Poetry installed, follow the steps located [here](https://python-poetry.org/docs/). Then, run `poetry install` in the server root (`/Server`) to create a virtual environment and install all dependencies. 

To run the server, use `poetry run python server`.

## docker
The preferred way to run the server in a non-development environment is to use [Docker](https://www.docker.com/).
1. Download and install Docker on the target machine and clone the repo.
2. To build the container, run `docker build --tag chatting-with-a-robot-server .`. 
3. To run the container, run `docker run -d -p 5000:5000 chatting-with-a-robot-server`. The `-p` option here specifies `host_port:internal_port`. The internal port of the server defaults to `5000`, so the second option here will *usually* be `5000`. However the first option is whatever is most convenient for the host machine. 
4. To stop the container, use `docker ps` to get the process name. Then run `docker stop <process name>` to stop the container.


## ffmpeg
ffmpeg can be obtained on their [download page](https://ffmpeg.org/download.html). Choose the build for your system and install it if you're on Linux/MacOS. For Windows builds, download the correct executable from one of the mirrors provided, extract it, and add that folder to the PATH.

# formatting
We have [black](https://github.com/psf/black) as a code formatter. Run either `black server/` or `poetry run black server/` to format all the code in the `server` directory.
