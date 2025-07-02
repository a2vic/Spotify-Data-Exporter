"""
Exporter pour les playlists Spotify de l'utilisateur.
"""

import os
from typing import Dict, List, Any
from pathlib import Path

from exporters.base_exporter import BaseExporter
from utils.api_utils import rate_limit_decorator


class PlaylistExporter(BaseExporter):
    """
    Exporter pour récupérer et sauvegarder les playlists de l'utilisateur.
    """

    def __init__(self, spotify_client, export_dir, export_format="json", export_tracks=True):
        """
        Initialise l'exporter de playlists.

        Args:
            spotify_client: Client Spotify authentifié
            export_dir: Répertoire d'export des données
            export_format: Format d'export (json ou csv)
            export_tracks: Si True, exporte également les pistes de chaque playlist
        """
        super().__init__(spotify_client, export_dir, export_format)
        self.export_tracks = export_tracks
        
        # Créer un sous-répertoire pour les pistes des playlists si nécessaire
        if self.export_tracks:
            self.tracks_dir = Path(self.export_dir) / "tracks"
            os.makedirs(self.tracks_dir, exist_ok=True)

    def get_user_playlists(self) -> List[Dict[str, Any]]:
        """
        Récupère toutes les playlists de l'utilisateur avec pagination.

        Returns:
            Liste des playlists de l'utilisateur
        """
        return self.paginate("current_user_playlists")

    @rate_limit_decorator()
    def get_playlist_tracks(self, playlist_id: str) -> List[Dict[str, Any]]:
        """
        Récupère toutes les pistes d'une playlist avec pagination.

        Args:
            playlist_id: ID de la playlist

        Returns:
            Liste des pistes de la playlist
        """
        return self.paginate("playlist_items", playlist_id=playlist_id)

    def export(self) -> Dict[str, Any]:
        """
        Exporte les playlists de l'utilisateur et optionnellement leurs pistes.

        Returns:
            Métadonnées de l'export
        """
        print("Exportation des playlists utilisateur...")
        
        # Récupérer les playlists
        playlists = self.get_user_playlists()
        
        # Sauvegarder les playlists
        playlists_filepath = self.save_data(playlists, "playlists")
        
        print(f"Playlists exportées avec succès: {playlists_filepath}")
        
        # Statistiques pour le rapport
        export_stats = {
            "type": "playlists",
            "count": len(playlists),
            "filepath": playlists_filepath,
            "tracks_exported": False,
            "tracks_count": 0
        }
        
        # Exporter les pistes de chaque playlist si demandé
        if self.export_tracks and playlists:
            print(f"Exportation des pistes pour {len(playlists)} playlists...")
            
            total_tracks = 0
            tracks_filepaths = []
            
            for playlist in playlists:
                playlist_id = playlist["id"]
                playlist_name = playlist["name"]
                
                print(f"  Exportation des pistes pour la playlist '{playlist_name}'...")
                
                # Récupérer les pistes
                tracks = self.get_playlist_tracks(playlist_id)
                
                # Sauvegarder les pistes
                filename = f"playlist_{playlist_id}_tracks"
                filepath = self.save_data(tracks, str(self.tracks_dir / filename))
                
                tracks_filepaths.append(filepath)
                total_tracks += len(tracks)
                
                print(f"  {len(tracks)} pistes exportées pour '{playlist_name}'")
            
            export_stats["tracks_exported"] = True
            export_stats["tracks_count"] = total_tracks
            export_stats["tracks_filepaths"] = tracks_filepaths
            
            print(f"Total de {total_tracks} pistes exportées pour toutes les playlists")
        
        return export_stats
