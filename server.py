from espnet2.tasks.asr import ASRTask
from espnet2.bin.asr_inference import Speech2Text
import numpy as np
import torch
import socket 
from pydub import AudioSegment
from time import time

HOST = '0.0.0.0'
PORT = 6006

model = Speech2Text(
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
model.to('cuda')
preprocess_fn = ASRTask.build_preprocess_fn(model.asr_train_args, False)

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

def inference(frame):
    start=time()
    frame = pcm2float(frame.get_array_of_samples())
    tens = preprocess_fn('1',{'speech':frame}) # input : (uid,dict)-> output : dict{'speech':array}
    input = torch.from_numpy(tens['speech'])
    output = model(input) # input : dict{'speech':Tensor,'speech_lengths':Tensor}
    end=time()
    lap=end-start
    
    return output[0][0],lap


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen()
print("Running...")
client_socket, addr = server_socket.accept()
print('Connected by', addr)
error_check=0
timepool=[]
while True:
    step = 100000
    buf = b''
    while True:
        try:
            data = client_socket.recv(step)
        except:
            error_check +=1
            if error_check == 1000:
                break
        # print('data : ', data.decode())
        # if data.decode() == 'End':
        #     exit(0)
        if len(data) <= 0:
            exit()
        
        if data:
            buf += data

        if len(buf) < step:
            step = step - len(data)
        elif len(buf) >= step:
            break

    audio_data = AudioSegment(buf, sample_width=2, frame_rate=16000, channels=1)
    inf_result = inference(audio_data)
    client_socket.sendall(inf_result[0].encode())
    timepool.append(inf_result[1])
    if len(timepool)==20:
        print(np.average(timepool))

client_socket.close()
server_socket.close()