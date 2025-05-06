import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd

# Cấu hình Spotify API
client_id = "your client id"  # Thay bằng client_id của bạn
client_secret = "your client secret"  # Thay bằng client_secret của bạn

# Xác thực API
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))


def extract_playlist_data(playlist_url):
    playlist_id = playlist_url.split("playlist/")[-1].split("?")[0]
    results = sp.playlist_tracks(playlist_id)

    data = []

    for item in results["items"]:
        track = item["track"]
        if not track:
            continue

        # Trích xuất thông tin cần thiết
        track_id = track.get("id", None)
        track_name = track.get("name", None)
        track_popularity = track.get("popularity", None)
        artists = track.get("artists", [])
        artist_name = ", ".join([artist.get("name", "") for artist in artists])
        artist_id = artists[0].get("id", None) if artists else None

        # Lấy thông tin về nghệ sĩ
        artist_info = sp.artist(artist_id) if artist_id else {}
        artist_genres = artist_info.get("genres", [])
        artist_popularity = artist_info.get("popularity", None)

        # Append dữ liệu
        data.append({
            "playlist_url": playlist_url,
            "year":None,
            "track_id": track_id,
            "track_name": track_name,
            "track_popularity": track_popularity,
            "album": None,
            "artist_id":None,
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

    return data


# Playlist URL
playlist_url = " "

# Trích xuất dữ liệu
playlist_data = extract_playlist_data(playlist_url)

# Tạo DataFrame và lưu thành file CSV
df = pd.DataFrame(playlist_data)
df.to_csv("your path", index=False)
print("Dữ liệu đã được lưu vào playlist_data.csv")
