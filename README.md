# subtitle-xtranslator
[![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/sevengivings/subtitle-xtranslator/blob/main/README.en.md)

A Python script to extract text from audio/video and translate subtitle using Google Cloud, Naver Papago, DeepL API and dpl-Rapidapi translation API. 

OpenAI의 Whisper와 자막을 위해 조금 변형한 stable-ts 및 faster-whisper를 사용하여 비디오 AI 음성 인식 및 번역 과정을 자동화하기 위한 파이썬 프로그램입니다.

OpenAI의 최첨단 AI 범용 음성인식 기능 덕분에 동영상 자막 제작이 매우 편리해졌고, 구글과 네이버, DeepL은 인공지능 기반의 번역 서비스를 제공하고 있습니다.

이 프로그램은 비디오로부터 자막을 만들기 위해 위의 음성인식 및 번역 기능을 결합하여 작업이 편리하도록 구성했습니다. 

## [최신 버전업 내용]
- 2023-11-17 app.py의 웹 화면 구성을 변경하고, 여러 개의 MP3를 처리할 수 있게 하였습니다. 20231117a 버전은 윈도우11, WSL Ubuntu, Colab에서 테스트 했습니다. 다만, Colab에서는 처음 한번만 정상 작동해서 "런타임 다시 시작"을 한 후 다시 !python app.py를 해줘야 합니다. 

![161156](https://github.com/sevengivings/subtitle-xtranslator/assets/2328500/8706496d-c522-4be5-871e-d49bea4bae33)

- 2023-11-12 아래 WebUI(Gradio.app)로 만든 app.py는 Colab에서도 테스트 해 볼 수 있습니다. 진행 과정을 실시간으로 보여주는 기능은 작업 중입니다... 

- 2023-11-11 WebUI를 위한 아주 기초적인 앱을 만들어 보았습니다. 명령프롬프트나 파워쉘에서 venv 환경을 실행(activate.bat or activate.ps1)한 상태에서 pip install gradio를 한번 해준 후 python app.py를 실행하고 링크를 Ctrl 누른 채로 마우스 클릭해주시면 됩니다. 임시 폴더로 mp4를 복사하여 작업하게 되어 있어 오래 걸리므로 ffmpeg -i .\input.mp4 -vn -ab 128k .\output.mp3 를 통해 mp3로 만들어 준 후 작업하는 것이 좋겠습니다. 

- 2023-11-09 윈도우에서는 명령프롬프트용 배치파일인 install_venv.bat를 실행하여 파이썬 venv 환경을 쉽게 설치할 수 있습니다(주의: 아래 설치 설명 중 3 ~ 5번의 내용에 해당합니다. 그 이전과 이후 단계는 직접 작업하셔야 합니다.) 

- 2023-11-08 Google Colab에서 실행해 볼 수 있도록 .ipynb 파일을 추가하였습니다. Colab에서는 github에서 불러온 경우 사본으로 저장 한 후에 수정이 가능하므로 DEEPL_API_KEY 값을 넣어 줄 수 있고 자막 추출 후 번역까지 진행할 수 있습니다. 넣지 않아도 자막 추출은 가능합니다. audio_langugate와 subtitle_language 값을 적절히 바꾸면 됩니다(ko, en, ja, fr, cn 등등).    

- 2023-08-27 faster-whisper 지원 추가로 적은 VRAM(예: MX150 2GB)을 가진 노트북에서도 medium모델 가동이 가능(공유 VRAM이 있는 경우)합니다. 다만, cuDNN 및 cuBLAS가 필요합니다. Quantization로 int8을 기본 값으로 지정해 두었습니다. 비록 처리 속도가 느리지만 CPU로만 이용할 경우에 faster-whisper가 좋은 선택이 될 것으로 보입니다.   

## [기능과 특징] 

- 동영상에서 자막을 만들 수 있는 stable-ts, whisper 또는 faster-whisper 지원
- 구글 클라우드 번역(ADC 또는 API KEY), 네이버 파파고 번역, DeepL 및 DeepL Rapidapi버전 번역 서비스 지원
- 의미 없는 짧은 자막이나 반복되는 자막 제거 지원

## [한계]

- 음성 인식이 완전하지 않아서 누락되는 음성이나 잘못 인식될 수 있습니다. 프로페셔널한 용도로 사용은 권장하지 않습니다.
- stable-ts와 whisper 명령어로 했을 때와 이 프로그램을 사용했을 때, Whisper WebUI를 썼을 때 각각 자막의 품질이나 개수가 다를 수 있습니다(참고로 stable-ts는 자막 추출 용도로 최적화한 프로그램이기도 하지만 Whisper 오리지널에 비해 인식 누락이 있는 편입니다. 하지만, 없는데 추출된 귀신 소리, 무의미한 반복, 뒷부분 추출 안되는 등의 문제는 적은 편입니다.)
- 유료로 번역 API를 사용하는 경우 사전에 본 스크립트를 충분히 테스트한 후 문제가 없을 때 이용 하시기 바랍니다. 잠재적인 버그나 알 수 없는 이유로 생길 수 있는 피해에 대해 책임지지 않습니다. 

## [관련 프로그램 링크]

- stable-ts : GitHub - jianfch/stable-ts: ASR with reliable word-level timestamps using OpenAI's Whisper(https://github.com/jianfch/stable-ts)
- Whisper : General-purpose speech recognition model(https://github.com/openai/whisper)
- faster-whisper : reimplementation of whisper using CTranslate2(https://github.com/guillaumekln/faster-whisper) 

## [사용법] 

이 스크립트를 실행하려면 몇 가지 전제 조건을 준비해야 합니다(아래 섹션 참조 - [윈도우10/11 기준 준비 작업]). 

아래는 전체 사용법을 보기 위해 -h를 실행한 모습입니다. 

```
usage: subtitle-xtranslator.py [-h] [--framework FRAMEWORK] [--model MODEL] [--device DEVICE]
                               [--audio_language AUDIO_LANGUAGE] [--subtitle_language SUBTITLE_LANGUAGE]
                               [--skip_textlength SKIP_TEXTLENGTH] [--translator TRANSLATOR]
                               [--text_split_size TEXT_SPLIT_SIZE]
                               audio [audio ...]

positional arguments:
  audio                 audio/video file(s) to transcribe

options:
  -h, --help            show this help message and exit
  --framework FRAMEWORK
                        name of the stable-ts, whisper or faster-whisper framework to use (default: stable-ts)
  --model MODEL         tiny, base, small, medium, large model to use (default: medium)
  --device DEVICE       device to use for PyTorch inference (default: cuda)
  --audio_language AUDIO_LANGUAGE
                        language spoken in the audio, specify None to perform language detection (default: ja)
  --subtitle_language SUBTITLE_LANGUAGE
                        subtitle target language (default: ko)
  --skip_textlength SKIP_TEXTLENGTH
                        skip short text in the subtitles, useful for removing meaningless words (default: 1)
  --translator TRANSLATOR
                        none, google, papago, deepl-api or deepl-rapidapi (default: none)
  --text_split_size TEXT_SPLIT_SIZE
                        split the text into small lists to speed up the translation process (default: 1000)
  --condition_on_previous_text
                        if True, provide the previous output of the model as a prompt for the next window; disabling
                        may make the text inconsistent across windows, but the model becomes less prone to getting
                        stuck in a failure loop (default: False)
  --demucs              stable-ts only, whether to reprocess the audio track with Demucs to isolate vocals/remove
                        noise; pip install demucs PySoundFile; Demucs official repo:
                        https://github.com/facebookresearch/demucs (default: False)
  --vad                 stable-ts only, whether to use Silero VAD to generate timestamp suppression mask; pip install
                        silero; Official repo: https://github.com/snakers4/silero-vad (default: False)
  --mel_first           stable-ts only, process entire audio track into log-Mel spectrogram first instead in chunksif
                        audio is not transcribing properly compared to whisper, at the cost of more memory usage for
                        long audio tracks (default: False)
```

아래 명령은 각 인자들의 기본 값을 명시적으로 표시하여 실행해 본 것입니다. 일어로 된 영상에서 추출할 경우입니다. 

```
(venv) C:\Users\loginid> python .\subtitle-xtranslator.py --framework=stable-ts --model=medium --device=cuda --audio_language=ja --skip_textlength=1  '.\inputvideo1.mp4' '.\inputvideo2.mp4' '.\inputvideo3.mp4'
```

실제로 위 명령의 기본값을 그대로 쓴 것이라서 인자(아규먼트)를 생략해도 됩니다. 다만 --translator의 기본은 none이라서 번역은 하지 않고 자막 추출만 하게 됩니다. 

```
(venv) C:\Users\loginid> python .\subtitle-xtranslator.py '.\inputvideo1.mp4' '.\inputvideo2.mp4' '.\inputvideo3.mp4'
```

물론 추출된 자막을 한국어로 자동 번역을 하기 위해서는 --translator google, --translator papago, --translator deepl-api, --translator deepl-rapidapi 중 하나를 사용하면 됩니다. 

번역기를 이용하기 위하여 API 키를 제공하려면 환경 변수를 사용 합니다. 

파파고용 API 키 제공 방법은 다음과 같습니다. 먼저 개발자 등록을 하여 테스트 계정을 설정해야 합니다. 하루에 무료로 제공되는 번역량은 1만자입니다. 상용으로 전환할 경우 백만자당 2만원이 청구되는 것 같습니다. 

```
(venv) C:\Users\loginid> Set-Item -Path env:NAVER_CLOUD_ID -Value "your_id" 
(venv) C:\Users\loginid> Set-Item -Path env:NAVER_CLIENT_SECRET -Value "your_password"
```

Google의 경우 ADC(애플리케이션 기본 자격 증명 - 특수 파일 생성) 또는 API 키를 선택할 수 있으며, 다음은 API 키에 대한 설명입니다. ADC는 로컬 컴퓨터에 클라우드 사용을 위한 인증 파일을 만드는 방법이라서 API 키 유출을 걱정할 필요가 없습니다. 물론 해당 파일이 유출되면 안되겠지요... 다소 번거롭지만 소스코드에 API 키를 내장하는 것보다는 아래와 같이 환경 변수로 지정해 주는 것이 보안에 더 좋아 보입니다. 다만, 해당 세션에서만 작동하므로 컴퓨터를 껐다 켜거나 파워쉘과 venv를 다시 로딩했다면 또 해주어야 하는 번거로움은 있습니다. 

구글 클라우드 번역을 이용하려면 구글 클라우드 콘솔에서 프로젝트를 새로 하나 만들고 Google Cloud Translation서비스를 선택하고 ADC를 설정하거나 API key를 만들어야 합니다. ADC말고 API key만 받는 방법은 좀 더 간단해 보입니다(https://urame.tistory.com/entry/GoogleGCP-Translation-API%EB%B2%88%EC%97%AD-API-%EC%8B%A0%EC%B2%AD-%EB%B0%8F-PYTHON-%ED%85%8C%EC%8A%A4%ED%8A%B8). 

- https://console.cloud.google.com/
- https://cloud.google.com/translate/docs/basic/translating-text
- https://cloud.google.com/docs/authentication/provide-credentials-adc?hl=ko#local-dev 

비용 : 요금은 Cloud Translation에 제공된 문자 수로 조정됩니다. 예를 들어 한 달에 575,000자를 전송하여 처리한 경우 $1.50가 청구됩니다. 처음 500,000자는 무료이고 다음 75,000자는 $20달러/100만자(영문 기준) 요율로 청구됩니다. 7.5만자 x 0.2달러/만자 = 1.5달러 

```
(venv) C:\Users\loginid> Set-Item -Path env:GOOGLE_API_KEY -Value "your_api_key"
```

DeepL은 직접적인 방식과 간접적인 방식이 있습니다. 

직접적인 방식은 아래와 같이 키를 환경 변수로 제공하면 됩니다. 월 50만자까지 무료로 이용 가능합니다.  
```
(venv) C:\Users\loginid> Set-Item -Path env:DEEPL_API_KEY -Value "your_api_key"
```

DeepL API 번역을 이용하려면 최초 1회 관련 패키지를 설치해 주어야 합니다. 
```
(venv) C:\Users\loginid> pip install --upgrade deepl
```

또한 https://rapidapi.com/splintPRO/api/dpl-translator 를 통해서 간접적으로 사용할 수 있는데 응답 속도는 (해외 서버라서) 느린 편이지만 잘 작동합니다. 3천 글자를 넘길 경우 길게는 10초도 넘을 수 있습니다.  

신용카드를 등록한 후, 무료로 월 100번의 호출과 300,000만자까지 지원됩니다. 1회 호출당 3천글자까지 가능합니다. 무료 계정이라고 해도 호출 회수가 100회에서 넘어가면 과금이 되므로 주의해야 합니다. 

(주의: deepl-rapidapi의 경우 무료 계정은 월100번만 호출할 수 있으므로, text_split_size는 3000으로 설정 필요)

```
(venv) C:\Users\loginid> Set-Item -Path env:DEEPL_RAPIDAPI_KEY -Value "your_api_key" 
```

그러면 예를 들어 보겠습니다. --translator로는 deepl-translator를 사용하고 추출 방법은 stable-ts를 선택하는데, stable-ts의 demucs=True, vad=True, mel_first=True 옵션을 사용하고 싶다면 이렇게 하면 됩니다. 영어로 되어 있는 동영상입니다. 

```
(venv) C:\Users\loginid> Set-Item -Path env:DEEPL_RAPIDAPI_KEY -Value "your_api_key" 
(venv) C:\Users\loginid> python .\subtitle-xtranslator.py --demucs --vad --mel_first --audio_language en --translator deepl-rapidapi --text_split_size 3000 'Y:\video_cut.mp4'
```

demucs, vad, mel_first에 관하여는 stable-ts의 개발자 팁에서는 다음과 같은 이야기가 있습니다. 
- 음악에는 demucs=True, vad=True를 사용하지만 음악이 아닌 경우에도 작동합니다.
- 오디오가 Whisper에 비해 제대로 추출되지 않는 경우, 긴 오디오 트랙의 경우 메모리 사용량을 늘어나지만 mel_first=True를 사용해 보세요.

demucs와 vad를 사용하려면 다음 패키지들도 설치하여야 합니다. 

```
(venv) C:\Users\loginid> pip install wheel 
(venv) C:\Users\loginid> pip install demucs PySoundFile
(venv) C:\Users\loginid> pip install silero
```  
만약 설치 중 오류가 나면 https://visualstudio.microsoft.com/ko/visual-cpp-build-tools/ 를 설치할 필요가 있습니다. 

다만, demucs의 경우 동영상이 긴 경우 GPU메모리 많이 사용하며, 8GB VRAM에서는 안 될 수 있고(예: 2시간40분 MP4가 13GB VRAM을 요구), 추가 처리 시간(6~7분)을 필요로 합니다. vad도 마찬가지로 동영상을 처음부터 끝까지 탐색하므로 오래 걸립니다.  

실제 stable-ts와 deepl-api를 이용하여 추출과 번역을 하는 모습을 동영상으로 담았습니다. https://www.youtube.com/watch?v=Orq6CGHw8Ag  

## [윈도우10/11 기준 준비 작업]

### 1.파이썬 설치

파이썬은 최신 버전을 설치를 합니다. 윈도우11의 명령 프롬프트나 파워쉘 아무데서나 python이라고 치면 실행될 수 있도록 하는 것이 목표입니다.

https://www.python.org/downloads 
https://www.python.org/ftp/python/3.11.4/python-3.11.4-amd64.exe

### 2.CUDA 설치

최신 판을 찾아서 설치합니다. 설치 완료 후 cuda가 설치되어 있는 지 확인하려면 파워쉘(Windows PowerShell 앱)을 띄우고, nvidia-smi 라고 명령을 내려 보면 알 수 있습니다.

https://developer.nvidia.com/cuda-toolkit
https://developer.download.nvidia.com/compute/cuda/12.2.1/local_installers/cuda_12.2.1_536.67_windows.exe 

만약 faster-whisper를 사용하려면 cuDNN 및 cuBLAS의 설치가 필요합니다. cuDNN은 NVIDIA 개발자 계정이 필요한데, cudnn-windows-x86_64-8.9.4.25_cuda12-archive.zip의 압축을 해제 후  C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.2에 덮어 써주면 설치가 됩니다. cuBLAS는 아래에 venv 환경이 만들어진 후 pip install nvidia-cublas-cu12 명령을 통해 설치됩니다. 

### 3.파워쉘 실행

윈도우키를 누르고 R키를 누르면 좌측에 실행 창이 나타납니다. 이곳에 "powershell"을 입력하고 확인을 누르면 파워쉘을 실행할 수 있습니다(이외에 다양한 방법으로 실행 가능).

파워쉘 창에서 python이라고 치고 [Enter]키를 누르면 다음과 같이 응답이 나와야 합니다.

```
PS C:\Users\login_id> python

Python 3.10.11 (tags/v3.10.11:7d4cc5a, Apr  5 2023, 00:38:17) [MSC v.1929 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license" for more information.
>>>
```

위 >>> 에서 나오기 위해서는 exit() 을 입력합니다.

### 4.VENV 환경 만들어 주기

파이썬은 패키지를 필요할 때마다 설치하게 되는데, 시스템에 설치된 파이썬에 그냥 설치하다보면 가끔 뭔가가 꼬이게 되고 문제가 가끔 생기는데 아주 머리가 아픈 경우가 있습니다. 물론, 이 기능만 이용하겠다하면 상관없지만 그래도 제거가 편하도록 가상의 환경을 만들어 줍니다.

아래는 사용자 디렉터리에 그냥 설치했는데 다른 드라이브나 폴더에 해도 됩니다(주의: 경로 상에 한글이 없는 곳에서 작업해주세요. 혹시 윈도우 로그인명이 한글이라면 다른 곳에 설치가 필요합니다.)

용량이 4.5GB가량 되므로 적절한 디스크 드라이브에 설치하시면 좋습니다. 

(주의: 경로상에 한글이 포함되면 안됩니다.)  

```
PS C:\Users\login_id> python -m venv venv 
PS C:\Users\login_id> .\venv\Scripts\Activate.ps1
```
만약 .ps1가 실행이 안되면 파워쉘을 관리자 권한으로 실행한 후, 아래 명령을 한번 실행해 줍니다. 

```
PS C:\WINDOWS\system32> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned
```

위와 같이 해주면, 가상 환경 준비가 끝납니다. 처음에 실행할 때 보안 관련 문의가 나오는데 Always를 선택해 줍니다. venv가 성공적으로 실행되면 프롬프트가 바뀝니다. 


### 5.GPU버전의 pyTorch설치 및 관련 패키지들 설치

GPU버전의 토치를 설치합니다(메모리 부족으로 설치 실패 시 --no-cache-dir 추가).

```
(venv) PS C:\Users\login_id> pip install torch==2.0.1+cu118 --extra-index-url https://download.pytorch.org/whl/cu118
```

잘 설치가 되었는 지 확인하기 위해 python을 입력하고 간단한 프로그램을 짭니다. (주의) "version" 은 글자의 좌우에 언더바가 2개씩 있습니다.

```
(venv) PS C:\Users\login_id> python
Python 3.11.4 [MSC v.1929 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license" for more information.
>>> import torch
>>> print(torch.__version__)
2.0.1+cu118
>>> exit()
```

위 과정에서 아래와 같은 오류가 난다면, https://aka.ms/vs/16/release/vc_redist.x64.exe 를 추가로 설치한 후 재시도를 하여 봅니다. 

```
(venv) PS C:\Users\login_id> python
Python 3.11.5 (tags/v3.11.5:cce6ba9, Aug 24 2023, 14:38:34) [MSC v.1936 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license" for more information.
>>> import torch
Microsoft Visual C++ Redistributable is not installed, this may lead to the DLL load failure.
                 It can be downloaded at https://aka.ms/vs/16/release/vc_redist.x64.exe
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "C:\Users\login_id\venv\Lib\site-packages\torch\__init__.py", line 133, in <module>
    raise err
OSError: [WinError 126] 지정된 모듈을 찾을 수 없습니다. Error loading "C:\Users\login_id\venv\Lib\site-packages\torch\lib\c10.dll" or one of its dependencies.
```


이 상태에서 향후 필요한 패키지들을 설치합니다. 

```
(venv) PS C:\Users\login_id> pip install -U openai-whisper 
(venv) PS C:\Users\login_id> pip install -U stable-ts 
(venv) PS C:\Users\login_id> pip install -U google-cloud-translate
```

혹은 같이 첨부된 requirements.txt를 이용할 수도 있습니다. 

```
(venv) PS C:\Users\login_id> pip install -r requirements.txt 
```

참고로, 그동안 테스트할 때 stable-ts는 주로 2.6.2를 사용 했었는데, 계속 업그레이드가 이루어지고 있으므로 최신 버전을 설치하고 결과가 만족스럽지 않을 때에 특정 버전으로 바꾸어 설치하는 방법도 고려해 볼 수 있습니다.  

```
pip install stable-ts==2.6.2
```

만약 faster-whisper를 사용할 예정이라면, 아래 명령을 추가로 진행해 줍니다. 

```
pip install nvidia-cublas-cu12
pip install faster-whisper
```

### 6.FFMPEG 설치 및 파이썬 인터프리터 상태에서 영상 자막 만들기

영상에서 음성을 추출을 하다보니 외부 프로그램이 하나 필요합니다.

https://www.gyan.dev/ffmpeg/builds/#release-builds 에서 ffmpeg-release-essentials.zip 을 받아서 압축 해제한 후, 앞으로 작업할 디렉터리나 환경변수에서 Path가 설정되어 있는 곳에 복사하여도 됩니다. 그냥 C:\Users\login_id\venv\Scripts 밑에 복사하는 것이 속편하겠습니다. 

### 7.짧은 영상을 파이썬 코드로 추출해 보기 

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

### 8.subtitle-xtranslator.py 받아서 이용하기

만약 git를 설치해 두었다면 아래와 같이 받으면 됩니다. 그렇지 않다면 https://github.com/sevengivings/subtitle-xtranslator 에 접속해서 우측에 "<> CODE"라는 명령버튼이 보입니다. 버튼을 누르면 Download ZIP 메뉴를 통해 압축 파일로 받을 수 있고, 적당한 곳에 압축 해제한 후 이용할 수 있습니다.
```
(venv) C:\Users\login_id> git clone https://github.com/sevengivings/subtitle-xtranslator
```
(주의) 만약 한글로 된 안내 메시지를 보려면 압축 파일의 locale 디렉토리도 필요합니다.

## [단일 exe로 만들기]

지금까지는 python .\subtitle-xtranslator.py로 실행을 했습니다. 다소 불편하므로 exe파일로 만든 후, venv\Scripts에 복사하여 아무 드라이브나 디렉토리에서도 실행할 수 있도록 해보겠습니다.
```
(venv) C:\Users\login_id> pip install pyinstaller
(venv) C:\Users\login_id> pyinstaller --onefile .\subtitle-xtranslator.py 
```
위 결과로 나오는 C:\Users\login_id\dist\subtitle-xtranslator.exe를 윈도우의 경로 PATH가 지정된 아무 곳에나 복사하면 됩니다. 이제 어느 곳에서나 실행이 가능해집니다(venv와 관계 없이).

위 방식으로 만들면 약 2.7GB의 크기를 가지고 있어서 만드는데, 그리고 실행할 때 오래(1~2분) 걸리기도 하고 실용적이지는 못해 보입니다. 
