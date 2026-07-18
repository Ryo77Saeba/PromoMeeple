#! /usr/bin/python3
import os
import subprocess

# Emplacements des répertoires
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "Stream")
GLOBAL_M3U_PATH = os.path.join(BASE_DIR, "youtube.m3u")

os.makedirs(OUTPUT_DIR, exist_ok=True)
global_channels = []

def grab(url, channel_id, metadata_header):
    """Utilise yt-dlp pour extraire le véritable lien m3u8 direct de YouTube."""
    stream_link = None
    try:
        # On lance yt-dlp pour récupérer l'URL brute du flux HLS (m3u8)
        # -g permet d'afficher uniquement l'URL finale
        cmd = ["yt-dlp", "-g", "-f", "best", url]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30)
        
        if result.returncode == 0:
            stream_link = result.stdout.strip()
    except Exception as e:
        print(f"Erreur lors de l'extraction pour {channel_id}: {e}")

    # Si yt-dlp échoue, on met l'URL YouTube d'origine en secours
    if not stream_link:
        print(f"⚠️ Impossible d'extraire le flux pour {channel_id}. Utilisation du lien de secours.")
        stream_link = url

    # Génération du fichier m3u8 individuel requis
    individual_content = "#EXTM3U x-tvg-url=\"https://github.com/botallen/epg/releases/download/latest/epg.xml\"\n"
    individual_content += f"{metadata_header}\n{stream_link}\n"
    
    file_path = os.path.join(OUTPUT_DIR, f"{channel_id}.m3u8")
    with open(file_path, 'w', encoding='utf-8') as f_out:
        f_out.write(individual_content)
    
    # Stockage pour la playlist globale
    global_channels.append((metadata_header, stream_link))
    print(f"✅ Lien direct extrait avec succès pour [{channel_id}]")

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

# Écriture de la playlist globale youtube.m3u
with open(GLOBAL_M3U_PATH, 'w', encoding='utf-8') as f_global:
    f_global.write("#EXTM3U x-tvg-url=\"https://github.com/botallen/epg/releases/download/latest/epg.xml\"\n")
    for header, link in global_channels:
        f_global.write(f"{header}\n{link}\n")

print(f"\n🚀 Fichier global mis à jour à la racine : youtube.m3u")
