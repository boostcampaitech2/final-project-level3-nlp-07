from flask import Flask, render_template, templating,request,redirect
import flask
import os
from flask_socketio import SocketIO,join_room,leave_room,emit,send
import logging
import ssl
from password import password
from multiprocessing import Process, Pipe
from Stream_input import stream_input
from threading import Thread
from engineio.payload import Payload

Payload.max_decode_packets = 100

logger = logging.getLogger()


static_files = {
    '/static': './public',
}
ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
print(ROOT_PATH)
STATIC_FOLDER = os.path.join(ROOT_PATH, "src/public")
TEMPLATE_FOLDER = os.path.join(ROOT_PATH, "src/view")
app=Flask(__name__,static_url_path='/public',static_folder=STATIC_FOLDER,template_folder=TEMPLATE_FOLDER)

@app.before_request
def before_request():
    if request.url.startswith('http://'):
        url = request.url.replace('http://', 'https://', 1)
        code = 301
        return redirect(url, code=code)

@app.route('/')
def index():
  return render_template("index.html")

sio = SocketIO(app, async_mode='threading',cors_allowed_origins="*")
pipes={}
@sio.on('connect')
def connect():
    print('connect')

@sio.on('join_room')
def join(data):
    sid=request.sid
    room = data['room']
    join_room(room)
    pipes[sid]={}
    pipes[sid]["serv"],pipes[sid]["mdl"]=Pipe()
    Process(target=stream_input,args=(sio,pipes[sid]["mdl"],sid,room)).start()
    emit('joined',sid,to=sid)
    emit("welcome",to=room,skip_sid=sid)

@sio.on('offer')
def offer(offer,roomName):
    sid=request.sid
    emit('offer',offer,room=roomName,skip_sid=sid)

@sio.on('answer')
def answer(answer,roomName):
    sid=request.sid
    emit('answer',answer,room=roomName,skip_sid=sid)

@sio.on('ice')
def ice(ice,roomName):
    sid=request.sid
    emit('ice',ice,room=roomName,skip_sid=sid)

@sio.on('audio_stream')
def stream(sid,stream,roomName):
    print(len(stream),"LENLENLENLNENLENELENLENENL",len(stream))
    pipes[sid]['serv'].send(stream)
    if pipes[sid]['serv'].poll():
        data=pipes[sid]['serv'].recv()
        print('#########################################')
        print(data)
        print('#########################################')
        emit('infer',data,room=roomName,skip_sid=sid)


@sio.on('leave_room')
def leave(data):
    room = data['room']
    leave_room(room)

if __name__ == '__main__':
    ssl_context=ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    ssl_context.load_cert_chain(certfile='certificate.crt', keyfile='private.key',password=password())
    sio.run(app,host="0.0.0.0",port=6006,ssl_context=ssl_context,debug=True)
    