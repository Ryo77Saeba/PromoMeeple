import subprocess
import json
import os

# Astuce : On peut aussi utiliser l'URL /embed/ de la vidéo si l'URL /live est bloquée
CHANNELS = [
    ("Tokyo Shinjuku Kabukicho Live", "https://www.youtube.com/embed/DjdUEyjx8GM?si=_aUfUbed5WgY_Rug"),

]

def generate_po_token():
    """Génère un PO-Token temporaire avec le module Node.js."""
    try:
        # Exécute un script Node rapide pour récupérer un token
        node_cmd = ["npx", "youtube-po-token-generator"]
        res = subprocess.run(node_cmd, capture_output=True, text=True, check=False)
        if res.returncode == 0 and res.stdout.strip():
            data = json.loads(res.stdout)
            return data.get("poToken"), data.get("visitorData")
    except Exception as e:
        print(f"Impossible de générer le PO-Token: {e}")
    return None, None

def get_live_m3u8(youtube_url, po_token=None, visitor_data=None):
    """Extrait l'URL .m3u8 via yt-dlp."""
    try:
        cmd = ["yt-dlp", "--no-warnings"]
        
        # Injection du PO-Token si généré
        if po_token and visitor_data:
            extractor_arg = f"youtube:po_token=web+{po_token};visitor_data={visitor_data}"
            cmd.extend(["--extractor-args", extractor_arg])
        else:
            # Fallback sur les clients TV/Embed
            cmd.extend(["--extractor-args", "youtube:player_client=tv,android_embed,web"])

        cmd.extend(["-g", youtube_url])
        
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
    print("Génération du PO-Token YouTube...")
    po_token, visitor_data = generate_po_token()
    if po_token:
        print("--> PO-Token généré avec succès !")
    else:
        print("--> Génération du PO-Token ignorée / échec, passage en mode direct.")

    content = "#EXTM3U\n"
    for name, url in CHANNELS:
        print(f"Récupération du flux pour : {name}...")
        stream_url = get_live_m3u8(url, po_token, visitor_data)
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
