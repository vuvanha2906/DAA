from sklearn.feature_extraction.text import CountVectorizer
import numpy as np

def preprocess_track(track):
    genres = " ".join(track['artist_genres']) if isinstance(track['artist_genres'], list) else ""
    text = f"{track['artist_name']} {genres}"
    return text.lower()


def add_features(tracks):
    vectorizer = CountVectorizer()

    # Dù có thiếu trường, ta vẫn tạo text (sẽ thành chuỗi rỗng nếu thiếu)
    text_features = [
        preprocess_track(t) if isinstance(t.get('artist_name'), str) else ""
        for t in tracks
    ]

    try:
        X = vectorizer.fit_transform(text_features).toarray()
    except ValueError:
        # Trường hợp tất cả text rỗng => không tạo được vector đặc trưng
        X = np.zeros((len(tracks), 1))

    popularity = np.array([t.get("track_popularity", 0) for t in tracks]).reshape(-1, 1)

    # Kích thước X và popularity có thể khác nếu X không được tạo đúng
    if X.shape[0] != popularity.shape[0]:
        X = np.zeros((len(tracks), 1))

    features = np.hstack((X, popularity))

    for i, t in enumerate(tracks):
        t["features"] = features[i] if i < len(features) else np.zeros(features.shape[1])

    return tracks

