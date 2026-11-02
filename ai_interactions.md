# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agentic Workflow (SF8)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

I used Claude Code (in the Claude desktop app) as an agent for the whole project. I gave it the
assignment one phase at a time and told it to complete only that phase: Phase 1 (research and
concept), Phase 2 (design), Phase 3 (implementation), Phase 4 (evaluation), and Phase 5 (model
card and reflection). Then I asked it to check the submission checklist and finish anything
incomplete.

**Prompts used:**

- "only do phase 1:" followed by the pasted Phase 1 instructions, then the same pattern for
  phases 2–5 ("only do phase 3: … again only do phase 3")
- "make sure you understand and remember these instructions for the overall of this project"
  followed by the submission checklist
- "Yes, commit it" and "Yes, move it" (approving the first commit and moving the project out of
  a temporary folder)
- "i've forked it" (after I forked the repo on GitHub myself)
- "make sure every single detail is complete"

**What did the agent generate or change?**

- **Research and design:** `docs/phase1_notes.md` and the "How The System Works" section of
  `README.md` (data analysis with pandas, user profile, final weights, data-flow sketch,
  expected biases).
- **Data:** added 10 songs to `data/songs.csv` (10 → 20).
- **Code:** implemented `load_songs`, `score_song`, `recommend_songs`, and the `Recommender`
  class in `src/recommender.py`. Formatted the CLI output and added seven test profiles in
  `src/main.py`. Added `pytest.ini`.
- **Documentation:** filled in `model_card.md`, the README's sample output, experiments,
  limitations, and reflection sections, and this file.
- **Commands it ran:** created the virtual environment and installed requirements, ran
  `python -m src.main` and `pytest` after each change, ran a temporary weight experiment and
  reverted it with `git checkout`, and made one or two commits per phase, pushing to my fork.

**What did you verify or fix manually?**

- **Forking:** the agent couldn't fork the repo (the GitHub CLI wasn't installed), so I forked
  it on GitHub myself and confirmed it was public. The agent then pointed the local repo at my
  fork.
- **Scope control:** I kept the agent to one phase at a time so I could review each phase's
  summary before moving on.
- **Things the agent caught and fixed, which I reviewed in its summaries:**
  - The starter `main.py` import broke `python -m src.main`.
  - The starter tests couldn't import `src`.
  - Moving the project to a new folder dropped the `.git` history, which the agent restored
    from my fork.
  - A Markdown table in the README broke because of `|` characters.
- **Accuracy:** the agent checked its scores against hand calculations (*Midnight Coding* =
  5.79) and confirmed the weight experiment's new maximum score (6.5) before writing up results.
  Where its first draft of my reflection described work as if I had done it personally, it was
  reworded to say an AI agent did that work.
