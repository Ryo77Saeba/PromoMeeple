#! /usr/bin/python3
import os

# Emplacements des répertoires
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "Stream")
GLOBAL_M3U_PATH = os.path.join(BASE_DIR, "youtube.m3u")

print(f"--- Démarrage du script ---")
print(f"Dossier de sortie : {OUTPUT_DIR}")

os.makedirs(OUTPUT_DIR, exist_ok=True)
global_channels = []

def grab(url, channel_id, metadata_header):
    """Traduit l'URL YouTube en un lien de flux direct via une API de relais IPTV."""
    if not metadata_header:
        print(f"⚠️ Ligne ignorée : Pas d'entête d'informations défini avant l'URL {url}")
        return

    video_id = ""
    url = url.strip()
    
    # Extraction propre de l'identifiant (ID)
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

    if not video_id or len(video_id) < 3:
        print(f"❌ Impossible d'extraire un ID valide pour l'URL : {url}")
        return

    # Génération du fichier m3u8 individuel
    individual_content = "#EXTM3U x-tvg-url=\"https://github.com/botallen/epg/releases/download/latest/epg.xml\"\n"
    individual_content += f"{metadata_header}\n{stream_link}\n"
    
    file_path = os.path.join(OUTPUT_DIR, f"{channel_id}.m3u8")
    with open(file_path, 'w', encoding='utf-8', newline='\n') as f_out:
        f_out.write(individual_content)
    
    # Stockage pour la playlist globale
    global_channels.append((metadata_header, stream_link))
    print(f"✅ Fichier créé avec succès : Stream/{channel_id}.m3u8")

# --- Lecture du fichier de configuration ---
config_path = os.path.join(BASE_DIR, "youtube_channel_info.txt")
print(f"Lecture du fichier de configuration : {config_path}")

if not os.path.exists(config_path):
    print(f"❌ ERREUR CRITIQUE : Le fichier {config_path} est introuvable !")
    exit(1)

current_tvg_id = "default_id"
current_header = ""
line_count = 0

with open(config_path, 'r', encoding='utf-8-sig') as f:  # utf-8-sig gère les caractères invisibles (BOM)
    for line in f:
        line_count += 1
        line = line.strip()
        
        # Ignorer les lignes vides et les commentaires
        if not line or line.startswith('~~') or line.startswith('#'):
            continue
            
        # Détection de la ligne d'information (contient le séparateur '|')
        if '|' in line:
            parts = line.split('|')
            if len(parts) >= 4:
                ch_name = parts[0].strip()
                grp_title = parts[1].strip().title()
                tvg_logo = parts[2].strip()
                tvg_id = parts[3].strip()
                
                current_tvg_id = tvg_id
                current_header = f'#EXTINF:-1 group-title="{grp_title}" tvg-logo="{tvg_logo}" tvg-id="{tvg_id}", {ch_name}'
            else:
                print(f"⚠️ Ligne {line_count} mal formatée (il manque des sections avec '|') : {line}")
                
        # Détection de l'URL YouTube
        elif line.startswith('http'):
            grab(line, current_tvg_id, current_header)
        else:
            print(f"❓ Ligne {line_count} non reconnue (ni une info |, ni une URL http) : {line}")

# Écriture de la playlist globale
if global_channels:
    with open(GLOBAL_M3U_PATH, 'w', encoding='utf-8', newline='\n') as f_global:
        f_global.write("#EXTM3U x-tvg-url=\"https://github.com/botallen/epg/releases/download/latest/epg.xml\"\n")
        for header, link in global_channels:
            f_global.write(f"{header}\n{link}\n")
    print(f"\n🚀 Félicitations ! Fichier global mis à jour : {GLOBAL_M3U_PATH} ({len(global_channels)} chaînes insérées)")
else:
    print("\n❌ ERREUR : Aucune chaîne n'a pu être générée. Vérifiez votre fichier youtube_channel_info.txt.")
