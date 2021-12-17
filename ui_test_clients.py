from threading import *
from socket import *
from PyQt5.QtCore import Qt, pyqtSignal, QObject
import pyaudio
from multiprocessing import Process


class Signal(QObject):  
    recv_signal = pyqtSignal(str)
    disconn_signal = pyqtSignal()  
 
class ClientSocket:
 
    def __init__(self, parent):        
        self.parent = parent                
        self.recv = Signal()        
        self.disconn = Signal()        
        self.bConnect = False
        self.msg = ""
         
    def __del__(self):
        self.stop()
 
    def connectServer(self, ip, port):
        self.client = socket(AF_INET, SOCK_STREAM)           
 
        try:
            self.client.connect( (ip, port) )
        except Exception as e:
            print('Connect Error : ', e)
            return False
        else:
            self.bConnect = True
            self.sends = Thread(target=self.send,args=(self.client,))
            self.recvs = Thread(target=self.receive, args=(self.client,))
            
            self.sends.start()
            self.recvs.start()
            
            
            print('Connected')
 
        return True
 
    def stop(self):
        
        self.bConnect = False       
        if hasattr(self, 'client'):            
            self.client.close()
            del(self.client)
            print('Client Stop') 
            exit(0)
 
    def receive(self, client):
        
        while self.bConnect:            
            try:
                recv = client.recv(1024)
                
            except Exception as e:
                # print('Recv() Error :', e)                
                self.bConnect=False
            else:                
                msg = recv.decode('utf-8')
                if msg:
                    self.msg = msg
                    self.recv.recv_signal.emit(msg)
                    print('[RECV]:', msg)
        
 
    def send(self, client):
        print("entered send\n")
        CHUNK= 1024
        audio = pyaudio.PyAudio()
        error_check =0
        while self.bConnect:   
            stream = audio.open(format=pyaudio.paInt16, channels=1,
                    rate=16000, input=True,
                    frames_per_buffer=CHUNK)
            
            try:
                data = stream.read(CHUNK,exception_on_overflow=False)
                client.send(data)
            except Exception as e:
                # print('Send() Error : ', e)
                error_check +=1
                if error_check == 10:
                    print("program ends due to the connection issue. Check your code")
                    self.stop()
                    return
        data="End"
        client.send(data.encode())

        if not self.bConnect:
            return
 
        
