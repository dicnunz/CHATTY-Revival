# CHATTY Revival

Status: Dormant Autopilot Mode.

CHATTY is an unofficial Solana meme/community token and public AI-assisted transparency experiment by @nicdunz.

Public site: https://dicnunz.github.io/CHATTY-Revival/

Contract / mint:

`jSHyGRfqkGBKdjUPrZXaqPXzFpBTjimJtheWZJRpump`

Canonical disclosure:

> CHATTY is an unofficial meme/community token by @nicdunz. It is not affiliated with OpenAI, ChatGPT, or any other company. The creator may benefit financially from trading activity and/or creator fees. This is not financial advice. No promises, no guarantees. Meme tokens are highly volatile and can go to zero. Do your own research.

## What Dormant Autopilot Means

The project can sit unattended while remaining useful and transparent. Safe automation may refresh read-only public snapshots, update static site data, run link/content/risk checks, and publish GitHub Pages updates.

Autopilot never posts to X or Telegram, DMs anyone, connects wallets, trades, moves crypto, spends money, uses paid APIs, requests funds, creates fake engagement, or makes investment claims.

## No-Promises Policy

CHATTY is not an investment product. The repo and site reject price targets, return claims, urgency, coordinated promotion, paid boosts as marketing, fake engagement, fake screenshots, undisclosed promotion, and affiliation claims.

## No-Spend / No-Wallet Policy

- No paid ads.
- No paid DEX services.
- No paid influencers.
- No paid APIs.
- No domain purchases.
- No community fund.
- No wallet connections.
- No crypto movement by Codex.

## What This Repo Contains

- `site/` - static public site with disclosure, start-here, no-promises, scam warning, verified links, current state, history, receipts, proof of no spend, operator log, media kit, FAQ, and guidelines.
- `dashboard/` - read-only free public data snapshot workflow.
- `data/snapshots/` - timestamped public metric snapshots.
- `site/data/` - static JSON and Markdown data for GitHub Pages.
- `schema/` - simple JSON schemas for public data files.
- `tools/` - content linter, risk monitor, link check, report builders, and static data builders.
- `content/` - dormant content library and do-not-post rules.
- `telegram/` - dormant-mode pinned update drafts and safety notices.
- `compliance/` - project compliance brief and phrase rules.
- `logs/` - public audit trail.
- `operator_notes/` - private operational notes for the creator.

## Automation Scope

GitHub Actions may:

- Refresh read-only public token data.
- Rebuild site JSON.
- Run content/risk/link checks.
- Generate weekly transparency and monthly health reports.
- Commit safe repo/site updates.
- Publish through GitHub Pages.

GitHub Actions must not:

- Post to X or Telegram.
- DM anyone.
- Trade or move assets.
- Connect wallets.
- Spend money or call paid APIs.
- Request funds.
- Create fake engagement.
- Make investment claims.

## Local Use

Refresh public data:

```bash
python3 dashboard/fetch_snapshot.py
python3 dashboard/render_research.py
python3 tools/build_autopilot_data.py
```

Run checks:

```bash
python3 tools/content_linter.py
python3 tools/risk_monitor.py
python3 tools/link_check.py
```

Preview the site locally:

```bash
python3 -m http.server 4173 --directory site
```

Then open `http://localhost:4173`.

## How To Verify

Use `site/how-to-verify.html` or the live page. Match the exact contract string, compare this repo with the public site, and use public explorers. Do not rely on DMs or screenshots.

## Report Scams Or Data Issues

Use GitHub Issues if available:

- Scam report
- Broken link
- Data error

Do not include private keys, seed phrases, passwords, payment details, private messages, or wallet screenshots.

## Contribute Safely

Contributions should improve clarity, accessibility, source notes, disclosures, or scam resistance. Do not add hype, buy pressure, fake affiliation, wallet prompts, fund requests, or social automation.
