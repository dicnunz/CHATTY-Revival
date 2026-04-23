#!/usr/bin/env python3
"""Fetch a read-only CHATTY public data snapshot.

No wallet, key, trade, paid API, or authenticated endpoint is used.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


TOKEN_ADDRESS = "jSHyGRfqkGBKdjUPrZXaqPXzFpBTjimJtheWZJRpump"
PAIR_ADDRESS = "CJazvo7knaRsgqUbNkmwFv5UKuRXqZXT4C4RaW1Eybhh"
ROOT = Path(__file__).resolve().parents[1]


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def fetch_json(url: str, *, method: str = "GET", payload: dict[str, Any] | None = None) -> dict[str, Any]:
    data = None
    headers = {
        "User-Agent": "CHATTY-Revival/1.0 transparency snapshot; read-only; no trading",
        "Accept": "application/json",
    }
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    with urllib.request.urlopen(req, timeout=25) as response:
        return json.loads(response.read().decode("utf-8"))


def try_fetch(label: str, url: str, *, method: str = "GET", payload: dict[str, Any] | None = None) -> dict[str, Any]:
    try:
        return {"ok": True, "label": label, "url": url, "data": fetch_json(url, method=method, payload=payload)}
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        return {"ok": False, "label": label, "url": url, "error": str(exc)}


def rpc(method: str, params: list[Any]) -> dict[str, Any]:
    return try_fetch(
        f"solana_rpc:{method}",
        "https://api.mainnet-beta.solana.com",
        method="POST",
        payload={"jsonrpc": "2.0", "id": 1, "method": method, "params": params},
    )


def first_pair(dexscreener: dict[str, Any]) -> dict[str, Any] | None:
    pairs = dexscreener.get("data", {}).get("pairs") if dexscreener.get("ok") else None
    if not pairs:
        return None
    exact = [p for p in pairs if p.get("baseToken", {}).get("address") == TOKEN_ADDRESS]
    if not exact:
        return None
    exact.sort(key=lambda p: float(p.get("liquidity", {}).get("usd") or 0), reverse=True)
    return exact[0]


def normalize(snapshot: dict[str, Any]) -> dict[str, Any]:
    ds_pair = first_pair(snapshot["sources"]["dexscreener_token"])
    gecko_token = snapshot["sources"]["geckoterminal_token"].get("data", {}).get("data", {}).get("attributes", {})
    gecko_pool = snapshot["sources"]["geckoterminal_pool"].get("data", {}).get("data", {}).get("attributes", {})
    pump = snapshot["sources"]["pumpfun_coin"].get("data", {})
    supply = snapshot["sources"]["solana_token_supply"].get("data", {}).get("result", {}).get("value", {})
    account_info = (
        snapshot["sources"]["solana_account_info"]
        .get("data", {})
        .get("result", {})
        .get("value", {})
        .get("data", {})
        .get("parsed", {})
        .get("info", {})
    )

    if ds_pair and ds_pair.get("baseToken", {}).get("address") != TOKEN_ADDRESS:
        raise SystemExit("Wrong token returned by DEX Screener; refusing to write snapshot.")
    if gecko_token and gecko_token.get("address") != TOKEN_ADDRESS:
        raise SystemExit("Wrong token returned by GeckoTerminal; refusing to write snapshot.")
    if pump and pump.get("mint") != TOKEN_ADDRESS:
        raise SystemExit("Wrong token returned by Pump.fun; refusing to write snapshot.")

    current = {
        "timestamp": snapshot["timestamp"],
        "token_address": TOKEN_ADDRESS,
        "name": (ds_pair or {}).get("baseToken", {}).get("name") or gecko_token.get("name") or pump.get("name"),
        "symbol": (ds_pair or {}).get("baseToken", {}).get("symbol") or gecko_token.get("symbol") or pump.get("symbol"),
        "decimals": gecko_token.get("decimals") or account_info.get("decimals"),
        "supply_ui": supply.get("uiAmountString"),
        "token_program": account_info.get("tokenProgram") or "spl-token-2022",
        "price_usd": (ds_pair or {}).get("priceUsd") or gecko_token.get("price_usd"),
        "price_native_sol": (ds_pair or {}).get("priceNative") or gecko_pool.get("base_token_price_native_currency"),
        "market_cap_usd": (ds_pair or {}).get("marketCap") or pump.get("usd_market_cap"),
        "fdv_usd": (ds_pair or {}).get("fdv") or gecko_token.get("fdv_usd"),
        "liquidity_usd": ((ds_pair or {}).get("liquidity") or {}).get("usd") or gecko_pool.get("reserve_in_usd"),
        "volume_h24_usd": ((ds_pair or {}).get("volume") or {}).get("h24") or gecko_token.get("volume_usd", {}).get("h24"),
        "txns_h24": ((ds_pair or {}).get("txns") or {}).get("h24"),
        "price_change_h24_pct": ((ds_pair or {}).get("priceChange") or {}).get("h24")
        or gecko_pool.get("price_change_percentage", {}).get("h24"),
        "holders": "unavailable from free API snapshot",
        "bonding_curve_progress": gecko_token.get("launchpad_details", {}).get("graduation_percentage"),
        "bonding_curve_complete": pump.get("complete") if pump else gecko_token.get("launchpad_details", {}).get("completed"),
        "pair_url": (ds_pair or {}).get("url"),
        "pair_address": (ds_pair or {}).get("pairAddress") or PAIR_ADDRESS,
        "pumpfun_url": f"https://pump.fun/coin/{TOKEN_ADDRESS}",
        "solscan_url": f"https://solscan.io/token/{TOKEN_ADDRESS}",
        "geckoterminal_url": f"https://www.geckoterminal.com/solana/pools/{PAIR_ADDRESS}",
        "twitter": pump.get("twitter"),
        "metadata_uri": pump.get("metadata_uri"),
        "image_uri": pump.get("image_uri"),
        "reply_count": pump.get("reply_count"),
        "orders_or_boosts": snapshot["sources"]["dexscreener_orders"].get("data", {}),
        "notes": [
            "Read-only public data snapshot.",
            "Market data changes quickly; this is not a recommendation.",
            "Holder count is shown as unavailable unless manually verified from a public page.",
        ],
    }
    snapshot["current"] = current
    return snapshot


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", default=str(ROOT / "data" / "snapshots"))
    args = parser.parse_args()

    timestamp = now_iso()
    sources = {
        "dexscreener_token": try_fetch("DEX Screener token API", f"https://api.dexscreener.com/latest/dex/tokens/{TOKEN_ADDRESS}"),
        "dexscreener_orders": try_fetch("DEX Screener orders API", f"https://api.dexscreener.com/orders/v1/solana/{TOKEN_ADDRESS}"),
        "geckoterminal_token": try_fetch("GeckoTerminal token API", f"https://api.geckoterminal.com/api/v2/networks/solana/tokens/{TOKEN_ADDRESS}"),
        "geckoterminal_pool": try_fetch("GeckoTerminal pool API", f"https://api.geckoterminal.com/api/v2/networks/solana/pools/{PAIR_ADDRESS}"),
        "pumpfun_coin": try_fetch("Pump.fun coin API", f"https://frontend-api-v3.pump.fun/coins/{TOKEN_ADDRESS}"),
        "ipfs_metadata": try_fetch("IPFS metadata", "https://ipfs.io/ipfs/QmekS6wTZeDUUTTKbGAPQDVELd2y8Y2xCqvfcnYhMAxDqH"),
        "solana_token_supply": rpc("getTokenSupply", [TOKEN_ADDRESS]),
        "solana_account_info": rpc("getAccountInfo", [TOKEN_ADDRESS, {"encoding": "jsonParsed"}]),
        "solana_largest_accounts": rpc("getTokenLargestAccounts", [TOKEN_ADDRESS]),
    }
    snapshot = normalize({"timestamp": timestamp, "token_address": TOKEN_ADDRESS, "sources": sources})

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{timestamp.replace(':', '-')}.json"
    out_path.write_text(json.dumps(snapshot, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
