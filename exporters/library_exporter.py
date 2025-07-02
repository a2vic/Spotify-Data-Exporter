"""
Exporter pour les éléments sauvegardés dans la bibliothèque de l'utilisateur Spotify.
"""

import os
from typing import Dict, List, Any
from pathlib import Path

from exporters.base_exporter import BaseExporter
from utils.api_utils import rate_limit_decorator


class LibraryExporter(BaseExporter):
    """
    Exporter pour récupérer et sauvegarder les éléments de la bibliothèque de l'utilisateur
    (pistes sauvegardées, albums sauvegardés).
    """

    def __init__(self, spotify_client, export_dir, export_format="json"):
        """
        Initialise l'exporter de bibliothèque.

        Args:
            spotify_client: Client Spotify authentifié
            export_dir: Répertoire d'export des données
            export_format: Format d'export (json ou csv)
        """
        super().__init__(spotify_client, export_dir, export_format)
        
        # Créer les sous-répertoires pour les différents types d'éléments
        self.tracks_dir = Path(self.export_dir) / "tracks"
        self.albums_dir = Path(self.export_dir) / "albums"
        
        os.makedirs(self.tracks_dir, exist_ok=True)
        os.makedirs(self.albums_dir, exist_ok=True)

    def get_saved_tracks(self) -> List[Dict[str, Any]]:
        """
        Récupère toutes les pistes sauvegardées de l'utilisateur avec pagination.

        Returns:
            Liste des pistes sauvegardées
        """
        return self.paginate("current_user_saved_tracks")

    def get_saved_albums(self) -> List[Dict[str, Any]]:
        """
        Récupère tous les albums sauvegardés de l'utilisateur avec pagination.

        Returns:
            Liste des albums sauvegardés
        """
        return self.paginate("current_user_saved_albums")

    def export_saved_tracks(self) -> Dict[str, Any]:
        """
        Exporte les pistes sauvegardées de l'utilisateur.

        Returns:
            Métadonnées de l'export
        """
        print("Exportation des pistes sauvegardées...")
        
        # Récupérer les pistes sauvegardées
        tracks = self.get_saved_tracks()
        
        # Sauvegarder les pistes
        filepath = self.save_data(tracks, str(self.tracks_dir / "saved_tracks"))
        
        print(f"{len(tracks)} pistes sauvegardées exportées avec succès: {filepath}")
        
        return {
            "type": "saved_tracks",
            "count": len(tracks),
            "filepath": filepath
        }

    def export_saved_albums(self) -> Dict[str, Any]:
        """
        Exporte les albums sauvegardés de l'utilisateur.

        Returns:
            Métadonnées de l'export
        """
        print("Exportation des albums sauvegardés...")
        
        # Récupérer les albums sauvegardés
        albums = self.get_saved_albums()
        
        # Sauvegarder les albums
        filepath = self.save_data(albums, str(self.albums_dir / "saved_albums"))
        
        print(f"{len(albums)} albums sauvegardés exportés avec succès: {filepath}")
        
        return {
            "type": "saved_albums",
            "count": len(albums),
            "filepath": filepath
        }

    def export(self) -> Dict[str, Any]:
        """
        Exporte tous les éléments de la bibliothèque de l'utilisateur.

        Returns:
            Métadonnées de l'export
        """
        # Exporter les pistes sauvegardées
        tracks_stats = self.export_saved_tracks()
        
        # Exporter les albums sauvegardés
        albums_stats = self.export_saved_albums()
        
        # Combiner les statistiques
        return {
            "type": "library",
            "saved_tracks": tracks_stats,
            "saved_albums": albums_stats,
            "total_items": tracks_stats["count"] + albums_stats["count"]
        }
