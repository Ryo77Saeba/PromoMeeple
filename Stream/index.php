<?php
// Stream/index.php

if (!isset($_GET['id'])) {
    die("ID de chaine manquant.");
}

$channel_id = preg_replace('/[^a-zA-Z0-9_\-]/', '', $_GET['id']);

// 1. URL officielle du live YouTube
$youtube_url = "https://www.youtube.com/channel/" . $channel_id . "/live";
if (strpos($channel_id, '@') === 0) {
    $youtube_url = "https://www.youtube.com/" . $channel_id . "/live";
}

// 2. Commande pour extraire le m3u8 à la volée
// Assurez-vous que yt-dlp est disponible sur votre hébergement web
$cmd = "yt-dlp -g -f best " . escapeshellarg($youtube_url);
$stream_url = shell_exec($cmd);

$stream_url = trim($stream_url);

if (empty($stream_url) || strpos($stream_url, 'http') !== 0) {
    // Si yt-dlp échoue, redirection vers un message d'erreur ou flux de secours
    header("HTTP/1.1 500 Internal Server Error");
    die("Impossible de recuperer le flux.");
}

// 3. Redirection 302 vers le vrai flux YouTube (généré avec VOTRE adresse IP)
header("Location: " . $stream_url, true, 302);
exit;
?>
