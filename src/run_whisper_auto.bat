@echo off
REM ----
REM Windows 批次啟動檔：啟動虛擬環境並執行主程式
REM ----

REM 切換工作目錄到 .bat 所在資料夾
cd /d "%~dp0"

REM 啟用虛擬環境（改成你實際的路徑）
if exist "..\whisper-env\Scripts\activate.bat" (
    call "..\whisper-env\Scripts\activate.bat"
) else (
    echo ?? 找不到虛擬環境 activate，請先建立 whisper-env
)

REM 檢查是哪種使用模式
if "%~1"=="" (
    echo 使用方式：run_whisper_auto.bat [資料夾或音訊檔]
    python run_whisper_auto_1.4.py
) else (
    python run_whisper_auto_1.4.py --input-folder "%~1"
)

echo.
pause
