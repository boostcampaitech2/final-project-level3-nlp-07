from bentoml.adapters import FileInput,BaseInputAdapter
from pydub import AudioSegment
from pydub.utils import db_to_float
from multiprocessing import Process,Pipe
from espnet2.tasks.asr import ASRTask
from espnet2.bin.asr_inference import Speech2Text
import numpy as np
import torch
from bentoml import env, artifacts, api, BentoService
from bentoml.frameworks.pytorch import PytorchModelArtifact
from simplewrapper import CustomTorchModel




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




@env(infer_pip_packages=True)
@artifacts([PytorchModelArtifact('model')])
class SpeechInference(BentoService):
    '''
    Minimum prediction of ASR
    '''
    
    
    @api(input=FileInput())
    def predict(self,input):
        '''
        Inference code for audio input. 
        '''
        model = Speech2Text(
        asr_train_config="./espnet-asr/tools/.cache/espnet/92e47619a479aae2effafd3f190d40e7/exp/asr_train_asr_transformer2_ddp_raw_bpe/config.yaml",
        asr_model_file='./espnet-asr/tools/.cache/espnet/92e47619a479aae2effafd3f190d40e7/exp/asr_train_asr_transformer2_ddp_raw_bpe/valid.acc.ave_10best.pth',
        lm_train_config=None,
        lm_file=None,
        token_type=None,
        bpemodel=None,
        device='cuda',
        maxlenratio=0.0,
        minlenratio=0.0,
        dtype='float32',
        beam_size=20,
        ctc_weight=0.3,
        lm_weight=1.0,
        penalty=0.0,
        nbest=1,
    )
        preprocess_fn=ASRTask.build_preprocess_fn(
                    model.asr_train_args, False)
        frames=AudioSegment.from_wav(input)
        frames=pcm2float(frames.get_array_of_samples())
        print(frames)
        frames = preprocess_fn(frames)
        self.artifacts.model.eval()
        outputs = self.artifacts.model(frames)
        return outputs[0]
        
        
if __name__ == '__main__':
    
    bento_service = SpeechInference()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = Speech2Text(
        asr_train_config="./espnet-asr/tools/.cache/espnet/92e47619a479aae2effafd3f190d40e7/exp/asr_train_asr_transformer2_ddp_raw_bpe/config.yaml",
        asr_model_file='./espnet-asr/tools/.cache/espnet/92e47619a479aae2effafd3f190d40e7/exp/asr_train_asr_transformer2_ddp_raw_bpe/valid.acc.ave_10best.pth',
        lm_train_config=None,
        lm_file=None,
        token_type=None,
        bpemodel=None,
        device='cuda',
        maxlenratio=0.0,
        minlenratio=0.0,
        dtype='float32',
        beam_size=20,
        ctc_weight=0.3,
        lm_weight=1.0,
        penalty=0.0,
        nbest=1,
    )
    
    model = CustomTorchModel(model)
    
    bento_service.pack("model",model)
    saved_path = bento_service.save()
    print(saved_path)