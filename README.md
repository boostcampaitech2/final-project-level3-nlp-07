# Final Project : I Can Read Your Voice
> 청력이 약하신 분들의 경우 전화 통화에 있어 청해력이 떨어질 수 있다. 이에 도움을 드리기 위해 통화 내용을 실시간으로 텍스트 변환하여 출력해 통화 내용의 이해를 보조하는 것을 목표로 Speech-To-Text 서비스를 개발한다.


![](../header.png)

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

Pretrained : "https://zenodo.org/record/4103351/files/asr_train_asr_transformer2_ddp_raw_bpe_valid.acc.ave.zip?download=1"  
Datasets : https://aihub.or.kr/aidata/105  



## 개발 환경 설정

모든 개발 의존성 설치 방법과 자동 테스트 슈트 실행 방법을 운영체제 별로 작성합니다.

```sh
make install
npm test
```

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
