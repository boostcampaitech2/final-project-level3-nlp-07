from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import sys
import ui_test_clients as client
 
 
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
 
port = 5614
 
class CWidget(QWidget):
    
    def __init__(self):
        super().__init__()  
        self.c = client.ClientSocket(self)
        self.initUI()
 
 
    def __del__(self):
        self.c.stop()
 
 
    def initUI(self):
        self.setWindowTitle('Call!')
        self.topLabel = QLabel('PyApp_prototype_v1.0')
        self.te=QTextEdit() 
        self.te.setText("Awaiting Call....")
        
        box = QVBoxLayout()
        
        self.btn = QPushButton('통화 연결')
        self.btn.setStyleSheet("background-color: Green")
        
        self.btn.clicked.connect(self.connectClicked)
        self.c.recv.recv_signal.connect(self.answerReceived) 
        
        box.addWidget(self.topLabel)
        box.addWidget(self.btn)
        box.addWidget(self.te)
      
        # 전체 배치
        self.setLayout(box)
        self.show()
    
    def answerReceived(self):
        buffer = self.c.msg
        self.te.append(buffer)
    
    
    def connectClicked(self):
        if self.c.bConnect == False:
            ip = '118.67.135.206'
            port = 6013
            self.c.connectServer(ip,int(port))
            self.btn.setStyleSheet("background-color: Red")   
            self.btn.setText('끊기')
            self.c.bConnect=True
        else:
            self.c.stop()
            exit()

            
    def updateDisconnect(self):
        self.btn.setText('Call')
 
 
    def sendMsg(self):
        sendmsg = self.sendmsg.toPlainText()       
        self.c.send(sendmsg)        
        self.sendmsg.clear()
 
 
    def endcall(self):
        self.c.disconn = "ENDCALL"
 
 
    def closeEvent(self, e):
        self.c.stop()       
 
 
 
if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = CWidget()
    sys.exit(app.exec_())