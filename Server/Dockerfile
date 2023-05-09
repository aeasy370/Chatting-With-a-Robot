FROM python:3.10-bullseye

WORKDIR /app
COPY requirements.txt requirements.txt
COPY server server
COPY scripts scripts
COPY diagnostic.json diagnostic.json

RUN apt-get -y update
RUN apt-get install -y ffmpeg
RUN pip3 install -r requirements.txt
RUN python -m nltk.downloader punkt
RUN python -m nltk.downloader averaged_perceptron_tagger
RUN python scripts/download_model_medium.py
CMD ["python3", "server"]
