# subtitle-xtranslator
[![ko](https://img.shields.io/badge/lang-ko-red.svg)](https://github.com/sevengivings/subtitle-xtranslator/blob/main/README.md)

A Python script to extract text from audio/video and translate subtitle

Thanks to state-of-arts AI general-purpose speech recognition function of Whisper(https://github.com/openai/whisper), making subtitle from videos is very convenient. Also, Google, Naver and DeepL provide AI based translation service.

This program combines above transcribing and translation functions. 

[Features] 

- supports Stable-ts or Whisper to make subtitle from video
- supports Google cloud translation(ADC or API KEY), Naver Papago translation, DeepL-Rapidapi translation
- supports removal of no-meaning short subtitles or repeated subtitles

[Usage] 

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
                        name of the stable-ts or Whisper framework to use (default: stable-ts)
  --model MODEL         tiny, base, small, medium, large model to use (default: medium)
  --device DEVICE       device to use for PyTorch inference (default: cuda)
  --audio_language AUDIO_LANGUAGE
                        language spoken in the audio, specify None to perform language detection (default: ja)
  --subtitle_language SUBTITLE_LANGUAGE
                        subtitle target language (default: ko)
  --skip_textlength SKIP_TEXTLENGTH
                        skip short text in the subtitles, useful for removing meaningless words (default: 1)
  --translator TRANSLATOR
                        none, google, papago or deepl-rapidapi (default: none)
  --text_split_size TEXT_SPLIT_SIZE
                        split the text into small lists to speed up the translation process (default: 1000)
```


To run this script, you should prepare some prerequisites.(see below section) 
```
(venv) C:\Users\loginid> python .\subtitle-xtranslator.py --framework=stable-ts --model=medium --device=cuda --audio_language=ja --subtitle_language=ko --skip_textlength=1 --translator none --text_split_size=1000 '.\inputvideo1.mp4' '.\inputvideo2.mp4' '.\inputvideo3.mp4'
```

Actually, values of above command are default so equal to the following. 
```
(venv) C:\Users\loginid> python .\subtitle-xtranslator.py '.\inputvideo1.mp4' '.\inputvideo2.mp4' '.\inputvideo3.mp4'
```

To provide api key to this program, you should use environment variables. 

For Naver Papago API key 
```
(venv) C:\Users\loginid> Set-Item -Path env:NAVER_CLOUD_ID -Value "your_id" 
(venv) C:\Users\loginid> Set-Item -Path env:NAVER_CLIENT_SECRET -Value "your_password"
```

For Google you can choose ADC(Application Default Credential - special file creation) or API key, the following is about API key. 

```
(venv) C:\Users\loginid> Set-Item -Path env:GOOGLE_API_KEY -Value "your_api_key"
```

For now, DeepL does not provide pro service, but we can access DeepL-Rapidapi service(needs credit card).  
For DeepL-Rapidapi it is required to set environment variable. https://rapidapi.com/splintPRO/api/deepl-translator 
```
(venv) C:\Users\loginid> Set-Item -Path env:DEEPL_RAPIDAPI_KEY -Value "your_api_key" 
```
(Caution)Although you choose free version, if you exceed quota(100 calls per month) payment is required. 

[Prerequisites] 

1.Install Python

Python is currently running 3.11.3, but the latest version isn't that important, so we'll install it with the version below. The goal is to be able to type python anywhere in the command prompt or powershell on Windows 11 and have it run.

https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe

2.Install CUDA library 

To verify that CUDA is installed after the installation is complete, fire up Powershell (the Windows PowerShell app) and run the command nvidia-smi.

https://developer.nvidia.com/cuda-11-7-1-download-archive?target_os=Windows&target_arch=x86_64&target_version=11&target_type=exe_local

3.Run the Powershell

Press the Windows key and then the R key to bring up the Run window on the left. Type "powershell" into it and press OK to run Powershell (and many other ways to run it).

In the Powershell window, type python and press [Enter], and you should see a response like this.

```
PS C:\Users\login_id> python

Python 3.10.11 (tags/v3.10.11:7d4cc5a, Apr  5 2023, 00:38:17) [MSC v.1929 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license" for more information.
>>>
```

To get out of the above >>>, type exit().

4.Creating a VENV Environment and Installing Python Packages

Python installs packages whenever it needs them, and if you just install them on top of whatever Python is installed on your system, sometimes things get messed up and it can be a real headache. Of course, if that's all you want to do, that's fine, but it creates a virtual environment that makes uninstalling easier.

Below, I just installed it in my user directory, but you can put it in any other drive or folder. (Note: make sure there are no Korean characters in the path, or you'll need to install it somewhere else if your Windows login name is Korean).

It's about 4.5GB in size, so you'll want to install it on a suitable disk drive.

```
PS C:\Users\login_id> python -m venv venv 
PS C:\Users\login_id> .\venv\Scripts\Activate.ps1
```

Once you've done this, your virtual environment is ready to go. 

Install the required packages.

```
(venv) PS C:\Users\login_id> pip install -U git+https://github.com/jianfch/stable-ts.git
(venv) PS C:\Users\login_id> pip install git+https://github.com/openai/whisper.git
(venv) PS C:\Users\login_id> pip install google-cloud-translate==2.0.1
```

5.Install the GPU version of pyTorch

After the above steps, you should be able to use it right away, but it seems to install the CPU version of pyTorch. This time, install the GPU version of torch.

```
(venv) PS C:\Users\login_id> pip install torch==2.0.1+cu117 --extra-index-url https://download.pytorch.org/whl/cu117
```

To verify that it installed well, type in python and write a simple program. (Note that "version" has two underbars to the left and right of the letter.

```
(venv) PS C:\Users\login_id> python
Python 3.10.11 (tags/v3.10.11:7d4cc5a, Apr  5 2023, 00:38:17) [MSC v.1929 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license" for more information.
>>> import torch
>>> print(torch.__version__)
2.0.1+cu117
>>> exit()
```

6.Install ffmpeg 

To extract the audio from the video, we need an external program.

Download ffmpeg-release-essentials.zip from https://www.gyan.dev/ffmpeg/builds/#release-builds, unzip it, and copy ffmpeg.exe to .\venv\Scripts directory. 

* Translated with www.DeepL.com/Translator (free version)
