from flask import Flask, render_template, request,redirect
import os
from flask.wrappers import Response
from flask_socketio import SocketIO,emit,join_room
import ssl
from pydub.utils import db_to_float
from pydub.audio_segment import AudioSegment
from password import password
from utils import inference
from engineio.payload import Payload
from struct import pack
import io
from flask_cors import CORS

Payload.max_decode_packets = 100

static_files = {
    '/static': './public',
}

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

STATIC_FOLDER = os.path.join(ROOT_PATH, "src/public")
TEMPLATE_FOLDER = os.path.join(ROOT_PATH, "src/view")

RATE = 16000
CHUNK = 1024
SILENCE_THRESH = db_to_float(-35)
min_silence=int(RATE/CHUNK*0.2)
endure=0
frames=None
ticker=False
ind=0

app=Flask(__name__,static_url_path='/public',static_folder=STATIC_FOLDER,template_folder=TEMPLATE_FOLDER)
sio = SocketIO(app, async_mode='threading',cors_allowed_origins="*")
CORS(app)
infer=inference()
@app.before_request
def before_request():
    if request.url.startswith('http://'):
        url = request.url.replace('http://', 'https://', 1)
        code = 301
        return redirect(url, code=code)

@app.route('/')
def index():
  return render_template("index.html")

@app.route('/',methods=['POST'])
def streams():
    global ind
    global frames
    global ticker
    global endure
    data=request.data
    if len(data)%2==1:
        data+=b'\x00'
    with open('export_audios/test.wav','wb') as f:
        f.write(data)
        f.seek(0)
    sound=AudioSegment.from_wav('export_audios/test.wav')
    print(sound.rms)
    try:
        frames += sound
    except:
        frames=sound
    if len(frames)>10000:
            ticker=False
            ind+=1
            sio.start_background_task(emit('infer',infer(frames)))
            print("##################inferred####################")
            frames=None
            endure=0
    elif sound.rms<SILENCE_THRESH*32768:
        if not ticker:
            frames=frames[-64:]
            endure=0
        elif endure<min_silence:
            endure+=1
        elif len(frames)<=300:
            pass
        else:
            ticker=False
            ind+=1
            sio.start_background_task(emit('infer',infer(frames)))
            print("##################inferred####################")
            frames=None
            endure=0
    else:
        ticker=True
        endure=0
    return Response(status=200)


@sio.on('connect')
def connect():
    print('connected')

@sio.on('join_room')
def jr(sid,data):
    join_room(data['room'])
    sio.emit("welcome")
    print('join_room')

@sio.on('start_stream')
def start_stream():
    print('start_stream')

@sio.on('audio')
def stream(sid,data,roomName):
    global frames
    global ticker
    global endure
    global ind
    int_array=list(eval(data).values())
    if int_array:
        sound=int_array
        srms=(sum([i**2 for i in sound])/len(sound))**0.5
        print(srms,SILENCE_THRESH*32768)
        try:
            frames += sound
        except:
            frames=sound
        if len(frames)>10000:
                ticker=False
                ind+=1
                sio.start_background_task(emit('infer',infer(frames),to=roomName))
                print("##################inferred####################")
                frames=None
                endure=0
        elif srms<SILENCE_THRESH*32768:
            if not ticker:
                frames=frames[-64:]
                endure=0
            elif endure<min_silence:
                endure+=1
            elif len(frames)<=300:
                pass
            else:
                ticker=False
                ind+=1
                sio.start_background_task(emit('infer',infer(frames),to=roomName))
                print("##################inferred####################")
                frames=None
                endure=0
        else:
            ticker=True
            endure=0

if __name__ == '__main__':
    ssl_context=ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    ssl_context.load_cert_chain(certfile='certificate.crt', keyfile='private.key',password=password())
    sio.run(app,host="0.0.0.0",port=6006,ssl_context=ssl_context,debug=True)
    