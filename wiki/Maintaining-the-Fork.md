# Maintaining the fork

🇬🇧 English · [🇭🇺 Magyar](Maintaining-the-Fork.hu.md)

Goal: keep your own development safe so an upstream update or sync can never overwrite it.

## Good news first

- There is **no automatic upstream-sync** in this repo. No workflow, action, or Dependabot config
  pulls from `openai/openai-agents-python`. Nothing syncs on its own.
- The only ways upstream code could land here are **manual**: clicking GitHub's **"Sync fork"**
  button, or running `git pull`/`git merge`/`git reset` against an upstream remote on your machine.

So "staying safe" is mostly about *not* doing those two things — plus, optionally, fully detaching.

## Level 1 — local safeguard (do this now)

On every clone you work in, remove the upstream remote so an accidental pull can't reach it:

```bash
git remote remove upstream        # if it exists
git remote -v                     # should show only 'origin' -> your fork
```

If you want to keep upstream for occasional cherry-picking, keep it **fetch-only** and never merge
its branch into yours:

```bash
git remote set-url --push upstream DISABLED
```

## Level 2 — never click "Sync fork"

On GitHub, the **"Sync fork"** button on your repo merges upstream's default branch into yours. It
does not silently delete your commits, and it can create conflicts or unwanted merge commits. Leave
it alone. Protect `main` as well: **Settings → Branches → Add rule** for `main` (require PRs, block
force-pushes) so nothing rewrites your history.

## Level 3 — fully detach from the fork network (optional, permanent)

GitHub still labels this repo a *fork*, which is why new PRs default to the upstream repo and why the
"Sync fork" button appears. To make it a standalone repository:

**Option A — ask GitHub Support.** GitHub can detach a fork from its parent network. Open a request
at <https://support.github.com/> ("detach my fork into a standalone repository"). This keeps your
URL, stars, and history.

**Option B — re-create as a fresh repo (full control, new URL).**

```bash
# 1. Create a new EMPTY repo on GitHub (not a fork), e.g. Pocomotoxx/agents-platform
# 2. Mirror your history into it:
git clone --bare https://github.com/Pocomotoxx/agents-python.git tmp-mirror
cd tmp-mirror
git push --mirror https://github.com/Pocomotoxx/agents-platform.git
cd .. && rm -rf tmp-mirror
# 3. Point your working clone at the new origin:
git remote set-url origin https://github.com/Pocomotoxx/agents-platform.git
```

The new repo is not part of any fork network, so `gh pr create` targets it by default and there is no
"Sync fork" button. Archive or delete the old fork afterwards.

## Pulling specific upstream fixes later (on purpose)

Detaching does not mean you can never take an upstream fix — it means nothing happens automatically.
When you *want* a specific upstream change, cherry-pick it deliberately:

```bash
git remote add upstream https://github.com/openai/openai-agents-python.git   # temporary
git fetch upstream
git log --oneline upstream/main -20            # find the commit you want
git cherry-pick <sha>                          # apply just that one
git remote remove upstream                     # detach again
```

## License note

This fork is MIT. The upstream copyright (© 2025 OpenAI) must stay in `LICENSE`. You may add your own
copyright line for your contributions, e.g.:

```
Copyright (c) 2025 OpenAI
Copyright (c) 2026 Pocomotoxx (fork modifications)
```

Do not remove the original notice — that is the one thing the MIT license requires of a fork.
