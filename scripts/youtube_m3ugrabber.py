#! /usr/bin/python3
import os

# Emplacements des répertoires
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "Stream")
GLOBAL_M3U_PATH = os.path.join(BASE_DIR, "youtube.m3u")

os.makedirs(OUTPUT_DIR, exist_ok=True)
global_channels = []

def grab(url, channel_id, metadata_header):
    """Traduit l'URL YouTube en un lien de flux direct via une API de relais IPTV."""
    video_id = ""
    url = url.strip()
    
    # Extraction propre et robuste de l'identifiant (ID)
    if "channel/" in url:
        video_id = url.split("channel/")[1].split("/")[0].split("?")[0]
        stream_link = f"https://youtube-to-m3u.online/api/live/{video_id}.m3u8"
    elif "@" in url:
        video_id = url.split("youtube.com/")[1].split("/")[0].split("?")[0]
        stream_link = f"https://youtube-to-m3u.online/api/live/{video_id}.m3u8"
    else:
        if "v=" in url:
            video_id = url.split("v=")[1].split("&")[0].split("?")[0]
        elif "live/" in url:
            video_id = url.split("live/")[1].split("?")[0].split("&")[0]
        else:
            video_id = url.split("/")[-1].split("?")[0].split("&")[0]
        stream_link = f"https://youtube-to-m3u.online/api/video/{video_id}.m3u8"

    if not video_id:
        print(f"⚠️ Impossible d'extraire l'ID pour l'URL : {url}")
        return

    # Génération du fichier m3u8 individuel pour GitHub Pages
    individual_content = "#EXTM3U x-tvg-url=\"https://github.com/botallen/epg/releases/download/latest/epg.xml\"\n"
    individual_content += f"{metadata_header}\n{stream_link}\n"
    
    file_path = os.path.join(OUTPUT_DIR, f"{channel_id}.m3u8")
    with open(file_path, 'w', encoding='utf-8', newline='\n') as f_out:
        f_out.write(individual_content)
    
    # Stockage pour la playlist globale youtube.m3u
    global_channels.append((metadata_header, stream_link))
    print(f"✅ Fichier créé : Stream/{channel_id}.m3u8 (ID: {video_id})")

# --- Lecture du fichier de configuration ---
config_path = os.path.join(BASE_DIR, "youtube_channel_info.txt")
current_tvg_id = "default_id"
current_header = ""

with open(config_path, 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('~~'):
            continue
            
        # Fiabilisation : Si la ligne contient '|', c'est forcément une ligne de description
        if '|' in line:
            parts = line.split('|')
            if len(parts) >= 4:
                ch_name = parts[0].strip()
                grp_title = parts[1].strip().title()
                tvg_logo = parts[2].strip()
                tvg_id = parts[3].strip()
                
                current_tvg_id = tvg_id
                current_header = f'#EXTINF:-1 group-title="{grp_title}" tvg-logo="{tvg_logo}" tvg-id="{tvg_id}", {ch_name}'
        # Sinon, si elle commence par http, c'est l'URL YouTube associée
        elif line.startswith('http'):
            grab(line, current_tvg_id, current_header)

# Écriture de la playlist globale
with open(GLOBAL_M3U_PATH, 'w', encoding='utf-8', newline='\n') as f_global:
    f_global.write("#EXTM3U x-tvg-url=\"https://github.com/botallen/epg/releases/download/latest/epg.xml\"\n")
    for header, link in global_channels:
        f_global.write(f"{header}\n{link}\n")

print(f"\n🚀 Playlist générée avec des liens de flux directs et purs (.m3u8) !")
