@echo off
title Celestial Whisper - Spotify Floating Lyrics
cd /d "%~dp0"
py main.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo If you encountered an error, make sure dependencies are installed:
    echo py -m pip install -r requirements.txt
    pause
)
