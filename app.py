import gradio as gr
import os

def subtitle_xtranslator(framework, model, device, audio_language, subtitle_language, skip_textlength, translator, translator_api_key, audio_file):
  os.environ["DEEPL_API_KEY"] = translator_api_key

  command = f"python subtitle-xtranslator.py --framework {framework} --model {model} --device {device} --audio_language {audio_language} --subtitle_language {subtitle_language} --skip_textlength {skip_textlength} --translator {translator} {audio_file}"

  output = os.popen(command).readlines()
  subtitle = ""
  logs = "" 
  lines = [] 
  for line in output:
    if line.startswith("[Info] Processed: "):
      # extract file name without extension from audio_file, and add '.srt' 
      subtitle_file = audio_file.rsplit(".", 1)[0] + '.srt'
      # read subtitles from subtitle_file
      subtitle_lines = open(subtitle_file, 'r', encoding='UTF8').readlines() 
      subtitle = '\n'.join(subtitle_lines)
      logs = '\n'.join(lines)
      download_link = f"{subtitle_file}"
    else: 
      lines.append(line)  
 
  return subtitle, logs, download_link

# Create a Gradio interface for the subtitle_xtranslator function.
interface = gr.Interface( 
    fn=subtitle_xtranslator,
    inputs=[
        gr.Dropdown(["stable-ts", "whisper", "faster-whisper"], label="framework"),
        gr.Dropdown(["small", "medium", "large-v2", "large-v3"], label="model"),
        gr.Dropdown(["cuda", "cpu"], label="device"),
        gr.Dropdown(["ko","en","ja","zh","fr"], label="audio_language"),
        gr.Dropdown(["ko","en","ja","zh","fr"], label="subtitle_language"),
        gr.Dropdown(["0","1","2","3"], label="skip_textlength"),
        gr.Dropdown(["none", "google", "deepl-api", "deepl-rapidapi"], label="translator"),
        gr.Textbox(label="translator_api_key", placeholder="your translator api key"),    
        gr.File(label="Audio File"),
    ],
    outputs=[
        gr.Textbox(label="Subtitles"),
        gr.Textbox(label="logs"),
        gr.File(label="Download Subtitles"),
    ],
    title="Subtitle XTranslator",
    description="Extracts subtitles and translates .srt using subtitle-xtranslator.py."
)

if __name__ == "__main__":
    interface.launch(show_api=False, share=True) 