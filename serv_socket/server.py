import socketio
from engineio.payload import Payload
from flask import Flask,render_template
from pydub import AudioSegment
from utils import inference,STORAGE
import eventlet
import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(os.path.dirname(__file__))),"ref/punct/src"))

from inference import punct_inference

Payload.max_decode_packets = 10000

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
STATIC_FOLDER = os.path.join(ROOT_PATH, "src")
TEMPLATE_FOLDER = os.path.join(ROOT_PATH, "src/view")

sio = socketio.Server(async_mode='eventlet', ping_timeout=60)
app=Flask(__name__,static_url_path='/src',static_folder=STATIC_FOLDER,template_folder=TEMPLATE_FOLDER)
app.wsgi_app = socketio.WSGIApp(sio,app.wsgi_app)
storage=STORAGE()

@app.route('/')
def index():
    return render_template("ui.html")

@sio.on('connect')
def connect(sid, environ):
    print('connect')

@sio.on('join')
def join(sid,):
    print('join')
    sio.emit("welcome")

@sio.on('start_stream')
def start_stream(*args):
    print('start_stream')

@sio.on('audio')
def stream(sid,data):
    frames,endure,ticker=storage.get_values()
    sound=AudioSegment(data=data,sample_width=2,frame_rate=16000,channels=1)
    thresh=storage.get_mean_rms(sound.rms)
    try:
        frames += sound
    except:
        frames=sound
    
    if sound.rms<thresh:
        if not ticker:
            frames=frames[-64:]
            endure=0
        elif endure<storage.min_silence:
            endure+=1
        elif len(frames)<=300:
            pass
        else:
            ticker=False
            sio.emit('infer',inference(frames))
            frames=frames[-64:]
            endure=0
    else:
        ticker=True
        endure=0
    storage.save_values(frames,endure,ticker)

@sio.on('leave')
def leave(sid,ftext):
    sio.emit("leave")
    sio.emit('final',punct_inference(ftext))
    storage.initialize()
    print('leave')


if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 6006)), app)