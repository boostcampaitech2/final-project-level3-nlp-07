import comm07_pb2
import comm07_pb2_grpc
from espnet2.tasks.asr import ASRTask
from espnet2.bin.asr_inference import Speech2Text
import numpy as np
import torch 
import grpc
from concurrent import futures
from pydub import AudioSegment
from punk_model import DeepPunctuation
from config import *
import json






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
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.tokenizer = AutoTokenizer.from_pretrained('klue/roberta-small')
        self.token_style = 'roberta'
        self.punk_model = DeepPunctuation('klue/roberta-small', freeze_bert=False, lstm_dim=-1).to(self.device)
        self.punk_model.load_state_dict(torch.load(model_save_path))
        self.punk_model.eval()
        
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
    
    def punk_inference(self,input):
        words_original_case = input.split()
        words = input.split()
        word_pos = 0
        sequence_len = 256
        result = ""
        decode_idx = 0
        punctuation_map = {0: '', 1: ',', 2: '.', 3: '?'}

        while word_pos < len(words):
            x = [TOKEN_IDX['roberta']['START_SEQ']]
            y_mask = [0]

            while len(x) < sequence_len and word_pos < len(words):
                tokens = self.tokenizer.tokenize(words[word_pos])
                if len(tokens) + len(x) >= sequence_len:
                    break
                else:
                    for i in range(len(tokens) - 1):
                        x.append(self.tokenizer.convert_tokens_to_ids(tokens[i]))
                        y_mask.append(0)
                    x.append(self.tokenizer.convert_tokens_to_ids(tokens[-1]))
                    y_mask.append(1)
                    word_pos += 1
            x.append(TOKEN_IDX['roberta']['END_SEQ'])
            y_mask.append(0)
            if len(x) < sequence_len:
                x = x + [TOKEN_IDX['roberta']['PAD'] for _ in range(sequence_len - len(x))]
                y_mask = y_mask + [0 for _ in range(sequence_len - len(y_mask))]
            attn_mask = [1 if token != TOKEN_IDX['roberta']['PAD'] else 0 for token in x]

            x = torch.tensor(x).reshape(1,-1)
            y_mask = torch.tensor(y_mask)
            attn_mask = torch.tensor(attn_mask).reshape(1,-1)
            x, attn_mask, y_mask = x.to(self.device), attn_mask.to(self.device), y_mask.to(self.device)

            with torch.no_grad():
                    y_predict = self.punk_model(x, attn_mask)
                    y_predict = y_predict.view(-1, y_predict.shape[2])
                    y_predict = torch.argmax(y_predict, dim=1).view(-1)
            for i in range(y_mask.shape[0]):
                if y_mask[i] == 1:
                    result += words_original_case[decode_idx] + punctuation_map[y_predict[i].item()] + ' '
                    decode_idx += 1
        
        return result

    def Talker(self,request,context):
        return comm07_pb2.InfReply(answer=self.inference(request.audio))
    
    def get_punkt(self,request,context):
        request.answer.to(JSON)
        return comm07_pb2.PunkedReply(punked=self.punk_inference(request.answer))

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    comm07_pb2_grpc.add_Comm07Servicer_to_server(Comm07Servicer(),server)
    server.add_insecure_port('[::]:6006')
    server.start()
    print("Server, on.")
    server.wait_for_termination()


if __name__ == '__main__':
    serve()

        
    
        
    
