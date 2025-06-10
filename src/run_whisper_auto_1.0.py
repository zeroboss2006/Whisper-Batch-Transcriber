import os
import re
import json
import whisper
import zipfile
import soundfile as sf
from pathlib import Path
from datetime import timedelta

def format_timestamp(seconds, for_vtt=False):
    td = timedelta(seconds=float(seconds))
    ts = str(td)
    if "." not in ts:
        ts += ".000"
    else:
        ts = ts[:-3]
    return ts if for_vtt else ts.replace(".", ",")

def transcribe_file(input_path, language, model, parent_folder):
    filename_raw = Path(input_path).stem
    filename_stem = re.sub(r'[\\/:*?"<>|]', "_", filename_raw)
    result = model.transcribe(input_path, language=language, verbose=True)
    zip_path = parent_folder / f"{filename_stem}.zip"

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        def save_and_zip(filename, content):
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
            zipf.write(filename)
            os.remove(filename)

        # SRT
        srt_content = ""
        for i, seg in enumerate(result["segments"], start=1):
            srt_content += f"{i}\n{format_timestamp(seg['start'])} --> {format_timestamp(seg['end'])}\n{seg['text'].strip()}\n\n"
        save_and_zip(f"{filename_stem}.srt", srt_content)

        # TXT
        txt_content = "\n\n".join(seg["text"].strip() for seg in result["segments"] if seg["text"].strip())
        save_and_zip(f"{filename_stem}.txt", txt_content)

        # MD
        md_lines = [f"# 語音筆記：{filename_raw}\n"]
        for seg in result["segments"]:
            start = format_timestamp(seg["start"])
            end = format_timestamp(seg["end"])
            text = seg["text"].strip()
            if text:
                md_lines.append(f"## [{start} – {end}]\n{text}\n")
        save_and_zip(f"{filename_stem}.md", "\n".join(md_lines))

        # JSON 完整
        with open(f"{filename_stem}.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        zipf.write(f"{filename_stem}.json")
        os.remove(f"{filename_stem}.json")

        # JSON segments-only
        segments_only = {"segments": [{"start": seg["start"], "end": seg["end"], "text": seg["text"].strip()} for seg in result["segments"]]}
        with open(f"{filename_stem}_segments_only.json", "w", encoding="utf-8") as f:
            json.dump(segments_only, f, ensure_ascii=False, indent=2)
        zipf.write(f"{filename_stem}_segments_only.json")
        os.remove(f"{filename_stem}_segments_only.json")

        # VTT
        vtt_content = "WEBVTT\n\n"
        for seg in result["segments"]:
            start = format_timestamp(seg["start"], for_vtt=True)
            end = format_timestamp(seg["end"], for_vtt=True)
            vtt_content += f"{start} --> {end}\n{seg['text'].strip()}\n\n"
        save_and_zip(f"{filename_stem}.vtt", vtt_content)

    print(f"✅ 完成：{zip_path}")

if __name__ == "__main__":
    input_path = input("請輸入檔案完整路徑：").strip('"').strip()
    if not os.path.exists(input_path):
        print("檔案不存在。")
        exit()

    language = "Chinese"  # v1.0僅支援預設語言，如需調整請自行修改
    model_choice = "base"
    model = whisper.load_model(model_choice)
    input_path_obj = Path(input_path)
    transcribe_file(str(input_path_obj), language, model, input_path_obj.parent)