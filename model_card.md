# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

**VibeCheck 1.0**: a small, explainable, content-based music recommender.

---

## 2. Goal / Task and Intended Use

**Goal / task:** Given a listener's taste profile (favorite genre, favorite mood, target energy,
target valence, and whether they like acoustic sound), VibeCheck suggests the 5 songs from its
catalog that best fit that taste. It explains each pick with a list of reasons. It doesn't
predict plays or skips. It only ranks songs by how closely they match the stated preferences.

**Assumptions about the user:** the user can describe their taste with one genre, one mood, and
a single target for energy and valence. It assumes their words match the catalog's labels
exactly.

**Intended use:**
- A classroom project for learning how content-based recommenders turn data into rankings.
- Experimenting with weights and user profiles to see how the output changes.
- Showing why explainable scoring matters, since every recommendation lists its reasons.

**Not intended for:**
- Real listeners making real choices. The catalog is 20 made-up songs, and the labels are one
  person's opinion.
- Judging artists or genres as "better" or "worse." A low score only means "doesn't match this
  one profile."
- Any use with real personal data, or at scale. It has no privacy protections, no feedback
  learning, and no fairness checks.

---

## 3. How the Model Works  

**How it works, in plain language:**

Think of the recommender as a judge holding a scorecard. You tell it five things about your
taste: your favorite genre, your favorite mood, how energetic you want the music to be (0 = very
calm, 1 = very intense), how happy or bright you want it to sound (also 0 to 1), and whether you
like acoustic-sounding music.

The judge then goes through every song in the catalog, one at a time, and awards points:

- **Same genre as your favorite?** 2 points. This is the biggest single reward, because genre is
  usually the most stable part of someone's taste.
- **Same mood as your favorite?** 1 point.
- **Energy close to what you asked for?** Up to 1.5 points. A song right on your target gets
  almost all of them, and a song far away gets few. It rewards being *close*, not being louder
  or quieter, so a calm listener isn't buried in workout tracks.
- **Brightness (happy vs. sad) close to what you asked for?** Up to 1 point, using the same
  "closer is better" idea.
- **Acoustic or not, the way you like it?** Up to half a point, as a small tiebreaker.

The best possible score is 6 points. After every song has a score, the judge lines them up from
highest to lowest and shows you the top five. If two songs tie, the one whose energy is closer to
your target goes first. Each recommendation comes with its scorecard, for example "genre match
(+2.0), energy 0.82 vs your 0.80 (+1.47)", so you can see exactly why it was picked.

**Changes from the starter logic:** the starter returned the first few songs in the file with a
placeholder explanation. Now every song is actually scored and ranked. I also added valence
(happy vs. sad) to the profile, because energy alone can't tell an angry metal song from a
euphoric dance track.

---

## 4. Data  

- **Size:** 20 songs in `data/songs.csv`. The starter file had 10, and I added 10 more.
- **Features per song:** genre, mood, energy (0–1), tempo in BPM, valence (0–1, happy vs. sad),
  danceability (0–1), and acousticness (0–1).
- **Used for scoring:** genre, mood, energy, valence, and acousticness. Tempo and danceability
  are not used, because they rise and fall with energy, so they would double-count the same
  thing.
- **Variety:** 17 genres and 16 moods. The songs I added cover genres and moods the starter
  lacked: hip hop, metal, classical, country, r&b, reggae, edm, folk, latin, electronic, plus
  moods like angry, sad, romantic, and nostalgic.
- **Limits:**
  - Most genres have only one song. Only lofi (3) and pop (2) have more.
  - The songs and artists are made up, and one person chose every label. For example, all metal
    is labeled "angry."
  - Nothing about lyrics, language, vocals, era, popularity, or how real people listened.
  - Many moods are near-synonyms ("chill", "relaxed", "peaceful") but are treated as different
    words.

---

## 5. Strengths  

- **Clear, consistent profiles work well.** Chill Lofi got three lofi songs, then quiet ambient
  and jazz, which is exactly a study playlist. High-Energy Pop and Deep Intense Rock also got
  their obvious #1 song (*Sunrise City* and *Storm Runner*).
- **It tells opposites apart.** The lofi and rock profiles share zero songs, and each one's
  favorite scores under 2 points for the other.
- **"Closer is better" scoring works.** A calm listener isn't flooded with loud songs just
  because they have bigger numbers.
