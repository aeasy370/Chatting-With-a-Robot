from flask import Flask, request, redirect, url_for, send_from_directory
import os
import whisper

UPLOAD_FOLDER = './servaudiofiles/'
ALLOWED_EXTENSIONS = {'mp3', '3gp'}
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/", methods = ['POST','GET'])
def upload_audio():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'no file'
        file = request.files['file']
        if file.filename == '':
            return ''
        if file:
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return ''
    if request.method == 'GET':
        return ''

app.add_url_rule(
    "/<filename>", endpoint="return_text", build_only=True
)
@app.route("/<filename>", methods = ['GET'])
def return_text(filename):
    if '.mp3' not in filename:
        return ''
    print(f'filename: {filename}')
    whisper_audio = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    print(f'whisper_audio: {whisper_audio}')
    model = whisper.load_model('base.en')
    result = model.transcribe(whisper_audio)
    return result['text']
