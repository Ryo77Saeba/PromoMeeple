#! /usr/bin/python3

banner = r'''
'''

import requests
import os
import sys

windows = False
if 'win' in sys.platform:
    windows = True

# La fonction accepte maintenant le "channel_id" en paramètre
def grab(url, channel_id):
    response = requests.get(url, timeout=15).text
    if '.m3u8' not in response:
        if '.m3u8' not in response:
            if windows:
                # Utilisation de l'ID de la chaîne ici
                print(f'https://raw.githubusercontent.com/Ryo77Saeba/PromoMeeple/refs/heads/main/Stream/{channel_id}.m3u')
                return
            os.system(f'curl "{url}" > temp.txt')
            response = ''.join(open('temp.txt').readlines())
            if '.m3u8' not in response:
                # Utilisation de l'ID de la chaîne ici aussi
                print(f'https://raw.githubusercontent.com/Ryo77Saeba/PromoMeeple/refs/heads/main/Stream/{channel_id}.m3u')
                return
    end = response.find('.m3u8') + 5
    tuner = 100
    while True:
        if 'https://' in response[end-tuner : end]:
            link = response[end-tuner : end]
            start = link.find('https://')
            end = link.find('.m3u8') + 5
            break
        else:
            tuner += 5
    print(f"{link[start : end]}")

print('#EXTM3U x-tvg-url="https://github.com/botallen/epg/releases/download/latest/epg.xml"')
print(banner)

# Variable temporaire pour stocker l'ID extrait de la ligne précédente
current_tvg_id = "moose_na"

with open('../youtube_channel_info.txt') as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('~~'):
            continue
        if not line.startswith('https:'):
            line = line.split('|')
            ch_name = line[0].strip()
            grp_title = line[1].strip().title()
            tvg_logo = line[2].strip()
            tvg_id = line[3].strip()
            
            # On mémorise le tvg-id actuel pour la ligne d'URL qui va suivre
            current_tvg_id = tvg_id
            
            print(f'\n#EXTINF:-1 group-title="{grp_title}" tvg-logo="{tvg_logo}" tvg-id="{tvg_id}", {ch_name}')
        else:
            # On transmet l'ID mémorisé à la fonction grab
            grab(line, current_tvg_id)
            
if 'temp.txt' in os.listdir():
    os.system('rm temp.txt')
    os.system('rm watch*')
