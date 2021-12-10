import torch
import torch.nn as nn
from ESPNET.asr_inference import Speech2Text




class TestWrapperModel(nn.Module):
    def __init__(self, model):
        super(TestWrapperModel,self).__init__()
        
        self.s2t = model
        
    def forward(self,x):
        return self.s2t(x)
    
    
        
    