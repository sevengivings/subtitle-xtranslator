# subtitle-xtranslator
[![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/sevengivings/subtitle-xtranslator/blob/master/README.en.md)

A Python script to extract text from audio/video and translate subtitle

OpenAI의 Whisper와 자막을 위해 조금 변형한 stable-ts를 사용하여 비디오 AI 음성 인식 및 번역 과정을 자동화하기 위한 파이썬 프로그램입니다. 

위스퍼(https://github.com/openai/whisper)의 최첨단 AI 범용 음성인식 기능 덕분에 동영상 자막 제작이 매우 편리해졌고, 구글과 네이버는 인공지능 기반의 번역 서비스를 제공하고 있습니다.

이 프로그램은 비디오로부터 자막을 만들기 위해 위의 음성인식 및 번역 기능을 결합한 프로그램입니다. 

[기능과 특징] 

- 동영상에서 자막을 만들 수 있는 stable-ts 또는 Whisper 지원
- 구글 클라우드 번역(ADC 또는 API KEY) 또는 네이버 파파고 번역 서비스 지원
- 의미 없는 짧은 자막이나 반복되는 자막 제거 지원

[한계]

음성 인식이 완전하지 않아서 누락되는 음성이나 잘못 인식될 수 있습니다. 프로페셔널한 용도로 사용은 권장하지 않습니다.
stable-ts와 whisper 명령어로 했을 때와 이 프로그램을 사용했을 때, Whisper WebUI를 썼을 때 각각 자막의 품질이나 개수가 다를 수 있습니다(최적화 파라미터가 많아서 모두 알 수 없으며, 참고로 stable-ts는 자막 추출 용도로 최적화한 프로그램이기도 하지만 Whisper 오리지널에 비해 인식 누락이 있는 편입니다. 하지만, 없는데 추출된 귀신 소리, 무의미한 반복, 뒷부분 추출 안되는 등의 문제는 적은 편입니다.)

[관련 프로그램 링크]

stable-ts : GitHub - jianfch/stable-ts: ASR with reliable word-level timestamps using OpenAI's Whisper(https://github.com/jianfch/stable-ts)
Whisper : General-purpose speech recognition model(https://github.com/openai/whisper)

[사용법] 

이 스크립트를 실행하려면 몇 가지 전제 조건을 준비해야 합니다(아래 섹션 참조). 
```
(venv) C:\Users\loginid> python .\subtitle-xtranslator.py --framework=stable-ts --model=medium --device=cuda --audio_language=ja --subtitle_language=ko --skip_textlength=1 --translator none --text_split_size=1000 '.\inputvideo1.mp4' '.\inputvideo2.mp4' '.\inputvideo3.mp4'
```

실제로 위 명령의 기본값을 그대로 쓴 것이라서 인자(아규먼트)를 생략해도 됩니다. 물론 한국어로 번역을 하기 위해서는 --translator google 이나 --translator papago 를 생략하면 안됩니다. 
```
(venv) C:\Users\loginid> python .\subtitle-xtranslator.py '.\inputvideo1.mp4' '.\inputvideo2.mp4' '.\inputvideo3.mp4'
```

이 프로그램에 번역을 위해 API 키를 제공하려면 환경 변수를 사용해야 합니다. 

파파고용 API 키 제공 방법은 다음과 같습니다. 먼저 개발자 등록을 하여 테스트 계정을 설정해야 합니다. 하루에 무료로 제공되는 번역량은 1만자입니다. 상용으로 전환할 경우 백만자당 2만원이 청구되는 것 같습니다. 

```
(venv) C:\Users\loginid> Set-Item -Path env:NAVER_CLOUD_ID -Value "your_id" 
(venv) C:\Users\loginid> Set-Item -Path env:NAVER_CLIENT_SECRET -Value "your_password"
```

Google의 경우 ADC(애플리케이션 기본 자격 증명 - 특수 파일 생성) 또는 API 키를 선택할 수 있으며, 다음은 API 키에 대한 설명입니다. ADC는 로컬 컴퓨터에 클라우드 사용을 위한 인증 파일을 만드는 방법이라서 API 키 유출을 걱정할 필요가 없습니다. 물론 해당 파일이 유출되면 안되겠지요... 다소 번거롭지만 소스코드에 API 키를 내장하는 것보다는 아래와 같이 환경 변수로 지정해 주는 것이 보안에 더 좋아 보입니다. 다만, 해당 세션에서만 작동하므로 컴퓨터를 껐다 켜거나 파워쉘과 venv를 다시 로딩했다면 또 해주어야 하는 번거로움은 있습니다. 

구글 클라우드 번역을 이용하려면 구글 클라우드 콘솔에서 프로젝트를 새로 하나 만들고 Google Cloud Translation서비스를 선택하고 ADC를 설정하거나 API key를 만들어야 합니다. 혹은 API key만 받는 방법은 좀 더 간단해 보입니다(https://urame.tistory.com/entry/GoogleGCP-Translation-API%EB%B2%88%EC%97%AD-API-%EC%8B%A0%EC%B2%AD-%EB%B0%8F-PYTHON-%ED%85%8C%EC%8A%A4%ED%8A%B8). 

- https://console.cloud.google.com/
- https://cloud.google.com/translate/docs/basic/translating-text
- https://cloud.google.com/docs/authentication/provide-credentials-adc?hl=ko#local-dev 

비용 : 요금은 Cloud Translation에 제공된 문자 수로 조정됩니다. 예를 들어 한 달에 575,000자를 전송하여 처리한 경우 $1.50가 청구됩니다. 처음 500,000자는 무료이고 다음 75,000자는 $20,000(영문 기준) 요율로 청구됩니다.

```
(venv) C:\Users\loginid> Set-Item -Path env:GOOGLE_API_KEY -Value "your_api_key"
```

[윈도우10/11 기준 준비 작업]

1.파이썬 설치

파이썬이 현재 3.11.3이 릴리즈 중이지만, 최신 버전이 그다지 중요하지 않으므로 아래 버전으로 설치를 합니다. 윈도우11의 명령 프롬프트나 파워쉘 아무데서나 python이라고 치면 실행될 수 있도록 하는 것이 목표입니다.

https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe

2.CUDA 설치

브라우저로 편리하게 이용이 가능한 Whisper WebUI판에서는 cuda 11.7을 requirements.txt에 명시를 해 놓아서 같은 버전으로 설치해 봅니다. 설치 완료 후 cuda가 설치되어 있는 지 확인하려면 파워쉘(Windows PowerShell 앱)을 띄우고, nvidia-smi 라고 명령을 내려 보면 알 수 있습니다.

https://developer.nvidia.com/cuda-11-7-1-download-archive?target_os=Windows&target_arch=x86_64&target_version=11&target_type=exe_local

3.파워쉘 실행

윈도우키를 누르고 R키를 누르면 좌측에 실행 창이 나타납니다. 이곳에 "powershell"을 입력하고 확인을 누르면 파워쉘을 실행할 수 있습니다(이외에 다양한 방법으로 실행 가능).

파워쉘 창에서 python이라고 치고 [Enter]키를 누르면 다음과 같이 응답이 나와야 합니다.

```
PS C:\Users\login_id> python

Python 3.10.11 (tags/v3.10.11:7d4cc5a, Apr  5 2023, 00:38:17) [MSC v.1929 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license" for more information.
>>>
```

위 >>> 에서 나오기 위해서는 exit() 을 입력합니다.

4.VENV 환경 만들어 주기 및 파이썬 패키지 설치하기

파이썬은 패키지를 필요할 때마다 설치하게 되는데, 시스템에 설치된 파이썬에 그냥 설치하다보면 가끔 뭔가가 꼬이게 되고 문제가 가끔 생기는데 아주 머리가 아픈 경우가 있습니다. 물론, 이 기능만 이용하겠다하면 상관없지만 그래도 제거가 편하도록 가상의 환경을 만들어 줍니다.

아래는 사용자 디렉터리에 그냥 설치했는데 다른 드라이브나 폴더에 해도 됩니다(주의: 경로 상에 한글이 없는 곳에서 작업해주세요. 혹시 윈도우 로그인명이 한글이라면 다른 곳에 설치가 필요합니다.)

용량이 4.5GB가량 되므로 적절한 디스크 드라이브에 설치하시면 좋습니다.

```
PS C:\Users\login_id> python -m venv venv 
PS C:\Users\login_id> .\venv\Scripts\Activate.ps1
```

위와 같이 해주면, 가상 환경 준비가 끝납니다. 처음에 실행할 때 보안 관련 문의가 나오는데 Always를 선택해 줍니다. venv가 성공적으로 실행되면 프롬프트가 바뀝니다. 

이 상태에서 향후 필요한 패키지들을 설치합니다.

```
(venv) PS C:\Users\login_id> pip install -U git+https://github.com/jianfch/stable-ts.git
(venv) PS C:\Users\login_id> pip install git+https://github.com/openai/whisper.git
(venv) PS C:\Users\login_id> pip install google-cloud-translate==2.0.1
```

5.GPU버전의 pyTorch설치

위 과정이 끝나면 바로 쓸 수 있기는 한데, CPU버전의 pyTorch가 설치되는 것 같습니다. 이번에는 GPU버전의 토치를 설치합니다. 아래 예는 cu117로 되어 있는데 cu118로 해도 잘 됩니다.

```
(venv) PS C:\Users\login_id> pip install torch==2.0.1+cu117 --extra-index-url https://download.pytorch.org/whl/cu117
```

잘 설치가 되었는 지 확인하기 위해 python을 입력하고 간단한 프로그램을 짭니다. (주의) "version" 은 글자의 좌우에 언더바가 2개씩 있습니다.

```
(venv) PS C:\Users\login_id> python
Python 3.10.11 (tags/v3.10.11:7d4cc5a, Apr  5 2023, 00:38:17) [MSC v.1929 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license" for more information.
>>> import torch
>>> print(torch.__version__)
2.0.1+cu117
>>> exit()
```

6.FFMPEG 설치 및 파이썬 인터프리터 상태에서 영상 자막 만들기

영상에서 음성을 추출을 하다보니 외부 프로그램이 하나 필요합니다.

https://www.gyan.dev/ffmpeg/builds/#release-builds 에서 ffmpeg-release-essentials.zip 을 받아서 압축 해제한 후, 앞으로 작업할 디렉터리나 환경변수에서 Path가 설정되어 있는 곳에 복사하여도 됩니다. 그냥 C:\Users\login_id\venv\Scripts 밑에 복사하는 것이 속편하겠습니다. 

7.짧은 영상을 파이썬 코드로 추출해 보기 

짧은 영상 하나를 테스트하는 과정을 보여드립니다(실제로는 중간에 warning이 나오지만 작동에 문제는 없습니다).
```
(venv) PS C:\Users\login_id> python
Python 3.10.11 (tags/v3.10.11:7d4cc5a, Apr  5 2023, 00:38:17) [MSC v.1929 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license" for more information.
>>> import torch
>>> import stable_whisper
>>> model = stable_whisper.load_model("small", device="cuda")
>>> result = model.transcribe(verbose=True, word_timestamps=False, language="ko", audio="20220902_131203.mp4")
[00:12.800 --> 00:16.080]  아 아까 딱 찍었어야 되는데
[00:19.580 --> 00:21.580]  불행랑을 치는 걸 찍었어야 되는데
[00:30.000 --> 00:34.980]  진출하되겠지
>>> result.to_srt_vtt("20220902_131203.srt")
Saved: C:\Users\login_id\20220902_131203.srt
>>> exit()
```
word_timestamps=True가 기본 값인데, 말하는 중 단어가 하이라이트 되는 기능이 있습니다. 2GB의 VRAM을 가진 그래픽카드라서 small 모델로 했는데, 몇 마디(불행랑->줄행랑, 진출하되겠지는 그냥 파도 소리가 자막화 되었네요)는 잘못 인식했네요. 8GB VRAM이라면 medium으로 하면 됩니다.
