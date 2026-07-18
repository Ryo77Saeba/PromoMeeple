#! /usr/bin/python3
import requests
import os
import re

# =====================================================================
# 1. EMPLACEMENT DE VOTRE CIBLE : Le dossier "Stream" à la racine
# =====================================================================
OUTPUT_DIR = "Stream"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def grab(url, channel_id, metadata_header):
    """Va chercher le flux en direct et l'écrit dans le fichier de la chaîne."""
    content = "#EXTM3U x-tvg-url=\"https://github.com/botallen/epg/releases/download/latest/epg.xml\"\n"
    content += metadata_header + "\n"
    
    stream_link = None
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=15).text
        
        match = re.search(r'(https://[^\s"\']+\.m3u8)', response)
        if match:
            stream_link = match.group(1)
    except Exception:
        pass

    # Si le live n'est pas trouvé, on applique votre lien de secours
    if not stream_link:
        stream_link = f'https://raw.githubusercontent.com/Ryo77Saeba/PromoMeeple/refs/heads/main/Stream/{channel_id}.m3u8'

    content += stream_link + "\n"

    # =====================================================================
    # 2. ÉCRITURE DANS LE FICHIER CIBLE : Stream/{channel_id}.m3u8
    # =====================================================================
    file_path = os.path.join(OUTPUT_DIR, f"{channel_id}.m3u8")
    with open(file_path, 'w', encoding='utf-8') as f_out:
        f_out.write(content)
    print(f"Fichier créé avec succès : {file_path}")


# --- Début de la lecture de votre configuration ---
current_tvg_id = "default_id"
current_header = ""

with open('../youtube_channel_info.txt', 'r', encoding='utf-8') as f:
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
                # On prépare la ligne d'en-tête de la chaîne
                current_header = f'#EXTINF:-1 group-title="{grp_title}" tvg-logo="{tvg_logo}" tvg-id="{tvg_id}", {ch_name}'
        else:
            # Dès qu'on croise l'URL, on génère le fichier m3u8 dédié à cette chaîne
            grab(line, current_tvg_id, current_header)
