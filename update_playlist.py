import urllib.request
import json
import re
import subprocess

# Astuce : On peut aussi utiliser l'URL /embed/ de la vidéo si l'URL /live est bloquée
CHANNELS = [
    ("Tokyo Shinjuku Kabukicho Live", "https://www.youtube.com/watch?v=DjdUEyjx8GM"),
    ("Tokyo Shinjuku Kabukicho Live II", "https://www.youtube.com/watch?v=gFRtAAmiFbE"),
    ("Shibuya Scramble Crossing Live", "https://www.youtube.com/watch?v=8H3nRCFVR6Y"),
    ("Shibuya Scramble Crossing Live II", "https://www.youtube.com/watch?v=dfVK7ld38Ys"),
    ("Mont Fuji Live", "https://www.youtube.com/watch?v=YQ4wbAl_7zo"),
    ("Fujikawaguchiko - Mont Fuji", "https://www.youtube.com/watch?v=eU8A7QQOcso"),
    ("Shinjuku Eki Live", "https://www.youtube.com/watch?v=Zhmmh7l6KEw"),
    ("Tokyo Asakusa Live", "https://www.youtube.com/watch?v=MwcMURMzJ7A")
]

def get_video_id(youtube_url):
    """Récupère l'ID fixe de la vidéo live (11 caractères)."""
    match = re.search(r'v=([a-zA-Z0-9_-]{11})', youtube_url)
    if match:
        return match.group(1)
        
    try:
        req = urllib.request.Request(
            youtube_url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8')
            matches = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', html)
            if matches:
                return matches[0]
            canonical = re.search(r'href="https://www.youtube.com/watch\?v=([a-zA-Z0-9_-]{11})"', html)
            if canonical:
                return canonical.group(1)
    except Exception as e:
        print(f"Erreur d'extraction d'ID pour {youtube_url}: {e}")
    return None

def generate_m3u():
    content = "#EXTM3U\n"
    
    for name, url in CHANNELS:
        print(f"Traitement : {name}...")
        video_id = get_video_id(url)
        
        if video_id:
            print(f"--> ID extrait : {video_id}")
            
            # 1. Relais principal m3u.ch (Très rapide, compatible HLS IPTV)
            link_m3uch = f"https://m3u.ch/live/{video_id}.m3u8"
            
            # 2. Relais de secours 1 (Raw YouTube Live Gateway)
            link_gateway = f"https://youtube-live-stream.vercel.app/api/live?id={video_id}"
            
            # 3. Relais de secours 2 (Piped API Stream)
            link_piped = f"https://pipedapi.kavin.rocks/streams/{video_id}"

            # Lien principal
            content += f'#EXTINF:-1 group-title="YouTube Live",{name}\n'
            content += f'{link_m3uch}\n'
            
            # Miroir de secours dans la liste IPTV
            content += f'#EXTINF:-1 group-title="YouTube Live (Miroir)",{name} (Secours)\n'
            content += f'{link_gateway}\n'
            
        else:
            print(f"❌ Impossible de trouver l'ID pour {name}")

    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write(content)
    print("\nFichier playlist.m3u généré avec succès !")

if __name__ == "__main__":
    generate_m3u()
