import pyaudio
import socket
from multiprocessing import Process


def send_function(client_socket):
    CHUNK = 19683
    audio = pyaudio.PyAudio()
    stream = audio.open(format=pyaudio.paInt16, channels=1,
                    rate=16000, input=True,
                    frames_per_buffer=CHUNK)
    while 1:
        data = stream.read(CHUNK, exception_on_overflow=False)
        client_socket.send(data)
    
    
def recv_function(client_socket):
    while 1:
        output = client_socket.recv(4096)
        print(output.decode(), '\n')

if __name__ == "__main__":
    HOST = '101.101.208.204'
    PORT = 6018

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))

    # start Recording
    print("recording start")

    send_process = Process(target=send_function, args=(client_socket,))
    recv_process = Process(target=recv_function, args=(client_socket,))

    send_process.start()
    recv_process.start()
    send_process.join()
    recv_process.join()

    client_socket.close() 
