#!/usr/bin/env python3
"""Risk monitor for CHATTY static files and drafts."""

from __future__ import annotations

import datetime as dt
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOKEN_ADDRESS = "jSHyGRfqkGBKdjUPrZXaqPXzFpBTjimJtheWZJRpump"
PAIR_ADDRESS = "CJazvo7knaRsgqUbNkmwFv5UKuRXqZXT4C4RaW1Eybhh"
UNAVAILABLE = "Unavailable from free public snapshot"
LOG_PATH = ROOT / "logs" / "risk_alerts.md"

BANNED = {
    r"\bbuy now\b": "buy-pressure phrase",
    r"\bguaranteed\b": "guarantee phrase",
    r"\brisk[- ]?free\b": "risk-free phrase",
    r"\b100x\b": "return hype",
    r"\bmoon soon\b": "price hype",
    r"\bsend it\b": "hype phrase",
    r"\bsendor\b": "hype phrase",
    r"\blfg\b": "hype phrase",
    r"\b1m\b": "market-cap target",
    r"\b100k soon\b": "market-cap target",
    r"\bmillions\b": "market-cap target",
    r"\bmillion coded\b": "market-cap target",
    r"\bbuy every dip\b": "buy-pressure phrase",
    r"\bdon[’']t fade\b": "urgency/pressure phrase",
    r"\bnext stop\b": "price/market-cap target",
    r"\bdiamond hand\b": "hold-pressure phrase",
    r"\bape in\b": "buy-pressure phrase",
    r"\beasy money\b": "profit hype",
    r"\bnext doge\b": "comparative profit hype",
    r"\binsider\b": "insider implication",
    r"\blisting soon\b": "unverified listing claim",
    r"\bburn coming\b": "profit-support roadmap claim",
    r"\bbuyback\b": "profit-support claim",
    r"\block supply\b": "profit-support claim",
    r"\braid(?: this)?\b": "coordination/spam phrase",
    r"\braids\b": "coordination/spam phrase",
    r"\bofficial chatgpt\b": "false affiliation",
    r"\bofficial openai\b": "false affiliation",
    r"\bdex paid officially\b": "unverified DEX/payment claim",
    r"\bwith dex this moon hard\b": "DEX price-hype claim",
    r"\bmoon hard\b": "price hype",
    r"\bdev followed by chatgpt\b": "affiliation/endorsement implication",
    r"\bofficial launch\b": "official-status implication",
    r"\bendorsed by chatgpt\b": "false endorsement",
    r"\bchatgpt mascot\b": "affiliation/confusion phrase",
    r"\bopenai mascot\b": "affiliation/confusion phrase",
    r"\bcreator rewards\b": "fund/reward language",
    r"\bdonations\b": "fund collection language",
    r"\bwallet for donations\b": "fund collection language",
    r"\babout to explode\b": "price hype",
}

ALLOWED_CONTEXTS = [
    "not financial advice",
    "no financial advice",
    "no buy recommendation",
    "does not tell anyone to buy",
    "do not ask anyone to buy",
    "no instruction to buy",
    "no buy pressure",
    "rejects price targets",
    "rejects coordinated pumps",
    "no coordinated pumping",
    "coordinated pumps",
    "Pump.fun",
    "no spam",
    "anti-spam",
    "no-pump",
    "pump coordination",
    "no public investment claims",
    "not allowed",
    "remove or warn",
    "warn or remove",
    "do not include",
    "do not post",
    "do not use",
    "never",
    "rejects",
    "avoid",
    "warned on",
    "examples of what not to post",
    "risky wording",
    "risky dex profile wording",
    "found risky dex",
    "safer replacement",
    "not found",
    "remove `",
    "safe correction",
    "explicitly forbidden",
]

SCAN_DIRS = ["site", "content", "telegram", "compliance", "strategy", "logs", "dexscreener"]
SCAN_SUFFIXES = {".html", ".md", ".js", ".json", ".yml", ".yaml", ".py"}
ALLOWED_ADDRESSES = {TOKEN_ADDRESS, PAIR_ADDRESS}
ALLOWED_ADDRESSES.update({TOKEN_ADDRESS.lower(), PAIR_ADDRESS.lower()})
EXEMPT_BANNED_LIST_FILES = {
    Path("compliance/compliance_brief.md"),
    Path("content/content_policy_linter.md"),
    Path("telegram/remove_or_warn_phrases.md"),
    Path("telegram/moderation_rules_active_market.md"),
    Path("telegram/hype_control_admin_note.md"),
    Path("telegram/group_settings_safety_recommendations.md"),
    Path("dexscreener/profile_correction_request.md"),
}
PUBLIC_DISCLOSURE_PATHS = {
    Path("README.md"),
    Path("AUTOPILOT_POLICY.md"),
    Path("NO_PROMISES.md"),
    Path("SCAM_WARNING.md"),
    Path("SECURITY.md"),
}


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def masked(text: str) -> str:
    out = text
    for phrase in ALLOWED_CONTEXTS:
        out = re.sub(re.escape(phrase), "_" * len(phrase), out, flags=re.IGNORECASE)
    return out


