import comm07_pb2
import comm07_pb2_grpc
from espnet2.tasks.asr import ASRTask
from espnet2.bin.asr_inference import Speech2Text
import numpy as np
import torch 
import grpc
from concurrent import futures
from pydub import AudioSegment








class Comm07Servicer(comm07_pb2_grpc.Comm07Servicer):
    ''' Provides methods for functions of this comm07 server.'''
    
    def __init__(self):
        self.model = Speech2Text(
                    asr_train_config="/opt/ml/final-project-level3-nlp-07/espnet-asr/tools/.cache/espnet/92e47619a479aae2effafd3f190d40e7/exp/asr_train_asr_transformer2_ddp_raw_bpe/config.yaml",
                    asr_model_file='/opt/ml/final-project-level3-nlp-07/espnet-asr/tools/.cache/espnet/92e47619a479aae2effafd3f190d40e7/exp/asr_train_asr_transformer2_ddp_raw_bpe/valid.acc.ave_10best.pth',
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
        self.preprocess_fn = ASRTask.build_preprocess_fn(self.model.asr_train_args, False)
        
    def pcm2float(self,sig, dtype='float32'):
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
    
    def pre_pipeline(self,audio):
        frame = AudioSegment(audio,sample_width=2, frame_rate=16000, channels=1)
        frame = self.pcm2float(frame.get_array_of_samples())
        tens = self.preprocess_fn('1',{'speech':frame}) # input : (uid,dict)-> output : dict{'speech':array}
        inputs = torch.from_numpy(tens['speech'])
        return inputs
    
    def inference(self,input):
        input=self.pre_pipeline(input)
        output = self.model(input) # input : dict{'speech':Tensor,'speech_lengths':Tensor}
        return output[0][0]
    
    def Talker(self,request,context):
        return comm07_pb2.InfReply(answer=self.inference(request.audio))
    

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    comm07_pb2_grpc.add_Comm07Servicer_to_server(Comm07Servicer(),server)
    server.add_insecure_port('[::]:6006')
    server.start()
    print("Server, on.")
    server.wait_for_termination()


if __name__ == '__main__':
    serve()

        
    
        
    