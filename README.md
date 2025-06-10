# Whisper Batch Transcriber
## 目錄
- [簡介](#簡介)
- [安裝](#安裝)
- [使用範例](#使用範例)
- [參數說明](#參數說明)
- [注意事項](#注意事項)
- [授權](#授權)
- [貢獻](#貢獻)
- 
## 簡介
本工具為 Whisper 批次語音轉錄腳本，支援資料夾一次轉檔、模型選擇、裝置選擇與繁體轉換。
需先安裝 [OpenAI Whisper](https://github.com/openai/whisper) 與相關依賴。

## 安裝
```bash
python -m venv whisper-env
source whisper-env/bin/activate  # 或 Windows: whisper-env\Scripts\activate
pip install -r requirements.txt
```

## 使用範例

1. 建立並啟動虛擬環境：
```bat
python -m venv whisper-env
whisper-env\Scripts\activate
pip install -r requirements.txt
```
2. 執行方式：
拖曳資料夾或單一檔案到 run_whisper_auto.bat 上執行
或在 cmd 中：
```bat
複製
cd src
run_whisper_auto.bat C:\path\to\media
```
3. 功能描述：
自動啟動 virtualenv
自動識別參數型態（資料夾 vs 無參數）
執行完保留 console 窗口讓使用者查看日誌

## 參數說明

本工具支援下列 CLI 參數，可按需搭配使用：

| 參數 | 說明 | 範例 |
|------|------|------|
| `--input-folder <path>` | 指定資料夾進行批次處理 | `--input-folder ./media` |
| `--input-file <path>` | 處理單一音訊或影片檔案 | `--input-file ./video.mp4` |
| `--model <base/medium/large‑v2>` | 選擇 Whisper 模型大小 | `--model large‑v2` |
| `--device <auto/cpu/cuda>` | 選擇運算裝置（auto 自動判斷） | `--device cuda` |
| `--language <Chinese/English>` | 設定語言 | `--language English` |
| `--no-prompt` | 跳過覆蓋詢問 · 無輸入時默認處理所有檔案 | `--no-prompt` |
| `-h`, `--help` | 查看完整參數說明 | `-h` |

## 注意事項
- 本工具僅為自動化批次包裝，不包含 whisper 本體
- 若需完整原始碼，請至 [OpenAI/whisper 官方 repo](https://github.com/openai/whisper)

## 授權
[![License](https://img.shields.io/badge/license-MIT-green)](#license)
[![Built with Python](https://img.shields.io/badge/python-3.9%2B-blue)](#installation)
