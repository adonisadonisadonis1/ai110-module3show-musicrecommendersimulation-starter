# Phase 1 Notes: Understanding the Problem

> These are my Phase 1 notes, written before the dataset was expanded and before the recipe was
> finalized. The final recipe (adds valence, max 6.0 points) is in the README under
> "Algorithm Recipe (final)".

## Step 1: How real platforms recommend

**Prompt used:**
> How do platforms like Spotify and YouTube predict what a user will love next? Explain the
> difference between collaborative filtering (using other users' behavior) and content-based
> filtering (using song attributes), and list the main data types each one relies on.

### Collaborative filtering ("people like you also liked…")
- Ignores what a song *is* and looks only at who interacts with it.
- Builds a huge user × item matrix (plays, likes, skips, saves) and finds patterns: if users A
  and B overlap heavily, recommend A's songs to B. Modern versions learn **embeddings**
  (vectors) for users and songs via matrix factorization or neural networks, so "taste" is a
  point in space and songs near it are good bets.
- Spotify also mines **playlists**: songs that appear together on millions of user playlists are
  treated as similar (word2vec-style co-occurrence).
- **Strength:** finds surprising connections no metadata would reveal.
- **Weakness:** *cold start*. A brand-new song or user has no history. It also has popularity
  bias, because tracks that are already popular get recommended more and stay popular.

### Content-based filtering ("this song sounds like what you play")
- Describes each item by its attributes, builds a profile of what the user likes, and recommends
  items whose attributes match.
- Spotify gets attributes from audio analysis (energy, tempo, valence, danceability,
  acousticness), from NLP on lyrics, blogs, and reviews, and from editorial tags (genre, mood).
- **Strength:** works for new songs with zero plays, and it's easy to explain ("because it's
  upbeat pop").
- **Weakness:** filter bubble. It only recommends more of the same and can't find a jazz track
  that a rock fan would secretly love.

### In practice: hybrid + ranking pipeline
Real systems run in stages:
1. **Candidate generation.** Pull a few thousand songs from millions using collaborative and
   content signals.
2. **Scoring/ranking.** A model predicts the chance the user plays, saves, or skips each one.
3. **Re-ranking.** Apply business rules: diversity, freshness, no repeated artists, and mixing
   in some exploration.

### Main data types
| Kind | Examples | Used by |
|---|---|---|
| Explicit feedback | likes/hearts, thumbs down, follows, saves | Collaborative |
| Implicit feedback | plays, **skips** (especially < 30 s), replays, listen duration, search queries | Collaborative |
| Context | time of day, device, playlist currently open, location | Both |
| Co-occurrence | songs sharing playlists or listening sessions | Collaborative |
| Audio features | tempo, energy, valence, danceability, acousticness, loudness | Content |
| Metadata/tags | genre, **mood**, artist, release year, language | Content |
| Text | lyrics, reviews, blog descriptions | Content |

Implicit signals far outnumber explicit ones. A skip is one of the strongest negative signals a
platform has.

**Our simulator has no other users, so it will be purely content-based.**

---

## Step 2: Key features in `data/songs.csv`

10 songs, columns: `genre, mood, energy, tempo_bpm, valence, danceability, acousticness`.

Correlations between the numeric features (computed with pandas):

|              | energy | tempo | valence | dance | acoustic |
|--------------|-------:|------:|--------:|------:|---------:|
| energy       | 1.00 | 0.96 | 0.19 | 0.86 | **-0.99** |
| tempo_bpm    | 0.96 | 1.00 | 0.13 | 0.76 | -0.92 |
| valence      | 0.19 | 0.13 | 1.00 | 0.42 | -0.14 |

What this means:
- **Energy, tempo, and acousticness are basically one axis** in this catalog (calm and acoustic
  vs. loud and fast). Scoring all three would count the same thing three times.
- **Valence (musical positivity) is the only independent numeric axis.** It separates
  "sad-energetic" (*Storm Runner*, valence 0.48) from "happy-energetic" (*Sunrise City*, 0.84).
- Tempo is in BPM (60–152), not 0–1, so it would need normalizing before use. Since energy
  already carries that signal, skip it.
- Genre is sparse (7 genres across 10 songs), and `indie pop` ≠ `pop` under an exact string match.

**Recommended features:**
- **genre** (categorical). The strongest "identity" signal.
- **mood** (categorical). The vibe label.
- **energy** (numeric). The calm↔intense axis.
- **valence** (numeric, optional). The sad↔happy axis.
- **acousticness** (numeric, small weight). Already in `UserProfile` as `likes_acoustic`.

**Does this match how I'd define a "vibe"?** Mostly, yes. When I describe a vibe I think in two
dimensions: *how intense* (energy) and *how bright or dark* (valence). That's the classic
arousal/valence model of emotion. Genre is more like "which room" the vibe lives in. What these
features miss is texture: vocals vs. instrumental, lyrics, era, and production style.
*Night Drive Loop* and *Storm Runner* have similar numbers but feel very different.

---

## Step 3: Algorithm Recipe

**Prompt used:**
> How do I score a numeric feature like energy so that songs closer to the user's preference
> score higher, rather than just rewarding higher or lower values?

### Closeness, not magnitude
Rewarding raw energy (`score += energy`) would push the loudest songs to the top for *every*
user, including someone who wants to study. Instead, reward **closeness**:

```
similarity = 1 - |song.energy - user.target_energy|     # 1.0 = perfect match, 0.0 = opposite
```

Because energy and valence are both in 0–1, this stays in 0–1. A user targeting 0.4 gets 1.0 for
*Midnight Coding* (0.42 → 0.98) and only 0.47 for *Gym Hero* (0.93).

### Scoring Rule (one song)

| Component | Points | Rule |
|---|---|---|
| Genre match | **+2.0** | `song.genre == user.favorite_genre` |
| Mood match | **+1.0** | `song.mood == user.favorite_mood` |
| Energy closeness | **0 – 1.5** | `1.5 × (1 − |song.energy − target_energy|)` |
| Acoustic fit | **0 – 0.5** | `0.5 × acousticness` if `likes_acoustic`, else `0.5 × (1 − acousticness)` |
| *(optional)* Valence closeness | 0 – 1.0 | `1.0 × (1 − |song.valence − target_valence|)` |

Max ≈ 5.0 (6.0 with valence). Every component also produces a reason string, e.g.
`"genre match (+2.0)"` and `"energy 0.82 close to your 0.80 (+1.47)"`, which feeds
`explain_recommendation`.

**Why is genre worth more than mood?** Genre is a stable, long-term preference. A pop fan rarely
wants death metal, even if the mood matches. Mood changes hour to hour, and the energy/valence
numbers already partly encode it, so mood gets a smaller bonus. Energy closeness (up to 1.5) is
weighted high enough that a perfect-energy song from another genre can beat a same-genre song
with the wrong energy. That stops genre from completely dominating.

**Sanity check against the starter test** (user: pop / happy / 0.8 / not acoustic):
- *Test Pop Track*: 2 + 1 + 1.5×1.0 + 0.5×0.8 = **4.90**
- *Chill Lofi Loop*: 0 + 0 + 1.5×0.6 + 0.5×0.1 = **0.95** → pop ranks first ✅

### Ranking Rule (the list)
1. Score every song with the Scoring Rule.
2. Sort by score, highest first. Break ties by smallest energy distance.
3. Return the top `k`.
4. *(stretch)* Re-rank for diversity, e.g. at most one song per artist in the top k.

### Why both rules are needed
- The **Scoring Rule** answers *"how good is this one song for this user?"* It's a local,
  absolute judgment and only needs one song and one profile.
- The **Ranking Rule** answers *"what should the user actually see, and in what order?"* It needs
  the whole list: it compares scores, handles ties, cuts to k, and can apply list-level goals
  like diversity or "don't show the same artist twice." Those can't be expressed one song at a
  time.

Keeping them separate also mirrors real systems (a model scores, a re-ranker arranges) and lets
you change one without touching the other. For example, you can tune weights without changing
how you pick the top 5.
