#!/usr/bin/env python3
"""Tiny CHATTY Telegram bot using the public Bot API.

Requires CHATTY_TELEGRAM_BOT_TOKEN in the local environment.
Does not DM, trade, delete, moderate, or join other groups.
"""

from __future__ import annotations

import json
import os
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TOKEN = os.environ.get("CHATTY_TELEGRAM_BOT_TOKEN")
CONTRACT = "jSHyGRfqkGBKdjUPrZXaqPXzFpBTjimJtheWZJRpump"
DISCLOSURE = (
    "CHATTY is unofficial and not affiliated with OpenAI/ChatGPT. "
    "The creator may benefit from trading/creator fees. Not financial advice. "
    "No promises. Can go to zero."
)


def api(method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    if not TOKEN:
        raise SystemExit("Set CHATTY_TELEGRAM_BOT_TOKEN locally first.")
    query = urllib.parse.urlencode(params or {})
    url = f"https://api.telegram.org/bot{TOKEN}/{method}"
    if query:
        url += f"?{query}"
    with urllib.request.urlopen(url, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def snapshot_text() -> str:
    path = ROOT / "site" / "data" / "token_snapshot.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return "Stats unavailable. Run dashboard/fetch_snapshot.py and dashboard/render_research.py."
    return (
        f"Snapshot: {data.get('timestamp', 'unavailable')}\n"
        f"Price: {data.get('price_usd', 'unavailable')}\n"
        f"Market cap: {data.get('market_cap_usd', 'unavailable')}\n"
        f"Liquidity: {data.get('liquidity_usd', 'unavailable')}\n"
        f"24h volume: {data.get('volume_h24_usd', 'unavailable')}\n"
        "Data is volatile and not a recommendation."
    )


def response_for(text: str) -> str | None:
    command = text.strip().split()[0].lower()
    if command == "/contract":
        return f"CHATTY contract / mint:\n`{CONTRACT}`\n\n{DISCLOSURE}"
    if command == "/disclosure":
        return DISCLOSURE
    if command == "/rules":
        return "No spam. No financial advice. No price promises. No fake screenshots. No impersonation. No group trading plans. Report scam links."
    if command == "/stats":
        return f"{snapshot_text()}\n\n{DISCLOSURE}"
    if command == "/faq":
        return "CHATTY is an unofficial meme/community experiment by @nicdunz. It is not affiliated with OpenAI/ChatGPT. It can go to zero."
    return None


def main() -> int:
    offset = 0
    while True:
        updates = api("getUpdates", {"offset": offset, "timeout": 25}).get("result", [])
        for update in updates:
            offset = update["update_id"] + 1
            message = update.get("message") or {}
            chat = message.get("chat") or {}
            text = message.get("text") or ""
            reply = response_for(text)
            if reply and chat.get("id"):
                api("sendMessage", {"chat_id": chat["id"], "text": reply, "parse_mode": "Markdown"})
        time.sleep(1)


if __name__ == "__main__":
    raise SystemExit(main())
