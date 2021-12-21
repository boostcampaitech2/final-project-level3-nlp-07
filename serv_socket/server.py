import socketio
from engineio.payload import Payload
from flask import Flask,render_template
from pydub import AudioSegment
from utils import inference
from pydub.utils import db_to_float
import os
import eventlet


Payload.max_decode_packets = 10000
        
RATE = 16000
CHUNK = 1024
SILENCE_THRESH = db_to_float(-40)
min_silence=6 #int(RATE/CHUNK*0.2)
endure=0
frames=None
ticker=False

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
STATIC_FOLDER = os.path.join(ROOT_PATH, "src")
TEMPLATE_FOLDER = os.path.join(ROOT_PATH, "src/view")

sio = socketio.Server(async_mode='eventlet', ping_timeout=60)
app=Flask(__name__,static_url_path='/src',static_folder=STATIC_FOLDER,template_folder=TEMPLATE_FOLDER)
app.wsgi_app = socketio.WSGIApp(sio,app.wsgi_app)
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
    global frames
    global ticker
    global endure
    sound=AudioSegment(data=data,sample_width=2,frame_rate=RATE,channels=1)
    try:
        frames += sound
    except:
        frames=sound   
    if sound.rms<SILENCE_THRESH*sound.max_possible_amplitude:
        if not ticker:
            frames=sound
            endure=0
        elif endure<min_silence:
            endure+=1
        elif len(frames)<=300:
            pass
        else:
            ticker=False
            sio.start_background_task(sio.emit('infer',inference(frames)))
            frames=None
            endure=0
    else:
        ticker=True
        endure=0

@sio.on('leave')
def leave(sid):
    sio.emit('leave')
    print('leave')


if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 6006)), app)