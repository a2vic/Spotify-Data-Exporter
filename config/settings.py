"""
Fichier de configuration pour l'export des données Spotify.
"""

import os
from pathlib import Path

# Répertoire de base pour l'export des données
BASE_DIR = Path(__file__).resolve().parent.parent
EXPORT_DIR = BASE_DIR / "exports"

# Configuration de l'authentification Spotify
SPOTIFY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID", "")
SPOTIFY_CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET", "")
SPOTIFY_REDIRECT_URI = os.environ.get("SPOTIFY_REDIRECT_URI", "http://localhost:8888/callback")

# Fichier pour stocker le token de rafraîchissement
TOKEN_CACHE_PATH = BASE_DIR / ".spotify_token_cache"

# Scopes OAuth requis pour l'accès aux données
SPOTIFY_SCOPES = [
    "user-read-private",           # Informations de profil
    "user-read-email",             # Adresse e-mail
    "playlist-read-private",       # Playlists privées
    "playlist-read-collaborative", # Playlists collaboratives
    "user-library-read",           # Pistes et albums sauvegardés
    "user-follow-read",            # Artistes suivis
    "user-read-recently-played",   # Historique d'écoute récent
    "user-top-read",               # Top artistes et pistes
    "user-read-playback-position", # Positions de lecture
]

# Paramètres pour la gestion des limitations d'API
API_RETRY_ATTEMPTS = 3
API_RETRY_DELAY = 2  # secondes

# Formats d'export disponibles
EXPORT_FORMATS = ["json", "csv"]
DEFAULT_EXPORT_FORMAT = "json"

# Paramètres de pagination
DEFAULT_LIMIT = 50  # Nombre maximum d'éléments par requête

# Structure des répertoires d'export
EXPORT_STRUCTURE = {
    "profile": EXPORT_DIR / "profile",
    "playlists": EXPORT_DIR / "playlists",
    "library": {
        "tracks": EXPORT_DIR / "library" / "tracks",
        "albums": EXPORT_DIR / "library" / "albums",
    },
    "following": EXPORT_DIR / "following",
    "history": {
        "recently_played": EXPORT_DIR / "history" / "recently_played",
        "top_tracks": EXPORT_DIR / "history" / "top_tracks",
        "top_artists": EXPORT_DIR / "history" / "top_artists",
    }
}
