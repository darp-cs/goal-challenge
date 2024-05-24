from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import pyaudio
import numpy as np
import asyncio
from datetime import datetime
import wave
import websockets
app = FastAPI()


CHUNK_SIZE = 1024
rate = 16000
clip_duration = 4
audio = pyaudio.PyAudio()
output_path = './'
overlap = 0
channels =1
stream = audio.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=16000,
                    output=True,
                    frames_per_buffer=CHUNK_SIZE)


def prepare_file(self, filename, mode='wb'):
        wavefile = wave.open(filename, mode)
        wavefile.setnchannels(channels)
        wavefile.setsampwidth(stream.get_sample_size(pyaudio.paInt16))
        wavefile.setframerate(rate)
        return wavefile

@app.websocket("/record")
async def websocket_handler(websocket: WebSocket):
        frames = []
        await websocket.accept()
        try:
            # async for message in websocket.receive_bytes():
                data = await websocket.receive_bytes()
                # while True:
                audio_data = np.frombuffer(data, dtype=np.int16)
                print('Begin recording...')
                stream.write(audio_data.tobytes())
                # try:
                #     fps = int(rate / CHUNK_SIZE * clip_duration)
                #     while True:
                #         if len(frames) > fps:
                #             clip = []
                #             for i in range(0, fps):
                #                 clip.append(frames[i])
                #             fname = ''.join([output_path, '/clip-', datetime.utcnow().strftime('%Y%m%d%H%M%S'), '.wav'])
                #             wavefile = prepare_file(fname)
                #             wavefile.writeframes(b''.join(clip))
                #             wavefile.close()
                #             frames = frames[(clip_duration -overlap - 1):]
                #         break
                # except KeyboardInterrupt as e:
                #     print('Terminating recording...')
                #     stream.stop_recording()
                #     print('OK')
                # # stream.write(audio_date.tobytes())
        except WebSocketDisconnect:
            stream.stop_stream()
            stream.close()
            print('Web socket disconnected')
        finally:
            stream.stop_stream()
            stream.close()
            # audio.close(stream)
        
        # await websocket.send_text(f"Received data")
    # try:
    #     async for message in websocket:
    #         print(message)
    #         audio_data = np.frombuffer(message, dtype=np.int16)
    #         stream.write(audio_data.tobytes())
    #         #stream.write(message)
    # finally:
    #     stream.stop_stream()
    #     stream.close()
    #     audio.terminate()





@app.get("/")
def hello_world():
    return "HELLO WORLD"