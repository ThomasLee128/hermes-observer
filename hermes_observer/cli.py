from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .observer import Observer
from .wake import classify_observer_intent


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only Hermes business status observer.")
    parser.add_argument("--config", default="observer.config.example.json", help="Path to observer config JSON.")
    parser.add_argument("--message", default="", help="User message that triggered Observer.")
    parser.add_argument("--classify", default="", help="Only classify a message.")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of human text.")
    parser.add_argument("--no-learn", action="store_true", help="Do not update wake-learning files.")
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    if args.classify:
        print(json.dumps(classify_observer_intent(args.classify), ensure_ascii=False, indent=2))
        return 0

    observer = Observer(Path(args.config))
    report, payload = observer.report(args.message, learn=not args.no_learn)
    if args.json:
        print(json.dumps({"report": report, "payload": payload}, ensure_ascii=False, indent=2))
    else:
        print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
