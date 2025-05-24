import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Spotify authentication
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id='your id',
    client_secret='your secret',
    redirect_uri='http://127.0.0.1:8888/callback',
    scope='user-library-read playlist-read-private playlist-read-collaborative'
))

# Read data from CSV
data = pd.read_csv("playlist_2010to2023.csv")
data.artist_genres = data.artist_genres.apply(lambda x: eval(x))
data.track_id = data.track_id.apply(lambda x: f"https://open.spotify.com/track/{x}")

# Process data to create all_tracks
all_tracks = []
for _, row in data.iterrows():
    all_tracks.append({
        'track_id': row['track_id'],
        'track_name': row['track_name'],
        'artist_name': row['artist_name'],
        'artist_genres': row['artist_genres'],
        'track_popularity': row['track_popularity']
    })

# Track recommendation history
recommended_track_ids = set()

# Get user playlists
def get_user_playlists():
    playlists = sp.current_user_playlists()
    playlist_list = []
    for playlist in playlists['items']:
        playlist_list.append({
            'name': playlist['name'],
            'id': playlist['id'],
            'track_count': playlist['tracks']['total'],
            'playlist_url': playlist['external_urls']['spotify']
        })
    return playlist_list

# Get tracks in a playlist
def get_playlist_tracks(playlist_id):
    results = sp.playlist_tracks(playlist_id)
    track_list = []
    for item in results['items']:
        track = item['track']
        track_list.append({
            'name': track['name'],
            'artist': track['artists'][0]['name'],
            'track_url': track['external_urls']['spotify'],
            'duration_ms': track['duration_ms']
        })
    return track_list