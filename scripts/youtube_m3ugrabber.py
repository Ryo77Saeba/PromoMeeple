#! /usr/bin/python3
import requests
import os
import re

def grab(url, channel_id):
    try:
        # Version moderne sans curl/wget : requests suffit largement en Python
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=15).text
        
        # Extraction propre du lien m3u8 via une expression régulière
        match = re.search(r'(https://[^\s"\']+\.m3u8)', response)
        if match:
            print(match.group(1))
            return
    except Exception:
        pass

    # Lien de secours si le live n'est pas trouvé ou en cas d'erreur
    print(f'https://raw.githubusercontent.com/Ryo77Saeba/PromoMeeple/refs/heads/main/Stream/{channel_id}.m3u8')

# En-tête M3U obligatoire
print('#EXTM3U x-tvg-url="https://github.com/botallen/epg/releases/download/latest/epg.xml"')

current_tvg_id = "default_id"

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
                
                # Sauvegarde immédiate de l'ID nettoyé
                current_tvg_id = tvg_id
                
                print(f'\n#EXTINF:-1 group-title="{grp_title}" tvg-logo="{tvg_logo}" tvg-id="{tvg_id}", {ch_name}')
        else:
            # Envoi de l'URL et de l'ID associé
            grab(line, current_tvg_id)
