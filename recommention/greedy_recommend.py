from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def greedy_recommendation(playlist_tracks, all_tracks, recommended_ids, top_n=10):
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

    playlist_authors = {
        a.strip().lower()
        for t in playlist_tracks
        for a in t.get('artist_name', '').split(',')
    }

    playlist_genres = {
        g.strip().lower()
        for t in playlist_tracks
        for g in (t.get('artist_genres', '').split(',') if isinstance(t.get('artist_genres'), str) else t.get('artist_genres', []))
    }

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

    delta = 3
    genre_bonus_per_match = 5
    scored_candidates = []

    for i, track in enumerate(candidates):
        popularity = track.get('track_popularity', 50)
        author_score = 0
        genre_score = 0

        author_names = [a.strip().lower() for a in track.get('artist_name', '').split(',')]
        for a in author_names:
            if a in playlist_authors:
                bonus = int((100 - popularity) // 10) * 10
                author_score += max(0, bonus)

        genres = (
            track.get('artist_genres', '').split(',') if isinstance(track.get('artist_genres'), str)
            else track.get('artist_genres', [])
        )
        for g in genres:
            if g.strip().lower() in playlist_genres:
                genre_score += genre_bonus_per_match

        similarity = similarities[i]
        total_score = author_score + genre_score + popularity + delta * similarity
        scored_candidates.append((total_score, track))

    scored_candidates.sort(key=lambda x: x[0], reverse=True)
    recommended = [{**track, 'score': round(score, 2)} for score, track in scored_candidates[:top_n]]
    return recommended

