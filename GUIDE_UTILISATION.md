# Guide d'utilisation de Spotify Data Exporter

Ce guide détaille les étapes pour configurer, installer et utiliser l'outil d'export de données Spotify.

## Table des matières

1. [Configuration initiale](#configuration-initiale)
2. [Installation](#installation)
3. [Utilisation de base](#utilisation-de-base)
4. [Options avancées](#options-avancées)
5. [Structure des données exportées](#structure-des-données-exportées)
6. [Résolution des problèmes courants](#résolution-des-problèmes-courants)

## Configuration initiale

### Création d'une application Spotify

1. Connectez-vous au [Dashboard Spotify Developer](https://developer.spotify.com/dashboard/)
2. Cliquez sur "Create an App"
3. Remplissez les informations requises :
   - Nom de l'application : "Spotify Data Exporter" (ou autre nom de votre choix)
   - Description : "Outil personnel pour exporter mes données Spotify"
   - Site web : vous pouvez laisser vide ou mettre une URL personnelle
   - Type d'application : Web API
4. Acceptez les conditions d'utilisation et cliquez sur "Create"
5. Une fois l'application créée, notez votre **Client ID** et **Client Secret**
6. Cliquez sur "Edit Settings" et ajoutez l'URI de redirection suivante :
   ```
   http://127.0.0.1:8888/callback
   ```
7. Sauvegardez les paramètres

## Installation

### Prérequis

- Python 3.7 ou supérieur
- pip (gestionnaire de paquets Python)

### Étapes d'installation

1. Clonez ou téléchargez ce projet dans un répertoire de votre choix
2. Ouvrez un terminal et naviguez vers le répertoire du projet
3. Installez les dépendances requises :
   ```bash
   pip install -r requirements.txt
   ```
   Note : Si vous rencontrez des problèmes avec l'installation des dépendances,vous pouvez les installer individuellement :
   ```bash
   pip install spotipy python-dotenv pandas
   ```

4. Créez un fichier `.env` à la racine du projet avec les informations suivantes :
   ```
   SPOTIFY_CLIENT_ID=votre_client_id
   SPOTIFY_CLIENT_SECRET=votre_client_secret
   SPOTIFY_REDIRECT_URI=http://localhost:8888/callback
   ```
   Remplacez `votre_client_id` et `votre_client_secret` par les valeurs obtenues lors de la création de votre application Spotify.

## Utilisation de base

### Première exécution

1. Ouvrez un terminal et naviguez vers le répertoire du projet
2. Exécutez la commande suivante :
   ```bash
   python cli.py
   ```
3. L'outil va vous demander de vous authentifier auprès de Spotify :
   - Une URL sera affichée dans le terminal
   - Ouvrez cette URL dans votre navigateur
   - Connectez-vous à votre compte Spotify si nécessaire
   - Autorisez l'application à accéder à vos données
   - Vous serez redirigé vers une page avec un code d'autorisation dans l'URL
   - Copiez ce code et collez-le dans le terminal lorsque demandé
4. L'outil commencera à exporter vos données Spotify
5. Une fois l'export terminé, un rapport sera affiché indiquant le nombre d'éléments exportés et leur emplacement

### Exécutions suivantes

Pour les exécutions suivantes, l'authentification sera automatique grâce au token de rafraîchissement sauvegardé. Il vous suffira d'exécuter :

```bash
python cli.py
```

## Options avancées

### Format d'export

Par défaut, les données sont exportées au format JSON. Vous pouvez spécifier le format CSV avec l'option `-f` :

```bash
python cli.py -f csv
```

### Répertoire d'export personnalisé

Par défaut, les données sont exportées dans le répertoire `exports/` à la racine du projet. Vous pouvez spécifier un autre répertoire avec l'option `-o` :

```bash
python cli.py -o /chemin/vers/mon/repertoire
```

### Fichier d'environnement personnalisé

Si vous avez plusieurs comptes Spotify ou applications, vous pouvez spécifier un fichier d'environnement différent avec l'option `-e` :

```bash
python cli.py -e .env.autre_compte
```

### Spécifier les identifiants directement

Vous pouvez également spécifier les identifiants directement dans la ligne de commande :

```bash
python cli.py --client-id votre_client_id --client-secret votre_client_secret
```

## Structure des données exportées

Les données exportées sont organisées dans une structure de répertoires cohérente :

```
exports/
├── profile/                    # Données du profil utilisateur
│   └── profile.json
├── playlists/                  # Playlists de l'utilisateur
│   ├── playlists.json          # Liste des playlists
│   └── tracks/                 # Pistes de chaque playlist
│       └── playlist_{id}_tracks.json
├── library/                    # Bibliothèque de l'utilisateur
│   ├── tracks/                 # Pistes sauvegardées
│   │   └── saved_tracks.json
│   └── albums/                 # Albums sauvegardés
│       └── saved_albums.json
├── following/                  # Artistes suivis
│   └── followed_artists.json
├── history/                    # Historique d'écoute et tops
│   ├── recently_played/        # Pistes récemment écoutées
│   │   └── recently_played.json
│   ├── top_tracks/             # Top pistes
│   │   ├── top_tracks_short_term.json   # 4 semaines
│   │   ├── top_tracks_medium_term.json  # 6 mois
│   │   └── top_tracks_long_term.json    # Plusieurs années
│   └── top_artists/            # Top artistes
│       ├── top_artists_short_term.json
│       ├── top_artists_medium_term.json
│       └── top_artists_long_term.json
└── export_report_{timestamp}.json  # Rapport d'export
```

### Format des fichiers JSON

Chaque fichier JSON exporté contient une structure avec des métadonnées et les données elles-mêmes :

```json
{
  "metadata": {
    "export_date": "2025-07-02T06:00:00.000000",
    "export_type": "ProfileExporter"
  },
  "data": {
    // Données exportées
  }
}
```

### Format des fichiers CSV

Les fichiers CSV contiennent les données sous forme tabulaire, avec une ligne d'en-tête et une ligne par élément. Les structures complexes (listes, objets) sont sérialisées en JSON dans les cellules.

## Résolution des problèmes courants

### Erreur d'authentification

Si vous rencontrez des erreurs d'authentification :
1. Vérifiez que votre Client ID et Client Secret sont corrects dans le fichier `.env`
2. Assurez-vous que l'URI de redirection est correctement configurée dans le dashboard Spotify Developer
3. Supprimez le fichier `.spotify_token_cache` à la racine du projet pour forcer une nouvelle authentification

### Limitations de l'API Spotify

- L'API Spotify limite l'historique d'écoute aux 50 dernières pistes
- Les tops artistes et pistes sont limités aux périodes prédéfinies par Spotify
- L'API ne permet pas d'accéder à l'historique d'écoute complet

### Erreurs de rate limiting

Si vous rencontrez des erreurs de rate limiting (429 Too Many Requests), l'outil réessaiera automatiquement après un délai. Si le problème persiste, essayez d'exécuter l'outil plus tard.

### Problèmes d'installation des dépendances

Si vous rencontrez des problèmes lors de l'installation des dépendances :
1. Assurez-vous d'utiliser une version compatible de Python (3.7+)
2. Essayez de mettre à jour pip : `python -m pip install --upgrade pip`
3. Installez les dépendances une par une pour identifier celle qui pose problème

Pour toute autre question ou problème, n'hésitez pas à ouvrir une issue sur le dépôt du projet.
