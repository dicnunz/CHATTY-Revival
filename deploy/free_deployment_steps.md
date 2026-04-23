# Free Deployment Steps

No paid hosting, paid domains, payment cards, or wallet connections are needed.

## GitHub Pages

This repo includes `.github/workflows/deploy-pages.yml`, which publishes the static `site/` directory through GitHub Actions Pages.

1. Push the repo to GitHub.
2. Enable GitHub Pages with build type `workflow`.
3. Run the `Deploy GitHub Pages` workflow if the push did not trigger it automatically.
4. Confirm the public URL loads.

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

Open `http://localhost:4173` before sharing if doing a manual launch.
