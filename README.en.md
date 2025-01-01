# subtitle-xtranslator
[![ko](https://img.shields.io/badge/lang-ko-red.svg)](https://github.com/sevengivings/subtitle-xtranslator/blob/main/README.md)

A Python script to extract text from audio/video and translate subtitle

Thanks to state-of-arts AI general-purpose speech recognition function of Whisper(https://github.com/openai/whisper), making subtitles from videos is very convenient. Also, Google, Naver, and DeepL provide AI-based translation services.

This program combines the above transcribing and translation functions. 

[Features] 

- supports stable-ts(https://github.com/jianfch/stable-ts), Whisper, or faster-whisper to make subtitles from video
- supports Google cloud translation(ADC or API KEY), Naver Papago translation, DeepL API translation
- supports the removal of no-meaning short subtitles or repeated subtitles

[Usage] 

```
usage: subtitle-xtranslator.py [-h] [--framework FRAMEWORK] [--model MODEL] [--device DEVICE]
                               [--audio_language AUDIO_LANGUAGE] [--subtitle_language SUBTITLE_LANGUAGE]
                               [--skip_textlength SKIP_TEXTLENGTH] [--translator TRANSLATOR]
                               [--text_split_size TEXT_SPLIT_SIZE] [--condition_on_previous_text] [--demucs] [--vad]
                               [--vad_threshold VAD_THRESHOLD] [--mel_first]
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
                        none, google, papago, deepl-api(default: none)
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
  --vad_threshold VAD_THRESHOLD
                        stable-ts only, threshold for detecting speech with Silero VAD. (Default: 0.2); low threshold
                        reduces false positives for silence detection (default: 0.2)
  --mel_first           stable-ts only, process entire audio track into log-Mel spectrogram first instead in chunksif
                        audio is not transcribing properly compared to whisper, at the cost of more memory usage for
                        long audio tracks (default: False)
```


To run this script, you should prepare some prerequisites. (see below section) 
```
(venv) C:\Users\loginid> python .\subtitle-xtranslator.py --framework=stable-ts --model=medium --device=cuda --audio_language=ja --subtitle_language=ko --skip_textlength=1 --translator none --text_split_size=1000 '.\inputvideo1.mp4' '.\inputvideo2.mp4' '.\inputvideo3.mp4'
```

Actually, the values of the above command are default so equal to the following. 
```
(venv) C:\Users\loginid> python .\subtitle-xtranslator.py '.\inputvideo1.mp4' '.\inputvideo2.mp4' '.\inputvideo3.mp4'
```

To provide API key to this program, you should use environment variables. 

For Naver Papago API key 
```
(venv) C:\Users\loginid> Set-Item -Path env:NAVER_CLOUD_ID -Value "your_id" 
(venv) C:\Users\loginid> Set-Item -Path env:NAVER_CLIENT_SECRET -Value "your_password"
```

For Google you can choose ADC(Application Default Credential - special file creation) or API key, the following is about API key. 

```
(venv) C:\Users\loginid> Set-Item -Path env:GOOGLE_API_KEY -Value "your_api_key"
```

For DeepL API, an environment variable is needed. 

```
(venv) C:\Users\loginid> Set-Item -Path env:DEEPL_API_KEY -Value "your_api_key"
```

[Prerequisites] 

1. Install Python

We need to install Python. The goal is to be able to type Python anywhere in the command prompt or Powershell on Windows 11 and have it run.

https://www.python.org

2. Install the CUDA library 

To verify that CUDA is installed after the installation is complete, fire up Powershell (the Windows PowerShell app) and run the command nvidia-smi.

https://developer.nvidia.com/cuda-toolkit

If you want to use faster-whisper, the cuDNN and cuBLAS are also needed. To get the cuDNN, the NVIDIA developer ID is needed. The cuBLAS can be installed using the pip command.   

3. Run the Powershell

Press the Windows key and then the R key to bring up the Run window on the left. Type "Powershell" into it and press OK to run Powershell (and many other ways to run it).

In the Powershell window, type Python and press [Enter], and you should see a response like this.

```
PS C:\Users\login_id> python

Python 3.10.11 (tags/v3.10.11:7d4cc5a, Apr  5 2023, 00:38:17) [MSC v.1929 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license" for more information.
>>>
```

To get out of the above >>>, type exit().

4. Creating a VENV Environment and Installing Python Packages

Python installs packages whenever it needs them, and if you just install them on top of whatever Python is installed on your system, sometimes things get messed up and it can be a real headache. Of course, if that's all you want to do, that's fine, but it creates a virtual environment that makes uninstalling easier.

Below, I just installed it in my user directory, but you can put it in any other drive or folder. (Note: Make sure there are no Korean characters in the path, or you'll need to install it somewhere else if your Windows login name is Korean).

It's about 4.5GB in size, so you'll want to install it on a suitable disk drive.

```
PS C:\Users\login_id> python -m venv venv 
PS C:\Users\login_id> .\venv\Scripts\Activate.ps1
```

If you cannot run .ps1, open Powershell as an administrator and run this command. 

```
PS C:\Windows\System32> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned
```

Once you've done this, your virtual environment is ready to go. 

Install the required packages. If you want to use "git+" command, Git should be installed. https://git-scm.com/download/win 

```
(venv) PS C:\Users\login_id> pip install git+https://github.com/openai/whisper.git
(venv) PS C:\Users\login_id> pip install -U git+https://github.com/jianfch/stable-ts.git
(venv) PS C:\Users\login_id> pip install google-cloud-translate
(venv) PS C:\Users\login_id> pip install --upgrade deepl
```

To run faster-whisper, you need to install some packages. 

```
(venv) PS C:\Users\login_id> pip install nvidia-cublas-cu12
(venv) PS C:\Users\login_id> pip install faster-whisper
```

5. Install the GPU version of PyTorch

After the above steps, you should be able to use it right away, but it seems to install the CPU version of PyTorch. This time, install the GPU version of the torch.

```
(venv) PS C:\Users\login_id> pip install torch==2.2.1+cu121 --extra-index-url https://download.pytorch.org/whl/cu121
```

To verify that it is installed well, type in Python and write a simple program. (Note that "version" has two underbars to the left and right of the letter.

```
(venv) PS C:\Users\login_id> python
Python 3.10.11 (tags/v3.10.11:7d4cc5a, Apr  5 2023, 00:38:17) [MSC v.1929 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license" for more information.
>>> import torch
>>> print(torch.__version__)
2.2.1+cu121
>>> exit()
```

If you see the following error message, you need to install https://aka.ms/vs/16/release/vc_redist.x64.exe 

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
OSError: [WinError 126] Module not found, Error loading "C:\Users\login_id\venv\Lib\site-packages\torch\lib\c10.dll" or one of its dependencies.
```

6. Install FFmpeg.exe  

To extract the audio from the video, we need an external program.

Download ffmpeg-release-essentials.zip from https://www.gyan.dev/ffmpeg/builds/#release-builds, unzip it, and copy ffmpeg.exe to .\venv\Scripts directory. 

* Translated with www.DeepL.com/Translator (free version)
