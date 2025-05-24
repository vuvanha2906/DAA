import numpy as np
import matplotlib.pyplot as plt
import random
import time
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict

# ----------------------
# Tạo dữ liệu giả
# ----------------------
def generate_fake_track(i):
    return {
        'track_id': f"track_{i}",
        'features': np.random.rand(10).tolist(),
        'track_popularity': random.randint(0, 100),
        'artist_name': f"artist_{random.randint(1, 30)}",
        'artist_genres': ['pop', 'rock', 'jazz', 'hiphop'][random.randint(0, 3)]
    }

def generate_data(num_tracks):
    all_tracks = [generate_fake_track(i) for i in range(num_tracks)]
    playlist = random.sample(all_tracks, min(5, len(all_tracks)))
    recommended_ids = set()
    return playlist, all_tracks, recommended_ids

# ----------------------
# Hàm greedy
# ----------------------
def greedy_recommendation(playlist_tracks, all_tracks, recommended_ids, top_n=5):
    if not playlist_tracks:
        return []

    example_vector = next(
        (t['features'] for t in all_tracks if t.get('features') is not None),
        np.zeros(10)
    )

    playlist_vectors = [
        np.array(t['features']) if t.get('features') is not None else np.zeros_like(example_vector)
        for t in playlist_tracks
    ]
    playlist_mean = np.mean(playlist_vectors, axis=0).reshape(1, -1)

    playlist_authors = set()
    playlist_genres = set()
    for t in playlist_tracks:
        for a in t.get('artist_name', '').split(','):
            playlist_authors.add(a.strip().lower())
        genres = t.get('artist_genres', [])
        if isinstance(genres, str):
            genres = [g.strip() for g in genres.split(',')]
        for g in genres:
            playlist_genres.add(g.strip().lower())

    candidates = [
        t for t in all_tracks
        if t['track_id'] not in recommended_ids
        and t['track_id'] not in {pt['track_id'] for pt in playlist_tracks}
    ]

    delta = 3
    genre_bonus_per_match = 5
    scored_candidates = []

    for track in candidates:
        author_str = track.get('artist_name', '')
        popularity = track.get('track_popularity', 50)
        features = track.get('features')
        vector = np.array(features) if features is not None else np.zeros_like(example_vector)

        author_score = 0
        for a in author_str.split(','):
            artist_clean = a.strip().lower()
            if artist_clean in playlist_authors:
                bonus = int((100 - popularity) // 10) * 10
                author_score += max(0, bonus)

        genre_score = 0
        genres = track.get('artist_genres', [])
        if isinstance(genres, str):
            genres = [g.strip() for g in genres.split(',')]
        for g in genres:
            if g.strip().lower() in playlist_genres:
                genre_score += genre_bonus_per_match

        similarity = cosine_similarity(vector.reshape(1, -1), playlist_mean)[0][0]
        total_score = author_score + genre_score + popularity + delta * similarity
        scored_candidates.append((total_score, track))

    scored_candidates.sort(key=lambda x: x[0], reverse=True)
    recommended = [{**track, 'score': round(score, 2)} for score, track in scored_candidates[:top_n]]
    return recommended

# ----------------------
# Hàm quy hoạch động
# ----------------------
def dp_recommendation(playlist_tracks, all_tracks, recommended_ids, top_n=5):
    if not playlist_tracks:
        return []

    example_vector = next(
        (t['features'] for t in all_tracks if t.get('features') is not None),
        np.zeros(10)
    )

    playlist_vectors = [
        np.array(t['features']) if t.get('features') is not None else np.zeros_like(example_vector)
        for t in playlist_tracks
    ]
    playlist_mean = np.mean(playlist_vectors, axis=0).reshape(1, -1)

    playlist_authors = set()
    playlist_genres = set()
    for t in playlist_tracks:
        for a in t.get('artist_name', '').split(','):
            playlist_authors.add(a.strip().lower())
        genres = t.get('artist_genres', [])
        if isinstance(genres, str):
            genres = [g.strip() for g in genres.split(',')]
        for g in genres:
            playlist_genres.add(g.strip().lower())

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
        author_score = 0
        for a in t.get('artist_name', '').split(','):
            a_clean = a.strip().lower()
            if a_clean in playlist_authors:
                bonus = int((100 - popularity) // 10) * 10
                author_score += max(0, bonus)
        genre_score = 0
        genres = t.get('artist_genres', [])
        if isinstance(genres, str):
            genres = [g.strip() for g in genres.split(',')]
        for g in genres:
            if g.strip().lower() in playlist_genres:
                genre_score += 2
        t['score'] = round(author_score + genre_score + popularity + 3 * cosine_score, 2)

    n = len(candidates)
    dp = [[[] for _ in range(top_n + 1)] for _ in range(n + 1)]
    dp[0][0] = []

    for i in range(1, n + 1):
        track = candidates[i - 1]
        track_artists = [a.strip().lower() for a in track.get('artist_name', '').split(',')]

        for k in range(top_n + 1):
            dp[i][k] = list(dp[i - 1][k])
            if k > 0:
                prev_tracks = dp[i - 1][k - 1]
                artist_count = defaultdict(int)
                for t_prev in prev_tracks:
                    for a in t_prev.get('artist_name', '').split(','):
                        artist_count[a.strip().lower()] += 1
                if all(artist_count[a] < 4 for a in track_artists):
                    candidate_tracks = prev_tracks + [track]
                    prev_score = sum(t['score'] for t in dp[i][k])
                    new_score = sum(t['score'] for t in candidate_tracks)
                    if new_score > prev_score:
                        dp[i][k] = candidate_tracks
    return dp[n][top_n] if dp[n][top_n] else sorted(candidates, key=lambda x: x['score'], reverse=True)[:top_n]

# ----------------------
# Đo thời gian và vẽ biểu đồ
# ----------------------
greedy_times = []
dp_times = []
sizes = list(range(10, 1001, 100)) + [3000]

for size in sizes:
    playlist, all_tracks, recommended_ids = generate_data(size)

    start = time.time()
    greedy_recommendation(playlist, all_tracks, recommended_ids, top_n=10)
    greedy_times.append(time.time() - start)

    start = time.time()
    dp_recommendation(playlist, all_tracks, recommended_ids, top_n=10)
    dp_times.append(time.time() - start)

# ----------------------
# Vẽ biểu đồ
# ----------------------
plt.figure(figsize=(10, 6))
plt.plot(sizes, greedy_times, label='Greedy', marker='o')
plt.plot(sizes, dp_times, label='Dynamic Programming', marker='s')
plt.xlabel("Số lượng bài hát")
plt.ylabel("Thời gian chạy (s)")
plt.title("So sánh thời gian chạy: Greedy vs Dynamic Programming")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
