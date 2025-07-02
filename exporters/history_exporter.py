"""
Exporter pour l'historique d'écoute et les tops artistes/pistes de l'utilisateur Spotify.
"""

import os
from typing import Dict, List, Any, Optional
from pathlib import Path
from enum import Enum

from exporters.base_exporter import BaseExporter
from utils.api_utils import rate_limit_decorator


class TimeRange(Enum):
    """Périodes disponibles pour les tops artistes/pistes."""
    SHORT_TERM = "short_term"  # 4 semaines
    MEDIUM_TERM = "medium_term"  # 6 mois
    LONG_TERM = "long_term"  # plusieurs années


class HistoryExporter(BaseExporter):
    """
    Exporter pour récupérer et sauvegarder l'historique d'écoute et les tops artistes/pistes.
    """

    def __init__(self, spotify_client, export_dir, export_format="json"):
        """
        Initialise l'exporter d'historique.

        Args:
            spotify_client: Client Spotify authentifié
            export_dir: Répertoire d'export des données
            export_format: Format d'export (json ou csv)
        """
        super().__init__(spotify_client, export_dir, export_format)
        
        # Créer les sous-répertoires pour les différents types d'historique
        self.recently_played_dir = Path(self.export_dir) / "recently_played"
        self.top_tracks_dir = Path(self.export_dir) / "top_tracks"
        self.top_artists_dir = Path(self.export_dir) / "top_artists"
        
        os.makedirs(self.recently_played_dir, exist_ok=True)
        os.makedirs(self.top_tracks_dir, exist_ok=True)
        os.makedirs(self.top_artists_dir, exist_ok=True)

    def get_recently_played(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Récupère l'historique récent d'écoute de l'utilisateur.
        
        Note: Cet endpoint est limité à 50 pistes maximum et ne supporte pas la pagination standard.

        Args:
            limit: Nombre maximum de pistes à récupérer (max 50)

        Returns:
            Liste des pistes récemment écoutées
        """
        response = self.spotify.current_user_recently_played(limit=min(limit, 50))
        return response.get('items', [])

    def get_top_items(self, item_type: str, time_range: TimeRange, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Récupère les tops artistes ou pistes de l'utilisateur.

        Args:
            item_type: Type d'élément ('artists' ou 'tracks')
            time_range: Période de temps (court, moyen ou long terme)
            limit: Nombre maximum d'éléments à récupérer

        Returns:
            Liste des tops artistes ou pistes
        """
        return self.paginate(
            "current_user_top_tracks" if item_type == "tracks" else "current_user_top_artists",
            time_range=time_range.value,
            limit=limit
        )

    def export_recently_played(self) -> Dict[str, Any]:
        """
        Exporte l'historique récent d'écoute de l'utilisateur.

        Returns:
            Métadonnées de l'export
        """
        print("Exportation de l'historique récent d'écoute...")
        
        # Récupérer l'historique récent
        tracks = self.get_recently_played()
        
        # Sauvegarder l'historique
        filepath = self.save_data(tracks, str(self.recently_played_dir / "recently_played"))
        
        print(f"{len(tracks)} pistes récemment écoutées exportées avec succès: {filepath}")
        
        return {
            "type": "recently_played",
            "count": len(tracks),
            "filepath": filepath
        }

    def export_top_tracks(self) -> Dict[str, Any]:
        """
        Exporte les tops pistes de l'utilisateur pour différentes périodes.

        Returns:
            Métadonnées de l'export
        """
        print("Exportation des tops pistes...")
        
        results = {}
        total_count = 0
        
        # Exporter pour chaque période
        for time_range in TimeRange:
            print(f"  Exportation des tops pistes ({time_range.value})...")
            
            # Récupérer les tops pistes
            tracks = self.get_top_items("tracks", time_range)
            
            # Sauvegarder les tops pistes
            filename = f"top_tracks_{time_range.value}"
            filepath = self.save_data(tracks, str(self.top_tracks_dir / filename))
            
            print(f"  {len(tracks)} tops pistes ({time_range.value}) exportées avec succès: {filepath}")
            
            results[time_range.value] = {
                "count": len(tracks),
                "filepath": filepath
            }
            
            total_count += len(tracks)
        
        return {
            "type": "top_tracks",
            "time_ranges": results,
            "total_count": total_count
        }

    def export_top_artists(self) -> Dict[str, Any]:
        """
        Exporte les tops artistes de l'utilisateur pour différentes périodes.

        Returns:
            Métadonnées de l'export
        """
        print("Exportation des tops artistes...")
        
        results = {}
        total_count = 0
        
        # Exporter pour chaque période
        for time_range in TimeRange:
            print(f"  Exportation des tops artistes ({time_range.value})...")
            
            # Récupérer les tops artistes
            artists = self.get_top_items("artists", time_range)
            
            # Sauvegarder les tops artistes
            filename = f"top_artists_{time_range.value}"
            filepath = self.save_data(artists, str(self.top_artists_dir / filename))
            
            print(f"  {len(artists)} tops artistes ({time_range.value}) exportés avec succès: {filepath}")
            
            results[time_range.value] = {
                "count": len(artists),
                "filepath": filepath
            }
            
            total_count += len(artists)
        
        return {
            "type": "top_artists",
            "time_ranges": results,
            "total_count": total_count
        }

    def export(self) -> Dict[str, Any]:
        """
        Exporte l'historique d'écoute et les tops artistes/pistes de l'utilisateur.

        Returns:
            Métadonnées de l'export
        """
        # Exporter l'historique récent d'écoute
        recently_played_stats = self.export_recently_played()
        
        # Exporter les tops pistes
        top_tracks_stats = self.export_top_tracks()
        
        # Exporter les tops artistes
        top_artists_stats = self.export_top_artists()
        
        # Combiner les statistiques
        return {
            "type": "history",
            "recently_played": recently_played_stats,
            "top_tracks": top_tracks_stats,
            "top_artists": top_artists_stats
        }