def files_to_scan() -> list[Path]:
    files: list[Path] = []
    for dirname in SCAN_DIRS:
        root = ROOT / dirname
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.is_file() and path.suffix.lower() in SCAN_SUFFIXES:
                files.append(path)
    files.extend([ROOT / "README.md", ROOT / "DISCLAIMER.md", ROOT / "AUTOPILOT_POLICY.md", ROOT / "NO_PROMISES.md", ROOT / "SCAM_WARNING.md"])
    return sorted({p for p in files if p.exists() and p.relative_to(ROOT) != Path("logs/risk_alerts.md")})


def add_problem(problems: list[str], path: Path, line: int, issue: str) -> None:
    problems.append(f"{path.relative_to(ROOT)}:{line}: {issue}")


def line_has_safety_context(line: str) -> bool:
    lower = line.lower()
    return any(phrase in lower for phrase in ALLOWED_CONTEXTS)


def check_text(path: Path, text: str) -> list[str]:
    problems: list[str] = []
    body = masked(text)
    rel = path.relative_to(ROOT)
    if rel not in EXEMPT_BANNED_LIST_FILES:
        for pattern, label in BANNED.items():
            for match in re.finditer(pattern, body, flags=re.IGNORECASE):
                line_no = body.count("\n", 0, match.start()) + 1
                line = text.splitlines()[line_no - 1] if line_no <= len(text.splitlines()) else ""
                if line_has_safety_context(line):
                    continue
                add_problem(problems, path, line_no, f"high-risk phrase `{match.group(0)}` ({label})")

    needs_disclosure = rel in PUBLIC_DISCLOSURE_PATHS or (rel.parts and rel.parts[0] == "site" and path.suffix == ".html")
    if needs_disclosure and "CHATTY" in text:
        lower = text.lower()
        if "not affiliated" not in lower and "disclosure" not in lower and "can go to zero" not in lower:
            add_problem(problems, path, 1, "public-facing CHATTY file may be missing disclosure/risk language")

    if "donation" in body.lower() or "community fund" in body.lower() or "send funds" in body.lower():
        allowed_fund_context = [
            "no community fund",
            "no funds requested",
            "do not post wallet addresses",
            "never request funds",
            "no fund requests",
            "not ask for funds",
            "asking for funds",
            "fund requests",
            "request funds",
            "collect donations",
            "donation request",
            "donation requests",
            "do not send funds",
            "explicitly forbidden",
            "remove or warn phrase list",
            "examples of what not to post",
        ]
        if rel not in EXEMPT_BANNED_LIST_FILES and not any(phrase in body.lower() for phrase in allowed_fund_context):
            add_problem(problems, path, 1, "fund/donation language needs explicit refusal context")

    for match in re.finditer(r"\b[1-9A-HJ-NP-Za-km-z]{32,44}\b", text):
        candidate = match.group(0)
        if re.fullmatch(r"[0-9a-f]{40}", candidate, flags=re.IGNORECASE):
            continue
        if candidate not in ALLOWED_ADDRESSES and not candidate.startswith("Qm"):
            add_problem(problems, path, text.count("\n", 0, match.start()) + 1, f"unknown wallet-like address `{candidate}`")

    return problems


def check_json_files(problems: list[str]) -> None:
    snapshot_path = ROOT / "site" / "data" / "token_snapshot.json"
    if snapshot_path.exists():
        data = json.loads(snapshot_path.read_text(encoding="utf-8"))
        if data.get("token_address") != TOKEN_ADDRESS:
            add_problem(problems, snapshot_path, 1, "wrong token address in site snapshot")
        for key in ["price_usd", "market_cap_usd", "liquidity_usd", "volume_h24_usd", "holders", "timestamp"]:
            value = data.get(key)
            if value is None or value == "":
                add_problem(problems, snapshot_path, 1, f"blank metric `{key}`")
        timestamp = data.get("timestamp")
        if isinstance(timestamp, str) and timestamp.endswith("Z"):
            snap_time = dt.datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            age = dt.datetime.now(dt.timezone.utc) - snap_time
            if age.days >= 7:
                add_problem(problems, snapshot_path, 1, f"stale snapshot: {age.days} days old")
    else:
        add_problem(problems, snapshot_path, 1, "missing site snapshot")


def write_log(problems: list[str]) -> None:
    LOG_PATH.parent.mkdir(exist_ok=True)
    if problems:
        body = "# Risk Alerts\n\n" + f"Last checked: {now_iso()}\n\n" + "\n".join(f"- {p}" for p in problems) + "\n"
    else:
        body = "# Risk Alerts\n\n" + f"Last checked: {now_iso()}\n\nNo high-risk content detected by the local monitor.\n"
    LOG_PATH.write_text(body, encoding="utf-8")


def main() -> int:
    problems: list[str] = []
    for path in files_to_scan():
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        problems.extend(check_text(path, text))
    check_json_files(problems)
    write_log(problems)
    if problems:
        print("\n".join(problems))
        return 1
    print("risk monitor passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
