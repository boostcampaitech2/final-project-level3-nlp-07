# Final Project : I Can Read Your Voice
> 청력이 약하신 분들의 경우 전화 통화에 있어 청해력이 떨어지는 경우가 있으며, 이에 도움을 드리기 위해 통화 내용을 실시간으로 텍스트 변환하여 출력해 통화 내용의 이해를 보조하는 것을 목표로 Speech-To-Text 서비스 개발


## TEAM : 조지KLUE니
### Members  

김보성|김지후|김혜수|박이삭|이다곤|전미원|정두해
:-:|:-:|:-:|:-:|:-:|:-:|:-:
![image1][image1]|![image2][image2]|![image3][image3]|![image4][image4]|![image5][image5]|![image6][image6]|![image7][image7]
[Github](https://github.com/Barleysack)|[Github](https://github.com/JIHOO97)|[Github](https://github.com/vgptnv)|[Github](https://github.com/Tentoto)|[Github](https://github.com/DagonLee)|[Github](https://github.com/ekdub92)|[Github](https://github.com/Doohae)

[image1]: https://avatars.githubusercontent.com/u/56079922?v=4
[image2]: https://avatars.githubusercontent.com/u/57887761?v=4
[image3]: https://avatars.githubusercontent.com/u/62708568?v=4
[image4]: https://avatars.githubusercontent.com/u/80071163?v=4
[image5]: https://avatars.githubusercontent.com/u/43575986?v=4
[image6]: https://avatars.githubusercontent.com/u/42200769?v=4
[image7]: https://avatars.githubusercontent.com/u/80743307?v=4  


### Contribution

`김보성`  Model Optimization • GRPC Communication

`김지후`  ASR Model Performance Comparison • Frontend

`김혜수`  Dataset Processing • Reference Paper Searching

`박이삭`  Audio Modeling(Data I/O) • Socket Communication

`전미원`  Socket Communication • Audio Model Structure Search

`정두해`  Punctuation Language Model • Dataset Processing

## Project Flow
![structure](https://user-images.githubusercontent.com/80743307/147149303-0057b8dd-1865-4b46-94b3-e77ac040ce9a.png)

## Main Tasks - Audio Modeling Part
Modeling Reference : https://github.com/hchung12/espnet-asr
- Pretrained : https://zenodo.org/record/4103351/files/asr_train_asr_transformer2_ddp_raw_bpe_valid.acc.ave.zip?download=1  
- Datasets : https://aihub.or.kr/aidata/105  
정확도가 높지만 streaming에 특화되지 않은 모델을 streaming 처리가 가능한 형태로 바꾸기 위해 오디오 파일 변환 과정 생략과 함께 아래와 같이 두 가지 Data I/O 방식 개선  
1. Frame-Cut with Stride : Silence 기준으로 frame이 나뉠 때 뒤 프레임의 초성 인식이 누락되는 경우 방지  
2. Long Silence Ignore : Silence가 길게 지속될 때 가짜 출력이 나오는 것을 방지  

### Frame-Cut with Stride
<img width="600" alt="stride" src="https://user-images.githubusercontent.com/80743307/147046780-8a1443d7-05c2-440f-a0e0-8292fed4975f.png">  

### Long Silence Ignore
<img width="600" alt="long silence" src="https://user-images.githubusercontent.com/80743307/147046792-dc98d6db-6634-4af5-aee2-ebbd591e3e61.png">  


## Main Tasks - Language Modeling Part
Modeling Reference : https://github.com/xashru/punctuation-restoration  
오디오 모델을 통해 출력된 텍스트 출력에는 온점(.), 반점(,), 물음표(?)와 같은 punctuation mark가 별도로 출력되지 않는 문제점을 발견하고 이러한 raw text가 입력으로 주어졌을 때 punctuation mark를 자동으로 삽입하는 언어 모델 개발
- Modeling : Pretrained "klue/roberta-small" + Bi-LSTM
- Datasets : AI Hub 감성대화말뭉치 https://aihub.or.kr/aidata/7978, AI Hub Ksponspeech https://aihub.or.kr/aidata/105

### LM Architecture
<img width="550" alt="Screen Shot 2021-12-22 at 11 51 53 PM" src="https://user-images.githubusercontent.com/80743307/147119074-07465635-035d-40f8-84a9-6c59f2a76b8d.png">

  


## Demonstration
![image](https://user-images.githubusercontent.com/80743307/147045534-f9119939-e9da-4c66-b29b-5af64d9291ca.png)  


## 설치 방법

Mac & Linux:

```sh
brew install portaudio
pip install -r requirements.txt
```

Windows:

```sh
sudo apt-get install portaudio
pip install -r requirements.txt
```




## 실행 방법

Client 구동
```sh
python client.py
```

서버 구동
```sh
python server.py
```
