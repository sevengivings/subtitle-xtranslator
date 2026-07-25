# Translate subtitle (Ollama TranslateGemma)  
# pip install requests 
# pip install tqdm 
import os 
import sys
import argparse
import re
import requests
from tqdm import tqdm

OLLAMA_TIMEOUT = (10, 600)
OLLAMA_OPTIONS = {
    "temperature": 0.0,
    "top_p": 0.9,
    "repeat_penalty": 1.05,
    "num_ctx": 8192,
}

SUBTITLE_STYLE_PROMPT = (
    "Many subtitles are short everyday Japanese, casual reactions, interjections, or adult video dialogue. "
    "Translate them into natural Korean spoken subtitle style. "
    "Keep short exclamations, moans, reactions, and backchannels short in Korean too. "
    "Do not over-explain unclear short utterances or add alternatives such as '(or ...)'. "
    "Do not sanitize adult context unnecessarily. "
    "Preserve concrete nouns, body parts, actions, and who is speaking when they are present in the source. "
    "If ASR text is unclear or noisy, choose one concise plausible subtitle translation without explaining uncertainty. "
    "Do not make the line more explicit than the source. "
)

def translate_text_ollama(host, port, model, source_lang, target_lang, text):
    url = f"http://{host}:{port}/api/chat"

    if '\n' in text or re.match(r'^\[\d+\]\s+', text.strip()):
        system_prompt = (
            f"You are a professional video subtitle translator. "
            f"Translate the following text from {source_lang} to {target_lang}. "
            f"{SUBTITLE_STYLE_PROMPT}"
            f"The input contains lines numbered [N]. "
            f"Translate each line separately and prefix the output with the same [N]. "
            f"Do not merge lines. Ensure the translation is natural, but strictly maintain the original line breaks. "
            f"Do not renumber lines. "
            f"Output only the translated text."
        )
    else:
        system_prompt = (
            f"You are a professional video subtitle translator. "
            f"Translate the following text from {source_lang} to {target_lang}. "
            f"{SUBTITLE_STYLE_PROMPT}"
            f"Ensure the translation is natural and conversational. "
            f"Do not include any introductory, concluding remarks, or notes. "
            f"Output only the translated text."
        )

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ],
        "stream": False,
        "options": OLLAMA_OPTIONS
    }

    try:
        # print(f"[Debug] Input: {text.strip()}")
        response = requests.post(url, json=payload, timeout=OLLAMA_TIMEOUT)
        response.raise_for_status()
        result = response.json()
        # print(f"[Debug] Output: {result}")
        translated_text = result.get("message", {}).get("content", "")
        
        return translated_text.strip()
    except Exception as e:
        raise RuntimeError(f"Ollama translation failed: {e}") from e

def parse_batch_translation(result, batch):
    local_to_original = {local_no: original_index for local_no, (original_index, _) in enumerate(batch, 1)}
    parsed = {}
    current_original_index = -1
    seen_local_numbers = set()

    for line in result.splitlines():
        line = line.strip()
        if not line:
            continue

        strict_match = re.match(r'^\[(\d+)\]\s*(.*)$', line)
        fallback_match = re.match(r'^(\d+)[\.\)]\s+(.*)$', line) if not strict_match else None
        match = strict_match or fallback_match

        if match:
            local_no = int(match.group(1))
            text = match.group(2).strip()

            if local_no not in local_to_original:
                print(f"[Warning] Batch output number out of range: [{local_no}]")
                current_original_index = -1
                continue

            if local_no in seen_local_numbers:
                print(f"[Warning] Duplicate batch output number: [{local_no}]")

            seen_local_numbers.add(local_no)
            original_index = local_to_original[local_no]
            parsed[original_index] = text
            current_original_index = original_index
        elif current_original_index != -1:
            if parsed[current_original_index]:
                parsed[current_original_index] += " " + line
            else:
                parsed[current_original_index] = line

    missing_local_numbers = set(local_to_original) - seen_local_numbers
    for local_no in sorted(missing_local_numbers):
        print(f"[Warning] Missing batch output number: [{local_no}]")

    return parsed

def has_abnormal_repetition(translated_text):
    match = re.search(r"(\b[\w\u00C0-\uFFFF]+\b)([,\.\;\s]+\1)+" , translated_text)
    if not match:
        return False, None

    repeated_text = match.group(1)
    total_occurrences = translated_text.count(repeated_text)
    if total_occurrences > 10:
        return True, match.group()

    return False, None

