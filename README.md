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
listener isn't flooded with gym tracks. (Phase 1 research and data analysis:
[docs/phase1_notes.md](docs/phase1_notes.md).)

### The data: `data/songs.csv`

The starter catalog had 10 songs in 7 genres. I added 10 more (ids 11–20) to cover genres and
moods that were missing: hip hop, metal, classical, country, r&b, reggae, edm, folk, latin, and
electronic, with moods like *angry*, *sad*, *romantic*, *nostalgic*, *euphoric*, and *melancholic*.
The catalog now has **20 songs, 17 genres, and 16 moods**. A few songs were added on purpose to
break patterns in the starter data:
- *Flamenco Fire* is high-energy **and** acoustic.
- *Grey Window* is low-energy **and** electronic.
- *Iron Cathedral* (metal) and *Laser Tide* (edm) have similar energy but opposite valence.

In the original 10 songs, energy and acousticness were almost the same signal (r = −0.99). In the
expanded set the correlation is −0.76, so acousticness now adds real information.

**`Song` features used**
- `genre`: categorical, exact match
- `mood`: categorical, exact match
- `energy`: 0–1, scored by closeness to the target
- `valence`: 0–1, scored by closeness to the target (the happy↔sad axis)
- `acousticness`: 0–1, small bonus based on acoustic preference
- `id`, `title`, `artist`: for identification and display
- *Not scored:* `tempo_bpm` and `danceability`. Both track energy closely (r = 0.90 for tempo),
  so scoring them would double-count intensity.

### The user profile

My design example is a "late-night study" listener. (The CLI in `src/main.py` runs the
starter "pop/happy" profile by default; see Sample Recommendation Output below.)

```python
user_prefs = {
    "favorite_genre": "lofi",
    "favorite_mood": "chill",
    "target_energy": 0.40,   # calm, but not asleep
    "target_valence": 0.60,  # slightly positive
    "likes_acoustic": True,
}
```

**Profile critique: can it tell "intense rock" from "chill lofi"?** Yes. I ran the draft recipe
against this profile and a contrasting "workout" profile (`rock`, `intense`, energy 0.90,
valence 0.50, not acoustic):

| Profile | *Library Rain* (lofi) | *Storm Runner* (rock) | Gap |
|---|---:|---:|---:|
| Study (lofi/chill) | **5.85** | 1.67 | 4.18 |
| Workout (rock/intense) | 1.65 | **5.92** | 4.27 |

Energy alone separates them (0.35 vs. 0.91), and genre and mood widen the gap. Weaknesses of
the profile:
- **One favorite genre is narrow.** With only 1–3 songs per genre, the genre bonus helps
  at most a couple of songs. After those, the ranking is decided by the numeric features.
- **Exact string matching.** `indie pop` gets no credit from a `pop` fan, and `chill`,
  `relaxed`, and `peaceful` count as three unrelated moods.
- **A single target energy assumes one vibe.** It can't express "chill *or* hype, but nothing in
  between."

For this simulation I'm keeping one genre and one mood (simple, and it matches the `UserProfile`
class the tests use). I'm adding `target_valence` because it's the only feature that separates
dark from bright songs at the same energy.

### Algorithm Recipe (final)

**Scoring Rule** (judges one song, maximum 6.0 points):

| Component | Points | How |
|---|---|---|
| Genre match | **+2.0** | `song.genre == favorite_genre` |
| Mood match | **+1.0** | `song.mood == favorite_mood` |
| Energy closeness | **0 – 1.5** | `1.5 × (1 − \|song.energy − target_energy\|)` |
| Valence closeness | **0 – 1.0** | `1.0 × (1 − \|song.valence − target_valence\|)` |
| Acoustic fit | **0 – 0.5** | `0.5 × acousticness` if `likes_acoustic`, else `0.5 × (1 − acousticness)` |

Closeness scoring (`1 − |difference|`) rewards songs *near* the target. It doesn't reward
"higher" or "lower" values. Each component also records a reason (for example,
`"genre match (+2.0)"`) so every recommendation can explain itself.

**Why these weights:**
- **Genre (2.0) beats mood (1.0).** Genre is a long-term preference, while mood changes hour to
  hour. Mood is also partly captured by energy and valence already, so a full 2.0 for mood would
  double-count it.
