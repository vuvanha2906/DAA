from collections import defaultdict
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def dp_recommendation(playlist_tracks, all_tracks, recommended_ids, top_n=10):
    if not playlist_tracks:
        return []

    # Vector mẫu
    example_vector = next(
        (t['features'] for t in all_tracks if t.get('features') is not None),
        np.zeros(10)
    )

    # Trung bình vector playlist
    playlist_vectors = [
        np.array(t['features']) if t.get('features') is not None else np.zeros_like(example_vector)
        for t in playlist_tracks
    ]
    playlist_mean = np.mean(playlist_vectors, axis=0).reshape(1, -1)

    # Nghệ sĩ trong playlist
    playlist_authors = set()
    for t in playlist_tracks:
        for a in t.get('artist_name', '').split(','):
            playlist_authors.add(a.strip().lower())

    # Thể loại trong playlist
    playlist_genres = set()
    for t in playlist_tracks:
        genres = t.get('artist_genres', [])
        if isinstance(genres, str):
            genres = [g.strip() for g in genres.split(',')]
        for g in genres:
            playlist_genres.add(g.strip().lower())

    # Các bài chưa có trong playlist
    candidates = [
        t for t in all_tracks
        if t['track_id'] not in recommended_ids
        and t['track_id'] not in {pt['track_id'] for pt in playlist_tracks}
    ]

    if not candidates:
        return []

    candidate_vectors = [
        np.array(t['features']) if t.get('features') is not None else np.zeros_like(example_vector)
        for t in candidates
    ]
    similarities = cosine_similarity(candidate_vectors, playlist_mean).flatten()

    for i, t in enumerate(candidates):
        cosine_score = similarities[i]
        popularity = t.get('track_popularity', 50)

        # Tính điểm tác giả
        author_score = 0
        for a in t.get('artist_name', '').split(','):
            a_clean = a.strip().lower()
            if a_clean in playlist_authors:
                bonus = int((100 - popularity) // 10) * 10
                author_score += max(0, bonus)

        # Tính điểm thể loại
        genre_score = 0
        genres = t.get('artist_genres', [])
        if isinstance(genres, str):
            genres = [g.strip() for g in genres.split(',')]
        for g in genres:
            if g.strip().lower() in playlist_genres:
                genre_score += 2

        # Tổng điểm
        t['score'] = round(author_score + genre_score + popularity + 3 * cosine_score, 2)

    # Bắt đầu DP để chọn top_n bài không quá 4 bài cho mỗi nghệ sĩ
    n = len(candidates)
    dp = [[[] for _ in range(top_n + 1)] for _ in range(n + 1)]
    dp[0][0] = []

    for i in range(1, n + 1):
        track = candidates[i - 1]
        track_artists = [a.strip().lower() for a in track.get('artist_name', '').split(',')]

        for k in range(top_n + 1):
            # Không chọn bài hiện tại
            dp[i][k] = list(dp[i - 1][k])

            if k > 0:
                prev_tracks = dp[i - 1][k - 1]

                # Đếm số bài hát của mỗi nghệ sĩ trong phương án hiện tại
                artist_count = defaultdict(int)
                for t_prev in prev_tracks:
                    for a in t_prev.get('artist_name', '').split(','):
                        artist_count[a.strip().lower()] += 1

                # Kiểm tra nếu thêm bài mới có vượt quá 2 bài/ nghệ sĩ
                if all(artist_count[a] < 4 for a in track_artists):
                    candidate_tracks = prev_tracks + [track]
                    prev_score = sum(t['score'] for t in dp[i][k])
                    new_score = sum(t['score'] for t in candidate_tracks)

                    if new_score > prev_score:
                        dp[i][k] = candidate_tracks

    # Kết quả cuối cùng
    return dp[n][top_n] if dp[n][top_n] else sorted(candidates, key=lambda x: x['score'], reverse=True)[:top_n]
