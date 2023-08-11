# Extract subtitle from video(stable-ts or whisper) and translate subtitle(google, papago or DeepL-Rapidapi) 

# Requires:
# - stable-ts (https://github.com/jianfch/stable-ts) (pip install stable-ts)
# - whisper (https://github.com/openai/whisper) (pip install git+https://github.com/openai/whisper.git )
# - torch + cuda
# - ffmpeg.exe (https://www.ffmpeg.org/) for stable-ts and whisper 
# - python-docx
# - google-cloud-translate for ADC credential

# OS: Windows 10/11 

import os 
import sys
import argparse
import torch
import stable_whisper
import whisper 
from whisper.utils import get_writer
import numpy as np
import gettext
import requests 
import urllib.request
import json

# stable-ts  
def extract_audio_stable_whisper(model, condition_on_previous_text, stable_demucs, stable_vad, vad_threshold, stable_mel_first, audio_language, input_file_name, output_file_name): 
    # Check if the file exists.
    if not os.path.exists(input_file_name):
        raise FileNotFoundError(f"The file {input_file_name} does not exist.")

    print(f'condition_on_previous_text: {condition_on_previous_text}, demucs: {stable_demucs}, vad: {stable_vad}, vad_threshold: {vad_threshold}, mel_first: {stable_mel_first}')
    # Extract the audio from the video.
    result = model.transcribe(verbose=True, word_timestamps=False, condition_on_previous_text=condition_on_previous_text, \
                              demucs=stable_demucs, vad=stable_vad, vad_threshold=vad_threshold, mel_first=stable_mel_first, \
                              language=audio_language, audio=input_file_name)
    result.to_srt_vtt(output_file_name + ".srt", word_level=False) 

# Whisper 
def extract_audio_whisper(model, condition_on_previous_text, audio_language, input_file_name):
    # Check if the file exists.
    if not os.path.exists(input_file_name):
        raise FileNotFoundError(f"The file {input_file_name} does not exist.")

    print(f'condition_on_previous_text: {condition_on_previous_text}')
          
    temperature = tuple(np.arange(0, 1.0 + 1e-6, 0.2))  # copied from Whisper original code 
    result = model.transcribe(input_file_name, temperature=temperature, verbose=True, word_timestamps=False, condition_on_previous_text=condition_on_previous_text, language=audio_language)
    output_dir = os.path.dirname(input_file_name)
    writer = get_writer("srt", output_dir)
    writer(result, input_file_name) 

# https://cloud.google.com/translate/docs/basic/translating-text?hl=ko#translate_translate_text-python
# This script is used to translate subtitles using Google Cloud Translate service 
# Google ADC(Application Default Credentials) is used to authenticate the request.
# https://cloud.google.com/docs/authentication/provide-credentials-adc#how-to 

# Set up Application Default Crendentials 
# https://cloud.google.com/docs/authentication/provide-credentials-adc#local-dev 
# Install and initialize the gcloud CLI.
# Create credential file: gcloud auth application-default login
def translate_text_adc(target: str, text: str) -> dict:
    """Translates text into the target language.

    Target must be an ISO 639-1 language code.
    See https://g.co/cloud/translate/v2/translate-reference#supported_languages
    """
    try:
        from google.cloud import translate_v2 as translate
    except ModuleNotFoundError:
        print(
            "Please install the Cloud client library using "
            '"pip install google-cloud-translate==2.0.1"'
        )
        sys.exit(1)

    translate_client = translate.Client()

    if isinstance(text, bytes):
        text = text.decode("utf-8")

    # Text can also be a sequence of strings, in which case this method
    # will return a sequence of results for each text.
    result = translate_client.translate(text, target_language=target)

    #print("Text: {}".format(result["input"]))
    #print("Translation: {}".format(result["translatedText"]))
    #print("Detected source language: {}".format(result["detectedSourceLanguage"]))

    return result 

# PowerShell 
# Set-Item -Path env:GOOGLE_API_KEY -Value "your_api_key"
def translate_text_apikey(target, text):
    api_key = os.environ['GOOGLE_API_KEY'] 
    endpoint = f'https://translation.googleapis.com/language/translate/v2'

    text = text
    target_language = target

    params = {
        'key': api_key,
        'q': text,
        'target': target_language
    }
    headers = {'Content-Length': str(len(str(params)))}
    response = requests.post(endpoint, data=params, headers=headers)
    if response.status_code != 200:
        raise Exception(response.text)
    
    data = response.json()
    try:
        translated_texts = [item['translatedText'] for item in data['data']['translations']]
    except KeyError:
        print(data)
        sys.exit(1)
    
    return translated_texts

