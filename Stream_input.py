import pyaudio
import wave
from pydub import AudioSegment, silence
from pydub.utils import db_to_float
import time
from collections import deque
from multiprocessing import Process,Queue,Lock,Pool


myaudio=deque()
lock=Lock()


def stream_input():
    #AUDIO INPUT
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    CHUNK = 1024
    RECORD_SECONDS = 1
    WAVE_OUTPUT_FILENAME = "output.wav"
    SILENCE_THRESH = db_to_float(-30)
    audio = pyaudio.PyAudio()
    kill=0
    check=0
    
    # start Recording
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    frames_per_buffer=CHUNK)

    min_silence=int(RATE/CHUNK*0.1)
    endure=0
    print ("recording start")
    while 1:
        while 1:
            data = stream.read(CHUNK,exception_on_overflow = False)
            sound=AudioSegment(data=data,sample_width=2,frame_rate=RATE,channels=CHANNELS)

            if sound.rms<SILENCE_THRESH*sound.max_possible_amplitude:
                if endure<min_silence:
                    endure+=1
                else:
                    break
            else:
                try:
                    frames += sound
                except:
                    frames=sound   
                endure=0
        with lock:
            try:
                
                if frames:
                    myaudio.append(check)
                    print("appending",len(myaudio))
                    del frames
                    
                    kill=0
            except:
                kill+=1
                if kill%20==0:
                    print("killing",kill)
                if kill==100:
                    myaudio.append('END')
                    print('added end')
                    print("SI ENDED")
                    return
            

def inference():
    while 1:
        with lock:
            print(len(myaudio))
            try:
                frame=myaudio.popleft()
                print(f"Poped {frame}")
            except:
                print("Waiting")
                time.sleep(1)
            else:
                print("POP!!")
        try:
            if frame=='END':
                print("INF ENDED")
                return
        except:
            pass
                #preprocessing
                #model inference

if __name__=="__main__":
    si = Process(target=stream_input)
    si.start()
    inf = Process(target=inference)
    inf.start()
    
    si.join()
    inf.join()
    
    exit(0)