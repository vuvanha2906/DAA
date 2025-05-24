from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def greedy_recommendation(playlist_tracks, all_tracks, recommended_ids, top_n=5):
    if not playlist_tracks:
        return []

    # Vector mẫu
    example_vector = next(
        (t['features'] for t in all_tracks if t.get('features') is not None),
        np.zeros(10)
    )

    # Vector trung bình của playlist
    playlist_vectors = [
        np.array(t['features']) if t.get('features') is not None else np.zeros_like(example_vector)
        for t in playlist_tracks
    ]
    playlist_mean = np.mean(playlist_vectors, axis=0).reshape(1, -1)

    # Nghệ sĩ trong playlist
    playlist_authors = set()
    for t in playlist_tracks:
        artists = t.get('artist_name', '')
        for a in artists.split(','):
            playlist_authors.add(a.strip().lower())

    # Thể loại trong playlist
    playlist_genres = set()
    for t in playlist_tracks:
        genres = t.get('artist_genres', [])
        if isinstance(genres, str):
            genres = [g.strip() for g in genres.split(',')]
        for g in genres:
            playlist_genres.add(g.strip().lower())

    # Ứng viên hợp lệ
    candidates = [
        t for t in all_tracks
        if t['track_id'] not in recommended_ids
        and t['track_id'] not in {pt['track_id'] for pt in playlist_tracks}
    ]

    if not candidates:
        return []

    # Trọng số cosine và genre
    delta = 3   # cosine similarity
    genre_bonus_per_match = 5

    scored_candidates = []

    for track in candidates:
        author_str = track.get('artist_name', '')
        popularity = track.get('track_popularity', 50)
        features = track.get('features')
        vector = np.array(features) if features is not None else np.zeros_like(example_vector)

        # 🎤 Điểm nghệ sĩ dựa theo mức độ phổ biến
        author_score = 0
        for i, a in enumerate(author_str.split(',')):
            artist_clean = a.strip().lower()
            if artist_clean in playlist_authors:
                # Nếu nghệ sĩ trùng → tính điểm theo popularity
                bonus = int((100 - popularity) // 10) * 10
                bonus = max(0, bonus)  # không để âm
                author_score += bonus

        # 🎼 Điểm thể loại
        genre_score = 0
        genres = track.get('artist_genres', [])
        if isinstance(genres, str):
            genres = [g.strip() for g in genres.split(',')]
        for g in genres:
            if g.strip().lower() in playlist_genres:
                genre_score += genre_bonus_per_match

        # 🎯 Cosine similarity
        similarity = cosine_similarity(vector.reshape(1, -1), playlist_mean)[0][0]

        total_score = author_score + genre_score + popularity + delta * similarity

        scored_candidates.append((total_score, track))

    # Sắp xếp và trả kết quả
    scored_candidates.sort(key=lambda x: x[0], reverse=True)

    recommended = [
        {**track, 'score': round(score, 2)}
        for score, track in scored_candidates[:top_n]
    ]

    return recommended
