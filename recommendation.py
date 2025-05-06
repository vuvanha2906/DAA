from features_utils import add_features
from greedy_recommend import greedy_recommendation
from dp_recommend import dp_recommendation
from spotify_api import all_tracks, get_user_playlists, get_playlist_tracks


# Thêm đặc trưng
all_tracks = add_features(all_tracks)

# Chọn một playlist người dùng
playlists = get_user_playlists()
target_playlist = playlists[0]  # hoặc cho người dùng chọn
playlist_tracks = get_playlist_tracks(target_playlist['id'])

# Lấy track đầu tiên làm điểm bắt đầu
start_track_id = playlist_tracks[0]['track_url'].split('/')[-1]
start_track = next((t for t in all_tracks if t['track_id'].endswith(start_track_id)), None)

if start_track:
    print("\n🎯 [Greedy] Recommended Playlist:")
    greedy_result = greedy_recommendation(start_track, all_tracks, k=5)
    for t in greedy_result:
        print(f"- {t['track_name']} ({t['artist_name']})")

print("\n🧠 [Dynamic Programming] Recommended Playlist (under 15 mins):")
dp_result = dp_recommendation(all_tracks)
for t in dp_result:
    print(f"- {t['track_name']} ({t['artist_name']})")

