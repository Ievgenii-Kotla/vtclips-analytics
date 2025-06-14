REM @echo off
call ..\.venv\Scripts\activate
python ..\src\vtc\vtc_main.py playlist -r -1 -ot
cmd /k