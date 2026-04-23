#!/usr/bin/env python3
"""Generate a monthly dormant autopilot health report."""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "logs" / "monthly_health_report.md"
SITE_OUT = ROOT / "site" / "data" / "monthly_health_report.md"
SNAPSHOT = ROOT / "site" / "data" / "token_snapshot.json"


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def snapshot_age_note() -> str:
    if not SNAPSHOT.exists():
        return "Snapshot file missing."
    data = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    timestamp = data.get("timestamp")
    if not timestamp:
        return "Snapshot timestamp unavailable."
    snap_time = dt.datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    age = dt.datetime.now(dt.timezone.utc) - snap_time
    if age.days >= 30:
        return f"Snapshot is stale: {age.days} days old."
    return f"Snapshot age is {age.days} days."


def main() -> int:
    body = f"""# CHATTY Monthly Autopilot Health Report

Generated: {now_iso()}

Mode: Dormant Autopilot Mode

## Snapshot Freshness

- {snapshot_age_note()}

## Safety Confirmation

- No X or Telegram autoposting.
- No wallet connections.
- No crypto movement.
- No money spent.
- No paid services.
- No fund requests.
- No fake engagement.
- No investment claims.

## Human Action

None required unless the creator chooses to intervene.
"""
    OUT.write_text(body, encoding="utf-8")
    SITE_OUT.parent.mkdir(parents=True, exist_ok=True)
    SITE_OUT.write_text(body, encoding="utf-8")
    print("monthly health report written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
