# ffprobe is required 
import gradio as gr
import os
import asyncio
import subprocess
import json
import datetime 
import time 

# get video length, ffprobe.exe is required 
def get_video_length(video_file):
  try: 
    out = subprocess.check_output(["ffprobe", "-v", "quiet", "-show_format", "-print_format", "json", video_file])
    ffprobe_data = json.loads(out)
    duration_seconds = float(ffprobe_data["format"]["duration"])
  except:
    duration_seconds = 0.0

  return int(duration_seconds)

async def subtitle_xtranslator(framework, model, device, audio_language, subtitle_language, skip_textlength, translator, translator_api_key, audio_file, progress=gr.Progress()):
  os.environ["DEEPL_API_KEY"] = translator_api_key
  os.environ['PYTHONIOENCODING'] = 'utf-8'

  command = f"python subtitle-xtranslator.py --framework {framework} --model {model} --device {device} --audio_language {audio_language} --subtitle_language {subtitle_language} --skip_textlength {skip_textlength} --translator {translator} --overwrite {audio_file}"
  video_length = get_video_length(audio_file)

  subtitle = ""
  logs = "" 
  lines = [] 
  download_link = "" 

  proc = await asyncio.create_subprocess_shell(command, stdout=asyncio.subprocess.PIPE)

  while True:
    line = await proc.stdout.readline()
    if not line:
      break; 
  
    line = str(line, encoding="utf-8") 

    if line.startswith("[Info] Processed: "):
        # extract file name without extension from audio_file, and add '.srt' 
        subtitle_file = audio_file.rsplit(".", 1)[0] + '.srt'
        # read subtitles from subtitle_file
        subtitle_lines = open(subtitle_file, 'r', encoding='UTF8').readlines() 
        subtitle = ''.join(subtitle_lines)
        logs = ''.join(lines)
        download_link = f"{subtitle_file}"

        return subtitle, logs, download_link
    else: 
        lines.append(line)        

        # get time data from subtitle '[01:25.300 --> 01:27.720]' or [01:30:25.000 --> 01:35:25.000]
        if line.find('-->') > 0: 
            time_data = line.split('-->')[0][1:-1]
            try: 
                time_data = datetime.datetime.strptime(time_data, '%H:%M:%S.%f')
            except ValueError:
                time_data = datetime.datetime.strptime(time_data, '%M:%S.%f')

            video_seconds = time_data.time().second + time_data.time().minute*60 + time_data.time().hour*3600 

            if video_length != 0.0 and video_seconds > 0:
                progress(video_seconds / video_length * 100) # not working 
                time.sleep(0.01)

  await proc.wait()

with gr.Blocks() as demo:
# Create a Gradio interface for the subtitle_xtranslator function.
    gr.Markdown("## WebUI for subtitle-extractor.py")
    with gr.Row(): 
        framework = gr.Dropdown(["stable-ts", "whisper", "faster-whisper"], label="framework", value="stable-ts")
        model = gr.Dropdown(["small", "medium", "large-v2", "large-v3"], label="model", value="medium")
        device = gr.Dropdown(["cuda", "cpu"], label="device", value="cuda")
        audio_language = gr.Dropdown(["ko","en","ja","zh","fr"], label="audio_language", value="ja")
        subtitle_language = gr.Dropdown(["ko","en","ja","zh","fr"], label="subtitle_language", value="ko")
        skip_textlength = gr.Dropdown(["0","1","2","3"], label="skip_textlength", value="1")
        translator = gr.Dropdown(["none", "google", "deepl-api", "deepl-rapidapi"], label="translator", value="none")
        audio_file = gr.File(label="Upload")
        subtitle_file = gr.File(label="Download")
    with gr.Row(): 
        translator_api_key = gr.Textbox(label="translator_api_key", placeholder="your translator api key")    
        processing_btn = gr.Button("Transcribe and translate")
    with gr.Row(): 
        subtitles = gr.Textbox(label="Subtitles")
        logs = gr.Textbox(label="logs") 

    processing_btn.click(subtitle_xtranslator, inputs=[framework, model, device, audio_language, subtitle_language, skip_textlength, translator, translator_api_key, audio_file], outputs=[subtitles, logs, subtitle_file]) 

if __name__ == "__main__":
    demo.launch(share=True) 