@echo off
python -m pip install --upgrade pip
python -m pip install requests yt-dlp

cd scripts
python youtube_m3ugrabber.py
pause
