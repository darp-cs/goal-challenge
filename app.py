from flask import Flask, render_template
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
from flask_sockets import Sockets, Rule
import whisper
import traceback
import base64
import tempfile

app = Flask(__name__)
sockets = Sockets(app)




# model = whisper.load_model('base.en')

def process_wav_bytes(webm_bytes: bytes, sample_rate: int = 16000):
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
        temp_file.write(webm_bytes)
        temp_file.flush()
        waveform = whisper.load_audio(temp_file.name, sr=sample_rate)
        return waveform

def transcribe_socket(ws):
    while not ws.closed:
        message = ws.receive()
        if message:
            print('message received', len(message), type(message))
            print(message)
            try:
                if isinstance(message, str):
                    message = base64.b64decode(message)
                audio = process_wav_bytes(bytes(message)).reshape(1, -1)
                # audio = whisper.pad_or_trim(audio)
                # transcription = whisper.transcribe(
                #     model,
                #     audio
                # )
            except Exception as e:
                traceback.print_exc()
                return
                

sockets.url_map.add(Rule('/transcribe', endpoint=transcribe_socket, websocket=True))

if __name__ == "__main__":
    print('serving on 8088')
    server = WSGIServer(('127.0.0.1', 8088), app, handler_class=WebSocketHandler)
    server.serve_forever()