- **The numeric features together (up to 3.0) can outweigh a genre match.** A song with the
  perfect energy and valence from a different genre can beat a same-genre song with the wrong
  feel. Without this, genre would decide everything.
- **Acousticness is a tiebreaker (0.5).** It's a texture preference, not the core of the vibe.

**Ranking Rule** (works on the whole list):
1. Score every song in the catalog.
2. Sort from highest to lowest score. Break ties by the smaller energy gap.
3. Return the top `k` (default 5), each with its score and reasons.

### Data flow

```
INPUT                      PROCESS (the loop)                        OUTPUT (the ranking)
─────                      ──────────────────                        ────────────────────
user_prefs  ─┐
             ├─► for each song in songs.csv:                ─►  sort all (song, score)
songs.csv   ─┘      genre match?        +2.0                     high → low
 (20 rows)          mood match?         +1.0                          │
                    energy closeness    0–1.5                         ▼
                    valence closeness   0–1.0                    top k songs
                    acoustic fit        0–0.5                    + score + "because…"
                    → (song, score, reasons)
```

Example: *Midnight Coding* (lofi, chill, energy 0.42) for the study profile scores
2.0 + 1.0 + 1.47 + 0.96 + 0.36 = **5.79** and ranks 2nd.

### Expected biases and limitations
- **Genre over-prioritization.** In a test with a contradictory profile (`classical`, but energy
  0.90), the only classical song (energy 0.18) still ranked 3rd on the genre bonus alone, ahead
  of high-energy songs that fit the requested vibe better.
- **Sparse labels.** Most genres and moods appear once, so many users get only 0–1 genre or mood
  matches. Results then fall back to the numeric features.
- **Exact-match labels miss near-synonyms** (`pop` vs. `indie pop`, `chill` vs. `relaxed`),
  which favors users whose tastes use the same words as the catalog.
- **Catalog bias.** The dataset is small, and the 10 songs I added reflect my own idea of each
  genre (for example, all metal is "angry"). The recommender can only be as diverse as the CSV.
- **No feedback loop.** Unlike real systems, it never learns from skips or replays, so a bad
  recommendation stays bad.

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

Output of `python -m src.main` with the default "pop/happy" profile:

```
Loaded songs: 20
================================================================
User profile: favorite_genre=pop, favorite_mood=happy, target_energy=0.8, target_valence=0.8, likes_acoustic=False
================================================================

1. Sunrise City by Neon Echo  [pop / happy]
   Score: 5.84 / 6.00
   Because:
     - genre match: pop (+2.0)
     - mood match: happy (+1.0)
     - energy 0.82 vs your 0.80 (+1.47)
     - valence 0.84 vs your 0.80 (+0.96)
     - non-acoustic fit, acousticness 0.18 (+0.41)

2. Gym Hero by Max Pulse  [pop / intense]
   Score: 4.75 / 6.00
   Because:
     - genre match: pop (+2.0)
     - energy 0.93 vs your 0.80 (+1.30)
     - valence 0.77 vs your 0.80 (+0.97)
     - non-acoustic fit, acousticness 0.05 (+0.47)

3. Rooftop Lights by Indigo Parade  [indie pop / happy]
   Score: 3.75 / 6.00
   Because:
     - mood match: happy (+1.0)
     - energy 0.76 vs your 0.80 (+1.44)
     - valence 0.81 vs your 0.80 (+0.99)
     - non-acoustic fit, acousticness 0.35 (+0.33)

4. Laser Tide by Pulsewave  [edm / euphoric]
   Score: 2.77 / 6.00
   Because:
     - energy 0.95 vs your 0.80 (+1.28)
     - valence 0.80 vs your 0.80 (+1.00)
     - non-acoustic fit, acousticness 0.02 (+0.49)

5. Concrete Crown by Kilo Verse  [hip hop / confident]
   Score: 2.75 / 6.00
   Because:
     - energy 0.78 vs your 0.80 (+1.47)
     - valence 0.62 vs your 0.80 (+0.82)
     - non-acoustic fit, acousticness 0.08 (+0.46)
```

These results match what I expected. *Sunrise City* matches on everything. *Gym Hero* comes 2nd
on the genre bonus even though its mood is "intense." *Rooftop Lights* is a happy song with
almost perfect energy, but it ranks 3rd because `indie pop` doesn't exactly match `pop`. That's
the exact-match bias noted above. Positions 4–5 have no label matches, so they are decided only
by energy, valence, and acousticness.

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



