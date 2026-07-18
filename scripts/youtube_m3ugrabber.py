def grab(url, channel_id, metadata_header):
    """Génère un lien permanent pointant vers le proxy PHP."""
    
    # URL de votre serveur ou de votre GitHub Pages où sera hébergé le script PHP
    # REMPLACEZ 'VotrePseudo' par votre identifiant GitHub réel
    PROXY_URL = f"https://ryo77saeba.github.io/PromoMeeple/Stream/index.php?id={channel_id}"
    
    # 1. Fichier m3u8 individuel stable
    individual_content = "#EXTM3U x-tvg-url=\"https://github.com/botallen/epg/releases/download/latest/epg.xml\"\n"
    individual_content += f"{metadata_header}\n{PROXY_URL}\n"
    
    file_path = os.path.join(OUTPUT_DIR, f"{channel_id}.m3u8")
    with open(file_path, 'w', encoding='utf-8') as f_out:
        f_out.write(individual_content)
    
    # 2. Ajout à la playlist globale
    global_channels.append((metadata_header, PROXY_URL))
    print(f"Lien permanent généré pour [{channel_id}] -> Redirection PHP configurée.")
