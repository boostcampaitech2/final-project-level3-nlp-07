import socketio
import pyaudio

sio = socketio.Client()

def streams(sio):
    audio=pyaudio.PyAudio()
    stream=audio.open(format=pyaudio.paInt16,channels=1,rate=16000,input=True,frames_per_buffer=2048)
    print('Sending...')
    while True:
        data=stream.read(2048)
        if data:
            sio.emit('audio',data)

@sio.on('welcome')
def welcome():
    print("connected")
    sio.start_background_task(streams, sio)
    sio.emit('start_stream')

@sio.on('infer')
def infer(data):
    print(data.decode())

def main():
    sio.connect('http://115.85.182.137:6017', wait_timeout = 20)
    sio.wait()

if __name__=='__main__':
    main()