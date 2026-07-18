#! /usr/bin/python3
import requests
import os
import re

# On force l'emplacement à la racine du projet (un dossier parent au-dessus de 'scripts')
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "Stream")
GLOBAL_M3U_PATH = os.path.join(BASE_DIR, "youtube.m3u")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Listes pour stocker les infos et générer le fichier global à la fin
global_channels = []

def grab(url, channel_id, metadata_header):
    """Va chercher le flux en direct et l'écrit dans le fichier de la chaîne."""
    stream_link = None
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=15).text
        
        match = re.search(r'(https://[^\s"\']+\.m3u8)', response)
        if match:
            stream_link = match.group(1)
    except Exception:
        pass

    # Lien de secours si le live n'est pas trouvé
    if not stream_link:
        stream_link = f'https://raw.githubusercontent.com/Ryo77Saeba/PromoMeeple/refs/heads/main/Stream/{channel_id}.m3u8'

    # 1. Sauvegarde pour le fichier individuel
    individual_content = "#EXTM3U x-tvg-url=\"https://github.com/botallen/epg/releases/download/latest/epg.xml\"\n"
    individual_content += metadata_header + "\n" + stream_link + "\n"
    
    file_path = os.path.join(OUTPUT_DIR, f"{channel_id}.m3u8")
    with open(file_path, 'w', encoding='utf-8') as f_out:
        f_out.write(individual_content)
    
    # 2. On garde en mémoire pour le fichier global
    global_channels.append((metadata_header, stream_link))
    print(f"Fichier individuel créé : Stream/{channel_id}.m3u8")


# --- Début de la lecture de votre configuration ---
current_tvg_id = "default_id"
current_header = ""

# Recherche du fichier de config à son emplacement correct
config_path = os.path.join(BASE_DIR, "youtube_channel_info.txt")

with open(config_path, 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('~~'):
            continue
            
        if not line.startswith('https:'):
            parts = line.split('|')
            if len(parts) >= 4:
                ch_name = parts[0].strip()
                grp_title = parts[1].strip().title()
                tvg_logo = parts[2].strip()
                tvg_id = parts[3].strip()
                
                current_tvg_id = tvg_id
                current_header = f'#EXTINF:-1 group-title="{grp_title}" tvg-logo="{tvg_logo}" tvg-id="{tvg_id}", {ch_name}'
        else:
            grab(line, current_tvg_id, current_header)

# 3. ÉCRITURE DU FICHIER GLOBAL (youtube.m3u)
with open(GLOBAL_M3U_PATH, 'w', encoding='utf-8') as f_global:
    f_global.write("#EXTM3U x-tvg-url=\"https://github.com/botallen/epg/releases/download/latest/epg.xml\"\n")
    for header, link in global_channels:
        f_global.write(f"{header}\n{link}\n")

print(f"Fichier global créé avec succès à la racine : youtube.m3u")
