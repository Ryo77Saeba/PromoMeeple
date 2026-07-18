#!/bin/bash
# Installation de yt-dlp et de la bibliothèque requests
python3 -m pip install --upgrade pip
python3 -m pip install requests yt-dlp

# Exécution du script
python3 $(dirname $0)/scripts/youtube_m3ugrabber.py
echo "Processus terminé !"
