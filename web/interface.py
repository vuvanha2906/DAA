from spotify_api import get_user_playlists, get_playlist_tracks, all_tracks
from Final.recommention.greedy_recommend import greedy_recommendation
from Final.recommention.dp_recommend import dp_recommendation
import streamlit as st

# Giao diện chính
st.title("🎵 Music Recommendation System")

# Lấy danh sách playlist và bài hát
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
                (t['features'] for t in all_tracks if
                 t['track_id'].split('/')[-1] == track.get('track_url', '').split('/')[-1] and 'features' in t),
                None
            ),
            'author': track['name'],
            'genre': track.get('genre', 'unknown'),  # giả sử bạn có 'genre'
            'popularity': track.get('popularity', 50)  # mặc định nếu không có
        }
        for track in playlist_tracks
    ]

# Chọn playlist
playlist_names = [p['name'] for p in playlists]
selected_playlist_name = st.selectbox("🎧 Chọn playlist của bạn", playlist_names)
selected_playlist = next(p for p in playlists if p['name'] == selected_playlist_name)
selected_playlist_id = selected_playlist['id']
selected_playlist_tracks = playlist_data[selected_playlist_id]

# Chọn 1 bài hát trong playlist
track_options = [f"{t['track_name']} by {t['artist_name']}" for t in selected_playlist_tracks]
selected_track_option = st.selectbox("🎼 Chọn 1 bài hát bạn thích", track_options)
selected_track_index = track_options.index(selected_track_option)
selected_track = selected_playlist_tracks[selected_track_index]

# Lưu lịch sử đề xuất cho từng playlist
if "history" not in st.session_state:
    st.session_state["history"] = {}
if selected_playlist_id not in st.session_state["history"]:
    st.session_state["history"][selected_playlist_id] = set()
recommended_ids = st.session_state["history"][selected_playlist_id]

# Hai nút đề xuất
col1, col2 = st.columns(2)

with col1:
    if st.button("🔁 Gợi ý (Tham lam)"):
        recommendations = greedy_recommendation([selected_track], all_tracks, recommended_ids, top_n=10)
        if recommendations:
            st.subheader("🎯 Gợi ý (Tham lam)")
            for track in recommendations:
                st.markdown(
                    f"- {track['track_name']} by {track['artist_name']} "
                    f"(⭐ Score: `{track['score']}`) [🎧]({track['track_id']})"
                )
                recommended_ids.add(track['track_id'])

        else:
            st.info("Không còn bài hát phù hợp để gợi ý.")

with col2:
    if st.button("🧠 Gợi ý (Quy hoạch động)"):
        recommendations = dp_recommendation([selected_track], all_tracks, recommended_ids, top_n=10)
        if recommendations:
            st.subheader("🎯 Gợi ý (Quy hoạch động)")
            for track in recommendations:
                st.markdown(
                    f"- {track['track_name']} by {track['artist_name']} "
                    f"(⭐ Score: `{track['score']}`) [🎧]({track['track_id']})"
                )
                recommended_ids.add(track['track_id'])
        else:
            st.info("Không còn bài hát phù hợp để gợi ý.")

with st.expander("⚙️ Tuỳ chọn khác"):
    if st.button("🔄 Reset đề xuất"):
        st.session_state["history"][selected_playlist_id] = set()
        st.success("Đã đặt lại lịch sử đề xuất cho playlist này.")
