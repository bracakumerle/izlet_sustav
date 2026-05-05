#!/usr/bin/env python3
"""
apple_ingest.py — Apple Music for Artists CSV ingestion
iZLET_sustav v1 | Layer: metrics_registry
Frekvencija: weekly manual trigger
Confidence: low (manual_csv)
"""

import json
import csv
import sys
import logging
from datetime import date

REGISTRY_PATH = "registries/metrics_registry.json"
CSV_PATH = sys.argv[1] if len(sys.argv) > 1 else "data/apple_export.csv"
PLATFORM_KEY = "apple_music"

logging.basicConfig(level=logging.INFO, format="[apple_ingest] %(levelname)s: %(message)s")
log = logging.getLogger(__name__)

def parse_csv(path):
    plays_total = 0
    listeners_peak = 0
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            plays_total += int(row.get("Plays", 0))
            listeners_peak = max(listeners_peak, int(row.get("Listeners", 0)))
    return plays_total, listeners_peak

def validate(plays, listeners, old_plays):
    assert plays >= 0
    assert listeners >= 0
    if listeners > plays:
        log.warning(f"listeners ({listeners}) > plays ({plays})")
    if old_plays is not None and plays < old_plays:
        raise ValueError(f"plays decreased: {plays} < {old_plays}")

def update_registry(plays, listeners):
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        registry = json.load(f)
    old_plays = registry.get(PLATFORM_KEY, {}).get("plays")
    validate(plays, listeners, old_plays)
    registry[PLATFORM_KEY] = {
        "plays": plays,
        "listeners": listeners,
        "last_updated": date.today().isoformat(),
        "source": "manual_csv",
        "confidence": "low",
        "status": "active"
    }
    with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)
    log.info(f"✓ plays={plays}, listeners={listeners}, date={date.today()}")

if __name__ == "__main__":
    try:
        plays, listeners = parse_csv(CSV_PATH)
        update_registry(plays, listeners)
    except (AssertionError, ValueError) as e:
        log.error(f"Validation failed: {e}")
        sys.exit(1)
    except FileNotFoundError as e:
        log.error(f"File not found: {e}")
        sys.exit(1)
