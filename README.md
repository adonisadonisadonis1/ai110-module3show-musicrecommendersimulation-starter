# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

Real platforms like Spotify and YouTube combine two approaches. **Collaborative filtering** learns
from the behavior of millions of users (plays, likes, skips, saves, shared playlists) and
recommends what similar listeners enjoyed. **Content-based filtering** describes each song by its
attributes (genre, mood, tempo, energy, valence) and recommends songs that resemble what you
already like. At scale, these signals feed a pipeline: generate a few thousand candidates, have a
model score each one by how likely you are to play or skip it, then re-rank the list for diversity
and freshness. My simulator has no other users, so it is purely **content-based**. It prioritizes
**genre** first (a stable, long-term taste), then how **close** a song's **energy** is to the
user's target, then **mood**. It rewards closeness rather than "more is better," so a calm
listener isn't flooded with gym tracks. Energy, tempo, and acousticness turned out to be almost
perfectly correlated in this dataset, so I use energy as the single intensity signal and avoid
counting the same thing three times. (Full research and data analysis:
[docs/phase1_notes.md](docs/phase1_notes.md).)

**`Song` features used**
- `genre` (categorical match)
- `mood` (categorical match)
- `energy` (0–1, closeness to target)
- `acousticness` (0–1, small bonus based on acoustic preference)
- `valence` (0–1, optional closeness for the happy↔sad axis)
- `id`, `title`, `artist` (identification and display; `artist` is used for an optional diversity rule)
- *Not scored:* `tempo_bpm` and `danceability` (redundant with energy in this catalog)

**`UserProfile` features**
- `favorite_genre`
- `favorite_mood`
- `target_energy` (0–1)
- `likes_acoustic` (bool)
- *(optional)* `target_valence` (0–1)

**Algorithm Recipe**

*Scoring Rule (one song):*
```
score  = 2.0  if genre matches
       + 1.0  if mood matches
       + 1.5 × (1 − |song.energy − target_energy|)
       + 0.5 × (acousticness if likes_acoustic else 1 − acousticness)
       [+ 1.0 × (1 − |song.valence − target_valence|)]   # optional
```
Each component also adds a human-readable reason, which is used for explanations.

*Ranking Rule (the list):* score every song, sort highest first (ties go to the smaller energy
gap), and return the top `k`. Optionally, cap each artist at one song for variety.

```
UserProfile ──┐
              ├─► score_song() for each Song ─► sort by score ─► top k + reasons
songs.csv ────┘
```

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Paste a sample of your recommender's output here as a text block so a reader can see what it produces:

```
# e.g.:
# User profile: genre=indie, mood=chill, energy=low
# Recommendations:
#   1. ...
#   2. ...
#   3. ...
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



