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

def get_streamlink_m3u8(youtube_url):
    """Utilise streamlink pour extraire le flux .m3u8 direct lisible sur IPTV."""
    try:
        # streamlink extrait le lien direct sans passer par les défis bot complexes de yt-dlp
        cmd = [
            "streamlink",
            "--stream-url",
            youtube_url,
            "best"  # Prend la meilleure qualité disponible
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        
        if result.returncode == 0 and result.stdout.strip():
            url = result.stdout.strip()
            print(f"--> Flux .m3u8 extrait avec succès !")
            return url
        else:
            print(f"Échec streamlink pour {youtube_url}.\nDétails: {result.stderr.strip()}")
            return None
    except Exception as e:
        print(f"Erreur inattendue : {e}")
        return None

def generate_m3u():
    content = "#EXTM3U\n"
    for name, url in CHANNELS:
        print(f"\nTraitement de : {name}...")
        stream_url = get_streamlink_m3u8(url)
        if stream_url:
            content += f'#EXTINF:-1 group-title="YouTube Live",{name}\n'
            content += f'{stream_url}\n'
        else:
            print(f"❌ Échec de la récupération pour {name}")

    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write(content)
    print("\nFichier playlist.m3u généré avec succès !")

if __name__ == "__main__":
    generate_m3u()
