# Whisper Batch Transcriber

[![License](https://img.shields.io/badge/license-MIT-green)](#license)
[![Built with Python](https://img.shields.io/badge/python-3.9%2B-blue)](#installation)

## 目錄
- [簡介](#簡介)
- [改版歷程](#改版歷程)
- [安裝](#安裝)
- [使用範例](#使用範例)
- [參數說明](#參數說明)
- [注意事項](#注意事項)
- [授權](#授權)
- [貢獻](#貢獻)

## 簡介
本工具為 Whisper 批次語音轉錄腳本，支援資料夾一次轉檔、模型選擇、裝置選擇與繁體轉換。
需先安裝 [OpenAI Whisper](https://github.com/openai/whisper) 與相關依賴。

## 改版歷程

### v1.0.0 — 初始版本
- 支援單檔音訊/影片轉錄。
- 輸出 `.srt`, `.txt`, `.md`, `.json`, `segments_only.json`, `.vtt` 六種格式。
- 自動打包成 `.zip`。

### v1.1.0 — 批次處理與進階選項
- 增加可用 `--input-folder` 處理整個資料夾。
- 顯示 `tqdm` 批次進度條。
- 支援 `--model`, `--device`, `--language` 參數。
- 超過 60 分鐘音訊自動提示建議使用 `large-v2` 模型。

### v1.2.0 — 自動繁體轉換
- 整合 `opencc-python-reimplemented`，輸出自動轉為繁體中文。
- 保持各格式內容段落與斷句結構一致。

### v1.3.0 — ZIP 自動命名與覆蓋提醒
- ZIP 檔案重覆自動加上 `(2)`, `(3)` 等後綴命名。
- 批次處理時若有既有 ZIP，會先列出並詢問是否繼續。

### v1.4.0 — 路徑檢查與錯誤處理強化
- 增強對不存在檔案／資料夾的提示。
- 改進路徑格式錯誤提示，如不支援的路徑型式。
- 完善整體異常情況錯誤訊息。

## 安裝
```bash
python -m venv whisper-env
source whisper-env/bin/activate  # 或 Windows: whisper-env\Scripts\activate
pip install -r requirements.txt
```

## 使用範例

1. 建立虛擬環境並安裝依賴（如上）。
2. 執行方式：
- **拖曳**資料夾/檔案到 `run_whisper_auto.bat` 上
- 或於命令行執行：
```bat
cd src
run_whisper_auto.bat C:\path\to\media
```
3. 功能說明：
- 自動啟動 virtualenv
- 自動識別參數型態（資料夾 vs 無參數）
- 執行完保留 console 視窗，便於查看日誌

## 參數說明
| 參數 | 說明 | 範例 |
|------|------|------|
| `--input-folder <path>` | 指定資料夾進行批次處理 | `--input-folder ./media` |
| `--input-file <path>` | 處理單一音訊或影片檔案 | `--input-file ./video.mp4` |
| `--model <base/medium/large‑v2>` | 選擇 Whisper 模型大小 | `--model large‑v2` |
| `--device <auto/cpu/cuda>` | 選擇運算裝置（auto 自動判斷） | `--device cuda` |
| `--language <Chinese/English>` | 設定語言 | `--language English` |
| `--no-prompt` | 跳過覆蓋詢問，適合自動化/定時任務 | `--no-prompt` |
| `-h`, `--help` | 查看完整參數說明 | `-h` |

## 注意事項
- 本工具僅為自動化批次包裝，不包含 whisper 本體
- 若需完整原始碼，請至 [OpenAI/whisper 官方 repo](https://github.com/openai/whisper)

## 授權
本專案採用 [MIT License](LICENSE) 開源授權。

## 貢獻
歡迎 Issue/PR！請參閱 [CONTRIBUTING.md](CONTRIBUTING.md) 了解開發規範與流程。

