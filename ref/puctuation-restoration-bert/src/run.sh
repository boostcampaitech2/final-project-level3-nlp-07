# Example script for training
python train.py \
--cuda=True \
--pretrained_model=klue/roberta-small \
--freeze_bert=False \
--lstm_dim=-1 \
--seed=1 \
--lr=5e-6 \
--epoch=10 \
--use_crf=False \
--augment_type=all  \
--augment_rate=0.1 \
--alpha_sub=0.4 \
--alpha_del=0.4 \
--data_path=../data/ \
--save_path=output