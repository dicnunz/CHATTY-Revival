#!/usr/bin/env python3
"""Generate a conservative weekly CHATTY transparency report."""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_DIR = ROOT / "data" / "snapshots"
OUT = ROOT / "logs" / "weekly_transparency_report.md"
SITE_OUT = ROOT / "site" / "data" / "weekly_transparency_report.md"
TOKEN_ADDRESS = "jSHyGRfqkGBKdjUPrZXaqPXzFpBTjimJtheWZJRpump"


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_latest() -> dict:
    files = sorted(SNAPSHOT_DIR.glob("*.json"))
    if not files:
        return {}
    return json.loads(files[-1].read_text(encoding="utf-8")).get("current", {})


def main() -> int:
    current = load_latest()
    body = f"""# Weekly CHATTY Transparency Report

Generated: {now_iso()}

Mode: Dormant Autopilot Mode

## Current Snapshot

- Token address: `{TOKEN_ADDRESS}`
- Latest snapshot timestamp: {current.get("timestamp", "Snapshot unavailable")}
- Price: {current.get("price_usd", "Unavailable from free public snapshot")}
- Market cap: {current.get("market_cap_usd", "Unavailable from free public snapshot")}
- Liquidity: {current.get("liquidity_usd", "Unavailable from free public snapshot")}
- 24h volume: {current.get("volume_h24_usd", "Unavailable from free public snapshot")}
- Holders: {current.get("holders", "Unavailable from free public snapshot")}

Unavailable means unavailable from the free read-only snapshot, not zero.

## Safety Posture

- No wallet action is part of this project.
- No trading, buying, selling, swaps, transfers, burns, locks, or bridges are performed.
- No paid boosts, paid DEX services, ads, influencers, paid APIs, domains, or bots are used.
- No X or Telegram posting is automated.
- No DMs, fake engagement, or coordinated promotion are used.
- Nothing here is financial advice. No promises, no guarantees. Meme tokens can go to zero.

## Manual Action Needed

None required. Human intervention is optional and should remain conservative.
"""
    OUT.write_text(body, encoding="utf-8")
    SITE_OUT.parent.mkdir(parents=True, exist_ok=True)
    SITE_OUT.write_text(body, encoding="utf-8")
    print("weekly transparency report written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
