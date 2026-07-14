import urllib.request
import json
import re
import subprocess

# Astuce : On peut aussi utiliser l'URL /embed/ de la vidéo si l'URL /live est bloquée
CHANNELS = [
    ("Tokyo Shinjuku Kabukicho Live", "https://www.youtube.com/embed/DjdUEyjx8GM?si=_aUfUbed5WgY_Rug")

]

INVIDIOUS_INSTANCES = [
    "https://inv.riverside.rocks",
    "https://invidious.drgns.space",
    "https://vid.puffyan.us",
    "https://invidious.nerdvpn.de"
]

def get_channel_live_id(youtube_url):
    """Récupère l'ID de la vidéo en direct depuis la page YouTube."""
    try:
        req = urllib.request.Request(
            youtube_url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8')
            # Cherche l'ID de la vidéo live dans le code HTML
            match = re.search(r'href="/watch\?v=([a-zA-Z0-9_-]{11})"', html)
            if match:
                return match.group(1)
            match_canonical = re.search(r'link rel="canonical" href="https://www.youtube.com/watch\?v=([a-zA-Z0-9_-]{11})"', html)
            if match_canonical:
                return match_canonical.group(1)
    except Exception as e:
        print(f"Erreur lors de la récupération de l'ID vidéo pour {youtube_url}: {e}")
    return None

def get_hls_from_invidious(video_id):
    """Interroge les instances Invidious pour obtenir le lien .m3u8 direct."""
    for instance in INVIDIOUS_INSTANCES:
        try:
            api_url = f"{instance}/api/v1/videos/{video_id}"
            req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    hls_url = data.get("hlsUrl")
                    if hls_url:
                        print(f"--> Flux trouvé via l'instance : {instance}")
                        return hls_url
        except Exception:
            continue
    return None

def get_live_m3u8(youtube_url):
    """Essaie de récupérer le flux via Invidious puis fallback sur yt-dlp."""
    # 1. Trouver l'ID du Live
    video_id = get_channel_live_id(youtube_url)
    
    if video_id:
        print(f"ID du Live détecté : {video_id}")
        # 2. Obtenir le lien .m3u8 via Invidious
        hls_url = get_hls_from_invidious(video_id)
        if hls_url:
            return hls_url

    # 3. Secours : Tentative via yt-dlp local si la méthode Invidious échoue
    print("Tentative de secours via yt-dlp...")
    try:
        cmd = [
            "yt-dlp",
            "--no-warnings",
            "--extractor-args", "youtube:player_client=ios,android",
            "-g",
            youtube_url
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if res.returncode == 0 and res.stdout.strip():
            return res.stdout.strip().split('\n')[0]
    except Exception as e:
        print(f"Erreur yt-dlp : {e}")

    return None

def generate_m3u():
    content = "#EXTM3U\n"
    for name, url in CHANNELS:
        print(f"\nRécupération du flux pour : {name}...")
        stream_url = get_live_m3u8(url)
        if stream_url:
            content += f'#EXTINF:-1 group-title="YouTube Live",{name}\n'
            content += f'{stream_url}\n'
        else:
            print(f"⚠️ Échec / Pas de live actif pour {name}")

    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write(content)
    print("\nFichier playlist.m3u mis à jour avec succès !")

if __name__ == "__main__":
    generate_m3u()