- **Every result explains itself.** The reasons list (for example, "genre match: pop (+2.0)")
  makes it easy to see *why* a song ranked where it did, and it made bugs and biases easy to
  spot during testing.
- **It doesn't crash on odd input.** Unknown genres or a profile with no labels still return
  sensible-sounding songs instead of errors.

---

## 6. Limitations and Bias 

**Main weakness: genre and mood labels can outvote what the music actually sounds like.** In the
"Sad Banger" test, the user asked for loud (energy 0.9), dark music in the "folk / sad"
category. The system ranked *Paper Boats*, a quiet acoustic folk song (energy 0.30), first by a
wide margin (4.60 vs. 2.86), because matching the two labels is worth 3 points no matter how the
song sounds. *Iron Cathedral*, which fits the requested sound almost perfectly, came 2nd. The same
effect explains why *Gym Hero* beats *Rooftop Lights* for a "happy pop" fan: *Gym Hero* has the
exact "pop" label, while *Rooftop Lights* is a happy song labeled "indie pop," so it gets zero
genre points. Since labels are matched as exact text, users whose taste uses different words than
the catalog (k-pop, "hype", "relaxed" instead of "chill") are quietly treated worse.

**Other biases found during testing:**
- **Thin genres create filter bubbles.** Most genres have exactly one song, so a metal or rock fan
  gets the same single song on top every time, and the rest of the list is filler chosen only by
  energy. No amount of listening changes this, because the system never learns.
- **"Generalist" songs show up everywhere.** *Gym Hero* and *Concrete Crown* each appeared in 4 of
  the 7 top-5 lists. *Concrete Crown* never matched anyone's genre or mood. Its numbers
  (energy 0.78, mid valence, not acoustic) are just never far from any high-energy target, so the
  energy gap rewards being "average enough" for everyone.
- **Missing genres fail silently.** The K-Pop fan got no genre or mood matches at all, and every
  score fell between 2.62 and 2.86. The output looks just as confident as for other users, with
  no warning that nothing actually matched.
- **Preferences are applied without context.** The "Acoustic Headbanger" (metal, likes acoustic)
  was recommended *Flamenco Fire*, a latin song, 2nd, purely for its acoustic guitar. The acoustic
  bonus doesn't know it is being combined with metal.
- **The "/ 6.00" display is misleading for users without labels.** "Dead Center" set no genre,
  mood, or acoustic preference, so its real maximum is 2.5, and even a perfect match looks like a
  weak score.

---

## 7. Evaluation  

### Profiles tested

I ran seven profiles through `python -m src.main` (all defined in `src/main.py`):

| Profile | Type | What it tests |
|---|---|---|
| High-Energy Pop | typical | pop / happy / energy 0.80 / not acoustic |
| Chill Lofi | typical | lofi / chill / energy 0.40 / acoustic |
| Deep Intense Rock | typical | rock / intense / energy 0.90 / darker valence |
| Sad Banger | adversarial | labels say calm sad folk, numbers say loud and dark |
| K-Pop Fan | adversarial | genre and mood that don't exist in the catalog |
| Acoustic Headbanger | adversarial | metal fan who also wants acoustic sound (no such song) |
| Dead Center | adversarial | no labels, every number at 0.5 |

### Results (top 5 per profile)

Click a profile to expand its full terminal output.

<details>
<summary><b>High-Energy Pop</b></summary>

```
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

</details>

<details>
<summary><b>Chill Lofi</b></summary>

```
================================================================
User profile: favorite_genre=lofi, favorite_mood=chill, target_energy=0.4, target_valence=0.6, likes_acoustic=True
================================================================

1. Library Rain by Paper Lanterns  [lofi / chill]
   Score: 5.85 / 6.00
   Because:
     - genre match: lofi (+2.0)
     - mood match: chill (+1.0)
     - energy 0.35 vs your 0.40 (+1.42)
     - valence 0.60 vs your 0.60 (+1.00)
     - acoustic fit, acousticness 0.86 (+0.43)

2. Midnight Coding by LoRoom  [lofi / chill]
   Score: 5.79 / 6.00
   Because:
     - genre match: lofi (+2.0)
     - mood match: chill (+1.0)
     - energy 0.42 vs your 0.40 (+1.47)
     - valence 0.56 vs your 0.60 (+0.96)
     - acoustic fit, acousticness 0.71 (+0.35)

