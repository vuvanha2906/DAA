from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def dp_recommendation(playlist_tracks, all_tracks, recommended_ids, top_n=5):
    if not playlist_tracks:
        return []

    # Lấy vector mẫu (nếu tất cả bị thiếu, mặc định vector 10 chiều)
    example_vector = next(
        (t['features'] for t in all_tracks if t.get('features') is not None),
        np.zeros(10)
    )

    # Đảm bảo mọi track đều có vector hợp lệ
    playlist_vectors = [
        np.array(t['features']) if t.get('features') is not None else np.zeros_like(example_vector)
        for t in playlist_tracks
    ]

    playlist_mean = np.mean(playlist_vectors, axis=0).reshape(1, -1)

    # Lọc các bài hát hợp lệ (không bị trùng)
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
        t['score'] = similarities[i]

    candidates.sort(key=lambda x: x['score'], reverse=True)
    return candidates[:top_n]
