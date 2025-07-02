"""
Module d'authentification pour l'API Spotify.
Gère l'authentification OAuth et le rafraîchissement des tokens.
"""

import os
import time
from typing import Optional, Dict, Any

import spotipy
from spotipy.oauth2 import SpotifyOAuth

from config.settings import (
    SPOTIFY_CLIENT_ID,
    SPOTIFY_CLIENT_SECRET,
    SPOTIFY_REDIRECT_URI,
    SPOTIFY_SCOPES,
    TOKEN_CACHE_PATH
)


class SpotifyAuthManager:
    """
    Gestionnaire d'authentification pour l'API Spotify.
    Gère l'authentification OAuth et le rafraîchissement des tokens.
    """

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        redirect_uri: Optional[str] = None,
        scopes: Optional[list] = None,
        token_cache_path: Optional[str] = None
    ):
        """
        Initialise le gestionnaire d'authentification.

        Args:
            client_id: ID client Spotify (par défaut: depuis les variables d'environnement)
            client_secret: Secret client Spotify (par défaut: depuis les variables d'environnement)
            redirect_uri: URI de redirection (par défaut: depuis les variables d'environnement)
            scopes: Liste des scopes OAuth requis (par défaut: depuis settings.py)
            token_cache_path: Chemin vers le fichier de cache du token (par défaut: depuis settings.py)
        """
        self.client_id = client_id or SPOTIFY_CLIENT_ID
        self.client_secret = client_secret or SPOTIFY_CLIENT_SECRET
        self.redirect_uri = redirect_uri or SPOTIFY_REDIRECT_URI
        self.scopes = scopes or SPOTIFY_SCOPES
        self.token_cache_path = token_cache_path or TOKEN_CACHE_PATH
        
        # Vérifier que les identifiants sont définis
        if not self.client_id or not self.client_secret:
            raise ValueError(
                "Les identifiants Spotify (client_id et client_secret) doivent être définis. "
                "Définissez-les en tant que paramètres ou via les variables d'environnement "
                "SPOTIFY_CLIENT_ID et SPOTIFY_CLIENT_SECRET."
            )
        
        # Initialiser le gestionnaire OAuth
        self.oauth_manager = SpotifyOAuth(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri,
            scope=" ".join(self.scopes),
            cache_path=str(self.token_cache_path)
        )
        
        self.client = None

    def authenticate(self) -> spotipy.Spotify:
        """
        Authentifie l'utilisateur et retourne un client Spotify authentifié.
        Si un token valide existe déjà, il sera utilisé.
        Sinon, le processus d'authentification OAuth sera lancé.

        Returns:
            Un client Spotify authentifié
        """
        # Vérifier si un token valide existe déjà
        token_info = self.oauth_manager.get_cached_token()
        
        # Si pas de token ou token expiré, lancer le processus d'authentification
        if not token_info:
            print("Aucun token d'accès trouvé. Lancement du processus d'authentification...")
            auth_url = self.oauth_manager.get_authorize_url()
            print(f"Veuillez visiter cette URL pour autoriser l'application: {auth_url}")
            
            # Attendre que l'utilisateur s'authentifie
            response_code = input("Entrez le code d'autorisation de l'URL de redirection: ")
            token_info = self.oauth_manager.get_access_token(response_code)
        
        # Créer le client Spotify avec le token d'accès
        self.client = spotipy.Spotify(auth=token_info["access_token"])
        
        return self.client

    def get_client(self) -> spotipy.Spotify:
        """
        Retourne un client Spotify authentifié.
        Si aucun client n'existe, lance le processus d'authentification.

        Returns:
            Un client Spotify authentifié
        """
        if not self.client:
            return self.authenticate()
        return self.client

    def refresh_token_if_needed(self) -> None:
        """
        Vérifie si le token d'accès est expiré et le rafraîchit si nécessaire.
        """
        token_info = self.oauth_manager.get_cached_token()
        
        # Si le token est expiré ou va expirer dans moins de 60 secondes
        if token_info and token_info["expires_at"] - time.time() < 60:
            print("Le token d'accès est expiré ou va bientôt expirer. Rafraîchissement...")
            token_info = self.oauth_manager.refresh_access_token(token_info["refresh_token"])
            
            # Mettre à jour le client avec le nouveau token
            if self.client:
                self.client = spotipy.Spotify(auth=token_info["access_token"])
