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
OUTPUT_DIR = "Stream"

def slugify(text):
    """Convertit le nom de la chaîne en nom de fichier propre (ex: "France 24" -> "france_24")."""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s_-]', '', text)
    return re.sub(r'[\s-]+', '_', text).strip('_')

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

def generate_individual_links():
    # S'assure que le dossier existant "Stream" est bien accessible
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    for name, url in CHANNELS:
        print(f"Traitement : {name}...")
        video_id = get_video_id(url)
        
        if video_id:
            print(f"--> ID extrait : {video_id}")
            
            # Construction du contenu du fichier M3U8 individuel
            stream_url = f"https://m3u.ch/live/{video_id}.m3u8"
            
            content = "#EXTM3U\n"
            content += f'#EXTINF:-1 group-title="YouTube Live" http-user-agent="{USER_AGENT}",{name}\n'
            content += f'#EXTVLCOPT:http-user-agent={USER_AGENT}\n'
            content += f'#EXTVLCOPT:http-referrer=https://www.youtube.com/\n'
            content += f'{stream_url}\n'
            
            # Génération du nom de fichier unique
            file_name = f"{slugify(name)}.m3u8"
            output_file = os.path.join(OUTPUT_DIR, file_name)
            
            # Écriture du fichier individuel
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"--> Fichier généré : {output_file}")
        else:
            print(f"❌ Impossible de trouver l'ID pour {name}")

if __name__ == "__main__":
    generate_individual_links()
