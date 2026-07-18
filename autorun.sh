Bash

#!/bin/bash

echo $(dirname $0)

# Installation de la bibliothèque requise
python3 -m pip install requests

# Déplacement dans le dossier des scripts
cd $(dirname $0)/scripts/

# Génération du fichier directement dans le dossier .Stream
python3 youtube_m3ugrabber.py > ../.Stream/youtube.m3u

echo m3u grabbed et enregistré dans .Stream