# use '\n' to seperate lines in the text 
def translate_text_papago(audio, target, text):
    # PowerShell 
    # Set-Item -Path env:NAVER_CLOUD_ID -Value "your_id_value"
    # Set-Item -Path env:NAVER_CLIENT_SECRET -Value "your_password_value"
    try:
        client_id = os.environ['NAVER_CLOUD_ID'] 
        client_secret = os.environ['NAVER_CLIENT_SECRET'] 
        print(_("[Info] Naver Papago will be used."))
    except KeyError:
        print(_("[Error] Please set NAVER_CLOUD_ID and NAVER_CLIENT_SECRET environment variables."))
        sys.exit(1)
        
    encText = urllib.parse.quote(text)
    data = "source=" + audio + "&target=" + target + "&text=" + encText   
    url = "https://openapi.naver.com/v1/papago/n2mt"

    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id",client_id)
    request.add_header("X-Naver-Client-Secret",client_secret)
    
    # if requests exceed quota, you will see 'urllib.error.HTTPError: HTTP Error 429: Too Many Requests'   
    response = urllib.request.urlopen(request, data=data.encode("utf-8"))
    rescode = response.getcode()
    
    if(rescode==200):
        response_body = response.read()
        json_data = response_body.decode('utf-8')
        translated_text = json.loads(json_data)["message"]["result"]["translatedText"]
        translated_list = translated_text.split('\n')
        #print(translated_list)    
        
        return translated_list
    else:
        print(_("[Error] Request failed with status code:") + rescode)

# https://rapidapi.com/splintPRO/api/deepl-translator
# free: 100 calls per month, 3000 characters per call, 300,000 characters per month 
# PowerShell 
# Set-Item -Path env:DEEPL_RAPIDAPI_KEY -Value "your_api_key"
def translate_text_deepl_rapidapi(audio, target, text):
    try:
        api_key = os.environ['DEEPL_RAPIDAPI_KEY'] 
        print(_("[Info] DeepL-Rapidapi will be used."))
    except KeyError:
        print(_("[Error] Please set DEEPL_RAPIDAPI_KEY environment variables."))
        sys.exit(1)
        
    url = f'https://deepl-translator.p.rapidapi.com/translate'

    text = text
    target_language = target.upper() 
    source_language = audio.upper() 

    payload = {
        'text': text,
        'source': source_language,
        'target': target_language
    }
    
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "deepl-translator.p.rapidapi.com"
    }   

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code != 200:
        raise Exception(response.text)
    
    data = response.json()
    try:
        translated_texts = data['text'] 
        translated_list = translated_texts.split('\n')
    except KeyError:
        print(data)
        sys.exit(1)
    
    return translated_list

