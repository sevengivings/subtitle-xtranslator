import gradio as gr
import os
import sys
from subprocess import PIPE, Popen

def subtitle_xtranslator(framework, model, device, audio_language, subtitle_language, skip_textlength, translator, translator_api_key, audio_file, progress=gr.Progress()):
    os.environ["DEEPL_API_KEY"] = translator_api_key
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    
    audio_file_name = f'"{audio_file}"'
    command = sys.executable + f' subtitle-xtranslator.py --framework {framework} --model {model} --device {device} --audio_language {audio_language} --subtitle_language {subtitle_language} --skip_textlength {skip_textlength} --translator {translator} --overwrite {audio_file_name}'    
    
    proc = Popen(command, stdout=PIPE, shell=True, encoding='utf-8')
    
    subtitle = ""
    logs = ""
    logs_list = []
    download_link = ""
    
    for line in iter(proc.stdout.readline, ""): 
        if line.startswith("[Info] Processed: "):
            # extract file name without extension from audio_file, and add '.srt'
            subtitle_file = audio_file.rsplit(".", 1)[0] + '.srt'
            # read subtitles from subtitle_file
            subtitle_lines = open(subtitle_file, 'r',
                                    encoding='UTF8').readlines()
            subtitle = ''.join(subtitle_lines)
            logs = ''.join(logs_list)
            download_link = f"{subtitle_file}"

            return subtitle, logs, download_link
        else:
            logs_list.append(line)
            
    return subtitle, logs, download_link

with gr.Blocks() as demo:
    # Create a Gradio interface for the subtitle_xtranslator function.
    gr.Markdown("## WebUI for subtitle-extractor.py 2023-11-16 preliminary version")
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
            ["none", "google", "deepl-api", "deepl-rapidapi"], label="translator", value="none")
        audio_file = gr.File(label="Upload", file_count="single")
        subtitle_file = gr.File(label="Download")
    with gr.Row():
        translator_api_key = gr.Textbox(
            label="translator_api_key", placeholder="your translator api key")
        processing_btn = gr.Button("Transcribe and translate")
    with gr.Row():
        subtitles = gr.Textbox(label="Subtitles")
        logs = gr.Textbox(label="logs")

    processing_btn.click(subtitle_xtranslator, inputs=[framework, model, device, audio_language, subtitle_language,
                         skip_textlength, translator, translator_api_key, audio_file], outputs=[subtitles, logs, subtitle_file],
                         scroll_to_output=True)

if __name__ == "__main__":
    if sys.platform == "win32": 
      demo.launch(share=False)
    else:
      demo.launch(share=True) 
