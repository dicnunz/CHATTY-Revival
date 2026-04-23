# CHATTY Revival

Transparent AI-assisted workspace for CHATTY, an unofficial Solana meme/community token by @nicdunz.

CHATTY is not affiliated with OpenAI, ChatGPT, or any other company. The creator may benefit financially from trading activity and/or creator fees. Nothing here is financial advice. No promises, no guarantees. Meme tokens are highly volatile and can go to zero.

Public site: https://dicnunz.github.io/CHATTY-Revival/

## What This Repo Contains

- `site/` - static public website with disclosure, current-state page, media kit, FAQ, and guidelines.
- `dashboard/` - read-only free public data snapshot workflow.
- `data/snapshots/` - timestamped public metric snapshots.
- `research/` - source notes, current state, and risk notes.
- `content/` - compliant X drafts, reply bank, and meme prompts.
- `telegram/` - pinned message, rules, daily update template, and moderator responses.
- `telegram_bot/` - optional no-dependency bot scaffold that requires a human-provided BotFather token.
- `compliance/` - project compliance brief and phrase rules.
- `logs/` - public audit trail.
- `operator_notes/` - private operational notes for the creator.

## Local Use

Refresh public data:

```bash
python3 dashboard/fetch_snapshot.py
python3 dashboard/render_research.py
```

Run content checks:

```bash
python3 tools/content_linter.py
```

Preview the site locally:

```bash
python3 -m http.server 4173 --directory site
```

Then open `http://localhost:4173`.

## Boundary

This repo intentionally does not trade, move funds, connect wallets, create fake engagement, use paid boosts, DM strangers, or publish posts automatically.
