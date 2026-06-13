---
name: commit
description: Save all current work and create a git commit whose message is a short, accurate summary of what changed. Stages every pending change (after a secrets guard), groups the diff into themes, and writes a conventional-commit message with a one-line subject plus a tight bullet summary. Use at the end of a session, or whenever the user says "commit", "save everything", or "write the changes".
disable-model-invocation: true
---

The user wants to save all current work and commit it with a short summary of what changed. Arguments: $ARGUMENTS

## Instructions

### 1. Survey what changed

Run these in parallel and read the results before touching anything:
- `git status --porcelain` — every modified, added, deleted, and untracked path
- `git diff` — unstaged changes
- `git diff --staged` — anything already staged
- `git branch --show-current` — current branch

If there is nothing to commit, tell the user and stop.

### 2. SECRETS GUARD — do this before staging anything

This repo's `.env` contains **live API keys** and is **not** gitignored (see `CLAUDE.md`). Never let it into a commit.

- If `.env`, `.env.*`, or any file containing credentials appears in `git status`:
  1. **Stop.** Do not stage it.
  2. Check whether `.gitignore` already excludes it; if not, add `.env` (and `.env.*`) to `.gitignore`.
  3. If `.env` is *already tracked* from a previous commit, warn the user explicitly and recommend `git rm --cached .env` + key rotation — do not do this silently.
- Also scan the diff for inline secrets (hardcoded `sk-`, `key=`, tokens, passwords). If any appear in non-`.env` files, stop and surface them to the user before committing.

Never use `git add -A` / `git add .` blindly. Stage explicit paths so an unexpected file can't ride along.

### 3. "Write everything" — finalize the work before committing

Before composing the message, make sure the session's work is actually captured, not just the code:
- If a module's `.ipynb` changed but its `learning.md` / `_index.md` weren't updated this session, remind the user (or, if they ask, run `/update-learning <module>`) so the journal isn't left behind.
- Don't fabricate journal content here — just flag the gap. The point of this step is that a commit shouldn't ship code without its learning record when one is expected.

### 4. Group the diff into themes

Read the actual diff and cluster the changes into 1–4 logical themes (e.g. "new commit skill", "notebook S5 added", "journal updated"). For each theme note:
- **what** changed (the concrete edit), not just which file
- **why**, if it's inferable from the diff or session context

This grouping is what makes the summary short *and* accurate — it's a synthesis of the diff, never a file listing.

### 5. Compose the commit message

Follow this repo's git-workflow rules:
- **Conventional-commit format:** `<type>: <description>` where type ∈ `feat | fix | refactor | docs | test | chore | perf | ci`.
- **Subject line:** imperative mood, ≤ 72 chars, no trailing period. It must summarize the *dominant* change.
- **Body:** a short bullet summary — one bullet per theme from step 4, each a tight phrase describing the change. Keep it to the few bullets that matter; this is a summary, not a changelog.
- **No attribution / co-author trailer** — attribution is disabled globally for this workspace.

Template:

```
<type>: <one-line summary of the dominant change>

- <theme 1: what changed>
- <theme 2: what changed>
- <theme 3: what changed>
```

If the change is genuinely a single small thing, a subject line alone (no body) is fine — don't pad it.

### 6. Show the user before committing

Print the proposed commit message and the exact list of paths you're about to stage. Then commit:
- Stage the explicit paths (step 2's guard already applied).
- Commit using a heredoc so the multi-line body is preserved:
  ```bash
  git commit -m "$(cat <<'EOF'
  <type>: <subject>

  - <bullet>
  - <bullet>
  EOF
  )"
  ```

### 7. Do NOT push unless asked

Committing is local and safe; pushing is outward-facing and this repo has unrotated keys history risk. Only `git push` if the user explicitly asked in $ARGUMENTS. Otherwise, after committing, tell the user the commit is local and offer to push.

### 8. Report

Confirm with:
- the commit hash and subject line (`git log -1 --oneline`)
- the files that were committed
- anything you deliberately left out (e.g. `.env` skipped, journal gap flagged)
- whether a push is still pending
