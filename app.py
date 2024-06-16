from flask import Flask, render_template
from flask_sockets import Sockets, Rule
import whisper
import traceback
import base64
import tempfile
import base64
import json
import logging


app = Flask(__name__)
sockets = Sockets(app)


HTTP_SERVER_PORT = 8088


model = whisper.load_model('base.en')

def process_wav_bytes(webm_bytes: bytes, sample_rate: int = 16000):
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
        temp_file.write(webm_bytes)
        temp_file.flush()
        waveform = whisper.load_audio(temp_file.name, sr=sample_rate)
        return waveform

def transcribe_socket(ws):
    
    app.logger.info("Connection accepted")
    
    while not ws.closed:
        message = ws.receive()
        

        if message:
            print('message received', len(message), type(message))
            print(message)
            try:
                # if isinstance(message, str):
                #     message = base64.b64decode(message)
                audio = process_wav_bytes(bytes(message)).reshape(1, -1)
                audio = whisper.pad_or_trim(audio)
                transcription = whisper.transcribe(
                    model,
                    audio
                )
            except Exception as e:
                traceback.print_exc()
                return
        # else:
        #     app.logger.info("No message received...")
        #     continue
                


sockets.url_map.add(Rule('/transcribe', endpoint=transcribe_socket, websocket=True))

if __name__ == "__main__":
    app.logger.setLevel(logging.DEBUG)
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    server = pywsgi.WSGIServer(('', HTTP_SERVER_PORT), app, handler_class=WebSocketHandler)
    print("Server listening on: http://localhost:" + str(HTTP_SERVER_PORT))
    server.serve_forever()
