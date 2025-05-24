import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd

# Thiết lập thông tin OAuth
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id="your id",
    client_secret="your secret",
    redirect_uri="http://127.0.0.1:8888/callback",
    scope="playlist-read-private playlist-read-collaborative"
))


def extract_playlist_data(playlist_url):
    playlist_id = playlist_url.split("playlist/")[-1].split("?")[0]

    data = []
    offset = 0
    limit = 100

    while True:
        results = sp.playlist_tracks(playlist_id, limit=limit, offset=offset)
        items = results.get("items", [])

        if not items:
            break  # Không còn bài nào nữa

        for item in items:
            track = item.get("track")
            if not track:
                continue

            track_id = track.get("id")
            track_name = track.get("name")
            track_popularity = track.get("popularity")
            artists = track.get("artists", [])
            artist_name = ", ".join([artist.get("name", "") for artist in artists])
            artist_id = artists[0].get("id", None) if artists else None

            # Lấy thông tin về nghệ sĩ
            artist_info = sp.artist(artist_id) if artist_id else {}
            artist_genres = artist_info.get("genres", [])
            artist_popularity = artist_info.get("popularity", None)

            data.append({
                "playlist_url": playlist_url,
                "year": None,
                "track_id": track_id,
                "track_name": track_name,
                "track_popularity": track_popularity,
                "album": None,
                "artist_id": artist_id,
                "artist_name": artist_name,
                "artist_genres": artist_genres,
                "artist_popularity": artist_popularity,
                "danceability": None,
                "energy": None,
                "key": None,
                "loudness": None,
                "mode": None,
                "speechiness": None,
                "acousticness": None,
                "instrumentalness": None,
                "liveness": None,
                "valence": None,
                "tempo": None,
                "duration_ms": None,
                "time_signature": None
            })

        offset += limit  # Tăng offset để lấy trang tiếp theo
        if offset >= results.get("total", 0):
            break  # Nếu đã lấy hết

    return data


playlist_url = "https://open.spotify.com/playlist/5psHmONFRLGATbI8imJB08?si=7tEMZTIcRXKhvMPZNiCj0Q&pi=D3DcI24uRzOnT&nd=1&dlsi=595e49ce21b040bf"  # (bạn thay URL)

# Lấy dữ liệu
playlist_data = extract_playlist_data(playlist_url)

# Lưu vào CSV
df = pd.DataFrame(playlist_data)
df.to_csv("playlist_data.csv", index=False)
print("Dữ liệu đã được lưu vào playlist_data.csv")
