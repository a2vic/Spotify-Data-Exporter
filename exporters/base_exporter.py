"""
Classe de base pour tous les exporters de données Spotify.
"""

import os
import json
import csv
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Iterator

import pandas as pd

from config.settings import DEFAULT_LIMIT, API_RETRY_ATTEMPTS, API_RETRY_DELAY
from utils.api_utils import retry_on_api_error


class BaseExporter(ABC):
    """
    Classe abstraite de base pour tous les exporters de données Spotify.
    Fournit des méthodes communes pour la pagination, la gestion des erreurs,
    et l'export des données dans différents formats.
    """

    def __init__(self, spotify_client, export_dir: Union[str, Path], export_format: str = "json"):
        """
        Initialise l'exporter.

        Args:
            spotify_client: Client Spotify authentifié
            export_dir: Répertoire d'export des données
            export_format: Format d'export (json ou csv)
        """
        self.spotify = spotify_client
        self.export_dir = Path(export_dir)
        self.export_format = export_format.lower()
        
        # Créer le répertoire d'export s'il n'existe pas
        os.makedirs(self.export_dir, exist_ok=True)
    
    @abstractmethod
    def export(self) -> Dict[str, Any]:
        """
        Méthode principale d'export à implémenter par chaque sous-classe.
        
        Returns:
            Dictionnaire contenant les métadonnées de l'export
        """
        pass
    
    def paginate(self, method, *args, **kwargs) -> List[Dict[str, Any]]:
        """
        Gère la pagination pour les appels API Spotify.
        
        Args:
            method: Méthode du client Spotify à appeler
            *args: Arguments positionnels pour la méthode
            **kwargs: Arguments nommés pour la méthode
            
        Returns:
            Liste des résultats de toutes les pages
        """
        # Définir la limite par défaut si non spécifiée
        if 'limit' not in kwargs:
            kwargs['limit'] = DEFAULT_LIMIT
            
        results = []
        response = retry_on_api_error(
            lambda: getattr(self.spotify, method)(*args, **kwargs),
            max_retries=API_RETRY_ATTEMPTS,
            delay=API_RETRY_DELAY
        )
        
        # Collecter les résultats de la première page
        if 'items' in response:
            results.extend(response['items'])
        
        # Paginer jusqu'à ce qu'il n'y ait plus de pages suivantes
        while response.get('next'):
            response = retry_on_api_error(
                lambda: self.spotify.next(response),
                max_retries=API_RETRY_ATTEMPTS,
                delay=API_RETRY_DELAY
            )
            if 'items' in response:
                results.extend(response['items'])
                
        return results
    
    def save_to_json(self, data: Dict[str, Any], filename: str) -> str:
        """
        Sauvegarde les données au format JSON.
        
        Args:
            data: Données à sauvegarder
            filename: Nom du fichier (sans extension)
            
        Returns:
            Chemin du fichier sauvegardé
        """
        filepath = self.export_dir / f"{filename}.json"
        
        # Ajouter des métadonnées
        data_with_meta = {
            "metadata": {
                "export_date": datetime.now().isoformat(),
                "export_type": self.__class__.__name__
            },
            "data": data
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data_with_meta, f, ensure_ascii=False, indent=2)
            
        return str(filepath)
    
    def save_to_csv(self, data: List[Dict[str, Any]], filename: str) -> str:
        """
        Sauvegarde les données au format CSV.
        
        Args:
            data: Liste de dictionnaires à sauvegarder
            filename: Nom du fichier (sans extension)
            
        Returns:
            Chemin du fichier sauvegardé
        """
        filepath = self.export_dir / f"{filename}.csv"
        
        # Convertir en DataFrame pandas pour faciliter l'export CSV
        df = pd.DataFrame(data)
        
        # Gérer les colonnes contenant des listes ou des dictionnaires
        for col in df.columns:
            if df[col].apply(lambda x: isinstance(x, (dict, list))).any():
                df[col] = df[col].apply(lambda x: json.dumps(x, ensure_ascii=False) if isinstance(x, (dict, list)) else x)
        
        df.to_csv(filepath, index=False, encoding='utf-8')
        return str(filepath)
    
    def save_data(self, data: Union[Dict[str, Any], List[Dict[str, Any]]], filename: str) -> str:
        """
        Sauvegarde les données dans le format spécifié.
        
        Args:
            data: Données à sauvegarder
            filename: Nom du fichier (sans extension)
            
        Returns:
            Chemin du fichier sauvegardé
        """
        if self.export_format == "csv":
            # Pour CSV, nous avons besoin d'une liste de dictionnaires
            if isinstance(data, dict):
                # Si c'est un dictionnaire simple, le convertir en liste
                if all(not isinstance(v, (dict, list)) for v in data.values()):
                    data = [data]
                # Si c'est un dictionnaire de dictionnaires, le transformer en liste
                else:
                    data = [{"key": k, **v} if isinstance(v, dict) else {"key": k, "value": v} 
                           for k, v in data.items()]
            return self.save_to_csv(data, filename)
        else:
            # Par défaut, sauvegarder en JSON
            return self.save_to_json(data, filename)
