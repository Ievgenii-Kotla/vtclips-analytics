REM @echo off
call ..\.venv\Scripts\activate
python ..\src\vtc\vtc_main.py playlist -r -1
cmd /k