# removes unnecessary short and repeated characters from the subtitle text and translate using Google Cloud Translate 
def translate_file(audio_language, subtitle_language, translator, text_split_size, input_file_name, skip_textlength):
    # Check if the file exists.
    if not os.path.exists(input_file_name):
        raise FileNotFoundError(_("[Error] The file does not exist:") + input_file_name)

    # Open the input file.
    with open(input_file_name, "r", encoding="utf-8") as f:
        lines = f.readlines()

    subtitle_text = {}
    subtitle_text_list = []
    time_sync_data_list = [] 
    time_sync_data = ""

    deleted_line = 0
    deleted_subtitle_text =  set()
    ignored_line = 0    
    ignored_subtitle = set()    

    latest_subtitle_text = ""
    
    # Iterate over the lines in the file.
    for line in lines: 
        # Ignore empty lines and lines that contain only numbers.
        if line.strip() == "" or line.strip().isdigit():
            continue

        # If the line contains "-->", it is time sync data.
        elif line.find("-->") != -1:
            # save time sync data to a varible for later use. 
            time_sync_data = line.strip()

        # Otherwise, the line is subtitle text.
        else:
            # ignore short text under n characters
            if len(line.strip()) > skip_textlength and time_sync_data.find('-->') != -1:
                # Add the line of text to the dictionary.
                value = subtitle_text.get(time_sync_data, "")
                if value is None or value == "":
                    if latest_subtitle_text ==  line.strip():
                        ignored_subtitle.add(line.strip())
                        ignored_line = ignored_line + 1
                        continue
                
                    latest_subtitle_text = subtitle_text[time_sync_data] = line.strip()
                    subtitle_text_list.append(latest_subtitle_text)
                    time_sync_data_list.append(time_sync_data)
                else: 
                    # join multiple lines of text into one line 
                    subtitle_text[time_sync_data] = subtitle_text[time_sync_data] + ", " + line.strip()
                    subtitle_text_list.append(subtitle_text[time_sync_data])   
                    time_sync_data_list.append(time_sync_data)              
            else: 
                deleted_line = deleted_line + 1
                deleted_subtitle_text.add(line.strip())
                
    # split lists into small lists 
    current_length = 0
    total_length = 0 
    current_list = [] 
    split_lists = []
    
    # Google Cloud Translate only supports maximum text segments : 128 
    num_of_segments = 0 
    for string in subtitle_text_list:
        if current_length + len(string) < text_split_size and (translator != "google" or num_of_segments < 127):
            current_list.append(string)
            current_length += len(string) + 1  # 1 for string = '\n'.join(split_list)
            num_of_segments += 1
        else:
            split_lists.append(current_list)
            current_list = [string]
            current_length = len(string)
            num_of_segments = 0
        
        total_length += len(string)

    if current_list:
        split_lists.append(current_list)
     
    # translate each splitted list 
    i = 0 
    for split_list in split_lists:
        if translator == "google":
            google_api_key = ""
            try: 
                google_api_key = os.environ['GOOGLE_API_KEY']
                print(_("[Info] Using Google Cloud Translate"))
            except KeyError:
                print(_("[Info] Using Google Cloud Translate (ADC)"))    
                        
            if google_api_key != "": 
                result = translate_text_apikey(subtitle_language, split_list)
                translated_list = result 
            else:
                result = translate_text_adc(subtitle_language, split_list)
                translated_list = [res['translatedText'] for res in result]
        elif translator == "papago":
            string = '\n'.join(split_list)
            # print(string)        
            result = translate_text_papago(audio_language, subtitle_language, string)   
            translated_list = result          
        elif translator == "deepl-rapidapi":
            string = '\n'.join(split_list)       
            result = translate_text_deepl_rapidapi(audio_language, subtitle_language, string)   
            translated_list = result  
        else: 
            print(_("[Error] Invalid translator"))
            sys.exit(1)               
        
        print(_("[Info] number of sentences translated: "), len(translated_list)) 
        
        # for safety, save to .srt file every successful translation.  
        # Save the subtitle text to a new file.
        # create a new file with the same name as the input file, consider file name contains multiple '.' 
        output_file_name = input_file_name.rsplit(".", 1)[0]
                
        with open(output_file_name + "_translated.srt", "a", encoding="utf-8") as fout:       
            for string in translated_list: 
                fout.write(f"{i+1}\n")
                fout.write(f"{time_sync_data_list[i]}\n")
                fout.write(f"{string.strip()}\n")
                if i != len(time_sync_data_list)-1:
                    fout.write("\n")     
                i += 1         
                    
        translated_list = []        
    
    # Print the total_length
    print(_("\n[Info] Number of characters: "), total_length)
    
    if len(deleted_subtitle_text) > 0:
        print(_("[Info]Number of short subtitles: "), deleted_line)          
        output_file_name = input_file_name.rsplit(".", 1)[0] 
        with open(output_file_name + "_deleted.txt", "w", encoding="utf-8") as f3:
            for text in deleted_subtitle_text:
                f3.write(text + "\n")
                
    if len(ignored_subtitle) > 0:
        print(_("\n[Info]Number of repeated subtitles: "), ignored_line)
        output_file_name = input_file_name.rsplit(".", 1)[0]
        with open(output_file_name + "_repeated.txt", "w", encoding="utf-8") as f4:
            for text in ignored_subtitle:
                f4.write(text + "\n")

