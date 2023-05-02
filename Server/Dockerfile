FROM python:3.9.16-bullseye

WORKDIR /app
COPY requirements.txt requirements.txt
COPY server server
COPY diagnostic.json diagnostic.json

RUN apt-get -y update
RUN apt-get install -y ffmpeg
RUN pip3 install -r requirements.txt
CMD ["python3", "server"]
