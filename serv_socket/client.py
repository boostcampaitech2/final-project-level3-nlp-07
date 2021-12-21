import socketio
import pyaudio

sio = socketio.Client()

class Worker:
    def __init__(self,):
        self.switch = True

    def do(self,sio):
        self.switch=True
        self.streams(sio)

    def streams(self,sio):
        audio=pyaudio.PyAudio()
        stream=audio.open(format=pyaudio.paInt16,channels=1,rate=16000,input=True,frames_per_buffer=2048)
        print('Sending...')
        while self.switch:
            data=stream.read(512)
            if data:
                sio.emit('audio',data)
        print('Stopped')

    def stop(self):
        self.switch = False


worker=Worker()

@sio.on('connect')
def connect():
    print('connected')

@sio.on('welcome')
def welcome():
    print("start stream")
    global worker
    sio.start_background_task(worker.do, sio)
    sio.emit('start_stream')

@sio.on('infer')
def infer(data):
    print(data)

@sio.on('leave')
def leave():
    print("disconnected")
    global worker
    worker.stop()
    

if __name__=='__main__':
    sio.connect('http://115.85.182.137:6017', wait_timeout = 20)
    sio.wait()