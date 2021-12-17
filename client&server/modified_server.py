from espnet2.tasks.asr import ASRTask
from espnet2.bin.asr_inference import Speech2Text
import numpy as np
import torch
import socket 
from pydub import AudioSegment
from multiprocessing import Process, Pipe

HOST = '0.0.0.0'
PORT = 6006
data = b''
model = Speech2Text(
        asr_train_config="./ref/mdl/exp/asr_train_asr_transformer2_ddp_raw_bpe/config.yaml",
        asr_model_file='./ref/mdl/exp/asr_train_asr_transformer2_ddp_raw_bpe/valid.acc.ave_10best.pth',
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
    frame = pcm2float(frame.get_array_of_samples())
    tens = preprocess_fn('1', {'speech':frame}) # input : (uid,dict)-> output : dict{'speech':array}
    input = torch.from_numpy(tens['speech'])
    print(type(input), input)
    output = model(input) # input : dict{'speech':Tensor,'speech_lengths':Tensor}
    print(output[0][0])
    return output[0][0]

def recv_function(client_socket):
    global data
    while 1:
        data = client_socket.recv()    
        if len(data) <= 0:
            exit()
    # step = 16384
    # while True:
    #     try:
    #         data = client_socket.recv(step)
    #     except:
    #         continue
    #     if len(data) <= 0:
    #         exit()
    #     buf += data

    #     if len(buf) < 16384:
    #         step = 16384 - len(data)
    #     elif len(buf) >= 16384:
    #         break

def send_function(client_socket):
    global data
    while 1:
        audio_data = AudioSegment(data, sample_width=2, frame_rate=16000, channels=1)
        client_socket.sendall(inference(audio_data).encode())


if __name__ == '__main__':
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print("Running...")
    client_socket, addr = server_socket.accept()
    print('Connected by', addr)

    # recv_conn, send_conn = Pipe()
    recv_process = Process(target=recv_function, args=(client_socket, recv_conn))
    send_process = Process(target=send_function, args=(client_socket, send_conn))

    recv_process.start()
    send_process.start()
    recv_process.join()
    send_process.join()

    client_socket.close()
    server_socket.close()
