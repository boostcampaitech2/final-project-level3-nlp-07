from pydub import AudioSegment
from pydub.utils import db_to_float
import time
from multiprocessing import Process,Pipe
from espnet2.tasks.asr import ASRTask
from espnet2.bin.asr_inference import Speech2Text
import numpy as np
import torch
from flask_socketio import emit

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

        
def stream_input(sio,pipe,sid,roomName):
    
    model = Speech2Text(
        asr_train_config="../ref/mdl/exp/asr_train_asr_transformer2_ddp_raw_bpe/config.yaml",
        asr_model_file='../ref/mdl/exp/asr_train_asr_transformer2_ddp_raw_bpe/valid.acc.ave_10best.pth',
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
    #AUDIO INPUT
    RATE = 16000
    CHUNK = 1024
    SILENCE_THRESH = db_to_float(-30)

    min_silence=int(RATE/CHUNK*0.2)
    endure=0
    while 1:
        while 1:
            try:
                data=pipe.recv()
            except:
                continue
            #sound=AudioSegment.from_ogg(data)
            sound=AudioSegment(data=data,sample_width=2,frame_rate=RATE,channels=1)
            
            if sound.rms<SILENCE_THRESH*sound.max_possible_amplitude:
                if endure<min_silence:
                    endure+=1
                elif len(frames)<=300:
                    pass
                else:
                    break
            else:
                endure=0

            try:
                frames += sound
            except:
                frames=sound   
        pipe.send(11111111111111111)
        '''try:
            pipe.send(inference(model,preprocess_fn,frames,sid,roomName))
        except:
            pipe.send(1)'''



def inference(model,preprocess_fn,frames,sid,roomName):
    frame=pcm2float(frames.get_array_of_samples())
    tens=preprocess_fn('1',{'speech':frame})#input : (uid,dict)-> output : dict{'speech':array}
    output=model(**{'speech':torch.from_numpy(tens['speech'])}) #input : dict{'speech':Tensor,'speech_lengths':Tensor}
    return output[0][0]
    
    
    
