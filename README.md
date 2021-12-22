# Final Project : I Can Read Your Voice
> 청력이 약하신 분들의 경우 전화 통화에 있어 청해력이 떨어질 수 있다. 이에 도움을 드리기 위해 통화 내용을 실시간으로 텍스트 변환하여 출력해 통화 내용의 이해를 보조하는 것을 목표로 Speech-To-Text 서비스 개발


## TEAM : 조지KLUE니
### Members  

김보성|김지후|김혜수|박이삭|이다곤|전미원|정두해
:-:|:-:|:-:|:-:|:-:|:-:|:-:
![image1][image1]|![image2][image2]|![image3][image3]|![image4][image4]|![image5][image5]|![image6][image6]|![image7][image7]
[Github](https://github.com/Barleysack)|[Github](https://github.com/JIHOO97)|[Github](https://github.com/vgptnv)|[Github](https://github.com/Tentoto)|[Github](https://github.com/DagonLee)|[Github](https://github.com/ekdub92)|[Github](https://github.com/Doohae)


## Main Task
정확도가 높지만 streaming에 특화되지 않은 모델을 streaming 처리가 가능한 형태로 바꾸기 위해 다음과 같이 두 가지 Data I/O 방식 개선  
1. Frame-Cut with Stride  
2. Long Silence Ignore  

### Frame-Cut with Stride
<img width="700" alt="stride" src="https://user-images.githubusercontent.com/80743307/147046780-8a1443d7-05c2-440f-a0e0-8292fed4975f.png">  

### Long Silence Ignore
<img width="700" alt="long silence" src="https://user-images.githubusercontent.com/80743307/147046792-dc98d6db-6634-4af5-aee2-ebbd591e3e61.png">  


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

## 사용 데이터셋 및 사전학습 모델

Pretrained : https://zenodo.org/record/4103351/files/asr_train_asr_transformer2_ddp_raw_bpe_valid.acc.ave.zip?download=1  
Datasets : https://aihub.or.kr/aidata/105  



## 정보

이름 – [@트위터 주소](https://twitter.com/dbader_org) – 이메일주소@example.com

XYZ 라이센스를 준수하며 ``LICENSE``에서 자세한 정보를 확인할 수 있습니다.

[https://github.com/yourname/github-link](https://github.com/dbader/)

## 기여 방법

1. (<https://github.com/yourname/yourproject/fork>)을 포크합니다.
2. (`git checkout -b feature/fooBar`) 명령어로 새 브랜치를 만드세요.
3. (`git commit -am 'Add some fooBar'`) 명령어로 커밋하세요.
4. (`git push origin feature/fooBar`) 명령어로 브랜치에 푸시하세요. 
5. 풀리퀘스트를 보내주세요.

<!-- Markdown link & img dfn's -->
[npm-image]: https://img.shields.io/npm/v/datadog-metrics.svg?style=flat-square
[npm-url]: https://npmjs.org/package/datadog-metrics
[npm-downloads]: https://img.shields.io/npm/dm/datadog-metrics.svg?style=flat-square
[travis-image]: https://img.shields.io/travis/dbader/node-datadog-metrics/master.svg?style=flat-square
[travis-url]: https://travis-ci.org/dbader/node-datadog-metrics
[wiki]: https://github.com/yourname/yourproject/wiki
