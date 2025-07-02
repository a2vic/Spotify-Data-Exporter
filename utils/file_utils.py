"""
Utilitaires pour la gestion des fichiers d'export.
"""

import os
import json
import shutil
from pathlib import Path
from typing import Dict, Any, Union, List, Optional
from datetime import datetime


def ensure_directory(directory: Union[str, Path]) -> Path:
    """
    S'assure qu'un répertoire existe, le crée si nécessaire.
    
    Args:
        directory: Chemin du répertoire
        
    Returns:
        Objet Path du répertoire
    """
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    return path


def create_export_structure(structure: Dict[str, Any]) -> None:
    """
    Crée la structure de répertoires pour l'export.
    
    Args:
        structure: Dictionnaire décrivant la structure des répertoires
    """
    def _create_dirs(struct, parent=None):
        for key, value in struct.items():
            if isinstance(value, dict):
                # Si c'est un dictionnaire, c'est une sous-structure
                if parent:
                    subdir = parent / key
                else:
                    subdir = Path(key)
                ensure_directory(subdir)
                _create_dirs(value, subdir)
            else:
                # Sinon, c'est un chemin direct
                ensure_directory(value)
    
    _create_dirs(structure)


def backup_file(filepath: Union[str, Path], backup_dir: Optional[Union[str, Path]] = None) -> Path:
    """
    Crée une sauvegarde d'un fichier existant.
    
    Args:
        filepath: Chemin du fichier à sauvegarder
        backup_dir: Répertoire de sauvegarde (par défaut: même répertoire que le fichier)
        
    Returns:
        Chemin du fichier de sauvegarde
    """
    filepath = Path(filepath)
    
    if not filepath.exists():
        return filepath
    
    # Déterminer le répertoire de sauvegarde
    if backup_dir:
        backup_dir = Path(backup_dir)
        ensure_directory(backup_dir)
    else:
        backup_dir = filepath.parent
    
    # Créer un nom de fichier avec timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"{filepath.stem}_{timestamp}{filepath.suffix}"
    backup_path = backup_dir / backup_filename
    
    # Copier le fichier
    shutil.copy2(filepath, backup_path)
    
    return backup_path


def merge_json_data(existing_data: Dict[str, Any], new_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fusionne des données JSON existantes avec de nouvelles données.
    
    Args:
        existing_data: Données JSON existantes
        new_data: Nouvelles données JSON
        
    Returns:
        Données fusionnées
    """
    # Fusionner les métadonnées
    if "metadata" in existing_data and "metadata" in new_data:
        merged_metadata = {**existing_data["metadata"]}
        merged_metadata["update_date"] = new_data["metadata"].get("export_date", datetime.now().isoformat())
        merged_metadata["previous_export_date"] = existing_data["metadata"].get("export_date")
    else:
        merged_metadata = new_data.get("metadata", {})
    
    # Fusionner les données
    if "data" in existing_data and "data" in new_data:
        # Si les deux sont des listes, les concaténer et supprimer les doublons
        if isinstance(existing_data["data"], list) and isinstance(new_data["data"], list):
            # Créer un ensemble d'identifiants pour les éléments existants
            existing_ids = set()
            id_field = _find_id_field(existing_data["data"])
            
            if id_field:
                existing_ids = {item.get(id_field) for item in existing_data["data"] if id_field in item}
                
                # Ajouter uniquement les nouveaux éléments
                merged_data = existing_data["data"].copy()
                for item in new_data["data"]:
                    if id_field not in item or item[id_field] not in existing_ids:
                        merged_data.append(item)
            else:
                # Si pas d'identifiant trouvé, simplement concaténer les listes
                merged_data = existing_data["data"] + new_data["data"]
        else:
            # Si ce ne sont pas des listes, prendre les nouvelles données
            merged_data = new_data["data"]
    else:
        merged_data = new_data.get("data", {})
    
    return {
        "metadata": merged_metadata,
        "data": merged_data
    }


def _find_id_field(data_list: List[Dict[str, Any]]) -> Optional[str]:
    """
    Trouve le champ d'identifiant dans une liste de dictionnaires.
    Cherche 'id', 'uri', 'href' dans cet ordre.
    
    Args:
        data_list: Liste de dictionnaires
        
    Returns:
        Nom du champ d'identifiant ou None si non trouvé
    """
    if not data_list or not isinstance(data_list, list):
        return None
    
    # Champs d'identifiant possibles par ordre de priorité
    id_fields = ["id", "uri", "href"]
    
    for item in data_list:
        if isinstance(item, dict):
            for field in id_fields:
                if field in item:
                    return field
    
    return None


def load_json_file(filepath: Union[str, Path]) -> Dict[str, Any]:
    """
    Charge un fichier JSON.
    
    Args:
        filepath: Chemin du fichier JSON
        
    Returns:
        Données JSON chargées
    """
    filepath = Path(filepath)
    
    if not filepath.exists():
        return {}
    
    with open(filepath, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}
