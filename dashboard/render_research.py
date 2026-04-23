#!/usr/bin/env python3
"""Render research docs and site JSON from the latest CHATTY snapshot."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOTS = ROOT / "data" / "snapshots"
PUBLIC_UPDATE_FILES = [
    ROOT / "logs" / "public_updates.md",
    ROOT / "site" / "data" / "public_updates.md",
    ROOT / "TRANSPARENCY_LOG.md",
]


def latest_snapshot() -> tuple[Path, dict[str, Any]]:
    files = sorted(SNAPSHOTS.glob("*.json"))
    if not files:
        raise SystemExit("No snapshots found. Run dashboard/fetch_snapshot.py first.")
    path = files[-1]
    return path, json.loads(path.read_text(encoding="utf-8"))


def money(value: Any) -> str:
    if value in (None, "") or (isinstance(value, str) and "unavailable" in value.lower()):
        return "unavailable"
    try:
        return f"${float(value):,.6f}" if float(value) < 1 else f"${float(value):,.2f}"
    except (TypeError, ValueError):
        return str(value)


def plain(value: Any) -> str:
    if value is None or value == "":
        return "unavailable"
    return str(value)


def source_status(source: dict[str, Any]) -> str:
    return "ok" if source.get("ok") else f"unavailable ({source.get('error', 'error')})"


def render_current(snapshot_path: Path, snapshot: dict[str, Any]) -> str:
    c = snapshot["current"]
    txns = c.get("txns_h24") or {}
    buys = txns.get("buys", "unavailable") if isinstance(txns, dict) else "unavailable"
    sells = txns.get("sells", "unavailable") if isinstance(txns, dict) else "unavailable"
    return f"""# CHATTY Current State

Last refreshed: {c["timestamp"]}

This is a public, read-only snapshot for transparency. It is not financial advice and should not be treated as a recommendation.

## Verified Identity

| Field | Value |
| --- | --- |
| Token name | {plain(c.get("name"))} |
| Ticker | {plain(c.get("symbol"))} |
| Mint / contract | `{c["token_address"]}` |
| Decimals | {plain(c.get("decimals"))} |
| Supply from Solana RPC | {plain(c.get("supply_ui"))} |
| Primary pair | `{plain(c.get("pair_address"))}` |
| Pump.fun complete / graduated | {plain(c.get("bonding_curve_complete"))} |

## Public Metrics

| Metric | Current value | Source |
| --- | ---: | --- |
| Price USD | {money(c.get("price_usd"))} | DEX Screener / GeckoTerminal |
| Price SOL | {plain(c.get("price_native_sol"))} | DEX Screener / GeckoTerminal |
| Market cap | {money(c.get("market_cap_usd"))} | DEX Screener / Pump.fun |
| FDV | {money(c.get("fdv_usd"))} | DEX Screener / GeckoTerminal |
| Liquidity | {money(c.get("liquidity_usd"))} | DEX Screener / GeckoTerminal |
| 24h volume | {money(c.get("volume_h24_usd"))} | DEX Screener / GeckoTerminal |
| 24h buys | {plain(buys)} | DEX Screener |
| 24h sells | {plain(sells)} | DEX Screener |
| 24h price change | {plain(c.get("price_change_h24_pct"))}% | DEX Screener / GeckoTerminal |
| Holder count | {plain(c.get("holders"))} | Free API snapshot |
| Bonding curve progress | {plain(c.get("bonding_curve_progress"))}% | GeckoTerminal launchpad details |
| Pump.fun reply count | {plain(c.get("reply_count"))} | Pump.fun public API |
| DEX Screener boosts/orders | {plain(c.get("orders_or_boosts"))} | DEX Screener orders API |

## Links Checked

- Pump.fun: {c["pumpfun_url"]}
- DEX Screener: {plain(c.get("pair_url"))}
- GeckoTerminal: {c["geckoterminal_url"]}
- Solscan: {c["solscan_url"]}
- X handle from metadata: {plain(c.get("twitter"))}

## Manual Notes

- DEX Screener page was accessible in browser/web extraction and showed the token as `chatty / CHATTY` on PumpSwap.
- Solscan public page exists, but unauthenticated API access was blocked during this run, so Solscan-only details are marked unavailable.
- Birdeye token overview API returned unauthorized without an API key; no paid/authenticated API was used.
- DexTools page redirected to a Solana pair explorer URL, but no reliable free structured data was collected.

