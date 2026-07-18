#!/bin/bash

# Installation de la bibliothèque requise
python3 -m pip install requests

# Exécution du script Python
python3 $(dirname $0)/scripts/youtube_m3ugrabber.py

echo "Processus de récupération terminé !"
