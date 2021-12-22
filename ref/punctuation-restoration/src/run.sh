# Example script for training
python train.py \
--cuda=True \
--pretrained_model=xlm-roberta-base \
--freeze_bert=False \
--lstm_dim=-1 \
--language=english \
--seed=1 \
--lr=5e-6 \
--epoch=10 \
--use_crf=False \
--augment_type=all  \
--augment_rate=0 \
--alpha_sub=0.4 \
--alpha_del=0.4 \
--data_path=/opt/ml/ \
--save_path=out