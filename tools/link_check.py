#!/usr/bin/env python3
"""Small dependency-free link checker for CHATTY static site files."""

from __future__ import annotations

import html.parser
import sys
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
PUBLIC_BASE = "https://dicnunz.github.io/CHATTY-Revival/"


class LinkParser(html.parser.HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag not in {"a", "img", "script", "link"}:
            return
        for key, value in attrs:
            if key in {"href", "src"} and value and not value.startswith("#"):
                self.links.append(value)


def local_target(page: Path, link: str) -> Path | None:
    parsed = urlparse(link)
    if parsed.scheme or link.startswith("mailto:"):
        return None
    return (page.parent / parsed.path).resolve()


def check_external(url: str) -> str | None:
    if not url.startswith("http"):
        return None
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "CHATTY-Revival link check"})
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            if response.status >= 400:
                return f"{url} returned {response.status}"
    except urllib.error.HTTPError as exc:
        if exc.code in {403, 405, 429}:
            return None
        return f"{url} returned {exc.code}"
    except (urllib.error.URLError, TimeoutError) as exc:
        return f"{url} failed: {exc}"
    return None


def main() -> int:
    problems: list[str] = []
    for page in sorted(SITE.glob("*.html")):
        parser = LinkParser()
        parser.feed(page.read_text(encoding="utf-8"))
        for link in parser.links:
            target = local_target(page, link)
            if target is not None:
                if not str(target).startswith(str(SITE.resolve())) or not target.exists():
                    problems.append(f"{page.relative_to(ROOT)}: missing local link `{link}`")
                continue
            if link.startswith(PUBLIC_BASE):
                continue
            issue = check_external(link)
            if issue:
                problems.append(f"{page.relative_to(ROOT)}: {issue}")
    if problems:
        print("\n".join(problems))
        return 1
    print("link check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
