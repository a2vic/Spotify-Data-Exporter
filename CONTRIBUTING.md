# Guide de contribution

Merci de votre intérêt pour contribuer à Spotify Data Exporter ! Ce document fournit des lignes directrices pour contribuer au projet.

## Environnement de développement

### Prérequis

- Python 3.7+
- Un compte développeur Spotify avec une application enregistrée

### Installation pour le développement

1. Clonez le dépôt :
```bash
git clone <url-du-repo>
cd spotipy
```

2. Créez un environnement virtuel et activez-le :
```bash
python -m venv venv
# Sur Windows
venv\Scripts\activate
# Sur macOS/Linux
source venv/bin/activate
```

3. Installez les dépendances de développement :
```bash
pip install -r requirements-dev.txt
```

4. Créez un fichier `.env` avec vos identifiants Spotify :
```
SPOTIFY_CLIENT_ID=votre_client_id
SPOTIFY_CLIENT_SECRET=votre_client_secret
SPOTIFY_REDIRECT_URI=http://localhost:8888/callback
```

## Structure du projet

```
spotipy/
├── auth/                   # Module d'authentification
├── config/                 # Configuration du projet
├── exporters/              # Exporters pour différents types de données
├── utils/                  # Utilitaires communs
├── tests/                  # Tests unitaires
├── exports/                # Répertoire pour les données exportées (généré)
├── main.py                 # Point d'entrée principal
├── cli.py                  # Interface en ligne de commande
└── requirements.txt        # Dépendances du projet
```

## Normes de codage

- Suivez la [PEP 8](https://www.python.org/dev/peps/pep-0008/) pour le style de code Python
- Utilisez des docstrings au format Google pour documenter les fonctions et les classes
- Maintenez une couverture de test adéquate pour les nouvelles fonctionnalités
- Utilisez des noms de variables et de fonctions explicites en français

## Tests

Exécutez les tests unitaires avec :

```bash
python -m unittest discover tests
```

## Processus de contribution

1. Créez une branche pour votre fonctionnalité ou correction de bug :
```bash
git checkout -b nom-de-votre-branche
```

2. Effectuez vos modifications et assurez-vous que les tests passent

3. Mettez à jour la documentation si nécessaire

4. Soumettez une pull request avec une description claire de vos modifications

## Ajouter un nouvel exporter

Pour ajouter un nouvel exporter pour un type de données Spotify :

1. Créez une nouvelle classe dans le répertoire `exporters/` qui hérite de `BaseExporter`
2. Implémentez la méthode abstraite `export()`
3. Ajoutez des méthodes spécifiques pour récupérer les données via l'API Spotify
4. Intégrez le nouvel exporter dans `main.py`
5. Ajoutez des tests unitaires pour votre exporter

Exemple :

```python
from exporters.base_exporter import BaseExporter

class MyNewExporter(BaseExporter):
    def __init__(self, spotify_client, export_dir, export_format="json"):
        super().__init__(spotify_client, export_dir, export_format)
    
    def get_my_data(self):
        # Utiliser self.paginate() pour gérer la pagination
        return self.paginate("spotify_method_name")
    
    def export(self):
        print("Exportation de mes données...")
        data = self.get_my_data()
        filepath = self.save_data(data, "my_data")
        print(f"{len(data)} éléments exportés: {filepath}")
        return {"type": "my_data", "count": len(data), "filepath": filepath}
```

## Signaler des problèmes

Si vous rencontrez des problèmes ou avez des suggestions, n'hésitez pas à ouvrir une issue en fournissant :

- Une description claire du problème
- Les étapes pour reproduire le problème
- Le comportement attendu et observé
- Toute information supplémentaire pertinente

Merci de contribuer à améliorer Spotify Data Exporter !
