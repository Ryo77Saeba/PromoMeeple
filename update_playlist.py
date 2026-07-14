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
    """Récupère l'ID fixe de la vidéo live sans bloquer."""
    # S'il y a déjà un v=...
    match = re.search(r'v=([a-zA-Z0-9_-]{11})', youtube_url)
    if match:
        return match.group(1)
        
    try:
        req = urllib.request.Request(
            youtube_url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8')
            matches = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', html)
            if matches:
                return matches[0]
    except Exception as e:
        print(f"Erreur d'extraction d'ID : {e}")
    return None

def generate_m3u():
    content = "#EXTM3U\n"
    
    for name, url in CHANNELS:
        print(f"Traitement de : {name}...")
        video_id = get_video_id(url)
        
        if video_id:
            print(f"--> ID trouvé : {video_id}")
            # Redirection HLS optimisée pour IPTV via le proxy ouvert de la communauté IPTV
            hls_redirect_url = f"https://yturl.ing/hls/{video_id}.m3u8"
            
            content += f'#EXTINF:-1 group-title="YouTube Live",{name}\n'
            content += f'{hls_redirect_url}\n'
        else:
            print(f"❌ Impossible d'extraire l'ID pour {name}")

    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write(content)
    print("\nFichier playlist.m3u généré avec succès !")

if __name__ == "__main__":
    generate_m3u()
