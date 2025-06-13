@echo off
REM 批次模式：自動執行（請根據需求調整參數）
REM 範例：資料夾批次、large-v2、GPU、中文、遇覆蓋自動跳過詢問

python run_whisper_auto_1.7.py --input-folder "D:\media" --model large-v2 --language zh --device gpu --no-prompt

pause
