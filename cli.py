#!/usr/bin/env python
"""
Interface en ligne de commande pour l'export des données Spotify.
"""

import os
import sys
import argparse
from pathlib import Path

# Charger les variables d'environnement avant tout import
import dotenv
if os.path.exists(".env"):
    print("Chargement des variables d'environnement depuis .env")
    dotenv.load_dotenv(".env")

from auth.spotify_auth import SpotifyAuthManager
from main import export_all_data
from config.settings import EXPORT_FORMATS, DEFAULT_EXPORT_FORMAT, EXPORT_DIR


def parse_arguments():
    """
    Parse les arguments de la ligne de commande.
    
    Returns:
        Arguments parsés
    """
    parser = argparse.ArgumentParser(
        description="Exporte les données personnelles Spotify via l'API officielle."
    )
    
    parser.add_argument(
        "-f", "--format",
        choices=EXPORT_FORMATS,
        default=DEFAULT_EXPORT_FORMAT,
        help=f"Format d'export des données (par défaut: {DEFAULT_EXPORT_FORMAT})"
    )
    
    parser.add_argument(
        "-o", "--output-dir",
        type=str,
        help="Répertoire d'export des données (par défaut: ./exports)"
    )
    
    parser.add_argument(
        "-e", "--env-file",
        type=str,
        default=".env",
        help="Fichier .env contenant les variables d'environnement (par défaut: .env)"
    )
    
    parser.add_argument(
        "--client-id",
        type=str,
        help="ID client Spotify (remplace la variable d'environnement SPOTIFY_CLIENT_ID)"
    )
    
    parser.add_argument(
        "--client-secret",
        type=str,
        help="Secret client Spotify (remplace la variable d'environnement SPOTIFY_CLIENT_SECRET)"
    )
    
    parser.add_argument(
        "--redirect-uri",
        type=str,
        help="URI de redirection Spotify (remplace la variable d'environnement SPOTIFY_REDIRECT_URI)"
    )
    
    return parser.parse_args()


def setup_environment(args):
    """
    Configure l'environnement d'exécution.
    
    Args:
        args: Arguments de la ligne de commande
    """
    # Charger les variables d'environnement depuis le fichier .env spécifié
    if args.env_file != ".env" and os.path.exists(args.env_file):
        print(f"Chargement des variables d'environnement depuis {args.env_file}")
        dotenv.load_dotenv(args.env_file, override=True)
    
    # Remplacer les variables d'environnement par les arguments de la ligne de commande
    if args.client_id:
        os.environ["SPOTIFY_CLIENT_ID"] = args.client_id
        
    if args.client_secret:
        os.environ["SPOTIFY_CLIENT_SECRET"] = args.client_secret
        
    if args.redirect_uri:
        os.environ["SPOTIFY_REDIRECT_URI"] = args.redirect_uri
    
    # Configurer le répertoire d'export
    if args.output_dir:
        global EXPORT_DIR
        EXPORT_DIR = Path(args.output_dir)


def check_requirements():
    """
    Vérifie que toutes les dépendances sont installées.
    
    Returns:
        True si toutes les dépendances sont installées, False sinon
    """
    try:
        import spotipy
        import pandas
        return True
    except ImportError as e:
        print(f"Erreur: Dépendance manquante - {e}")
        print("Veuillez installer les dépendances requises avec:")
        print("pip install -r requirements.txt")
        return False


def main():
    """
    Fonction principale de l'interface en ligne de commande.
    """
    # Vérifier les dépendances
    if not check_requirements():
        sys.exit(1)
    
    # Parser les arguments
    args = parse_arguments()
    
    # Configurer l'environnement
    setup_environment(args)
    
    try:
        # Initialiser l'authentification
        print("Initialisation de l'authentification Spotify...")
        auth_manager = SpotifyAuthManager()
        
        # Authentifier l'utilisateur
        spotify_client = auth_manager.authenticate()
        
        # Exporter toutes les données
        export_all_data(spotify_client, args.format)
        
    except Exception as e:
        print(f"Erreur lors de l'export des données: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