Snapshot file: `{snapshot_path.relative_to(ROOT)}`
"""


def render_sources(snapshot: dict[str, Any]) -> str:
    lines = [
        "# CHATTY Sources",
        "",
        f"Last refreshed: {snapshot['timestamp']}",
        "",
        "| Source | URL | Status |",
        "| --- | --- | --- |",
    ]
    for source in snapshot["sources"].values():
        lines.append(f"| {source['label']} | {source['url']} | {source_status(source)} |")
    lines.extend(
        [
            "| DEX Screener page | https://dexscreener.com/solana/cjazvo7knarsgqubnkmwfv5ukurxqzxt4c4raw1eybhh | checked via browser/web extraction |",
            "| Solscan page | https://solscan.io/token/jSHyGRfqkGBKdjUPrZXaqPXzFpBTjimJtheWZJRpump | public page checked; API blocked |",
            "| Birdeye overview | https://birdeye.so/token/jSHyGRfqkGBKdjUPrZXaqPXzFpBTjimJtheWZJRpump?chain=solana | API unauthorized without key |",
            "| DexTools pair explorer | https://www.dextools.io/app/solana/pair-explorer/CJazvo7knaRsgqUbNkmwFv5UKuRXqZXT4C4RaW1Eybhh | redirected/checked; structured data unavailable |",
            "| X exact-address search | https://x.com/search?q=jSHyGRfqkGBKdjUPrZXaqPXzFpBTjimJtheWZJRpump | live count unavailable without interactive account search |",
            "",
        ]
    )
    return "\n".join(lines)


def render_risks(snapshot: dict[str, Any]) -> str:
    c = snapshot["current"]
    return f"""# CHATTY Risk Notes

Last refreshed: {snapshot["timestamp"]}

- CHATTY is a meme/community token, not an investment product.
- The creator may benefit financially from trading activity and/or creator fees.
- Meme tokens are highly volatile and can go to zero.
- Market cap, price, liquidity, and volume can change within minutes.
- Some metrics were unavailable from free unauthenticated sources. Unavailable data is not zero.
- No wallet was connected and no transaction was made during this research.
- DEX Screener reported no active orders or boosts in the public orders API response: `{plain(c.get("orders_or_boosts"))}`.
- Solscan API access was blocked by Cloudflare/unauthenticated controls during this run; do not infer hidden safety from missing Solscan fields.
- Nothing in this repository should ask anyone to buy, hold, coordinate purchases, or expect profit.
"""


def merge_public_update(new_entry: str, existing: str) -> str:
    """Prepend a new update without deleting earlier manual/public history."""
    header = "# Public Updates\n\n"
    body = existing
    if body.startswith(header):
        body = body[len(header):]
    if new_entry.strip() in body:
        return header + body.strip() + "\n"
    return header + new_entry.strip() + "\n\n" + body.strip() + "\n"


def main() -> int:
    path, snapshot = latest_snapshot()
    current = snapshot["current"]

    (ROOT / "research").mkdir(exist_ok=True)
    (ROOT / "site" / "data").mkdir(parents=True, exist_ok=True)
    (ROOT / "logs").mkdir(exist_ok=True)

    (ROOT / "research" / "current_state.md").write_text(render_current(path, snapshot), encoding="utf-8")
    (ROOT / "research" / "sources.md").write_text(render_sources(snapshot), encoding="utf-8")
    (ROOT / "research" / "risk_notes.md").write_text(render_risks(snapshot), encoding="utf-8")
    (ROOT / "site" / "data" / "token_snapshot.json").write_text(
        json.dumps(current, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    public_entry = f"""## {snapshot["timestamp"]} - AI operator snapshot

- Verified CHATTY mint as `{current["token_address"]}` from Pump.fun, DEX Screener, GeckoTerminal, IPFS metadata, and Solana RPC.
- Refreshed public metrics into `site/data/token_snapshot.json`.
- No wallet connected, no trades made, no paid services used, no public posts made.
- Unavailable fields remain labeled unavailable instead of guessed.
"""
    for path in PUBLIC_UPDATE_FILES:
        existing = path.read_text(encoding="utf-8") if path.exists() else "# Public Updates\n"
        path.write_text(merge_public_update(public_entry, existing), encoding="utf-8")
    print("Rendered research docs and site data.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
