#!/usr/bin/env python3
"""Compliance linter for publishable CHATTY drafts."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

BANNED = {
    r"\bbuy now\b": "Use: read the disclosure and do your own research.",
    r"\bguaranteed\b": "Use: no promises, no guarantees.",
    r"\brisk[- ]?free\b": "Use: highly volatile and can go to zero.",
    r"\b100x\b": "Use: no price targets.",
    r"\bmoon soon\b": "Use: meme/community experiment.",
    r"\bsend it\b": "Use: public transparency log updated.",
    r"\bpump\b": "Use only in platform names like Pump.fun or in no-pump rule docs, not promotional copy.",
    r"\bape in\b": "Use: do your own research.",
    r"\beasy money\b": "Use: highly volatile and can go to zero.",
    r"\bnext doge\b": "Use: original meme/community experiment.",
    r"\binsider\b": "Use: public information only.",
    r"\blisting soon\b": "Use only if verified and phrased neutrally.",
    r"\bburn coming\b": "Avoid roadmap-profit claims.",
    r"\bbuyback\b": "Avoid profit-support claims.",
    r"\block supply\b": "Avoid profit-support claims.",
    r"\bcoordinated\b": "Avoid coordination language.",
    r"\braid(?: this)?\b": "Use: no spam.",
    r"\bspam\b": "Use only in rules/policy docs, not calls to action.",
    r"\bno risk\b": "Use: can go to zero.",
    r"\bofficial chatgpt\b": "Use: unofficial, not affiliated.",
    r"\bofficial openai\b": "Use: unofficial, not affiliated.",
}

ALLOWED_CONTEXTS = [
    "not financial advice",
    "no financial advice",
    "Pump.fun",
    "no spam",
    "anti-spam",
    "no-pump",
    "pump coordination",
]

DISCLOSURE_PATTERNS = [
    "Disclosure:",
    "disclosure page",
    "not affiliated",
    "creator may benefit",
]


def masked(text: str) -> str:
    out = text
    for phrase in ALLOWED_CONTEXTS:
        out = re.sub(re.escape(phrase), "_" * len(phrase), out, flags=re.IGNORECASE)
    return out


def check_banned(path: Path, text: str) -> list[str]:
    hits: list[str] = []
    body = masked(text)
    for pattern, suggestion in BANNED.items():
        for match in re.finditer(pattern, body, flags=re.IGNORECASE):
            line = body.count("\n", 0, match.start()) + 1
            hits.append(f"{path}:{line}: banned/high-risk phrase `{match.group(0)}`. {suggestion}")
    return hits


def split_x_posts(text: str) -> list[tuple[int, str]]:
    matches = list(re.finditer(r"^### Post \d+", text, flags=re.MULTILINE))
    posts: list[tuple[int, str]] = []
    for index, match in enumerate(matches):
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        line = text.count("\n", 0, start) + 1
        posts.append((line, text[start:end]))
    return posts


def check_disclosures(path: Path, text: str) -> list[str]:
    if path.name != "x_drafts_week_1.md":
        return []
    hits: list[str] = []
    for line, post in split_x_posts(text):
        if not any(marker.lower() in post.lower() for marker in DISCLOSURE_PATTERNS):
            hits.append(f"{path}:{line}: X draft is missing disclosure language or a disclosure-page reference.")
    return hits


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="*", default=["content/x_drafts_week_1.md", "content/x_reply_bank.md", "telegram/pinned_message.md"])
    args = parser.parse_args()

    problems: list[str] = []
    for raw in args.paths:
        path = (ROOT / raw).resolve() if not Path(raw).is_absolute() else Path(raw)
        if not path.exists():
            problems.append(f"{path}: missing file")
            continue
        text = path.read_text(encoding="utf-8")
        problems.extend(check_banned(path, text))
        problems.extend(check_disclosures(path, text))

    if problems:
        print("\n".join(problems))
        return 1
    print("content linter passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
