from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def greedy_recommendation(playlist_tracks, all_tracks, recommended_ids, top_n=5):
    if not playlist_tracks:
        return []

    # Đảm bảo tất cả track đều có features, nếu không thì thay bằng vector 0
    example_vector = next(
        (t['features'] for t in all_tracks if t.get('features') is not None),
        np.zeros(10)  # giả sử 10 chiều, bạn có thể thay bằng số chiều thực tế
    )

    playlist_vectors = [
        np.array(t['features']) if t.get('features') is not None else np.zeros_like(example_vector)
        for t in playlist_tracks
    ]

    playlist_mean = np.mean(playlist_vectors, axis=0).reshape(1, -1)

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

    sims = cosine_similarity(candidate_vectors, playlist_mean).flatten()

    top_indices = np.argsort(sims)[-top_n:][::-1]
    recommended = [candidates[i] for i in top_indices]

    return recommended
