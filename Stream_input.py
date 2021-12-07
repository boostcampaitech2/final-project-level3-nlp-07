import pyaudio
import wave
from pydub import AudioSegment, silence
from pydub.utils import db_to_float
import time
from collections import deque
import asyncio


myaudio=deque()

def stream_input():
    #AUDIO INPUT
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    CHUNK = 1024
    RECORD_SECONDS = 1
    WAVE_OUTPUT_FILENAME = "output.wav"
    SILENCE_THRESH = db_to_float(-40)
    audio = pyaudio.PyAudio()

    # start Recording
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    frames_per_buffer=CHUNK)

    min_silence=int(RATE/CHUNK*0.1)
    endure=0

    while 1:
        print ("recording")

        while 1:
            data = stream.read(CHUNK)
            sound=AudioSegment(data=data,sample_width=2,frame_rate=RATE,channels=CHANNELS)

            try:
                frames += sound
            except:
                frames=sound   

            if sound.rms<SILENCE_THRESH*sound.max_possible_amplitude:
                if endure<min_silence:
                    endure+=1
                else:
                    break
            else:
                endure=0

        myaudio.append(frames)
        del frames



