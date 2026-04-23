# Free Deployment Steps

No paid hosting, paid domains, payment cards, or wallet connections are needed.

## GitHub Pages

1. Review `DISCLAIMER.md`, `site/disclosure.html`, and `content/x_drafts_week_1.md`.
2. Create a GitHub repository manually if desired.
3. Push this repo.
4. In GitHub repo settings, enable Pages.
5. Set Pages source to the `main` branch and `/site` folder.
6. After publish, replace `[website link pending]` in Telegram/content drafts with the GitHub Pages URL.

## Cloudflare Pages Free Tier

1. Create a new Pages project from the repo.
2. Build command: leave blank.
3. Output directory: `site`.
4. Do not add paid services, domains, or payment details.

## Netlify Free Tier

1. Create a new site from the repo.
2. Build command: leave blank.
3. Publish directory: `site`.
4. Do not add paid services, domains, or payment details.

## Before Publishing

```bash
python3 dashboard/fetch_snapshot.py
python3 dashboard/render_research.py
python3 tools/content_linter.py
python3 -m http.server 4173 --directory site
```

Review `http://localhost:4173` manually before sharing.

