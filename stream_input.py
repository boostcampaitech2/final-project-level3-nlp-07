import pyaudio
from pydub import AudioSegment
from pydub.utils import db_to_float
import time
from multiprocessing import Process,Pipe
from espnet2.tasks.asr import ASRTask
from espnet2.bin.asr_inference import Speech2Text
import numpy as np
import torch

config_path = './ref/mdl/exp/asr_train_asr_transformer2_ddp_raw_bpe/config.yaml'
model_path = './ref/mdl/exp/asr_train_asr_transformer2_ddp_raw_bpe/model_kspon.pth',
model = Speech2Text(

        asr_train_config = config_path,
        asr_model_file = model_path,

        lm_train_config=None,
        lm_file=None,
        token_type=None,
        bpemodel=None,
        device='cuda' if torch.cuda.is_available() else 'cpu',
        maxlenratio=0.0,
        minlenratio=0.0,
        dtype='float32',
        beam_size=20,
        ctc_weight=0.3,
        lm_weight=1.0,
        penalty=0.0,
        nbest=1,
    )
preprocess_fn=ASRTask.build_preprocess_fn(model.asr_train_args, False)


def pcm2float(sig, dtype='float32'):
    sig = np.asarray(sig)
    if sig.dtype.kind not in 'iu':
        raise TypeError("'sig' must be an array of integers")
    dtype = np.dtype(dtype)
    if dtype.kind != 'f':
        raise TypeError("'dtype' must be a floating point type")
    i = np.iinfo(sig.dtype)
    abs_max = 2 ** (i.bits - 1)
    offset = i.min + abs_max
    return (sig.astype(dtype) - offset) / abs_max

        
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
    
    min_silence=int(RATE/CHUNK*0.2)
    endure=0
    print ("recording start")
    while 1:

        while 1:
            data = stream.read(CHUNK,exception_on_overflow = False)
            sound=AudioSegment(data=data,sample_width=2,frame_rate=16000,channels=CHANNELS)
            
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
            if len(frames)<=300:
                raise Exception("Too short!")

                
            pipe.send(frames)
            print("appending")
            del frames
                

            kill=0
        except:
            kill+=1
            if kill%20==0:
                print("killing",kill)
            if kill==200:
                pipe.send('END')
                print("SI ENDED\n")
                return



def inference(pipe):
    while 1:
        try:
            frame=pipe.recv()
            if type(frame)==str:
                print("INF ENDED")
                return 
        except:
            print("Waiting")
            time.sleep(1)
            continue
        else:
            frame=frame.set_frame_rate(16000)
            frame=frame.set_channels(1)
            frame=frame.set_sample_width(2)
            frame=pcm2float(frame.get_array_of_samples())
            tens=preprocess_fn('1',{'speech':frame})#input : (uid,dict)-> output : dict{'speech':array}
            output=model(**{'speech':torch.from_numpy(tens['speech'])}) #input : dict{'speech':Tensor,'speech_lengths':Tensor}
            print(output[0][0])
            


if __name__ == '__main__':
    parent_conn, child_conn = Pipe()
    si=Process(target=stream_input,args=(child_conn,))
    si.start()
    inf=Process(target=inference,args=(parent_conn))
    inf.start()
    si.join()
    inf.join()
    

    

