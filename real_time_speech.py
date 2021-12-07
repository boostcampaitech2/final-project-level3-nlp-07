import json
import pyaudio
import wave
import soundfile as sf
import array
import numpy as np
import torch
from speechbrain.pretrained import EncoderDecoderASR

CHUNK = 1024
FORMAT = pyaudio.paInt16
# Even if your default input is multi channel (like a webcam mic),
# it's really important to only record 1 channel, as the STT service
# does not do anything useful with stereo. You get a lot of "hmmm"
# back.
CHANNELS = 1
# Rate is important, nothing works without it. This is a pretty
# standard default. If you have an audio device that requires
# something different, change this.
RATE = 44100
MAX_RECORD = 60
REC_DURATION = 3
FINALS = []
LAST = None
FORMAT = pyaudio.paInt16
WAVFILE = "output.wav" #Temporary file name

def read_audio(timeout, model):
    """Read audio and sent it to the websocket port.
    This uses pyaudio to read from a device in chunks and send these
    over the websocket wire.
    """
    global RATE
    p = pyaudio.PyAudio()
    # NOTE(sdague): if you don't seem to be getting anything off of
    # this you might need to specify:
    #
    #    input_device_index=N,
    #
    # Where N is an int. You'll need to do a dump of your input
    # devices to figure out which one you want.
    RATE = int(p.get_default_input_device_info()['defaultSampleRate'])
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("* recording")
    rec = timeout or MAX_RECORD

    frames = []

    for i in range(0, int(RATE / CHUNK * rec)):
        data = stream.read(CHUNK)
        # print("Sending packet... %d" % i)
        # NOTE(sdague): we're sending raw binary in the stream, we
        # need to indicate that otherwise the stream service
        # interprets this as text control messages.
        frames.append(data)
        if i > 0 and i % (int(RATE/CHUNK) * REC_DURATION) == 0:
            pcm = array.array('h')
            pcm.frombytes(b''.join(frames))
            # normalize
            norm = np.linalg.norm(pcm)
            normal_array = pcm / norm
            # numpy to tensor conversion
            normal_array = torch.Tensor(normal_array)
            # reset frames
            frames.clear()
            print(f'normal array: {normal_array}')
            print(f'shape: {normal_array.shape}')
            print(model.real_time_predict(normal_array, RATE))

    # Disconnect the audio stream
    stream.stop_stream()
    stream.close()
    print("* done recording")

    ### Generate .wav file
    # wf = wave.open(WAVFILE, 'wb')
    # wf.setnchannels(CHANNELS)
    # wf.setsampwidth(p.get_sample_size(FORMAT))
    # wf.setframerate(RATE)
    # wf.writeframes(b''.join(frames))
    # wf.close()

    ### Generate tensor from audio output (normalized version)
    # pcm = array.array('h')
    # pcm.frombytes(b''.join(frames))
    # norm = np.linalg.norm(pcm)
    # normal_array = pcm / norm
    # normal_array = torch.Tensor(normal_array)

    # print(model.real_time_predict(normal_array, RATE))

    # ... and kill the audio device
    p.terminate()


def decode_audio(input_file):
    signal, sr = sf.read(input_file)
    return (signal, sr)


def main():
    asr_model = EncoderDecoderASR.from_hparams(source="ddwkim/asr-conformer-transformerlm-ksponspeech", savedir="pretrained_models/asr-conformer-transformerlm-ksponspeech",  run_opts={"device":"cpu"})
    read_audio(60, asr_model)
    # signal, sr = decode_audio(WAVFILE)
    # print(f'signal {signal}')
    # print(f'sr {sr}')


if __name__ == "__main__":
    main()