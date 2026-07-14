import subprocess
import os  # <-- AJOUT ICI

# Liste de vos chaînes YouTube Live
# Format : ("Nom de la chaîne", "URL du live YouTube")
CHANNELS = [
    ("Tokyo Shinjuku Kabukicho Live", "https://www.youtube.com/@kabukicho-1/live"),
    ("Kabukicho Live Channel II", "https://www.youtube.com/@kabukicho-2/live"),
    ("Shibuya Scramble Crossing Live Camera", "https://www.youtube.com/@ANNnewsCH/live")
]

def get_live_m3u8(youtube_url):
    """Extrait l'URL .m3u8 en direct via yt-dlp."""
    try:
        cmd = ["yt-dlp"]
        
        # Vérification et injection des cookies
        if os.path.exists("cookies.txt") and os.path.getsize("cookies.txt") > 0:
            print("--> Utilisation du fichier cookies.txt")
            cmd.extend(["--cookies", "cookies.txt"])
        else:
            print("⚠️ Attention: Fichier cookies.txt introuvable ou vide !")

        # Utilisation des clients compatibles (tv, android_vr, web)
        cmd.extend([
            "--extractor-args", "youtube:player_client=tv,android_vr,web",
            "-g",
            youtube_url
        ])
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        
        if result.returncode == 0 and result.stdout.strip():
            urls = result.stdout.strip().split('\n')
            return urls[0]
        else:
            print(f"Échec pour {youtube_url}.\nDétails: {result.stderr.strip()}")
            return None
    except Exception as e:
        print(f"Erreur inattendue pour {youtube_url}: {e}")
        return None

def generate_m3u():
    content = "#EXTM3U\n"
    for name, url in CHANNELS:
        print(f"Récupération du flux pour : {name}...")
        stream_url = get_live_m3u8(url)
        if stream_url:
            content += f'#EXTINF:-1 group-title="YouTube Live",{name}\n'
            content += f'{stream_url}\n'
        else:
            print(f"⚠️ Échec / Pas de live actif pour {name}")

    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write(content)
    print("Fichier playlist.m3u mis à jour avec succès !")

if __name__ == "__main__":
    generate_m3u()
