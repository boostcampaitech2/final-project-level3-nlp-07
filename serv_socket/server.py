import socketio
from engineio.payload import Payload
import eventlet
from pydub import AudioSegment
from utils import inference
from pydub.utils import db_to_float


Payload.max_decode_packets = 10000
        
RATE = 16000
CHUNK = 1024
SILENCE_THRESH = db_to_float(-35)
min_silence=int(RATE/CHUNK*0.2)
endure=0
frames=None
ticker=False

sio = socketio.Server(async_mode='eventlet', ping_timeout=60)
app = socketio.WSGIApp(sio)

@sio.on('connect')
def connect(*args):
    sio.emit("welcome")
    print('connect')

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
            frames=frames[-64:]
            endure=0
        elif endure<min_silence:
            endure+=1
        elif len(frames)<=300:
            pass
        else:
            ticker=False
            sio.emit('infer',inference(frames).encode())
            frames=None
            endure=0
    else:
        ticker=True
        endure=0

if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 6006)), app)