def validate_translations(translated_texts, time_sync_data_list):
    if len(translated_texts) != len(time_sync_data_list):
        raise RuntimeError(
            f"Output subtitle count mismatch: translations {len(translated_texts)}, timecodes {len(time_sync_data_list)}"
        )

    for i, translated_text in enumerate(translated_texts):
        if not translated_text or not translated_text.strip():
            raise RuntimeError(f"Empty translation remains at subtitle {i + 1}")
        if i >= len(time_sync_data_list) or "-->" not in time_sync_data_list[i]:
            raise RuntimeError(f"Missing timecode at subtitle {i + 1}")

def validate_srt_file(path, expected_count):
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        raise RuntimeError(f"Output file is empty or missing: {path}")

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    blocks = [block for block in re.split(r'\n\s*\n', content.strip()) if block.strip()]
    if len(blocks) != expected_count:
        raise RuntimeError(f"Output SRT count mismatch: expected {expected_count}, got {len(blocks)}")

    for i, block in enumerate(blocks, 1):
        lines = block.splitlines()
        if len(lines) < 3:
            raise RuntimeError(f"Invalid SRT block at subtitle {i}")
        if not lines[0].strip().isdigit() or int(lines[0].strip()) != i:
            raise RuntimeError(f"Invalid SRT number at subtitle {i}")
        if "-->" not in lines[1]:
            raise RuntimeError(f"Missing timecode at subtitle {i}")
        if not "\n".join(lines[2:]).strip():
            raise RuntimeError(f"Empty subtitle text at subtitle {i}")

def write_audit_files(output_file_name, deleted_subtitle_text, deleted_line, ignored_subtitle, ignored_line):
    if len(deleted_subtitle_text) > 0:
        print(("[Info] Number of short/invalid subtitles: "), deleted_line)
        with open(output_file_name + "_deleted.txt", "w", encoding="utf-8") as f3:
            for text in deleted_subtitle_text:
                f3.write(text + "\n")

    if len(ignored_subtitle) > 0:
        print(("\n[Info] Number of repeated subtitles: "), ignored_line)
        with open(output_file_name + "_repeated.txt", "w", encoding="utf-8") as f4:
            for text in ignored_subtitle:
                f4.write(text + "\n")

def find_original_backup_name(output_file_name):
    backup_name = output_file_name + "_original.srt"
    if not os.path.exists(backup_name):
        return backup_name

    suffix = 1
    while True:
        backup_name = f"{output_file_name}_original_{suffix}.srt"
        if not os.path.exists(backup_name):
            return backup_name
        suffix += 1

def replace_original_srt(input_file_name, translated_file_name):
    output_file_name = input_file_name.rsplit(".", 1)[0]
    backup_name = find_original_backup_name(output_file_name)

    os.replace(input_file_name, backup_name)
    try:
        os.replace(translated_file_name, input_file_name)
    except Exception:
        if os.path.exists(backup_name) and not os.path.exists(input_file_name):
            os.replace(backup_name, input_file_name)
        raise

