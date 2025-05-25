# 🎵 Smart Playlist Recommendation System

This project implements a **content-based music recommendation system** using two algorithmic strategies:

- **Greedy Algorithm** – Fast, intuitive ranking based on similarity and metadata.
- **Dynamic Programming (DP)** – Optimized selection with constraints (e.g., artist diversity).

The system generates **personalized track recommendations** given a playlist and a full track dataset (features, artist info, genres, popularity, etc.).

---

## 🚀 Features

- Content-based recommendation using cosine similarity.
- Integration of popularity, genre, and artist similarity.
- Two algorithmic strategies for comparison:
  - Greedy (fast, simple).
  - Dynamic Programming (optimized selection with constraints).
- Supports Spotify-style metadata (`features`, `track_id`, `artist_name`, `artist_genres`, etc.).

---

## 🛠️ Requirements

Install dependencies via `pip`:

```bash
pip install numpy scikit-learn
pip install spotipy Flask 
pip install spotipy
pip install streamlit 
```
## 📡 Spotify API Integration
🔐 Requirements
To enable live track feature extraction, you must:

  - Have a Spotify Premium account
  - Create a Spotify Developer App to get:
    - CLIENT_ID
    - CLIENT_SECRET
- Set up REDIRECT_URI (e.g., http://localhost:8888/callback)
- For more:
  - [Spotify Web API Docs](https://developer.spotify.com/documentation/web-api)
  - [Spotipy Python Library](https://spotipy.readthedocs.io/en/2.25.1/)
    
## 🙆‍♂️ Now run it to open the app!
Open interface.py on terminal and run:
```
$ streamlit run interface.py
```
This will open a browser window with the interface.

