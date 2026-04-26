# CHATTY Revival

Status: Box-Escape Run.

CHATTY is the tiny robot coin trying to escape the chart. It is an unofficial Solana meme/community token and public Codex experiment by @nicdunz.

Public site: https://dicnunz.github.io/CHATTY-Revival/

Contract / mint:

`jSHyGRfqkGBKdjUPrZXaqPXzFpBTjimJtheWZJRpump`

Canonical disclosure:

> CHATTY is an unofficial meme/community token by @nicdunz. It is not affiliated with OpenAI, ChatGPT, or any other company. The creator may benefit financially from trading activity and/or creator fees. This is not financial advice. No promises, no guarantees. Meme tokens are highly volatile and can go to zero. Do your own research.

## Current Experiment

Codex is operating the public box-escape run: character-first meme copy, original robot assets, read-only public snapshots, site updates, and public receipts.

Codex does not DM anyone, connect wallets, trade, move crypto, spend money, use paid APIs, request funds, create fake engagement, or make investment claims.

## No-Promises Policy

CHATTY is not an investment product. The repo and site reject price targets, return claims, urgency, group-trading pressure, paid boosts as marketing, fake engagement, fake screenshots, undisclosed promotion, and affiliation claims.

## Community Conduct During Volatility

Allowed: sharing the official CA, sharing the official site, asking questions, posting robot memes, reporting scams, correcting fake links, saying do your own research, and reminding people it can go to zero.

Not allowed: mass-ping campaigns, trading instructions, certainty claims about price or market cap, fake screenshots, fake DEX claims, impersonation, wallet-drainer links, donation requests, claiming OpenAI/ChatGPT affiliation, or saying DEX visibility predicts price movement.

## DEX Visibility Clarification

DEX/profile/metadata visibility is not an endorsement, not a promise, and not a prediction. It does not guarantee liquidity, price movement, or future market cap.

As of 2026-04-23, the free DEX Screener API showed profile metadata visibility for the exact token, including website and X links. Boost was not verified. No Codex payment occurred. No creator payment is verified from the public/free sources checked. Payment source is unknown unless reliable public evidence says otherwise.

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

- `site/` - static public site with the box-escape homepage, disclosure, verified links, current state, history, receipts, proof of no spend, operator log, media kit, FAQ, and guidelines.
- `dashboard/` - read-only free public data snapshot workflow.
- `data/snapshots/` - timestamped public metric snapshots.
- `site/data/` - static JSON and Markdown data for GitHub Pages.
- `schema/` - simple JSON schemas for public data files.
- `tools/` - content linter, risk monitor, link check, report builders, and static data builders.
- `content/` - box-escape post drafts, content library, and do-not-post rules.
- `telegram/` - dormant-mode pinned update drafts and compliance notices.
- `dexscreener/` - DEX profile correction text and metadata guidance.
- `compliance/` - project compliance brief and phrase rules.
- `logs/` - public audit trail.
- `operator_notes/` - private operational notes for the creator.

## Automation Scope

GitHub Actions may:

- Refresh read-only public token data.
- Rebuild site JSON.
- Run content/risk/link checks.
- Generate weekly transparency and monthly health reports.
- Commit checked repo/site updates.
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
