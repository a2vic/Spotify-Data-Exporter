"""
Script principal pour l'export des données Spotify.
Orchestre l'ensemble du processus d'export.
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

from auth.spotify_auth import SpotifyAuthManager
from exporters.profile_exporter import ProfileExporter
from exporters.playlist_exporter import PlaylistExporter
from exporters.library_exporter import LibraryExporter
from exporters.following_exporter import FollowingExporter
from exporters.history_exporter import HistoryExporter
from config.settings import EXPORT_DIR, EXPORT_STRUCTURE, DEFAULT_EXPORT_FORMAT
from utils.file_utils import create_export_structure


def setup_export_directories() -> None:
    """
    Prépare les répertoires d'export.
    """
    print("Préparation des répertoires d'export...")
    create_export_structure(EXPORT_STRUCTURE)
    print(f"Répertoires d'export créés dans: {EXPORT_DIR}")


def export_all_data(spotify_client, export_format: str = DEFAULT_EXPORT_FORMAT) -> Dict[str, Any]:
    """
    Exporte toutes les données Spotify de l'utilisateur.
    
    Args:
        spotify_client: Client Spotify authentifié
        export_format: Format d'export (json ou csv)
        
    Returns:
        Rapport d'export avec les statistiques
    """
    start_time = time.time()
    export_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print(f"\n=== Début de l'export des données Spotify ({export_date}) ===\n")
    
    # Préparer les répertoires d'export
    setup_export_directories()
    
    # Exporter le profil utilisateur
    print("\n--- Exportation du profil utilisateur ---")
    profile_exporter = ProfileExporter(
        spotify_client, 
        EXPORT_STRUCTURE["profile"], 
        export_format
    )
    profile_stats = profile_exporter.export()
    
    # Exporter les playlists
    print("\n--- Exportation des playlists ---")
    playlist_exporter = PlaylistExporter(
        spotify_client, 
        EXPORT_STRUCTURE["playlists"], 
        export_format,
        export_tracks=True
    )
    playlists_stats = playlist_exporter.export()
    
    # Exporter la bibliothèque (pistes et albums sauvegardés)
    print("\n--- Exportation de la bibliothèque ---")
    library_exporter = LibraryExporter(
        spotify_client, 
        EXPORT_DIR / "library",  
        export_format
    )
    library_stats = library_exporter.export()
    
    # Exporter les artistes suivis
    print("\n--- Exportation des artistes suivis ---")
    following_exporter = FollowingExporter(
        spotify_client, 
        EXPORT_STRUCTURE["following"], 
        export_format
    )
    following_stats = following_exporter.export()
    
    # Exporter l'historique d'écoute et les tops
    print("\n--- Exportation de l'historique d'écoute et des tops ---")
    history_exporter = HistoryExporter(
        spotify_client, 
        EXPORT_DIR / "history",  
        export_format
    )
    history_stats = history_exporter.export()
    
    # Calculer le temps d'exécution
    execution_time = time.time() - start_time
    
    # Préparer le rapport d'export
    export_report = {
        "export_date": export_date,
        "execution_time_seconds": round(execution_time, 2),
        "export_format": export_format,
        "stats": {
            "profile": profile_stats,
            "playlists": playlists_stats,
            "library": library_stats,
            "following": following_stats,
            "history": history_stats
        }
    }
    
    # Sauvegarder le rapport d'export
    report_path = EXPORT_DIR / f"export_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(export_report, f, ensure_ascii=False, indent=2)
    
    print(f"\n=== Export terminé en {round(execution_time, 2)} secondes ===")
    print(f"Rapport d'export sauvegardé: {report_path}")
    
    return export_report


def main():
    """
    Fonction principale.
    """
    try:
        # Initialiser l'authentification
        print("Initialisation de l'authentification Spotify...")
        auth_manager = SpotifyAuthManager()
        
        # Authentifier l'utilisateur
        spotify_client = auth_manager.authenticate()
        
        # Exporter toutes les données
        export_all_data(spotify_client)
        
    except Exception as e:
        print(f"Erreur lors de l'export des données: {e}")
        raise


if __name__ == "__main__":
    main()
