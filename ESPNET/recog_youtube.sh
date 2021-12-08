#!/bin/bash

# Copyright  2020  ETRI (author: Hoon Chung)
# Apache 2.0
for v in 6
do
    log() {
        local fname=${BASH_SOURCE[1]##*/}
        echo -e "$(date '+%Y-%m-%dT%H:%M:%S') (${fname}:${BASH_LINENO[0]}:${FUNCNAME[1]}) $*"
    }

    download_dir="/opt/ml/espnet-asr/tools/testdown/"
    length=5
    url="yes_$v"
    ngpu=0
    mdl=./mdl/ksponspeech.zip
    config=../conf/decode_asr.yaml
    output=output

    stage=1
    stop_stage=100


    log "$0 $*"

    . utils/parse_options.sh

    if [ $# -ne 0 ]; then 
        log "${help_message}"
        log "Error: No positional arguments are required."
        exit 2
    fi

    [ -z "${url}" ] && { log "${help_message}"; log "Error: --url is required"; exit 2; };
    [ -z "${length}" ] && { log "${help_message}"; log "Error: --length is required"; exit 2; };
    [ -z "${mdl}" ] && { log "${help_message}"; log "Error: --mdl is required"; exit 2; };

    split_dir=${download_dir}/split
    wav_scp=${download_dir}/wav.scp

    [ ! -d ${split_dir} ] && mkdir -p ${split_dir}

    if [ ${stage} -le 1 ] && [ ${stop_stage} -ge 1 ]; then

        [[ -f "${wav_scp}" ]] && rm ${wav_scp}

        youtube-dl --extract-audio --audio-format wav -o "${download_dir}/${url}.%(ext)s" "${url}"
        sox -t wav "${download_dir}/${url}.wav" -r 16000 -t wav -c 1 "${split_dir}/${url}.wav" trim 0 ${length}  : newfile : restart

        for wav_file in $(find -L $split_dir -iname "*.wav" | sort); do
        key=$(basename "${wav_file%.*}")
        echo "$key $wav_file" >> $wav_scp
        done  
    fi

    if [ ${stage} -le 2 ] && [ ${stop_stage} -ge 2 ]; then
        python3 ../bin/asr_inference.py \
        --ngpu ${ngpu} \
        --mdl ${mdl} \
        --wav_scp ${wav_scp} \
        --config ${config} \
        --output_dir ${output}/${url}
    fi
done
