REM @echo off
call ..\..\vtclips-analytics\venv\Scripts\activate
python vtc_main.py playlist -r -1
cmd /k