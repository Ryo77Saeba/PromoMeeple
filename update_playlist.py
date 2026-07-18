import urllib.request
import re

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

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Définition du chemin cible : fichier Stream.m3u dans le dossier Stream
OUTPUT_DIR = "Stream"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "Stream.m3u")

def get_video_id(youtube_url):
    """Extrait l'identifiant vidéo unique de 11 caractères du live YouTube."""
    match = re.search(r'v=([a-zA-Z0-9_-]{11})', youtube_url)
    if match:
        return match.group(1)
        
    try:
        req = urllib.request.Request(
            youtube_url, 
            headers={'User-Agent': USER_AGENT}
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
    # S'assure que le dossier existant est bien accessible
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    content = "#EXTM3U\n"
    
    for name, url in CHANNELS:
        print(f"Traitement : {name}...")
        video_id = get_video_id(url)
        
        if video_id:
            print(f"--> ID extrait : {video_id}")
            
            stream_url = f"https://m3u.ch/live/{video_id}.m3u8"

            content += f'#EXTINF:-1 group-title="YouTube Live" http-user-agent="{USER_AGENT}",{name}\n'
            content += f'#EXTVLCOPT:http-user-agent={USER_AGENT}\n'
            content += f'#EXTVLCOPT:http-referrer=https://www.youtube.com/\n'
            content += f'{stream_url}\n'
        else:
            print(f"❌ Impossible de trouver l'ID pour {name}")

    # Écriture dans Stream/Stream.m3u
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"\nFichier généré avec succès dans : {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_m3u()