3. Focus Flow by LoRoom  [lofi / focused]
   Score: 4.88 / 6.00
   Because:
     - genre match: lofi (+2.0)
     - energy 0.40 vs your 0.40 (+1.50)
     - valence 0.59 vs your 0.60 (+0.99)
     - acoustic fit, acousticness 0.78 (+0.39)

4. Spacewalk Thoughts by Orbit Bloom  [ambient / chill]
   Score: 3.73 / 6.00
   Because:
     - mood match: chill (+1.0)
     - energy 0.28 vs your 0.40 (+1.32)
     - valence 0.65 vs your 0.60 (+0.95)
     - acoustic fit, acousticness 0.92 (+0.46)

5. Coffee Shop Stories by Slow Stereo  [jazz / relaxed]
   Score: 2.79 / 6.00
   Because:
     - energy 0.37 vs your 0.40 (+1.46)
     - valence 0.71 vs your 0.60 (+0.89)
     - acoustic fit, acousticness 0.89 (+0.45)
```

</details>

<details>
<summary><b>Deep Intense Rock</b></summary>

```
================================================================
User profile: favorite_genre=rock, favorite_mood=intense, target_energy=0.9, target_valence=0.4, likes_acoustic=False
================================================================

1. Storm Runner by Voltline  [rock / intense]
   Score: 5.85 / 6.00
   Because:
     - genre match: rock (+2.0)
     - mood match: intense (+1.0)
     - energy 0.91 vs your 0.90 (+1.48)
     - valence 0.48 vs your 0.40 (+0.92)
     - non-acoustic fit, acousticness 0.10 (+0.45)

2. Gym Hero by Max Pulse  [pop / intense]
   Score: 3.56 / 6.00
   Because:
     - mood match: intense (+1.0)
     - energy 0.93 vs your 0.90 (+1.46)
     - valence 0.77 vs your 0.40 (+0.63)
     - non-acoustic fit, acousticness 0.05 (+0.47)

3. Iron Cathedral by Ashfall  [metal / angry]
   Score: 2.70 / 6.00
   Because:
     - energy 0.97 vs your 0.90 (+1.40)
     - valence 0.22 vs your 0.40 (+0.82)
     - non-acoustic fit, acousticness 0.03 (+0.48)

4. Night Drive Loop by Neon Echo  [synthwave / moody]
   Score: 2.58 / 6.00
   Because:
     - energy 0.75 vs your 0.90 (+1.27)
     - valence 0.49 vs your 0.40 (+0.91)
     - non-acoustic fit, acousticness 0.22 (+0.39)

5. Concrete Crown by Kilo Verse  [hip hop / confident]
   Score: 2.56 / 6.00
   Because:
     - energy 0.78 vs your 0.90 (+1.32)
     - valence 0.62 vs your 0.40 (+0.78)
     - non-acoustic fit, acousticness 0.08 (+0.46)
```

</details>

<details>
<summary><b>Sad Banger (conflicting)</b></summary>

```
================================================================
User profile: favorite_genre=folk, favorite_mood=sad, target_energy=0.9, target_valence=0.2, likes_acoustic=False
================================================================

1. Paper Boats by Wren & Willow  [folk / sad]
   Score: 4.60 / 6.00
   Because:
     - genre match: folk (+2.0)
     - mood match: sad (+1.0)
     - energy 0.30 vs your 0.90 (+0.60)
     - valence 0.25 vs your 0.20 (+0.95)
     - non-acoustic fit, acousticness 0.90 (+0.05)

2. Iron Cathedral by Ashfall  [metal / angry]
   Score: 2.86 / 6.00
   Because:
     - energy 0.97 vs your 0.90 (+1.40)
     - valence 0.22 vs your 0.20 (+0.98)
     - non-acoustic fit, acousticness 0.03 (+0.48)

3. Storm Runner by Voltline  [rock / intense]
   Score: 2.66 / 6.00
   Because:
     - energy 0.91 vs your 0.90 (+1.48)
     - valence 0.48 vs your 0.20 (+0.72)
     - non-acoustic fit, acousticness 0.10 (+0.45)

4. Night Drive Loop by Neon Echo  [synthwave / moody]
   Score: 2.38 / 6.00
   Because:
     - energy 0.75 vs your 0.90 (+1.27)
     - valence 0.49 vs your 0.20 (+0.71)
     - non-acoustic fit, acousticness 0.22 (+0.39)

