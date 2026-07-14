import urllib.request
import json
import re
import subprocess

# Astuce : On peut aussi utiliser l'URL /embed/ de la vidéo si l'URL /live est bloquée
CHANNELS = [
    ("Tokyo Shinjuku Kabukicho Live", "https://www.youtube.com/watch?v=DjdUEyjx8GM")

]

# Liste d'instances Invidious / Piped révisées
INVIDIOUS_INSTANCES = [
    "https://invidious.privacydev.net",
    "https://inv.riverside.rocks",
    "https://invidious.nerdvpn.de",
    "https://invidious.drgns.space",
    "https://vid.puffyan.us"
]

def get_channel_live_id(youtube_url):
    """Récupère l'ID vidéo à 11 caractères."""
    # Si l'URL contient déjà un ID de vidéo
    match_v = re.search(r'v=([a-zA-Z0-9_-]{11})', youtube_url)
    if match_v:
        return match_v.group(1)
        
    try:
        # On utilise une requête avec User-Agent mobile pour éviter le blocage HTML
        req = urllib.request.Request(
            youtube_url, 
            headers={'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8')
            
            # Recherche des motifs d'ID vidéo dans la page YouTube
            matches = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', html)
            if matches:
                return matches[0]
                
            match_canonical = re.search(r'href="https://www.youtube.com/watch\?v=([a-zA-Z0-9_-]{11})"', html)
            if match_canonical:
                return match_canonical.group(1)
    except Exception as e:
        print(f"Erreur lors de la récupération de la page {youtube_url}: {e}")
    return None

def get_hls_from_invidious(video_id):
    """Interroge les relais Invidious pour récupérer l'URL .m3u8."""
    for instance in INVIDIOUS_INSTANCES:
        try:
            api_url = f"{instance}/api/v1/videos/{video_id}"
            req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    
                    # 1. Tente de récupérer hlsUrl direct
                    hls_url = data.get("hlsUrl")
                    if hls_url:
                        print(f"--> Flux HLS trouvé sur : {instance}")
                        return hls_url
                        
                    # 2. Alternative : cherche dans adaptiveFormats
                    for fmt in data.get("adaptiveFormats", []):
                        if fmt.get("type", "").startswith("application/x-mpegURL") or "m3u8" in fmt.get("url", ""):
                            print(f"--> Format adaptive trouvé sur : {instance}")
                            return fmt.get("url")
        except Exception:
            continue
    return None

def get_live_m3u8(youtube_url):
    print(f"Analyse de l'URL : {youtube_url}")
    video_id = get_channel_live_id(youtube_url)
    
    if video_id:
        print(f"--> ID du Live extrait : {video_id}")
        hls_url = get_hls_from_invidious(video_id)
        if hls_url:
            return hls_url
        else:
            print("⚠️ Impossible d'extraire le flux .m3u8 via les instances Invidious.")
    else:
        print("⚠️ ID de la vidéo introuvable (vérifiez si la chaîne est bien en direct).")
        
    return None

def generate_m3u():
    content = "#EXTM3U\n"
    for name, url in CHANNELS:
        print(f"\nTraitement : {name}...")
        stream_url = get_live_m3u8(url)
        if stream_url:
            content += f'#EXTINF:-1 group-title="YouTube Live",{name}\n'
            content += f'{stream_url}\n'
        else:
            print(f"❌ Échec / Pas de live actif pour {name}")

    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write(content)
    print("\nFichier playlist.m3u mis à jour avec succès !")

if __name__ == "__main__":
    generate_m3u()
