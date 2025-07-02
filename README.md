# Spotify Data Exporter

A Python tool to automatically export your personal Spotify data via the official API.

## Features

- Complete export of personal Spotify data:
  - User profile
  - Playlists (with detailed content)
  - Library (saved tracks and albums)
  - Followed artists
  - Recent listening history
  - Top artists and tracks (short, medium, and long term)
- Secure OAuth authentication with token refresh management
- Automatic handling of API pagination and rate limits
- Export in different formats (JSON, CSV)
- Simple command-line interface
- Local storage of exported data

## Prerequisites

- Python 3.7+
- A Spotify developer account with a registered application
  - Create your application on [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/)
  - Note your Client ID and Client Secret
  - Add `http://127.0.0.1:8888/callback` as a redirect URI

## Installation

1. Clone this repository or download the source files

```bash
git clone https://github.com/your-username/spotify-data-exporter.git
cd spotify-data-exporter
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file at the root of the project with your Spotify credentials:
```
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8888/callback
```

## Usage

### Command Line

To start the export with default parameters:

```bash
python cli.py
```

Available options:

```
usage: cli.py [-h] [-f {json,csv}] [-o OUTPUT_DIR] [-e ENV_FILE] [--client-id CLIENT_ID] [--client-secret CLIENT_SECRET] [--redirect-uri REDIRECT_URI]

Export personal Spotify data via the official API.

options:
  -h, --help            show this help message and exit
  -f {json,csv}, --format {json,csv}
                        Data export format (default: json)
  -o OUTPUT_DIR, --output-dir OUTPUT_DIR
                        Data export directory (default: ./exports)
  -e ENV_FILE, --env-file ENV_FILE
                        .env file containing environment variables (default: .env)
  --client-id CLIENT_ID
                        Spotify client ID (overrides SPOTIFY_CLIENT_ID environment variable)
  --client-secret CLIENT_SECRET
                        Spotify client secret (overrides SPOTIFY_CLIENT_SECRET environment variable)
  --redirect-uri REDIRECT_URI
                        Spotify redirect URI (overrides SPOTIFY_REDIRECT_URI environment variable)
```

### Usage as a Python Module

```python
from auth.spotify_auth import SpotifyAuthManager
from main import export_all_data

# Initialize authentication
auth_manager = SpotifyAuthManager()
spotify_client = auth_manager.authenticate()

# Export data
export_report = export_all_data(spotify_client, export_format="json")
```

## Authentication Process

During the first use, the tool will ask you to authenticate with Spotify:

1. A URL will be displayed in the console
2. Open this URL in your browser
3. Log in to your Spotify account and authorize the application
4. You will be redirected to a callback URL
5. Copy the authorization code from the redirect URL and paste it into the console

Once authenticated, a refresh token will be saved locally for future use.

## Exported Data Structure

The data is organized in the `exports` directory (by default) according to the following structure:

```
exports/
├── profile/
│   └── profile.json
├── playlists/
│   ├── playlists.json
│   └── tracks/
│       └── playlist_{id}_tracks.json
├── library/
│   ├── tracks/
│   │   └── saved_tracks.json
│   └── albums/
│       └── saved_albums.json
├── following/
│   └── followed_artists.json
├── history/
│   ├── recently_played/
│   │   └── recently_played.json
│   ├── top_tracks/
│   │   ├── top_tracks_short_term.json
│   │   ├── top_tracks_medium_term.json
│   │   └── top_tracks_long_term.json
│   └── top_artists/
│       ├── top_artists_short_term.json
│       ├── top_artists_medium_term.json
│       └── top_artists_long_term.json
└── export_report_{timestamp}.json
```

## OAuth Scopes Used

The application uses the following OAuth scopes to access your data:

- `user-read-private`, `user-read-email`: Profile information
- `playlist-read-private`, `playlist-read-collaborative`: Private and collaborative playlists
- `user-library-read`: Saved tracks and albums
- `user-follow-read`: Followed artists
- `user-read-recently-played`: Recent listening history
- `user-top-read`: Top artists and tracks
- `user-read-playback-position`: Playback positions

## Known Limitations

- The Spotify API limits the listening history to the last 50 tracks
- Top artists and tracks are limited to Spotify's predefined periods (4 weeks, 6 months, several years)
- The API does not allow access to the complete listening history

## Contributing

Contributions are welcome! Feel free to open an issue to report a bug or suggest an improvement.


## License

This project is under the MIT license - a free and open-source license that allows anyone to use, modify, copy, distribute, sell, and even change the license of the code.

See the LICENSE file for the full text of the license.