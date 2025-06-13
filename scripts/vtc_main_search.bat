REM @echo off
call :\PythonProjects\vtclips-analytics\venv\Scripts\activate
python vtc_main.py keyword -r -1 -pr 0 1 100 -esd "2025-05-26 00:00:00+00:00"
cmd /k