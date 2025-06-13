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
import argparse
import sys

cc = OpenCC('s2t')

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

def main():
    parser = argparse.ArgumentParser(description="Whisper 批次轉檔工具")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--input-folder', type=str, help='指定要處理的資料夾')
    group.add_argument('--input-file', type=str, help='指定單一檔案')
    parser.add_argument('--model', type=str, default='base', choices=['base', 'medium', 'large-v2'], help='Whisper 模型')
    parser.add_argument('--device', type=str, default='auto', choices=['auto', 'cpu', 'cuda'], help='運算裝置')
    parser.add_argument('--language', type=str, default='Chinese', choices=['Chinese', 'English'], help='語音語言')
    parser.add_argument('--no-prompt', action='store_true', help='不進行覆蓋詢問，適合自動化')
    args = parser.parse_args()

    # 裝置判斷
    device = None
    if args.device == 'auto':
        device = "cuda" if torch.cuda.is_available() else "cpu"
    else:
        device = args.device

    print(f"\n使用裝置：{device.upper()}，模型：{args.model}，語言：{args.language}")
    model = whisper.load_model(args.model, device=device)

    exts = (".mp3", ".mp4", ".m4a", ".wav")

    # 單一檔案
    if args.input_file:
        input_path = Path(args.input_file)
        if not input_path.exists():
            print("檔案不存在。")
            sys.exit(1)
        transcribe_file(str(input_path), args.language, model, input_path.parent)
    else:
        input_folder = Path(args.input_folder)
        if not input_folder.exists():
            print("資料夾不存在。")
            sys.exit(1)
        files = [f for f in input_folder.glob("*") if f.suffix.lower() in exts]
        # 列出將被覆蓋的 zip
        existing_zips = [f"{f.stem}.zip" for f in files if (input_folder / f"{f.stem}.zip").exists()]
        if existing_zips and not args.no_prompt:
            print("⚠️ 以下 zip 檔案已存在：")
            for name in existing_zips:
                print("   -", name)
            print("是否繼續？\n1. 是（預設）\n2. 否")
            cont = input("輸入選項 [1-2]：").strip()
            if cont == "2":
                print("已取消。")
                sys.exit(0)
        for media_file in tqdm(files, desc="批次處理中", ncols=80):
            try:
                transcribe_file(str(media_file), args.language, model, input_folder)
            except Exception as e:
                print(f"❌ 轉換失敗：{media_file.name} ({e})")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("使用方式：run_whisper_auto.py --input-folder <資料夾> 或 --input-file <音訊檔>")
        print("建議直接拖曳資料夾或檔案到 run_whisper_auto.bat，或於命令列加參數")
        sys.exit(1)
    main()

