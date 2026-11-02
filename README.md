# 🎵 Music Recommender Simulation

## Project Summary

**VibeCheck 1.0** is a small, content-based music recommender that runs in the terminal. It
loads a 20-song catalog from `data/songs.csv`, scores every song against a user's taste profile
(favorite genre and mood, target energy and valence, acoustic preference), and prints the top 5
songs. Each song comes with a score out of 6 and a list of reasons showing where every point
came from. The CLI runs seven profiles, three typical and four adversarial, to show both where
the scoring works and where it can be tricked. The [Model Card](model_card.md) documents how it
works, how it was evaluated, and its biases.

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
   python3 -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows
   ```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the tests from the project root with:

```bash
pytest
```

`pytest.ini` adds the project root to the import path so the tests can import `src`.

---

## Sample Recommendation Output

Output of `python -m src.main` for the first profile, "High-Energy Pop" (pop/happy). The CLI
now runs seven profiles; all of their outputs are in [model_card.md](model_card.md#7-evaluation).

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

- **Weight shift (energy ×2, genre ×½):** I temporarily changed energy from 1.5 to 3.0 and genre
  from 2.0 to 1.0. *Rooftop Lights* (happy indie pop) moved above *Gym Hero* for the pop fan, and
  a loud metal song replaced a quiet folk song at #1 for the "Sad Banger" profile. Both changes
  were more accurate. Chill Lofi didn't change at all. The downside was that scores bunched
  together and genre almost stopped mattering, so I kept the original weights.
- **Adding valence:** energy alone couldn't tell an angry metal song from a euphoric EDM song
  (both are about 0.95 energy). Adding valence as a 0–1 "closer is better" feature separated
  them.
- **Different user types:** opposite profiles (Chill Lofi vs. Deep Intense Rock) share no songs.
  Adversarial profiles exposed problems. Matching labels beat a big energy mismatch, a genre not
  in the catalog gave low, nearly tied scores with no warning, and *Gym Hero* and
  *Concrete Crown* showed up in 4 of 7 lists.

Full outputs and comparisons: [model_card.md, section 7](model_card.md#7-evaluation).

---

## Limitations and Risks

- **Tiny, hand-labeled catalog:** 20 made-up songs, most genres with only one song, and every
  label chosen by one person.
- **Labels can outvote sound:** exact genre and mood matches are worth 3 points, enough to rank
  a quiet song first for someone asking for loud music.
- **Exact text matching:** "indie pop" gets no credit from a "pop" fan, and unknown genres
  (k-pop) fail silently.
- **No understanding of lyrics, language, vocals, or era**, and no learning from skips or replays.
- **Filter bubbles:** a fan of a one-song genre gets the same #1 every time.

More detail in [model_card.md, section 6](model_card.md#6-limitations-and-bias).

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

<!-- DRAFT written with my AI assistant: rewrite in your own words before submitting, then delete this comment. -->

**How recommenders turn data into predictions:** A recommender doesn't "understand" music. It
turns each song into a few numbers and labels, turns my taste into targets, and adds up points
for how well they match. Then it sorts. What surprised me is how much that simple loop can feel
like a real recommendation: the Chill Lofi list looked like a playlist I'd actually make. The
weights are where the "opinions" live. Changing genre from 2.0 to 1.0 and doubling energy
reshuffled several top-5 lists without any other code change.

**Where bias and unfairness show up:** Bias came from both the data and the rules. The data
has only one song for most genres, and one person chose every label, so a metal fan always gets
the same single metal song. The rules reward exact label matches, so a song labeled "indie pop"
gets nothing from a "pop" fan, and a K-Pop fan gets no matches at all, while the output still
looks just as confident. Real apps have the same risks at a much bigger scale: whoever writes
the labels and picks the weights decides whose taste counts. More details are in the
[Model Card](model_card.md), sections 6 and 9.
