# Translate subtitle (DeepL-API)  

import os 
import sys
import argparse
import re
import deepl

# for DeepL API translation, check if DEEPL_API_KEY is set in environment variables.
# How to set DeepL API key in PowerShell : Set-Item -Path env:DEEPL_API_KEY -Value "your-id"
# How to remove DeepL API key in PowerShell : Remove-Item -Path env:DEEPL_API_KEY
# How to set DeepL API key in Prompt : set DEEPL_API_KEY=your-id
def translate_text_deepl_api(deepl_api_key, subtitle_language, split_list): 
    translator = deepl.Translator(deepl_api_key)    

    usage = translator.get_usage()
    if usage.any_limit_reached:
        print(('[Error] DeepL API Translation limit reached.'))
        sys.exit(1) 
    if usage.character.valid:
        print(f"Character usage: {usage.character.count} of {usage.character.limit}")
    if usage.document.valid:
        print(f"Document usage: {usage.document.count} of {usage.document.limit}")

    if subtitle_language.upper() == "EN":
        subtitle_language = "EN-US"
        
    result = translator.translate_text(split_list, target_lang=subtitle_language.upper())

    return result 
    
# removes unnecessary short and repeated characters from the subtitle text and translate using Google Cloud Translate 
def translate_file(audio_language, subtitle_language, text_split_size, input_file_name, skip_textlength):
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
                
    # split lists into small lists 
    current_length = 0
    total_length = 0 
    current_list = [] 
    split_lists = []
    
    for string in subtitle_text_list:
        if current_length + len(string) < text_split_size:
            current_list.append(string)
            current_length += len(string) + 1  # 1 for string = '\n'.join(split_list)
        else:
            split_lists.append(current_list)
            current_list = [string]
            current_length = len(string)
        
        total_length += len(string)

    if current_list:
        split_lists.append(current_list)
     
    # translate each splitted list 
    i = 0 
    for split_list in split_lists:
        deepl_api_key = ""
        try: 
            deepl_api_key = os.environ['DEEPL_API_KEY']
            print(("[Info] Using DeepL API"))
        except KeyError:
            print(("[Error] Please set DEEPL_API_KEY environment variable."))
            sys.exit(1)

        result = translate_text_deepl_api(deepl_api_key, subtitle_language, split_list)
        translated_list = []  
        for translation in result:
            translated_list.append(translation.text)            
        
        print(("[Info] number of sentences translated: "), len(translated_list)) 
        
        # for safety, save to .srt file every successful translation.  
        # Save the subtitle text to a new file.
        # create a new file with the same name as the input file, consider file name contains multiple '.' 
        output_file_name = input_file_name.rsplit(".", 1)[0]
                
        with open(output_file_name + "_translated.srt", "a", encoding="utf-8") as fout:       
            for string in translated_list: 
                # remove meaningless repeated text
                match = re.search(r"(\b[\w\u00C0-\uFFFF]+\b)([,\.\;\s]+\1)+" , string)
                if match:
                    repeated_text = match.group(1)  # repeated text
                    total_occurrences = string.count(repeated_text)  # total occurrences of the repeated text 
                    if total_occurrences > 10:
                        print(f"over 10 times repeated pattern in one line removed: {time_sync_data_list[i]} {match.group()}")
                        deleted_line = deleted_line + 1
                        deleted_subtitle_text.add(time_sync_data_list[i] + ':' + string)
                        i += 1
                        continue

                fout.write(f"{i}\n")
                fout.write(f"{time_sync_data_list[i]}\n")
                fout.write(f"{string.strip()}\n")

                if i != len(time_sync_data_list)-1:
                    fout.write("\n")     
                i += 1         
                    
        translated_list = []        
    
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
    parser.add_argument("--source", type=str, default="ja", help="subtitle source language")
    parser.add_argument("--target", type=str, default="ko", help="subtitle target language")
    parser.add_argument("--skip_textlength", type=int, default=1, help="skip short text in the subtitles, useful for removing meaningless words")
    parser.add_argument("--text_split_size", type=int, default=1000, help="split the text into small lists to speed up the translation process")
   
    args = parser.parse_args().__dict__
    audio_language: str = args.pop("source")
    subtitle_language: str = args.pop("target")
    skip_textlength: int = args.pop("skip_textlength")
    text_split_size: int = args.pop("text_split_size")

    print("subtitle-translator DeepL-API 2025.02.17")

    for input_file_name in args.pop("subtitle"):
        print(f"\n[Info] Processing {input_file_name}")
        # check if the file exists 
        if not os.path.exists(input_file_name):
            print(f"[Error] The file does not exist: {input_file_name}")
            continue

        output_file_name = input_file_name.rsplit(".", 1)[0]
        translate_file(audio_language, subtitle_language, text_split_size, output_file_name + ".srt", skip_textlength)
            
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
