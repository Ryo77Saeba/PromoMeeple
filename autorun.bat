@echo off
:: Installation de la bibliothèque requise si elle n'est pas présente
pip install requests

:: Déplacement dans le dossier des scripts et exécution silencieuse
cd scripts
python youtube_m3ugrabber.py

echo.
echo Processus de recuperation termine avec succes !
pause