# removes unnecessary short and repeated characters from the subtitle text and translate using Ollama
def translate_file(audio_language, subtitle_language, input_file_name, skip_textlength, ollama_host, ollama_port, ollama_model, batch_translate=False, text_split_size=1000):
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
    translated_file_name = output_file_name + "_translated.srt"
    part_file_name = translated_file_name + ".part"
    total_length = sum(len(s) for s in subtitle_text_list)
    
    print(f"[Info] Starting translation of {len(subtitle_text_list)} lines with Ollama ({ollama_model})...")

    translated_batch = [""] * len(subtitle_text_list)
    try:
        if batch_translate:
            print(f"[Info] Batch translation mode enabled. Split size: {text_split_size}")

            current_length = 0
            current_batch = []
            batches = []

            for i, string in enumerate(subtitle_text_list):
                if current_batch and current_length + len(string) >= text_split_size:
                    batches.append(current_batch)
                    current_batch = []
                    current_length = 0

                current_batch.append((i, string))
                current_length += len(string) + 1

            if current_batch:
                batches.append(current_batch)

            for batch in tqdm(batches, desc="Translating batches"):
                numbered_batch = [f"[{local_no}] {line}" for local_no, (_, line) in enumerate(batch, 1)]
                full_text = "\n".join(numbered_batch)
                result = translate_text_ollama(ollama_host, ollama_port, ollama_model, audio_language, subtitle_language, full_text)
                parsed = parse_batch_translation(result, batch)

                for original_index, text in parsed.items():
                    translated_batch[original_index] = text

            missing_indices = [
                i for i, translated_text in enumerate(translated_batch)
                if not translated_text or not translated_text.strip()
            ]
            if missing_indices:
                print(f"[Warning] Retrying {len(missing_indices)} missing subtitle(s) one by one...")
                for i in tqdm(missing_indices, desc="Retrying missing lines"):
                    translated_batch[i] = translate_text_ollama(
                        ollama_host,
                        ollama_port,
                        ollama_model,
                        audio_language,
                        subtitle_language,
                        subtitle_text_list[i]
                    )
        else:
            iterator = tqdm(subtitle_text_list, desc="Translating lines")
            for i, string in enumerate(iterator):
                translated_batch[i] = translate_text_ollama(
                    ollama_host,
                    ollama_port,
                    ollama_model,
                    audio_language,
                    subtitle_language,
                    string
                )

        for i, translated_text in enumerate(translated_batch):
            repeated, repeated_pattern = has_abnormal_repetition(translated_text)
            if repeated:
                print(f"over 10 times repeated pattern in one line removed: {time_sync_data_list[i]} {repeated_pattern}")
                deleted_line = deleted_line + 1
                deleted_subtitle_text.add(time_sync_data_list[i] + ':' + translated_text)
                raise RuntimeError(f"Abnormal repeated translation at subtitle {i + 1}")

        validate_translations(translated_batch, time_sync_data_list)

        # Write to .part first so incomplete translations never become the final result.
        with open(part_file_name, "w", encoding="utf-8") as fout:
            for i, translated_text in enumerate(translated_batch):
                fout.write(f"{i + 1}\n")
                fout.write(f"{time_sync_data_list[i]}\n")
                fout.write(f"{translated_text.strip()}\n")

                if i != len(time_sync_data_list)-1:
                    fout.write("\n")

        validate_srt_file(part_file_name, len(time_sync_data_list))
        os.replace(part_file_name, translated_file_name)

        # Print the total_length
        print(("\n[Info] Number of characters: "), total_length)
        return translated_file_name
    except Exception:
        if os.path.exists(part_file_name):
            os.unlink(part_file_name)
        raise
    finally:
        write_audit_files(output_file_name, deleted_subtitle_text, deleted_line, ignored_subtitle, ignored_line)

if __name__ == "__main__":
    appname = 'subtitle-translator'

    parser= argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("subtitle", nargs="+", type=str, help="subtitle file(s) to translate")
    parser.add_argument("--source", type=str, default="japanese", help="subtitle source language")
    parser.add_argument("--target", type=str, default="korean", help="subtitle target language")
    parser.add_argument("--skip_textlength", type=int, default=0, help="skip short text in the subtitles, useful for removing meaningless words")
    parser.add_argument("--ollama_host", type=str, default="localhost", help="Ollama host IP address")
    parser.add_argument("--ollama_port", type=str, default="11434", help="Ollama port number")
    parser.add_argument("--ollama_model", type=str, default="hf.co/mradermacher/translategemma-12b-it-GGUF:Q8_0", help="Ollama model name to use")
    parser.add_argument("--batch_translate", action='store_true', help="Translate all lines")
    parser.add_argument("--text_split_size", type=int, default=300, help="split the text into small lists for batch translation")
   
    args = parser.parse_args().__dict__
    audio_language: str = args.pop("source")
    subtitle_language: str = args.pop("target")
    skip_textlength: int = args.pop("skip_textlength")
    ollama_host: str = args.pop("ollama_host")
    ollama_port: str = args.pop("ollama_port")
    ollama_model: str = args.pop("ollama_model")
    batch_translate: bool = args.pop("batch_translate")
    text_split_size: int = args.pop("text_split_size")

    print("subtitle-translator Ollama 2025.02.17")

    for input_file_name in args.pop("subtitle"):
        print(f"\n[Info] Processing {input_file_name}")
        # check if the file exists 
        if not os.path.exists(input_file_name):
            print(f"[Error] The file does not exist: {input_file_name}")
            continue

        output_file_name = input_file_name.rsplit(".", 1)[0]
        try:
            translated_file_name = translate_file(
                audio_language,
                subtitle_language,
                output_file_name + ".srt",
                skip_textlength,
                ollama_host,
                ollama_port,
                ollama_model,
                batch_translate,
                text_split_size
            )
            replace_original_srt(output_file_name + ".srt", translated_file_name)
            print (("[Info] final srt file is saved"))
        except Exception as e:
            print(f"[Error] Failed to process {input_file_name}: {e}")
            continue

    print(("[Info] Done"))

    sys.exit(0)