if __name__ == "__main__":
    appname = 'subtitle-xtranslator'
    localedir = './locale'
        
    en_i18n = gettext.translation(appname, localedir, fallback=True, languages=['ko'])  # Korean default
    en_i18n.install()

    parser= argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("audio", nargs="+", type=str, help="audio/video file(s) to transcribe")
    parser.add_argument("--framework", default="stable-ts", help="name of the stable-ts or Whisper framework to use")
    parser.add_argument("--model", default="medium", help="tiny, base, small, medium, large model to use")
    parser.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu", help="device to use for PyTorch inference")
    parser.add_argument("--audio_language", type=str, default="ja", help="language spoken in the audio, specify None to perform language detection")
    parser.add_argument("--subtitle_language", type=str, default="ko", help="subtitle target language")
    parser.add_argument("--skip_textlength", type=int, default=1, help="skip short text in the subtitles, useful for removing meaningless words")
    parser.add_argument("--translator", default="none", help="none, google, papago or deepl-rapidapi")
    parser.add_argument("--text_split_size", type=int, default=1000, help="split the text into small lists to speed up the translation process")

    parser.add_argument("--condition_on_previous_text", action='store_true',
                        help="if True, provide the previous output of the model as a prompt for the next window; "
                             "disabling may make the text inconsistent across windows, "
                             "but the model becomes less prone to getting stuck in a failure loop")
    # stable_ts only 
    parser.add_argument('--demucs', action='store_true',
                        help='stable-ts only, whether to reprocess the audio track with Demucs to isolate vocals/remove noise; '
                             'pip install demucs PySoundFile; '
                             'Demucs official repo: https://github.com/facebookresearch/demucs')
    parser.add_argument('--vad', action='store_true',
                        help='stable-ts only, whether to use Silero VAD to generate timestamp suppression mask; '
                             'pip install silero; '
                             'Official repo: https://github.com/snakers4/silero-vad')
    parser.add_argument('--vad_threshold', type=float, default=0.2,
                        help='stable-ts only, threshold for detecting speech with Silero VAD. (Default: 0.2); '
                             'low threshold reduces false positives for silence detection')
    parser.add_argument('--mel_first', action='store_true',
                        help='stable-ts only, process entire audio track into log-Mel spectrogram first instead in chunks'
                             'if audio is not transcribing properly compared to whisper, at the cost of more memory usage for long audio tracks')
   
    args = parser.parse_args().__dict__
    framework: str = args.pop("framework")
    model_name: str = args.pop("model")
    device: str = args.pop("device")
    audio_language: str = args.pop("audio_language")
    subtitle_language: str = args.pop("subtitle_language")
    skip_textlength: int = args.pop("skip_textlength")
    translator: str = args.pop("translator")
    text_split_size: int = args.pop("text_split_size")

    use_condition_on_previous_text: bool = args.pop("condition_on_previous_text")

    # stable_ts only
    use_demucs: bool = args.pop("demucs")
    use_vad: bool = args.pop("vad")
    vad_threshold: float = args.pop("vad_threshold")
    is_mel_first: bool = args.pop("mel_first")

    print("subtitle-xtranslator: AI subtitle extraction and translation tool")
    print("\nframework:" + framework + "\nmodel:" + model_name + "\ndevice:" + device  + "\naudio language:" + audio_language + "\nsubtitle language:" + subtitle_language  + "\nigonore n characters:" + str(skip_textlength) + "\ntranslator:" + translator + "\ntext_split_size:" + str(text_split_size))
    print("\nPython version: " + sys.version)
    print("Torch version: " + torch.__version__ + "\n")

    if framework == "stable-ts":   
        model = stable_whisper.load_model(model_name, device=device)
    elif framework == "whisper":
        model = whisper.load_model(model_name).to(device)        
    else: 
        print(_("[Error] transcribing framework shoud be stable-ts or whisper")) 
        sys.exit(1)        
        
    for input_file_name in args.pop("audio"):
        if not os.path.exists(input_file_name): 
            sys.exit(_("[Error] File does not exist: ") + input_file_name)
            
        # create a new file with the same name as the input file, consider file name contains multiple '.' 
        output_file_name = input_file_name.rsplit(".", 1)[0]

        # AI speech recognition  
        # Check if the file exists
        if not os.path.exists(output_file_name + ".srt"):           
            if framework == "stable-ts":   
                extract_audio_stable_whisper(model, use_condition_on_previous_text, use_demucs, use_vad, vad_threshold, is_mel_first, audio_language, input_file_name, output_file_name)
            elif framework == "whisper":
                extract_audio_whisper(model, use_condition_on_previous_text, audio_language, input_file_name)
        else: 
            print(_("[Warning] File already exists"))

        if translator != "none":
            if skip_textlength < 0:
                skip_textlength = 0 
                
            translate_file(audio_language, subtitle_language, translator, text_split_size, output_file_name + ".srt", skip_textlength)
            
            # Change the name of final srt same as video file name 
            os.rename(output_file_name + ".srt", output_file_name + "_original.srt")
            os.rename(output_file_name + "_translated.srt", output_file_name + ".srt")
            print (_("[Info] final srt file is saved"))
        else: 
            print(_("[Info] translator is none, so exit."))
    
    print(_("[Info] Done"))

    sys.exit(0)
