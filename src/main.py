"""
Command line runner for the Music Recommender Simulation.

Loads data/songs.csv, scores every song against a user profile, and prints
the top recommendations with the reasons behind each score.

Run from the project root with: python -m src.main
"""

from src.recommender import load_songs, recommend_songs


MAX_SCORE = 6.0  # genre 2.0 + mood 1.0 + energy 1.5 + valence 1.0 + acoustic 0.5


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

    # Default "pop/happy" profile
    user_prefs = {
        "favorite_genre": "pop",
        "favorite_mood": "happy",
        "target_energy": 0.80,
        "target_valence": 0.80,
        "likes_acoustic": False,
    }

    recommendations = recommend_songs(user_prefs, songs, k=5)
    print_recommendations(user_prefs, recommendations)


if __name__ == "__main__":
    main()
