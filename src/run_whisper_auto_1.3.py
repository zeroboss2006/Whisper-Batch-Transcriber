import os
import re
import json
import torch
import whisper
import zipfile
import soundfile as sf
from pathlib import Path
from datetime import timedelta
from tqdm import tqdm
from opencc import OpenCC

cc = OpenCC('s2t')  # 簡體轉繁體

def format_timestamp(seconds, for_vtt=False):
    td = timedelta(seconds=float(seconds))
    ts = str(td)
    if "." not in ts:
        ts += ".000"
    else:
        ts = ts[:-3]
    return ts if for_vtt else ts.replace(".", ",")

def convert(text):
    return cc.convert(text.strip())

def get_unique_zip_path(base_path):
    if not base_path.exists():
        return base_path
    i = 2
    while True:
        new_path = base_path.with_name(f"{base_path.stem}({i}){base_path.suffix}")
        if not new_path.exists():
            return new_path
        i += 1

def transcribe_file(input_path, language, model, parent_folder):
    filename_raw = Path(input_path).stem
    filename_stem = re.sub(r'[\\/:*?"<>|]', "_", filename_raw)

    # 音訊長度警告
    try:
        with sf.SoundFile(input_path) as f:
            duration_sec = len(f) / f.samplerate
        if duration_sec > 3600:
            print(f"⚠️ 音訊長度超過 60 分鐘：{filename_raw}，建議使用 large-v2 模型以提高準確度。\n")
    except:
        print(f"⚠️ 無法檢測長度（可能非純音訊格式）：{filename_raw}\n")

    result = model.transcribe(input_path, language=language, verbose=True)
    zip_path = parent_folder / f"{filename_stem}.zip"
    zip_path = get_unique_zip_path(zip_path)

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        def save_and_zip(filename, content):
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
            zipf.write(filename)
            os.remove(filename)

        # SRT
        srt_content = ""
        for i, seg in enumerate(result["segments"], start=1):
            srt_content += f"{i}\n{format_timestamp(seg['start'])} --> {format_timestamp(seg['end'])}\n{convert(seg['text'])}\n\n"
        save_and_zip(f"{filename_stem}.srt", srt_content)

        # TXT
        txt_content = "\n\n".join(convert(seg["text"]) for seg in result["segments"] if seg["text"].strip())
        save_and_zip(f"{filename_stem}.txt", txt_content)

        # MD
        md_lines = [f"# 語音筆記：{filename_raw}\n"]
        for seg in result["segments"]:
            start = format_timestamp(seg["start"])
            end = format_timestamp(seg["end"])
            text = convert(seg["text"])
            if text:
                md_lines.append(f"## [{start} – {end}]\n{text}\n")
        save_and_zip(f"{filename_stem}.md", "\n".join(md_lines))

        # JSON 完整
        result_converted = {
            key: [
                {k: (convert(v) if k == "text" else v) for k, v in seg.items()}
                for seg in val
            ] if key == "segments" else val
            for key, val in result.items()
        }
        with open(f"{filename_stem}.json", "w", encoding="utf-8") as f:
            json.dump(result_converted, f, ensure_ascii=False, indent=2)
        zipf.write(f"{filename_stem}.json")
        os.remove(f"{filename_stem}.json")

        # JSON segments-only
        segments_only = {"segments": [{"start": seg["start"], "end": seg["end"], "text": convert(seg["text"])} for seg in result["segments"]]}
        with open(f"{filename_stem}_segments_only.json", "w", encoding="utf-8") as f:
            json.dump(segments_only, f, ensure_ascii=False, indent=2)
        zipf.write(f"{filename_stem}_segments_only.json")
        os.remove(f"{filename_stem}_segments_only.json")

        # VTT
        vtt_content = "WEBVTT\n\n"
        for seg in result["segments"]:
            start = format_timestamp(seg["start"], for_vtt=True)
            end = format_timestamp(seg["end"], for_vtt=True)
            vtt_content += f"{start} --> {end}\n{convert(seg['text'])}\n\n"
        save_and_zip(f"{filename_stem}.vtt", vtt_content)

    print(f"✅ 完成：{zip_path}")

if __name__ == "__main__":
    input_path = input("請輸入檔案或資料夾完整路徑：").strip('"').strip()
    if not os.path.exists(input_path):
        print("檔案或資料夾不存在。")
        exit()

    print("請選擇語言：\n1. 中文\n2. 英文")
    lang_choice = input("輸入數字 [1-2]，預設為 1：").strip()
    language = "English" if lang_choice == "2" else "Chinese"

    print("\n請選擇模型：\n1. base\n2. medium\n3. large-v2")
    model_map = {"1": "base", "2": "medium", "3": "large-v2"}
    model_choice = model_map.get(input("輸入數字 [1-3]，預設為 1：").strip(), "base")

    print("\n選擇運算裝置：\n1. 自動\n2. 強制 CPU\n3. 強制 GPU")
    device_choice = input("輸入數字 [1-3]，預設為 1：").strip()
    if device_choice == "2":
        device = "cpu"
    elif device_choice == "3" and torch.cuda.is_available():
        device = "cuda"
    else:
        device = "cuda" if torch.cuda.is_available() else "cpu"

    print(f"\n使用裝置：{device.upper()}，模型：{model_choice}，語言：{language}")
    model = whisper.load_model(model_choice, device=device)

    input_path_obj = Path(input_path)
    exts = (".mp3", ".mp4", ".m4a", ".wav")

    if input_path_obj.is_file():
        transcribe_file(str(input_path_obj), language, model, input_path_obj.parent)
    elif input_path_obj.is_dir():
        files = [f for f in input_path_obj.glob("*") if f.suffix.lower() in exts]
        if any((input_path_obj / f"{f.stem}.zip").exists() for f in files):
            print("⚠️ 部分輸出檔案已存在。是否繼續？\n1. 是（預設）\n2. 否")
            cont = input("輸入選項 [1-2]：").strip()
            if cont == "2":
                print("已取消。"); exit()
        for media_file in tqdm(files, desc="批次處理中", ncols=80):
            try:
                transcribe_file(str(media_file), language, model, input_path_obj)
            except Exception as e:
                print(f"❌ 轉換失敗：{media_file.name} ({e})")
    else:
        print("不支援的路徑格式。")
