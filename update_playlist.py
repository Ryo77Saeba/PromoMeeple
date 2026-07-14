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

]

PIPED_INSTANCES = [
    "https://pipedapi.kavin.rocks",
    "https://api.piped.privacydev.net",
    "https://pipedapi.tokhmi.xyz",
    "https://pipedapi.mha.fi"
]

def get_channel_live_id(youtube_url):
    """Extrait l'ID de la vidéo (11 caractères) depuis l'URL du live."""
    match_v = re.search(r'v=([a-zA-Z0-9_-]{11})', youtube_url)
    if match_v:
        return match_v.group(1)
        
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
            match_canonical = re.search(r'href="https://www.youtube.com/watch\?v=([a-zA-Z0-9_-]{11})"', html)
            if match_canonical:
                return match_canonical.group(1)
    except Exception as e:
        print(f"Erreur lors de la lecture de la page {youtube_url}: {e}")
    return None

def get_hls_from_piped(video_id):
    """Interroge l'API Piped pour récupérer le lien .m3u8 du stream HLS."""
    for instance in PIPED_INSTANCES:
        try:
            api_url = f"{instance}/streams/{video_id}"
            req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=6) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    hls_url = data.get("hls")
                    if hls_url:
                        print(f"--> Flux HLS récupéré via Piped ({instance})")
                        return hls_url
        except Exception:
            continue
    return None

def get_direct_manifest_fallback(video_id):
    """Méthode de secours : construit le lien manifeste HLS standard de YouTube."""
    manifest_url = f"https://www.youtube.com/api/manifest/hls_variant/id/{video_id}/source/yt_live_broadcast/m3u8"
    print(f"--> Utilisation du lien manifeste direct YouTube")
    return manifest_url

def get_live_m3u8(youtube_url):
    print(f"Analyse : {youtube_url}")
    video_id = get_channel_live_id(youtube_url)
    
    if video_id:
        print(f"--> ID du Live extrait : {video_id}")
        
        # 1. Tentative via l'API Piped
        hls_url = get_hls_from_piped(video_id)
        if hls_url:
            return hls_url
            
        # 2. Secours direct via le manifeste YouTube
        return get_direct_manifest_fallback(video_id)
    else:
        print("⚠️ ID de la vidéo introuvable sur la page.")
        
    return None

def generate_m3u():
    content = "#EXTM3U\n"
    for name, url in CHANNELS:
        print(f"\nTraitement : {name}...")
        stream_url = get_live_m3u8(url)
        if stream_url:
            content += f'#EXTINF:-1 group-title="Live Cams in Japan" tvg-logo="https://cdn.jsdelivr.net/gh/SkylineWebcams/web@v2/skylinewebcams.svg",{name}\n'
            content += f'{stream_url}\n'
        else:
            print(f"❌ Échec / Pas de live actif pour {name}")

    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write(content)
    print("\nFichier playlist.m3u généré avec succès !")

if __name__ == "__main__":
    generate_m3u()
