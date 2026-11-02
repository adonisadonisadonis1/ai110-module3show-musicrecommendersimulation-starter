"""
Command line runner for the Music Recommender Simulation.

Loads data/songs.csv, scores every song against a user profile, and prints
the top recommendations with the reasons behind each score.

Run from the project root with: python -m src.main
"""

from src.recommender import (
    ACOUSTIC_WEIGHT,
    ENERGY_WEIGHT,
    GENRE_WEIGHT,
    MOOD_WEIGHT,
    VALENCE_WEIGHT,
    load_songs,
    recommend_songs,
)

MAX_SCORE = GENRE_WEIGHT + MOOD_WEIGHT + ENERGY_WEIGHT + VALENCE_WEIGHT + ACOUSTIC_WEIGHT

# Three typical listeners, then adversarial profiles meant to trick the scoring logic.
PROFILES = {
    "High-Energy Pop": {
        "favorite_genre": "pop",
        "favorite_mood": "happy",
        "target_energy": 0.80,
        "target_valence": 0.80,
        "likes_acoustic": False,
    },
    "Chill Lofi": {
        "favorite_genre": "lofi",
        "favorite_mood": "chill",
        "target_energy": 0.40,
        "target_valence": 0.60,
        "likes_acoustic": True,
    },
    "Deep Intense Rock": {
        "favorite_genre": "rock",
        "favorite_mood": "intense",
        "target_energy": 0.90,
        "target_valence": 0.40,
        "likes_acoustic": False,
    },
    # Adversarial: labels point one way (calm sad folk), numbers point the other (loud and dark).
    "Sad Banger (conflicting)": {
        "favorite_genre": "folk",
        "favorite_mood": "sad",
        "target_energy": 0.90,
        "target_valence": 0.20,
        "likes_acoustic": False,
    },
    # Adversarial: a genre and mood that do not exist in the catalog.
    "K-Pop Fan (missing genre)": {
        "favorite_genre": "k-pop",
        "favorite_mood": "hype",
        "target_energy": 0.85,
        "target_valence": 0.85,
        "likes_acoustic": False,
    },
    # Adversarial: metal fan who also prefers acoustic sound (no metal song is acoustic).
    "Acoustic Headbanger": {
        "favorite_genre": "metal",
        "favorite_mood": "angry",
        "target_energy": 0.95,
        "target_valence": 0.25,
        "likes_acoustic": True,
    },
    # Adversarial: no genre, mood, or acoustic preference; every number in the middle.
    "Dead Center (no labels)": {
        "target_energy": 0.50,
        "target_valence": 0.50,
    },
}


def print_recommendations(user_prefs: dict, recommendations: list) -> None:
    """Print the user profile and a numbered, explained list of recommendations."""
    profile = ", ".join(f"{key}={value}" for key, value in user_prefs.items())
    print("=" * 64)
    print(f"User profile: {profile}")
    print("=" * 64)
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"\n{rank}. {song['title']} by {song['artist']}  [{song['genre']} / {song['mood']}]")
        print(f"   Score: {score:.2f} / {MAX_SCORE:.2f}")
        print("   Because:")
        for reason in explanation.split("; "):
            print(f"     - {reason}")
    print()


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    for name, user_prefs in PROFILES.items():
        print(f"\n### {name}")
        recommendations = recommend_songs(user_prefs, songs, k=5)
        print_recommendations(user_prefs, recommendations)


if __name__ == "__main__":
    main()
