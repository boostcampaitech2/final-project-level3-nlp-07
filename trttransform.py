from espnet2.tasks.asr import ASRTask
from pydub.audio_segment import AudioSegment
from ESPNET.asr_inference import Speech2Text
import numpy as np
import torch
import torch.onnx
from modelwrapping import TestWrapperModel
import torch.nn as nn
import onnx

ONNX_FILE_PATH = '/opt/ml/final-project-level3-nlp-07/onnxtrans.onnx'

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

model = Speech2Text(
        asr_train_config="/opt/ml/final-project-level3-nlp-07/espnet-asr//tools/.cache/espnet/92e47619a479aae2effafd3f190d40e7/exp/asr_train_asr_transformer2_ddp_raw_bpe/config.yaml",
        asr_model_file='/opt/ml/final-project-level3-nlp-07/espnet-asr/tools/.cache/espnet/92e47619a479aae2effafd3f190d40e7/exp/asr_train_asr_transformer2_ddp_raw_bpe/valid.acc.ave_10best.pth',
        lm_train_config=None,
        lm_file=None,
        token_type=None,
        bpemodel=None,
        device='cuda',
        maxlenratio=0.0,
        minlenratio=0.0,
        dtype='float32',
        beam_size=20,
        ctc_weight=0.3,
        lm_weight=1.0,
        penalty=0.0,
        nbest=1,
    )

test_model = TestWrapperModel(model)
test_model.eval()


SOUND_PATH = "/opt/ml/final-project-level3-nlp-07/espnet-asr/tools/testdown/split/yes_6001.wav"
preprocess_fn=ASRTask.build_preprocess_fn(model.asr_train_args, False)
sound= AudioSegment.from_wav(SOUND_PATH)

sound = pcm2float(sound.get_array_of_samples())
sound= preprocess_fn('1',{'speech':sound})
sound =torch.from_numpy(sound['speech'])



onnx_model = torch.onnx.export(test_model,sound,"letussleep.onnx",input_names=['input'],
                  output_names=['output'],export_params=True,opset_version=10)

print(onnx.checker.check_model(onnx_model))
