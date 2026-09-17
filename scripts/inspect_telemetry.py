#!/usr/bin/env python3
"""
Local Developer Utility: Inspect Structured Telemetry & Operational Logs
Conforms to DOC-REP-6.2.3-001 (Option B - Local Developer Inspection Tool).

Usage:
  python scripts/inspect_telemetry.py <logfile.log>
  cat uvicorn.log | python scripts/inspect_telemetry.py
"""

import argparse
import json
import sys
from collections import Counter
from typing import Any, Iterable


def parse_telemetry_lines(lines: Iterable[str]) -> list[dict[str, Any]]:
    """Extracts valid JSON telemetry records from a stream of log lines."""
    records: list[dict[str, Any]] = []
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
        try:
            data = json.loads(line)
            if isinstance(data, dict) and ("event" in data or "telemetry_type" in data):
                records.append(data)
        except json.JSONDecodeError:
            # Check if line contains embedded JSON
            idx = line.find("{")
            if idx != -1:
                try:
                    data = json.loads(line[idx:])
                    if isinstance(data, dict) and ("event" in data or "telemetry_type" in data):
                        records.append(data)
                except json.JSONDecodeError:
                    continue
    return records


def print_summary(records: list[dict[str, Any]]) -> None:
    """Prints formatted aggregate telemetry metrics to stdout."""
    print("=" * 70)
    print("  AI-NATIVE TECHNOLOGY STUDIO — TELEMETRY INSPECTION SUMMARY")
    print("=" * 70)

    total_events = len(records)
    print(f"\nTotal Telemetry Records Parsed: {total_events}\n")

    if total_events == 0:
        print("No telemetry events found in the provided input.")
        print("=" * 70)
        return

    # Aggregate by event type
    product_events: Counter[str] = Counter()
    operational_events: Counter[str] = Counter()

    for r in records:
        event = r.get("event", "unknown")
        ttype = r.get("telemetry_type", "product")
        if ttype == "operational":
            operational_events[event] += 1
        else:
            product_events[event] += 1

    print("--- 1. Discovery Funnel & Product Telemetry ---")
    canonical_order = [
        "discovery_started",
        "discovery_stage_completed",
        "opportunity_map_viewed",
        "blueprint_unlock_started",
        "blueprint_unlocked",
        "estimate_viewed",
        "contact_submitted",
    ]
    for ev in canonical_order:
        cnt = product_events.get(ev, 0)
        print(f"  {ev:<30}: {cnt:>5}")

    other_product = {k: v for k, v in product_events.items() if k not in canonical_order}
    if other_product:
        print("\n  Other Product Events:")
        for ev, cnt in sorted(other_product.items()):
            print(f"    {ev:<28}: {cnt:>5}")

    print("\n--- 2. Operational & Security Telemetry ---")
    if operational_events:
        for ev, cnt in sorted(operational_events.items()):
            print(f"  {ev:<30}: {cnt:>5}")
    else:
        print("  (No operational events recorded)")

    print("\n" + "=" * 70)


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect in-house telemetry logs.")
    parser.add_argument("file", nargs="?", default=None, help="Path to log file (default: read from stdin)")
    args = parser.parse_args()

    if args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as f:
                records = parse_telemetry_lines(f)
        except Exception as exc:
            print(f"Error reading file '{args.file}': {exc}", file=sys.stderr)
            sys.exit(1)
    else:
        if sys.stdin.isatty():
            print("Reading from stdin (paste log lines or pipe output, Ctrl+Z/Ctrl+D to end)...", file=sys.stderr)
        records = parse_telemetry_lines(sys.stdin)

    print_summary(records)


if __name__ == "__main__":
    main()