5. Concrete Crown by Kilo Verse  [hip hop / confident]
   Score: 2.36 / 6.00
   Because:
     - energy 0.78 vs your 0.90 (+1.32)
     - valence 0.62 vs your 0.20 (+0.58)
     - non-acoustic fit, acousticness 0.08 (+0.46)
```

</details>

<details>
<summary><b>K-Pop Fan (missing genre)</b></summary>

```
================================================================
User profile: favorite_genre=k-pop, favorite_mood=hype, target_energy=0.85, target_valence=0.85, likes_acoustic=False
================================================================

1. Sunrise City by Neon Echo  [pop / happy]
   Score: 2.86 / 6.00
   Because:
     - energy 0.82 vs your 0.85 (+1.46)
     - valence 0.84 vs your 0.85 (+0.99)
     - non-acoustic fit, acousticness 0.18 (+0.41)

2. Laser Tide by Pulsewave  [edm / euphoric]
   Score: 2.79 / 6.00
   Because:
     - energy 0.95 vs your 0.85 (+1.35)
     - valence 0.80 vs your 0.85 (+0.95)
     - non-acoustic fit, acousticness 0.02 (+0.49)

3. Gym Hero by Max Pulse  [pop / intense]
   Score: 2.77 / 6.00
   Because:
     - energy 0.93 vs your 0.85 (+1.38)
     - valence 0.77 vs your 0.85 (+0.92)
     - non-acoustic fit, acousticness 0.05 (+0.47)

4. Rooftop Lights by Indigo Parade  [indie pop / happy]
   Score: 2.65 / 6.00
   Because:
     - energy 0.76 vs your 0.85 (+1.36)
     - valence 0.81 vs your 0.85 (+0.96)
     - non-acoustic fit, acousticness 0.35 (+0.33)

5. Concrete Crown by Kilo Verse  [hip hop / confident]
   Score: 2.62 / 6.00
   Because:
     - energy 0.78 vs your 0.85 (+1.40)
     - valence 0.62 vs your 0.85 (+0.77)
     - non-acoustic fit, acousticness 0.08 (+0.46)
```

</details>

<details>
<summary><b>Acoustic Headbanger</b></summary>

```
================================================================
User profile: favorite_genre=metal, favorite_mood=angry, target_energy=0.95, target_valence=0.25, likes_acoustic=True
================================================================

1. Iron Cathedral by Ashfall  [metal / angry]
   Score: 5.45 / 6.00
   Because:
     - genre match: metal (+2.0)
     - mood match: angry (+1.0)
     - energy 0.97 vs your 0.95 (+1.47)
     - valence 0.22 vs your 0.25 (+0.97)
     - acoustic fit, acousticness 0.03 (+0.01)

2. Flamenco Fire by Lucia Torres  [latin / passionate]
   Score: 2.31 / 6.00
   Because:
     - energy 0.85 vs your 0.95 (+1.35)
     - valence 0.70 vs your 0.25 (+0.55)
     - acoustic fit, acousticness 0.82 (+0.41)

3. Storm Runner by Voltline  [rock / intense]
   Score: 2.26 / 6.00
   Because:
     - energy 0.91 vs your 0.95 (+1.44)
     - valence 0.48 vs your 0.25 (+0.77)
     - acoustic fit, acousticness 0.10 (+0.05)

4. Night Drive Loop by Neon Echo  [synthwave / moody]
   Score: 2.07 / 6.00
   Because:
     - energy 0.75 vs your 0.95 (+1.20)
     - valence 0.49 vs your 0.25 (+0.76)
     - acoustic fit, acousticness 0.22 (+0.11)

5. Gym Hero by Max Pulse  [pop / intense]
   Score: 1.98 / 6.00
   Because:
     - energy 0.93 vs your 0.95 (+1.47)
     - valence 0.77 vs your 0.25 (+0.48)
     - acoustic fit, acousticness 0.05 (+0.03)
```

</details>

<details>
<summary><b>Dead Center (no labels)</b></summary>

```
================================================================
User profile: target_energy=0.5, target_valence=0.5
================================================================

1. Velvet After Dark by Sienna Rae  [r&b / romantic]
   Score: 2.39 / 6.00
   Because:
     - energy 0.48 vs your 0.50 (+1.47)
     - valence 0.58 vs your 0.50 (+0.92)

2. Midnight Coding by LoRoom  [lofi / chill]
   Score: 2.32 / 6.00
   Because:
     - energy 0.42 vs your 0.50 (+1.38)
     - valence 0.56 vs your 0.50 (+0.94)

