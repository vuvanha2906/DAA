from spotify_api import get_user_playlists, get_playlist_tracks, all_tracks
from greedy_recommend import greedy_recommendation
from dp_recommend import dp_recommendation
import streamlit as st



# Lấy danh sách playlist và bài hát trong playlist
st.title("🎵 Music Recommendation System")
playlists = get_user_playlists()
playlist_data = {}
for playlist in playlists:
    playlist_tracks = get_playlist_tracks(playlist['id'])
    playlist_data[playlist['id']] = [
        {
            'track_id': track.get('track_url', '').split('/')[-1],
            'track_name': track['name'],
            'artist_name': track['artist'],
            'features': next(
                (t['features'] for t in all_tracks if t['track_id'].split('/')[-1] == track.get('track_url', '').split('/')[-1] and 'features' in t),
                None
            )
        }
        for track in playlist_tracks
    ]

# Giao diện chọn playlist
playlist_names = [p['name'] for p in playlists]
selected_playlist_name = st.selectbox("🎧 Chọn playlist của bạn", playlist_names)
selected_playlist = next(p for p in playlists if p['name'] == selected_playlist_name)
selected_playlist_id = selected_playlist['id']
selected_playlist_tracks = playlist_data[selected_playlist_id]

# Lưu lịch sử đề xuất riêng cho từng playlist
if "history" not in st.session_state:
    st.session_state["history"] = {}
if selected_playlist_id not in st.session_state["history"]:
    st.session_state["history"][selected_playlist_id] = set()
recommended_ids = st.session_state["history"][selected_playlist_id]

# Các nút đề xuất
col1, col2 = st.columns(2)
with col1:
    if st.button("🔁 Đề xuất mới (Tham lam)"):
        recommendations = greedy_recommendation(selected_playlist_tracks, all_tracks, recommended_ids, top_n=5)
        if recommendations:
            st.subheader("🎯 Đề xuất (Tham lam)")
            for track in recommendations:
                st.markdown(f"- {track['track_name']} by {track['artist_name']} [🎧]({track['track_id']})")
                recommended_ids.add(track['track_id'])
        else:
            st.info("Không còn bài hát phù hợp để đề xuất.")

with col2:
    if st.button("🧠 Đề xuất mới (Quy hoạch động)"):
        recommendations = dp_recommendation(selected_playlist_tracks, all_tracks, recommended_ids, top_n=5)
        if recommendations:
            st.subheader("🎯 Đề xuất (Quy hoạch động)")
            for track in recommendations:
                st.markdown(f"- {track['track_name']} by {track['artist_name']} [🎧]({track['track_id']})")
                recommended_ids.add(track['track_id'])
        else:
            st.info("Không còn bài hát phù hợp để đề xuất.")

