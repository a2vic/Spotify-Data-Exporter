"""
Exporter pour les artistes suivis par l'utilisateur Spotify.
"""

from typing import Dict, List, Any
from pathlib import Path

from exporters.base_exporter import BaseExporter
from utils.api_utils import rate_limit_decorator


class FollowingExporter(BaseExporter):
    """
    Exporter pour récupérer et sauvegarder les artistes suivis par l'utilisateur.
    """

    def __init__(self, spotify_client, export_dir, export_format="json"):
        """
        Initialise l'exporter d'artistes suivis.

        Args:
            spotify_client: Client Spotify authentifié
            export_dir: Répertoire d'export des données
            export_format: Format d'export (json ou csv)
        """
        super().__init__(spotify_client, export_dir, export_format)

    def get_followed_artists(self) -> List[Dict[str, Any]]:
        """
        Récupère tous les artistes suivis par l'utilisateur avec pagination.
        
        Note: L'API Spotify pour les artistes suivis fonctionne différemment des autres endpoints
        en utilisant un curseur 'after' au lieu d'un 'offset'.

        Returns:
            Liste des artistes suivis
        """
        artists = []
        after = None
        limit = 50  # Maximum pour cet endpoint
        
        while True:
            response = self.spotify.current_user_followed_artists(limit=limit, after=after)
            
            # L'API retourne les artistes dans un format différent
            items = response.get('artists', {}).get('items', [])
            artists.extend(items)
            
            # Vérifier s'il y a une page suivante
            if not response.get('artists', {}).get('next'):
                break
                
            # Mettre à jour le curseur 'after' avec l'ID du dernier artiste
            if items:
                after = items[-1]['id']
            else:
                break
                
        return artists

    def export(self) -> Dict[str, Any]:
        """
        Exporte les artistes suivis par l'utilisateur.

        Returns:
            Métadonnées de l'export
        """
        print("Exportation des artistes suivis...")
        
        # Récupérer les artistes suivis
        artists = self.get_followed_artists()
        
        # Sauvegarder les artistes
        filepath = self.save_data(artists, "followed_artists")
        
        print(f"{len(artists)} artistes suivis exportés avec succès: {filepath}")
        
        return {
            "type": "followed_artists",
            "count": len(artists),
            "filepath": filepath
        }
