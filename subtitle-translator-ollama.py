# Translate subtitle (Ollama TranslateGemma)  

import os 
import sys
import argparse
import re
import requests
import json

def translate_text_ollama(host, port, model, source_lang, target_lang, text):
    url = f"http://{host}:{port}/api/chat"

    system_prompt = (
        f"You are a professional video subtitle translator. "
        f"Translate the following text from {source_lang} to {target_lang}. "
        f"Do not include any introductory, concluding remarks, or notes. "
        f"Output only the translated text."
    )

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ],
        "stream": False
    }

    try:
        # print(f"[Debug] Input: {text.strip()}")
        response = requests.post(url, json=payload)
        response.raise_for_status()
        result = response.json()
        # print(f"[Debug] Output: {result}")
        translated_text = result.get("message", {}).get("content", "")
        
        return translated_text.strip()
    except Exception as e:
        print(f"[Error] Ollama translation failed: {e}")
        sys.exit(1)
    
# removes unnecessary short and repeated characters from the subtitle text and translate using Ollama
def translate_file(audio_language, subtitle_language, input_file_name, skip_textlength, ollama_host, ollama_port, ollama_model):
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
            # ignore short text under n characters, and meaningless repeated text
            if len(line.strip()) > skip_textlength \
              and time_sync_data.find('-->') != -1:
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
                    subtitle_text_list[-1] = subtitle_text[time_sync_data]
                    time_sync_data_list[-1] = time_sync_data
            else: 
                deleted_line = deleted_line + 1
                deleted_subtitle_text.add(time_sync_data + ":" + line.strip())
                
    # translate each line
    output_file_name = input_file_name.rsplit(".", 1)[0]
    total_length = sum(len(s) for s in subtitle_text_list)
    
    print(f"[Info] Starting translation of {len(subtitle_text_list)} lines with Ollama ({ollama_model})...")

    with open(output_file_name + "_translated.srt", "w", encoding="utf-8") as fout:
        for i, string in enumerate(subtitle_text_list):
            if (i + 1) % 10 == 0:
                print(f"[Info] Translating line {i + 1}/{len(subtitle_text_list)}")
            
            translated_text = translate_text_ollama(ollama_host, ollama_port, ollama_model, audio_language, subtitle_language, string)
            
            # remove meaningless repeated text
            match = re.search(r"(\b[\w\u00C0-\uFFFF]+\b)([,\.\;\s]+\1)+" , translated_text)
            if match:
                repeated_text = match.group(1)  # repeated text
                total_occurrences = translated_text.count(repeated_text)  # total occurrences of the repeated text 
                if total_occurrences > 10:
                    print(f"over 10 times repeated pattern in one line removed: {time_sync_data_list[i]} {match.group()}")
                    deleted_line = deleted_line + 1
                    deleted_subtitle_text.add(time_sync_data_list[i] + ':' + translated_text)
                    continue

            fout.write(f"{i}\n")
            fout.write(f"{time_sync_data_list[i]}\n")
            fout.write(f"{translated_text.strip()}\n")

            if i != len(time_sync_data_list)-1:
                fout.write("\n")
            
            fout.flush()
    
    # Print the total_length
    print(("\n[Info] Number of characters: "), total_length)
    
    if len(deleted_subtitle_text) > 0:
        print(("[Info] Number of short subtitles: "), deleted_line)          
        output_file_name = input_file_name.rsplit(".", 1)[0] 
        with open(output_file_name + "_deleted.txt", "w", encoding="utf-8") as f3:
            for text in deleted_subtitle_text:
                f3.write(text + "\n")
                
    if len(ignored_subtitle) > 0:
        print(("\n[Info] Number of repeated subtitles: "), ignored_line)
        output_file_name = input_file_name.rsplit(".", 1)[0]
        with open(output_file_name + "_repeated.txt", "w", encoding="utf-8") as f4:
            for text in ignored_subtitle:
                f4.write(text + "\n")

if __name__ == "__main__":
    appname = 'subtitle-translator'

    parser= argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("subtitle", nargs="+", type=str, help="subtitle file(s) to translate")
    parser.add_argument("--source", type=str, default="japanese", help="subtitle source language")
    parser.add_argument("--target", type=str, default="korean", help="subtitle target language")
    parser.add_argument("--skip_textlength", type=int, default=1, help="skip short text in the subtitles, useful for removing meaningless words")
    parser.add_argument("--ollama_host", type=str, default="localhost", help="Ollama host IP address")
    parser.add_argument("--ollama_port", type=str, default="11434", help="Ollama port number")
    parser.add_argument("--ollama_model", type=str, default="translategemma-12b-it-GGUF:Q8_0", help="Ollama model name to use")
   
    args = parser.parse_args().__dict__
    audio_language: str = args.pop("source")
    subtitle_language: str = args.pop("target")
    skip_textlength: int = args.pop("skip_textlength")
    ollama_host: str = args.pop("ollama_host")
    ollama_port: str = args.pop("ollama_port")
    ollama_model: str = args.pop("ollama_model")

    print("subtitle-translator Ollama 2025.02.17")

    for input_file_name in args.pop("subtitle"):
        print(f"\n[Info] Processing {input_file_name}")
        # check if the file exists 
        if not os.path.exists(input_file_name):
            print(f"[Error] The file does not exist: {input_file_name}")
            continue

        output_file_name = input_file_name.rsplit(".", 1)[0]
        translate_file(audio_language, subtitle_language, output_file_name + ".srt", skip_textlength, ollama_host, ollama_port, ollama_model)
            
        # Change the name of final srt same as video file name 
        try: 
            os.unlink (output_file_name + "_original.srt")
        except FileNotFoundError: 
            pass
        os.rename(output_file_name + ".srt", output_file_name + "_original.srt")
        os.rename(output_file_name + "_translated.srt", output_file_name + ".srt")
        print (("[Info] final srt file is saved"))

    print(("[Info] Done"))

    sys.exit(0)
