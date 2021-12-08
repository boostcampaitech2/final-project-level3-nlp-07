import pyaudio
import wave
from pydub import AudioSegment, silence
from pydub.utils import db_to_float
import time
from collections import deque
from multiprocessing import Process,Pipe
from ESPNET.asr_inference import Speech2Text
from espnet2.tasks.asr import ASRTask
from espnet_asr.bin import asr_inference
import numpy as np

model,preprocess_fn=asr_inference.model()

def pcm2float(sig, dtype='float64'):
    sig = np.asarray(sig)
    if sig.dtype.kind not in 'iu':
        raise TypeError("'sig' must be an array of integers")
    dtype = np.dtype(dtype)
    if dtype.kind != 'f':
        raise TypeError("'dtype' must be a floating point type")
        
def stream_input(pipe):
    #AUDIO INPUT
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    CHUNK = 1024
    SILENCE_THRESH = db_to_float(-30)
    audio = pyaudio.PyAudio()
    kill=0
    
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
        try:
            if frames:
                pipe.send(frames)
                print("appending")
                del frames
                
                kill=0
        except:
            kill+=1
            if kill%20==0:
                print("killing",kill)
            if kill==100:
                pipe.send('END')
                print("SI ENDED")
                return
            

def inference(pipe):
    while 1:
        try:
            frame=pipe.recv()
        except:
            print("Waiting")
            time.sleep(1)
            continue
        else:
            if frame=='END':
                print("INF ENDED")
                return 
            frame=pcm2float(frame.get_array_of_samples())
            tens=preprocess_fn('1',frame)#input : (uid,array)-> output : Tensor (1,length)
            output=model({'speech':tens,'speech_len':tens.size(1)})
            print(output)

if __name__=="__main__":
    stream_pipe,inference_pipe=Pipe()
    si = Process(target=stream_input,args=(stream_pipe,))
    si.start()
    inf = Process(target=inference,args=(inference_pipe,))
    inf.start()
    
    si.join()
    inf.join()
    
    exit(0)
