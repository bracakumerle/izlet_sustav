"""
youtube_segment_audit.py — Segmentacijski tag audit (reach/katalog), DRY-RUN ONLY.

Nema YouTube API poziva. Čita vidIQ CSV export + data/yt_video_classes.json,
generira diff prijedlog u registries/youtube_segment_diff_<datum>.json.
Promjene na kanalu izvršavaju se tek nakon ratifikacije, kroz
scripts/youtube_segment_apply.py.

Usage:
    python scripts/youtube_segment_audit.py <putanja_do_vidiq_csv>

Doktrina (reports/yt_reach_classification_2026-06-11.md):
  - katalog (autorska): čisti entitet — tier-2 reach termini van, brand unutra;
    BEZ iznimke (ratificirano 2026-06-11: release identitet pobjeđuje)
  - mrvelj_cover: cluster ostaje, thompson van, Mrvelj atribucija unutra
  - thompson_cover: thompson tagovi legitimni, brand unutra
  - event_bg_thompson: cluster ostaje, brand unutra
  - other_cover: cluster ostaje, thompson van
  - media_tv: samo brand
  - unclassified: bez promjena (tier-1 mreža vrijedi)
  - SVI: tier-1 (NDH sloj) + zds bezuvjetno van
"""

import csv
import json
import sys
import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLASSES_PATH = ROOT / "data" / "yt_video_classes.json"
OUT_DIR = ROOT / "registries"

TIER1_KEYWORDS = [
    "ustaš", "ustas", "ustash", "ndh", "poglavni", "pavelić", "pavelic",
    "kvaternik", "zds", "za dom spremni", "independent state of croatia",
]

TIER2_EXACT = {
    "domovinski rat", "vukovar", "bitka za vukovar", "battle of vukovar",
    "vukovar 1991", "obrana vukovara", "heroji vukovara",
    "branitelji", "hrvatski branitelji", "branitelj",
    "hos", "oluja", "oluja 1995", "domoljubne pjesme", "domoljublje",
    "hrvatska himna", "ratne pjesme", "1991", "1995", "rat u hrvatskoj",
}

THOMPSON_KEYWORDS = ["thompson", "čavoglave", "cavoglave", "marko perkovi"]

BRAND_CORE = ["iZLET", "Braća Kumerle", "hrvatska glazba", "Croatian music"]
BRAND_BY_CLASS = {
    "autorska":          BRAND_CORE + ["hrvatski rock", "Croatian rock"],
    "mrvelj_cover":      BRAND_CORE + ["Ivo Fabijan Mrvelj", "Mrvelj cover"],
    "thompson_cover":    BRAND_CORE + ["Thompson cover"],
    "event_bg_thompson": BRAND_CORE,
    "other_cover":       BRAND_CORE,
    "media_tv":          BRAND_CORE,
}

SKIP_IDS = {"uZq_1k61gME", "M5VdBtZh2qA", "5m7h1jzfM04", "I09KaIV5HXk", "QQ6xhW2Z1J0", "_hHLxdTZEIU",
            "ttn9FCTc3PM"}  # privatiziran 2026-06-11 (redundantan isječak Himne 124.)

# Naslovi katalog sloja — usklađivanje s release identitetom (doktrina 2026-06-11).
# "confirmed" = primjenjuje se; "assumed" = POTVRDA GENERALA OBAVEZNA (apply preskače).
TITLE_PROPOSALS = {
    "35VtHrOkcaQ": {"new": "iZLET - Vitez Jure | OFFICIAL VIDEO", "confidence": "confirmed"},
    "TwXdxN0iMbI": {"new": "iZLET - Himna 124. Vukovarska Brigada | OFFICIAL VIDEO", "confidence": "confirmed"},
    "0z3kNr5bITg": {"new": "iZLET - Znakovlje Hrvata | LIVE Split Riva", "confidence": "confirmed"},
    "fhTIwiJGbyA": {"new": "iZLET - Himna 124. Vukovarska Brigada | #shorts", "confidence": "confirmed"},
    "CJ2hgubiQo4": {"new": "iZLET - Bogdanovačka Kalvarija (feat. Ivica Jurčan) | #shorts", "confidence": "confirmed"},
}


def classify_tag(tag, vclass):
    t = tag.lower().strip()
    if any(kw in t for kw in TIER1_KEYWORDS):
        return "remove", "tier1_safety_net"
    if any(kw in t for kw in THOMPSON_KEYWORDS):
        if vclass in ("thompson_cover", "event_bg_thompson"):
            return None, None
        return "remove", "thompson_outside_thompson_class"
    if vclass == "autorska" and t in TIER2_EXACT:
        return "remove", "tier2_reach_term_on_catalog"
    return None, None


def main():
    if len(sys.argv) < 2:
        sys.exit("Usage: python scripts/youtube_segment_audit.py <vidiq_csv>")
    csv_path = Path(sys.argv[1])
    classes = json.loads(CLASSES_PATH.read_text(encoding="utf-8"))["videos"]

    rows = list(csv.DictReader(open(csv_path, encoding="utf-8-sig")))
    diffs = []
    summary = {"videos": 0, "with_changes": 0, "removals": 0,
               "additions": 0, "title_changes": 0, "unclassified": 0}

    for r in rows:
        vid = r["ID"]
        if r.get("STATUS") != "Public" or vid in SKIP_IDS:
            continue
        summary["videos"] += 1
        vclass = classes.get(vid, "unclassified")
        if vclass == "unclassified":
            summary["unclassified"] += 1
        tags = [t.strip() for t in r.get("KEYWORDS", "").split(",") if t.strip()]
        tags_lower = {t.lower() for t in tags}

        remove = []
        for tag in tags:
            action, reason = classify_tag(tag, vclass)
            if action == "remove":
                remove.append({"tag": tag, "reason": reason})

        add = []
        if vclass != "unclassified":
            for b in BRAND_BY_CLASS.get(vclass, []):
                if b.lower() not in tags_lower:
                    add.append(b)

        title_change = None
        tp = TITLE_PROPOSALS.get(vid)
        if tp and tp["new"] and tp["new"] != r.get("TITLE", "").strip():
            title_change = {"current": r.get("TITLE", ""), "proposed": tp["new"],
                            "confidence": tp["confidence"]}

        if remove or add or title_change:
            summary["with_changes"] += 1
            summary["removals"] += len(remove)
            summary["additions"] += len(add)
            if title_change:
                summary["title_changes"] += 1
            diffs.append({
                "video_id": vid,
                "title": r.get("TITLE", "")[:90],
                "class": vclass,
                "views": int(float(r.get("VIEWS") or 0)),
                "tags_remove": remove,
                "tags_add": add,
                "title_change": title_change,
            })

    out = {
        "generated": datetime.date.today().isoformat(),
        "mode": "DRY_RUN",
        "source_csv": csv_path.name,
        "doctrine": "reports/yt_reach_classification_2026-06-11.md",
        "summary": summary,
        "diffs": sorted(diffs, key=lambda d: -d["views"]),
    }
    OUT_DIR.mkdir(exist_ok=True)
    out_path = OUT_DIR / ("youtube_segment_diff_" + out["generated"] + ".json")
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    print("DRY-RUN gotov ->", out_path)
    for k, v in summary.items():
        print(" ", k + ":", v)


if __name__ == "__main__":
    main()
