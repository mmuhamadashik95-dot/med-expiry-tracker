"""med-expiry-tracker: track a home medicine cabinet from the command line.

Add medicines with expiry dates, then check for expired or soon-to-expire
items (30/90-day windows) and get storage tips.

Educational/demo only — not medical advice. When in doubt about a medicine,
ask a pharmacist; never take an expired medicine.

Usage:
    python tracker.py add "Paracetamol 500mg" 2027-03-01 --qty 20
    python tracker.py list
    python tracker.py check
    python tracker.py remove "Paracetamol 500mg"
    python tracker.py demo
"""

import argparse
import json
import os
import sys
from datetime import date, timedelta

DISCLAIMER = "Educational/demo only — not medical advice. Never take an expired medicine; ask a pharmacist."

DEFAULT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cabinet.json")

STORAGE_TIPS = {
    "room": "Store at room temperature, away from heat and direct sunlight.",
    "cool-dry": "Store in a cool, dry place — not in a steamy bathroom.",
    "fridge": "Store in the fridge (2–8 °C); do not freeze unless the label says so.",
}
GENERAL_TIPS = [
    "Keep medicines out of reach of children.",
    "Keep them in their original packaging with the label visible.",
    "Check the expiry date before every use.",
]


def load(path):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save(path, items):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2)


def parse_date(s):
    y, m, d = (int(p) for p in s.split("-"))
    return date(y, m, d)


def status_of(expiry, today, warn_days=30, soon_days=90):
    """Return 'expired' | 'expiring-soon' | 'ok' for an expiry date."""
    delta = (expiry - today).days
    if delta < 0:
        return "expired"
    if delta <= warn_days:
        return "expiring-soon"
    if delta <= soon_days:
        return "watch"
    return "ok"


def add_item(path, name, expiry, qty=1, storage="room"):
    items = load(path)
    if any(i["name"].lower() == name.lower() for i in items):
        raise ValueError(f"{name!r} is already in the cabinet.")
    parse_date(expiry)  # validates format
    if storage not in STORAGE_TIPS:
        raise ValueError(f"Unknown storage type: {storage} (room, cool-dry, fridge)")
    items.append({"name": name, "expiry": expiry, "qty": qty, "storage": storage})
    save(path, items)
    return items[-1]


def remove_item(path, name):
    items = load(path)
    kept = [i for i in items if i["name"].lower() != name.lower()]
    if len(kept) == len(items):
        raise ValueError(f"{name!r} not found in the cabinet.")
    save(path, kept)
    return kept


def check(path, today=None, warn_days=30, soon_days=90):
    """Return a report dict grouping items by status."""
    today = today or date.today()
    groups = {"expired": [], "expiring-soon": [], "watch": [], "ok": []}
    for item in load(path):
        st = status_of(parse_date(item["expiry"]), today, warn_days, soon_days)
        groups[st].append(item)
    return {"today": today.isoformat(), "groups": groups}


def format_report(report):
    g = report["groups"]
    lines = [f"Medicine cabinet check — {report['today']}"]
    if g["expired"]:
        lines.append("\nEXPIRED — dispose of safely (do not take):")
        for i in g["expired"]:
            lines.append(f"  ✗ {i['name']} (expired {i['expiry']})")
    if g["expiring-soon"]:
        lines.append("\nEXPIRING WITHIN 30 DAYS — use first / replace soon:")
        for i in g["expiring-soon"]:
            lines.append(f"  ! {i['name']} (expires {i['expiry']})")
    if g["watch"]:
        lines.append("\nEXPIRING WITHIN 90 DAYS:")
        for i in g["watch"]:
            lines.append(f"  • {i['name']} (expires {i['expiry']})")
    if g["ok"]:
        lines.append("\nOK:")
        for i in g["ok"]:
            lines.append(f"  ✓ {i['name']} (expires {i['expiry']})")
    if not (g["expired"] or g["expiring-soon"] or g["watch"] or g["ok"]):
        lines.append("\nCabinet is empty. Add medicines with: tracker.py add <name> <YYYY-MM-DD>")
    lines.append("\nStorage tips:")
    for tip in GENERAL_TIPS:
        lines.append(f"  - {tip}")
    lines.append(DISCLAIMER)
    return "\n".join(lines)


def demo_data(today):
    return [
        {"name": "Old Cough Syrup", "expiry": (today - timedelta(days=40)).isoformat(),
         "qty": 1, "storage": "room"},
        {"name": "Paracetamol 500mg", "expiry": (today + timedelta(days=12)).isoformat(),
         "qty": 20, "storage": "cool-dry"},
        {"name": "Cetirizine 10mg", "expiry": (today + timedelta(days=60)).isoformat(),
         "qty": 14, "storage": "cool-dry"},
        {"name": "Vitamin D3", "expiry": (today + timedelta(days=300)).isoformat(),
         "qty": 30, "storage": "room"},
    ]


def main(argv=None):
    parser = argparse.ArgumentParser(description="Home medicine cabinet expiry tracker")
    parser.add_argument("--file", default=DEFAULT_FILE, help="cabinet JSON file")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_add = sub.add_parser("add")
    p_add.add_argument("name")
    p_add.add_argument("expiry", help="YYYY-MM-DD")
    p_add.add_argument("--qty", type=int, default=1)
    p_add.add_argument("--storage", default="room", choices=list(STORAGE_TIPS))
    p_list = sub.add_parser("list")
    p_check = sub.add_parser("check")
    p_check.add_argument("--warn", type=int, default=30)
    p_check.add_argument("--soon", type=int, default=90)
    p_rm = sub.add_parser("remove")
    p_rm.add_argument("name")
    sub.add_parser("demo")
    args = parser.parse_args(argv)

    try:
        if args.cmd == "add":
            item = add_item(args.file, args.name, args.expiry, args.qty, args.storage)
            print(f"Added: {item['name']} (expires {item['expiry']}, qty {item['qty']})")
            print(STORAGE_TIPS[args.storage])
        elif args.cmd == "list":
            items = load(args.file)
            if not items:
                print("Cabinet is empty.")
            for i in items:
                print(f"{i['name']} | expires {i['expiry']} | qty {i['qty']} | {i['storage']}")
        elif args.cmd == "check":
            print(format_report(check(args.file, warn_days=args.warn, soon_days=args.soon)))
        elif args.cmd == "remove":
            remove_item(args.file, args.name)
            print(f"Removed: {args.name}")
        elif args.cmd == "demo":
            save(args.file, demo_data(date.today()))
            print(format_report(check(args.file)))
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
