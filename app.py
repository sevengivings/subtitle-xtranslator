import gradio as gr
import os
import sys
import datetime
import json
import asyncio 
import subprocess 

# get video length, ffprobe.exe is required 
def get_video_length(video_file):
  try: 
    out = subprocess.check_output(["ffprobe", "-v", "quiet", "-show_format", "-print_format", "json", video_file])
    ffprobe_data = json.loads(out)
    duration_seconds = float(ffprobe_data["format"]["duration"])
  except:
    duration_seconds = -1

  return int(duration_seconds)

async def subtitle_xtranslator(framework, model, device, audio_language, subtitle_language, skip_textlength, translator, translator_api_key, audio_file, progress=gr.Progress()):
    os.environ["DEEPL_API_KEY"] = translator_api_key
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    
    audio_file_name = ""
    video_length = [] 
    total_video_length = 0
    for file in audio_file: 
        audio_file_name += f'"{file}" '
        length = get_video_length(file)
        video_length.append(length)
        total_video_length += length
        
    if total_video_length < 0:
        progress(0, desc="Starting... ffprobe is required for progressive bar")
    else: 
        progress(0, desc="Starting...")
    
    # {sys.executable} not working on Colab 
    command = f'python subtitle-xtranslator.py --framework {framework} --model {model} --device {device} --audio_language {audio_language} --subtitle_language {subtitle_language} --skip_textlength {skip_textlength} --translator {translator} --overwrite {audio_file_name}'    
    
    proc = await asyncio.create_subprocess_shell(command, stdout=asyncio.subprocess.PIPE)
    
    subtitle = ""
    logs = ""
    logs_list = []
    download_link = []
    file_count = len(audio_file)
    file_index = 0 
    video_seconds_processed = 0 
    
    while True: 
        line = await proc.stdout.readline() 
        if not line:
            break 

        line = str(line, encoding='utf-8')
        print('>' + line.strip())
        if line.startswith("[Info] Processed: ") or line.startswith("[정보] 처리된 파일: "):
            # extract file name without extension from audio_file, and add '.srt'
            subtitle_file = audio_file[file_index].rsplit(".", 1)[0] + '.srt'
            # read subtitles from subtitle_file
            subtitle_lines = open(subtitle_file, 'r',
                                    encoding='UTF8').readlines()
            
            subtitle += ''.join(subtitle_lines)
            logs += ''.join(logs_list)
            download_link.append(f"{subtitle_file}") 
            
            video_seconds_processed += video_length[file_index]
            
            file_index += 1 
            if file_index == file_count:
                break
        else:
            logs_list.append(line)
            
            # get time data from subtitle '[01:25.300 --> 01:27.720]' or [01:30:25.000 --> 01:35:25.000]
            if line.find('-->') > 0: 
                time_data_string = line.split('-->')[0][1:-1]
                try: 
                    time_data = datetime.datetime.strptime(time_data_string, '%H:%M:%S.%f')
                except ValueError:
                    time_data = datetime.datetime.strptime(time_data_string, '%M:%S.%f')

                video_seconds = time_data.time().second + time_data.time().minute*60 + time_data.time().hour*3600 
                # get video length from video_length list
                if video_length[file_index] != -1 and video_seconds > 0:
                    progress((video_seconds + video_seconds_processed)/ total_video_length, desc=f"processing {os.path.basename(audio_file[file_index])}") # not working 
    
    await proc.wait()        
    
    return subtitle, logs, download_link    

with gr.Blocks() as demo:
    # Create a Gradio interface for the subtitle_xtranslator function.
    gr.Markdown("### WebUI for subtitle-xtranslator.py v20231117a")
    with gr.Row():
        framework = gr.Dropdown(
            ["stable-ts", "whisper", "faster-whisper"], label="framework", value="stable-ts")
        model = gr.Dropdown(["small", "medium", "large-v2"], label="model", value="medium")
        device = gr.Dropdown(["cuda", "cpu"], label="device", value="cuda")
        audio_language = gr.Dropdown(
            ["ko", "en", "ja", "zh", "fr"], label="audio_language", value="ja")
        subtitle_language = gr.Dropdown(
            ["ko", "en", "ja", "zh", "fr"], label="subtitle_language", value="ko")
        skip_textlength = gr.Dropdown(
            ["0", "1", "2", "3"], label="skip_textlength", value="1")
        translator = gr.Dropdown(
            ["none", "google", "deepl-api"], label="translator", value="none")
        audio_file = gr.File(label="Upload multple mp3", file_count="multiple")
        subtitle_file = gr.File(label="Download subtitles", file_count="multiple")
    with gr.Row():
        translator_api_key = gr.Textbox(
            label="translator_api_key", placeholder="your translator api key")
        processing_btn = gr.Button("Transcribe and translate(Please be patient for progress bar update)")
    with gr.Row():
        subtitles = gr.Textbox(label="Subtitles")
        logs = gr.Textbox(label="logs")

    processing_btn.click(subtitle_xtranslator, inputs=[framework, model, device, audio_language, subtitle_language,
                         skip_textlength, translator, translator_api_key, audio_file], outputs=[subtitles, logs, subtitle_file])

if __name__ == "__main__":
    if sys.platform == "win32": 
      demo.launch(share=False)
    else:
      demo.launch(share=True) 
