@echo off
REM ----
REM Windows �妸�Ұ��ɡG�Ұʵ������Ҩð���D�{��
REM ----

REM �����u�@�ؿ��� .bat �Ҧb��Ƨ�
cd /d "%~dp0"

REM �ҥε������ҡ]�令�A��ڪ����|�^
if exist "..\whisper-env\Scripts\activate.bat" (
    call "..\whisper-env\Scripts\activate.bat"
) else (
    echo ?? �䤣��������� activate�A�Х��إ� whisper-env
)

REM �ˬd�O���بϥμҦ�
if "%~1"=="" (
    echo �ϥΤ覡�Grun_whisper_auto.bat [��Ƨ��έ��T��]
    python run_whisper_auto_1.4.py
) else (
    python run_whisper_auto_1.4.py --input-folder "%~1"
)

echo.
pause
