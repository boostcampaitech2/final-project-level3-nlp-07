# Final Project : I Can Read Your Voice
> 청력이 약하신 분들의 경우 전화 통화에 있어 청해력이 떨어지는 경우가 있으며, 이에 도움을 드리기 위해 통화 내용을 실시간으로 텍스트 변환하여 출력해 통화 내용의 이해를 보조하는 것을 목표로 실시간 스트리밍 Speech-To-Text 서비스 개발


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

`김보성`  Model Optimization • gRPC Communication

`김지후`  ASR Model Performance Comparison • Frontend

`김혜수`  Dataset Processing • Reference Paper Searching

`박이삭`  Auto Speech Recognition Modeling (Data I/O) • Socket Communication

`전미원`  Socket Communication • Audio Model Structure Search

`정두해`  Auto Punctuation Language Modeling • Dataset Processing

## Project Flow
<img width="750" alt="Screen Shot 2021-12-23 at 11 08 07 PM" src="https://user-images.githubusercontent.com/80743307/147251548-d99a3e7b-3df3-4b21-8a05-ff87a31c5f8b.png">


## Main Tasks - Audio Modeling Part
Modeling Reference : https://github.com/hchung12/espnet-asr
- Pretrained : https://zenodo.org/record/4103351/files/asr_train_asr_transformer2_ddp_raw_bpe_valid.acc.ave.zip?download=1  
- Datasets : https://aihub.or.kr/aidata/105  


정확도가 높지만 streaming에 특화되지 않은 모델을 streaming 처리가 가능한 형태로 바꾸기 위해 오디오 파일 변환 과정 생략과 함께 아래와 같은 방식으로 Data I/O 방식 개선  

### Definition of "Frame" in conversation
<img width="600" alt="Screen Shot 2021-12-24 at 2 31 36 AM" src="https://user-images.githubusercontent.com/80743307/147274395-6e9fba21-1ebb-482c-81c8-bb7bf521c6a4.png">



### Implementation 1: Silence Threshold
<img width="600" alt="Screen Shot 2021-12-24 at 2 20 51 AM" src="https://user-images.githubusercontent.com/80743307/147273397-ff275569-b723-4dc3-bad7-00a8b58d71da.png">

### Implementation 2: Silence Length
<img width="600" alt="Screen Shot 2021-12-24 at 2 20 45 AM" src="https://user-images.githubusercontent.com/80743307/147273409-790f4d49-7c3b-4d99-9c2e-24885adc02a8.png">

### Implementation 3: Long Silence Ignore
<img width="600" alt="Screen Shot 2021-12-24 at 2 21 11 AM" src="https://user-images.githubusercontent.com/80743307/147273427-c2e82346-f137-43fc-b7c3-b8df26338367.png">

### Implementation 4: Frame-Cut with Overlap
<img width="600" alt="Screen Shot 2021-12-24 at 2 21 03 AM" src="https://user-images.githubusercontent.com/80743307/147273475-d20c2411-aa1c-41f0-827e-c20fdf1b273e.png">




## Main Tasks - Language Modeling Part
Modeling Reference : https://github.com/xashru/punctuation-restoration  
- Modeling : Pretrained "klue/roberta-small" + Bi-LSTM
- Datasets : AI Hub 감성대화말뭉치 https://aihub.or.kr/aidata/7978, AI Hub Ksponspeech https://aihub.or.kr/aidata/105  


오디오 모델을 통해 출력된 텍스트 출력에는 온점(.), 반점(,), 물음표(?)와 같은 punctuation mark가 별도로 출력되지 않는 문제점을 발견하고 이러한 raw text가 입력으로 주어졌을 때 punctuation mark를 자동으로 삽입하는 언어 모델 개발  

### LM Architecture
<img width="550" alt="Screen Shot 2021-12-22 at 11 51 53 PM" src="https://user-images.githubusercontent.com/80743307/147119074-07465635-035d-40f8-84a9-6c59f2a76b8d.png">

  


## Demonstration
<img width="964" alt="Screen Shot 2021-12-24 at 12 05 15 PM" src="https://user-images.githubusercontent.com/80743307/147311038-dd94dedf-e644-43fd-84a5-b106e8b90bc6.png">



**시연 영상**

[![Demo Video](https://img.youtube.com/vi/J1TNSOZUbfU/0.jpg)](https://www.youtube.com/watch?v=J1TNSOZUbfU "너의 목소리가 보여 시연 연상")


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