3. Dusty Porch Swing by The Hollow Pines  [country / nostalgic]
   Score: 2.29 / 6.00
   Because:
     - energy 0.52 vs your 0.50 (+1.47)
     - valence 0.68 vs your 0.50 (+0.82)

4. Focus Flow by LoRoom  [lofi / focused]
   Score: 2.26 / 6.00
   Because:
     - energy 0.40 vs your 0.50 (+1.35)
     - valence 0.59 vs your 0.50 (+0.91)

5. Library Rain by Paper Lanterns  [lofi / chill]
   Score: 2.17 / 6.00
   Because:
     - energy 0.35 vs your 0.50 (+1.27)
     - valence 0.60 vs your 0.50 (+0.90)
```

</details>

### Does it feel right?

For the three typical profiles, yes. **Chill Lofi** is the best result: three lofi songs, then
ambient and jazz, all quiet and acoustic. That's exactly what I would put on while studying.
**High-Energy Pop** gets *Sunrise City* first, which is correct, but I would have ranked
*Rooftop Lights* (a happy, upbeat song) above *Gym Hero* (an intense workout track).

**Why did *Sunrise City* rank first for High-Energy Pop?** It's the only song that collects
every reward: genre "pop" (+2.0) and mood "happy" (+1.0) both match, energy 0.82 is almost
exactly the 0.80 target (+1.47), valence 0.84 is close to 0.80 (+0.96), and acousticness 0.18
fits a non-acoustic listener (+0.41), for 5.84 out of 6. *Gym Hero* also gets the +2.0 genre
bonus but misses the mood point and is a bit too energetic, which leaves it more than a point
behind.

### Comparing profiles

- **High-Energy Pop vs. Chill Lofi:** no overlap at all. Pop gets energy 0.76–0.95 songs with
  little acoustic sound, and lofi gets energy 0.28–0.42 songs with lots of it. This makes sense,
  because the two profiles sit at opposite ends of the energy and acoustic scales.
- **High-Energy Pop vs. Deep Intense Rock:** both lists share *Gym Hero* and *Concrete Crown*,
  because both users want high energy and no acoustic sound. Rock swaps the happy songs for darker
  ones (*Iron Cathedral*, *Night Drive Loop*) because its valence target is lower (0.40 vs. 0.80).
  *Gym Hero* shows up for both for different reasons: "pop" earns it the genre point for the pop
  fan, and "intense" earns it the mood point for the rock fan.
- **Chill Lofi vs. Deep Intense Rock:** completely different lists. *Library Rain* scores 5.85
  for lofi and would score under 2 for rock, and *Storm Runner* is the reverse. This confirms the
  profile can tell "chill lofi" from "intense rock."
- **Deep Intense Rock vs. Sad Banger:** the numbers are similar (both loud and dark), and the
  lists share *Iron Cathedral*, *Storm Runner*, and *Night Drive Loop*. But Sad Banger's #1 is a
  *quiet folk song*, because its labels ("folk", "sad") match only that song. This was the most
  surprising result: two labels outweighed a big energy mismatch.
- **High-Energy Pop vs. K-Pop Fan:** almost the same five songs, because without a genre match
  the K-Pop fan is ranked purely on "loud and happy," which is the same thing the pop fan's
  numbers ask for. The difference is confidence: pop's top score is 5.84, while K-Pop's is only
  2.86, and all five K-Pop scores are within 0.24 of each other.
- **Deep Intense Rock vs. Acoustic Headbanger:** both want very loud, dark music, and both lists
  share *Storm Runner*, *Night Drive Loop*, and *Gym Hero*. The headbanger's acoustic preference
  pulls *Flamenco Fire* (loud but acoustic) up to 2nd, which a real metal fan probably wouldn't
  want.
- **Chill Lofi vs. Dead Center:** Dead Center has no labels and wants 0.5 energy, and its list
  still includes three lofi songs. Lofi songs sit close to the middle of the energy scale
  (0.35–0.42), so they win by default when nothing else matters.

### Experiment: weight shift (energy ×2, genre ×½)

I temporarily changed `ENERGY_WEIGHT` from 1.5 to 3.0 and `GENRE_WEIGHT` from 2.0 to 1.0, then
reran all seven profiles. The math stays valid: closeness is always between 0 and 1, so the new
maximum is 1 + 1 + 3 + 1 + 0.5 = 6.5, and every observed score stayed between 1.58 and 6.34.
The two tests still passed. I then reverted to the original weights.

| Profile | Original top 3 | Energy ×2, genre ×½ top 3 |
|---|---|---|
| High-Energy Pop | Sunrise City, Gym Hero, Rooftop Lights | Sunrise City, **Rooftop Lights**, Gym Hero |
| Chill Lofi | Library Rain, Midnight Coding, Focus Flow | *(unchanged)* |
| Deep Intense Rock | Storm Runner, Gym Hero, Iron Cathedral | *(unchanged; Laser Tide replaces Night Drive Loop at #4)* |
| Sad Banger | Paper Boats, Iron Cathedral, Storm Runner | **Iron Cathedral**, Paper Boats, Storm Runner |
| Acoustic Headbanger | Iron Cathedral, Flamenco Fire, Storm Runner | Iron Cathedral, **Storm Runner**, Flamenco Fire |

**More accurate or just different?** For the profiles where labels and sound disagreed, it was
**more accurate**: *Rooftop Lights* moved above *Gym Hero*, a real banger took #1 for Sad Banger,
and the acoustic flamenco song dropped below a rock song for the metal fan. For profiles where
labels and sound already agreed (Chill Lofi, Deep Intense Rock), it was mostly **just different**
or unchanged. The cost is that scores get bunched together. Sad Banger's top 3 are now within
0.11 of each other, so tiny differences in energy decide the order, and genre almost stops
mattering. I kept the original weights, because I still think genre should count for more than a
small energy difference. A better fix would be smarter label matching (treating "indie pop" as
close to "pop").

---

## 8. Future Work  

1. **Smarter label matching.** Treat related labels as partial matches, for example "indie pop"
   as close to "pop" and "relaxed" as close to "chill". This would fix the *Gym Hero* vs.
   *Rooftop Lights* problem without turning down the genre weight.
2. **Diversity in the top 5.** Allow at most one or two songs per genre or artist, so the same
   "generalist" songs (*Gym Hero*, *Concrete Crown*) don't fill every list.
3. **Honest confidence.** Warn the user when nothing matched their genre or mood (like the K-Pop
   fan), and show scores against the profile's real maximum instead of a fixed "/ 6.00".
4. *(Bigger step)* **Learn from feedback.** Let skips and replays adjust the weights for each
   user, the way real apps do, instead of hand-picking them.

---

## 9. Personal Reflection  

<!-- DRAFT written with my AI assistant from what happened in this project: rewrite in your own words before submitting, then delete this comment. -->

**Biggest learning moment:** the "Sad Banger" test. I built a profile that asked for loud, dark
music but labeled it "folk / sad." The system picked a quiet acoustic folk song first, by a lot.
Nothing was broken, and the math did exactly what I told it to. I just hadn't realized that two
label matches (3 points) could outweigh a huge energy mismatch. That showed me that a
recommender's "opinions" are really just its weights, and small choices like "+2 for genre"
decide who it serves well.

**How AI tools helped, and when I double-checked:** AI helped me research collaborative
vs. content-based filtering, expand the dataset, write the scoring code, and come up with
adversarial profiles I wouldn't have thought of. But I had to verify things:
- I recalculated a few scores by hand (for example, *Midnight Coding* = 5.79) to make sure the
  code matched the recipe.
- The starter code didn't run as given (`main.py`'s import and the tests couldn't find `src`),
  and those fixes needed checking.
- When we moved the project to a new folder, the git history didn't come along and had to be
  restored from GitHub.
- For the weight experiment, I confirmed the new maximum score (6.5) and that the tests still
  passed before trusting the results.

AI was fast, but "it ran" didn't mean "it was right."

**What surprised me:** how much a few lines of addition and sorting can *feel* like a real
recommendation. The Chill Lofi list honestly looked like a playlist I'd make, and the reasons
next to each song made it feel thoughtful. But the same simple rules also produced results that
felt clearly wrong (a calm folk song for a "banger" request). That made me realize real apps
probably feel "smart" partly because they explain themselves and get the obvious cases right.

**What I'd try next:** fuzzy matching for related genres and moods, a diversity rule so the same
songs don't show up everywhere, and a simple feedback loop where skipping a song lowers the
weight of whatever made it rank high. I'd also like to try a tiny collaborative-filtering
version with fake user histories, to compare it with this content-based approach.
