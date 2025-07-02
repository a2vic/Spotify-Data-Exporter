"""
Exporter pour les données de profil utilisateur Spotify.
"""

from typing import Dict, Any
from pathlib import Path

from exporters.base_exporter import BaseExporter
from utils.api_utils import rate_limit_decorator


class ProfileExporter(BaseExporter):
    """
    Exporter pour récupérer et sauvegarder les données du profil utilisateur.
    """

    def __init__(self, spotify_client, export_dir, export_format="json"):
        """
        Initialise l'exporter de profil.

        Args:
            spotify_client: Client Spotify authentifié
            export_dir: Répertoire d'export des données
            export_format: Format d'export (json ou csv)
        """
        super().__init__(spotify_client, export_dir, export_format)

    @rate_limit_decorator()
    def get_user_profile(self) -> Dict[str, Any]:
        """
        Récupère les données du profil utilisateur.

        Returns:
            Données du profil utilisateur
        """
        return self.spotify.current_user()

    def export(self) -> Dict[str, Any]:
        """
        Exporte les données du profil utilisateur.

        Returns:
            Métadonnées de l'export
        """
        print("Exportation du profil utilisateur...")
        
        # Récupérer les données du profil
        profile_data = self.get_user_profile()
        
        # Sauvegarder les données
        filepath = self.save_data(profile_data, "profile")
        
        print(f"Profil utilisateur exporté avec succès: {filepath}")
        
        return {
            "type": "profile",
            "count": 1,
            "filepath": filepath
        }
