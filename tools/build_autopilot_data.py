#!/usr/bin/env python3
"""Build static CHATTY autopilot data files from local public snapshots."""

from __future__ import annotations

import datetime as dt
import json
import os
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_DIR = ROOT / "data" / "snapshots"
SITE_DATA = ROOT / "site" / "data"
UNAVAILABLE = "Unavailable from free public snapshot"
TOKEN_ADDRESS = "jSHyGRfqkGBKdjUPrZXaqPXzFpBTjimJtheWZJRpump"
PAIR_ADDRESS = "CJazvo7knaRsgqUbNkmwFv5UKuRXqZXT4C4RaW1Eybhh"


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def load_snapshots() -> list[dict[str, Any]]:
    snapshots: list[dict[str, Any]] = []
    for path in sorted(SNAPSHOT_DIR.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        current = data.get("current", {})
        if current.get("token_address") != TOKEN_ADDRESS:
            raise SystemExit(f"Refusing wrong-token snapshot: {path}")
        snapshots.append({"path": str(path.relative_to(ROOT)), "snapshot": data})
    return snapshots


def source_confidence(source: dict[str, Any]) -> str:
    if source.get("ok"):
        return "verified"
    error = str(source.get("error", "")).lower()
    if "403" in error or "unauthorized" in error or "forbidden" in error:
        return "blocked"
    return "unavailable"


def history_rows(snapshots: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in snapshots:
        c = item["snapshot"]["current"]
        rows.append(
            {
                "timestamp": c.get("timestamp") or UNAVAILABLE,
                "source_file": item["path"],
                "token_address": c.get("token_address") or TOKEN_ADDRESS,
                "price_usd": c.get("price_usd") or UNAVAILABLE,
                "market_cap_usd": c.get("market_cap_usd") or UNAVAILABLE,
                "liquidity_usd": c.get("liquidity_usd") or UNAVAILABLE,
                "volume_h24_usd": c.get("volume_h24_usd") or UNAVAILABLE,
                "holders": c.get("holders") or UNAVAILABLE,
                "bonding_curve_progress": c.get("bonding_curve_progress") or UNAVAILABLE,
                "notes": "Volatile historical public snapshot; not a trading signal.",
            }
        )
    return rows


def build_source_status(latest: dict[str, Any] | None) -> dict[str, Any]:
    sources = latest.get("sources", {}) if latest else {}
    rows = []
    for key, source in sorted(sources.items()):
        rows.append(
            {
                "key": key,
                "label": source.get("label", key),
                "url": source.get("url", UNAVAILABLE),
                "ok": bool(source.get("ok")),
                "confidence": source_confidence(source),
                "error": source.get("error") or "",
            }
        )
    rows.extend(
        [
            {
                "key": "x_post_url",
                "label": "Initial X transparency post URL",
                "url": UNAVAILABLE,
                "ok": False,
                "confidence": "unavailable",
                "error": "URL was not available from the browser/session or exact public search.",
            },
            {
                "key": "telegram_public_link",
                "label": "Telegram public link",
                "url": UNAVAILABLE,
                "ok": False,
                "confidence": "manual",
                "error": "No intentionally public Telegram link is known.",
            },
        ]
    )
    return {
        "timestamp": now_iso(),
        "token_address": TOKEN_ADDRESS,
        "source_status": rows,
        "confidence_labels": ["verified", "unavailable", "blocked", "manual", "stale"],
        "note": "Unavailable means unavailable from the free read-only snapshot, not zero.",
    }


def build_manifest() -> dict[str, Any]:
    return {
        "name": "chatty",
        "ticker": "CHATTY",
        "mode": "Dormant Autopilot Mode",
        "site_url": "https://dicnunz.github.io/CHATTY-Revival/",
        "repo_url": "https://github.com/dicnunz/CHATTY-Revival",
        "creator_x": "https://x.com/nicdunz",
        "telegram": UNAVAILABLE,
        "token_address": TOKEN_ADDRESS,
        "pair_address": PAIR_ADDRESS,
        "disclosure": "CHATTY is an unofficial meme/community token by @nicdunz. It is not affiliated with OpenAI, ChatGPT, or any other company. The creator may benefit financially from trading activity and/or creator fees. This is not financial advice. No promises, no guarantees. Meme tokens are highly volatile and can go to zero. Do your own research.",
        "autopilot_scope": [
            "read-only public data snapshots",
            "static site updates",
            "risk/content checks",
            "weekly transparency reports",
            "link and health checks",
        ],
        "never_automated": [
            "X posts",
            "Telegram posts",
            "DMs",
            "wallet connections",
            "trading",
            "payments",
            "fund requests",
            "fake engagement",
        ],
    }


def build_autopilot_status(final: bool = False) -> dict[str, Any]:
    run_url = os.environ.get("GITHUB_RUN_ID", "")
    pages_run = f"https://github.com/dicnunz/CHATTY-Revival/actions/runs/{run_url}" if run_url else "Unavailable from local run"
    return {
        "mode": "Dormant Autopilot Mode",
        "timestamp": now_iso(),
        "commit": git_commit(),
        "pages_run": pages_run,
        "no_wallet_connected": True,
        "no_crypto_moved": True,
        "no_money_spent": True,
        "no_paid_services": True,
        "no_social_autoposting": True,
        "no_investment_claims": True,
        "dormant": True,
        "final": final,
    }


def main() -> int:
    SITE_DATA.mkdir(parents=True, exist_ok=True)
    snapshots = load_snapshots()
    latest = snapshots[-1]["snapshot"] if snapshots else None
    history = {
        "timestamp": now_iso(),
        "token_address": TOKEN_ADDRESS,
        "note": "Volatile historical public snapshots, not trading signals.",
        "snapshots": history_rows(snapshots),
    }
    (SITE_DATA / "history.json").write_text(json.dumps(history, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (SITE_DATA / "source_status.json").write_text(json.dumps(build_source_status(latest), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (SITE_DATA / "project_manifest.json").write_text(json.dumps(build_manifest(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    status = build_autopilot_status(final=False)
    (SITE_DATA / "autopilot_status.json").write_text(json.dumps(status, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (SITE_DATA / "final_autopilot_status.json").write_text(json.dumps(build_autopilot_status(final=True), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("Built autopilot data files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
