import socketio
from engineio.payload import Payload
import eventlet
from pydub import AudioSegment
from pydub.utils import db_to_float
from espnet2.tasks.asr import ASRTask
from espnet2.bin.asr_inference import Speech2Text
import numpy as np
import torch

Payload.max_decode_packets = 10000

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

model = Speech2Text(
        asr_train_config="/opt/ml/final-project-level3-nlp-07/ref/mdl/exp/asr_train_asr_transformer2_ddp_raw_bpe/config.yaml",
        asr_model_file='/opt/ml/final-project-level3-nlp-07/ref/mdl/exp/asr_train_asr_transformer2_ddp_raw_bpe/valid.acc.ave_10best.pth',
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
        

RATE = 16000
CHUNK = 1024
SILENCE_THRESH = db_to_float(-30)
min_silence=int(RATE/CHUNK*0.2)
endure=0
frames=None
ticker=False

def inference(frames):
    frame=pcm2float(frames.get_array_of_samples())
    tens=preprocess_fn('1',{'speech':frame})#input : (uid,dict)-> output : dict{'speech':array}
    output=model(**{'speech':torch.from_numpy(tens['speech'])}) #input : dict{'speech':Tensor,'speech_lengths':Tensor}
    return output[0][0]
    

sio = socketio.Server(async_mode='eventlet', ping_timeout=60)
app = socketio.WSGIApp(sio)



@sio.on('connect')
def connect(*args):
    print(*args)
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
        if endure<min_silence:
            endure+=1
        elif len(frames)<=300:
            pass
        elif ticker:
            ticker=False
            sio.emit('infer',inference(frames).encode())
            frames=None
            endure=0
        else:
            frames=frames[-64:]
            endure=0
    else:
        ticker=True
        endure=0

if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 6006)), app)