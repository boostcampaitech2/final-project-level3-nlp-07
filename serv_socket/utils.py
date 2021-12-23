from espnet2.tasks.asr import ASRTask
from espnet2.bin.asr_inference import Speech2Text
import numpy as np
import torch


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

prev_frame = []

def inference(sio,frames,storage):
    frame=pcm2float(frames.get_array_of_samples())
    global prev_frame
    if len(prev_frame) != len(frame):
        prev_frame = frame
        print("Inference")
        tens=preprocess_fn('1',{'speech':frame}) #input : (uid,dict)-> output : dict{'speech':array}
        output=model(**{'speech':torch.from_numpy(tens['speech'])}) #input : dict{'speech':Tensor,'speech_lengths':Tensor}
        storage.update_min_silence(len(frames),len(output[0][0].replace(" ",'')))
        print(output[0][0])
        return sio.emit("infer",output[0][0])

class STORAGE:
    def __init__(self,):
        self.frames=None
        self.endure=0
        self.ticker=False
        self.mean_rms=[0,1]
        self.min_silence=6

    def initialize(self,):
        self.__init__()

    def get_values(self,):
        return self.frames,self.endure,self.ticker

    def save_values(self,frames,endure,ticker):
        self.frames=frames
        self.endure=endure
        self.ticker=ticker

    def update_min_silence(self,frames_len,char_num):
        self.min_silence=max(5,int(6*(1+((frames_len/1000*4.5/max(1,char_num)-1)*0.5))))
        # print('min_silence',self.min_silence)

    def get_mean_rms(self,rms):
        if not self.mean_rms[0]:
            self.mean_rms[0]=rms
        else:
            self.mean_rms[0]=((self.mean_rms[0]**2*self.mean_rms[1]+rms**2)/(self.mean_rms[1]+1))**0.5
        self.mean_rms[1]+=1
        thresh=0.4*self.mean_rms[0]
        # print("Thresh:",thresh)
        return max(330,thresh)