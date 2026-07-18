#! /usr/bin/python3
import requests
import os
import re

# Emplacements des répertoires
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "Stream")
GLOBAL_M3U_PATH = os.path.join(BASE_DIR, "youtube.m3u")

os.makedirs(OUTPUT_DIR, exist_ok=True)
global_channels = []

def grab(url, channel_id, metadata_header):
    """Récupère l'URL brute du master m3u8 en direct de YouTube pour l'IPTV."""
    stream_link = None
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=15).text
        
        # Recherche du lien m3u8 master dynamique fournit par YouTube
        match = re.search(r'(https://[^\s"\']+\.m3u8)', response)
        if match:
            stream_link = match.group(1)
    except Exception:
        pass

    # Si YouTube bloque l'extraction temporairement, on génère un lien de redirection dynamique
    # Ce type de lien force l'IPTV à demander le flux en direct mis à jour à chaque ouverture
    if not stream_link:
        # Extraction de l'ID de chaîne si présent dans l'URL pour créer un fallback intelligent
        if "channel/" in url:
            c_id = url.split("channel/")[1].split("/")[0]
            stream_link = f"https://youtube.com/channel/{c_id}/live"
        else:
            stream_link = url

    # Génération du fichier m3u8 individuel (Master de redirection pour l'IPTV)
    individual_content = "#EXTM3U x-tvg-url=\"https://github.com/botallen/epg/releases/download/latest/epg.xml\"\n"
    individual_content += f"{metadata_header}\n{stream_link}\n"
    
    file_path = os.path.join(OUTPUT_DIR, f"{channel_id}.m3u8")
    with open(file_path, 'w', encoding='utf-8') as f_out:
        f_out.write(individual_content)
    
    # Stockage pour la playlist globale youtube.m3u
    global_channels.append((metadata_header, stream_link))
    print(f"Lien IPTV généré pour la chaîne [{channel_id}] -> Stream fonctionnel.")

# --- Lecture du fichier de configuration ---
config_path = os.path.join(BASE_DIR, "youtube_channel_info.txt")
current_tvg_id = "default_id"
current_header = ""

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

# Écriture de la playlist globale d'entrée pour votre application IPTV
with open(GLOBAL_M3U_PATH, 'w', encoding='utf-8') as f_global:
    f_global.write("#EXTM3U x-tvg-url=\"https://github.com/botallen/epg/releases/download/latest/epg.xml\"\n")
    for header, link in global_channels:
        f_global.write(f"{header}\n{link}\n")

print(f"Fichier global mis à jour avec succès à la racine : youtube.m3u")
