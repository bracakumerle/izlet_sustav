"""
Generates:
  data/canonical_metrics.json   — machine
  CANONICAL_STATE.md            — human
Source: works_registry.json (root)
"""
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent.parent


# ── helpers ──────────────────────────────────────────────────────────────────

def pct(n, d):
    return round(n / d * 100, 1) if d else 0.0

def git_commit():
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=ROOT, text=True
        ).strip()
    except Exception:
        return "unknown"

def mb_rec_filled(w):
    return bool(
        w.get("musicbrainz_recording_id")
        or (w.get("musicbrainz") or {}).get("recording_id")
    )

def mb_work_filled(w):
    return bool(
        w.get("musicbrainz_work_id")
        or (w.get("musicbrainz") or {}).get("work_id")
    )

def filled(w, field):
    return bool(w.get(field))


# ── load source ───────────────────────────────────────────────────────────────

with open(ROOT / "works_registry.json", encoding="utf-8") as f:
    reg = json.load(f)

all_works = list(reg["works"].items())   # [(slug, dict)]
canonical = [(k, w) for k, w in all_works if w.get("type") != "cover"]
covers     = [(k, w) for k, w in all_works if w.get("type") == "cover"]

assert len(canonical) == 44, f"Expected 44 canonical, got {len(canonical)}"

D = 44   # kpi_denominator

# ── counts ────────────────────────────────────────────────────────────────────

counts = {
    "total_objects":   len(all_works),
    "canonical_works": len(canonical),
    "covers":          len(covers),
    "kpi_denominator": D,
    "by_type": {
        "canonical": len(canonical),
        "cover":     len(covers),
    }
}

# ── covers_excluded ──────────────────────────────────────────────────────────

covers_excluded = []
for slug, w in covers:
    reason = w.get("notes") or "cover — type:cover in registry"
    covers_excluded.append({
        "slug":   slug,
        "title":  w.get("title_normalized", slug),
        "reason": reason,
    })

# ── work_level_linkage ────────────────────────────────────────────────────────

cworks = [w for _, w in canonical]

def linkage(label, predicate):
    n = sum(1 for w in cworks if predicate(w))
    return {"filled": n, "denominator": D, "pct": pct(n, D)}

work_level_linkage = {
    "iswc":                    linkage("iswc",         lambda w: filled(w, "iswc")),
    "isrc":                    linkage("isrc",         lambda w: filled(w, "isrc")),
    "spotify_track_id":        linkage("spotify",      lambda w: filled(w, "spotify_track_id")),
    "musicbrainz_recording_id":linkage("mb_rec",       mb_rec_filled),
    "musicbrainz_work_id":     linkage("mb_work",      mb_work_filled),
    "discogs_master_id":       linkage("discogs",      lambda w: filled(w, "discogs_master_id")),
    "wikidata_qid":            linkage("wikidata",     lambda w: filled(w, "wikidata_qid")),
    "wikipedia_eligible":      linkage("wiki_elig",    lambda w: bool(w.get("wikipedia_eligible"))),
}

# ── external_presence (from snapshots) ───────────────────────────────────────

def load_snapshot(name):
    p = ROOT / "data" / name
    if p.exists():
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    return {}

mb  = load_snapshot("mb_snapshot.json")
yt  = load_snapshot("youtube_snapshot.json")
wd  = load_snapshot("wikidata_snapshot.json")

external_presence = {
    "musicbrainz": {
        "artist_mbid":          mb.get("mbid"),
        "artist_confirmed":     bool(mb.get("mbid")),
        "recording_count":      (mb.get("stats") or {}).get("recording_count"),
        "release_group_count":  (mb.get("stats") or {}).get("release_group_count"),
        "snapshot_fetched_at":  mb.get("fetched_at"),
    },
    "youtube": {
        "channel_id":           yt.get("channel_id"),
        "total_videos":         yt.get("total_videos"),
        "total_views":          yt.get("total_views"),
        "latest_video_date":    yt.get("latest_video_date"),
        "oldest_video_date":    yt.get("oldest_video_date"),
        "snapshot_fetched_at":  yt.get("fetched_at"),
    },
    "wikidata": {
        "q_ids":                wd.get("q_ids", []),
        "entity_count":         len(wd.get("entities", {})),
        "band_qid":             "Q139595518",
        "snapshot_fetched_at":  wd.get("fetched_at"),
    },
}

# ── assemble JSON ─────────────────────────────────────────────────────────────

metrics = {
    "_generated_at":   datetime.now(timezone.utc).isoformat(),
    "_source":         "works_registry.json",
    "_source_commit":  git_commit(),
    "_regen":          "python3 _build/make_canonical_metrics.py",
    "_warning":        "Machine-generated. Do not edit manually. Regenerate from works_registry.json.",
    "counts":                counts,
    "covers_excluded":       covers_excluded,
    "work_level_linkage":    work_level_linkage,
    "external_presence":     external_presence,
}

out_json = ROOT / "data" / "canonical_metrics.json"
with open(out_json, "w", encoding="utf-8") as f:
    json.dump(metrics, f, ensure_ascii=False, indent=2)

print(f"Written: {out_json}")


# ── CANONICAL_STATE.md ────────────────────────────────────────────────────────

def bar(n, d, width=20):
    filled_chars = int(round(n / d * width)) if d else 0
    return "█" * filled_chars + "░" * (width - filled_chars)

wll = work_level_linkage

lines = [
    "# CANONICAL STATE",
    f"**Generated:** {metrics['_generated_at'][:10]}  ",
    f"**Source:** `works_registry.json`  ",
    f"**Commit:** `{metrics['_source_commit']}`  ",
    f"**Ratified by:** {reg['meta'].get('ratified_by', '—')}  ",
    "",
    "---",
    "",
    "## Counts",
    "",
    f"| Field | Value |",
    f"|---|---|",
    f"| Total objects in registry | {counts['total_objects']} |",
    f"| Canonical works (type ≠ cover) | **{counts['canonical_works']}** |",
    f"| Covers excluded | {counts['covers']} |",
    f"| KPI denominator | **{counts['kpi_denominator']}** |",
    "",
]

if covers_excluded:
    lines += [
        "## Covers excluded",
        "",
        "| Slug | Title | Reason |",
        "|---|---|---|",
    ]
    for c in covers_excluded:
        lines.append(f"| `{c['slug']}` | {c['title']} | {c['reason']} |")
    lines.append("")

lines += [
    "---",
    "",
    "## Work-level linkage",
    "",
    f"| Field | Filled | / {D} | % | Coverage |",
    "|---|---|---|---|---|",
]

field_labels = {
    "iswc":                     "ISWC",
    "isrc":                     "ISRC",
    "spotify_track_id":         "Spotify track ID",
    "musicbrainz_recording_id": "MusicBrainz recording ID",
    "musicbrainz_work_id":      "MusicBrainz work ID",
    "discogs_master_id":        "Discogs master ID",
    "wikidata_qid":             "Wikidata QID",
    "wikipedia_eligible":       "Wikipedia eligible",
}

for field, lbl in field_labels.items():
    s = wll[field]
    lines.append(
        f"| {lbl} | {s['filled']} | {D} | {s['pct']}% | `{bar(s['filled'], D)}` |"
    )

lines += [
    "",
    "---",
    "",
    "## External presence",
    "",
    "### MusicBrainz",
    "",
    f"| Key | Value |",
    "|---|---|",
    f"| Artist MBID | `{external_presence['musicbrainz']['artist_mbid']}` |",
    f"| Artist confirmed | {external_presence['musicbrainz']['artist_confirmed']} |",
    f"| Recording count (snapshot) | {external_presence['musicbrainz']['recording_count']} |",
    f"| Release group count (snapshot) | {external_presence['musicbrainz']['release_group_count']} |",
    f"| Snapshot fetched | {(external_presence['musicbrainz']['snapshot_fetched_at'] or '')[:10]} |",
    "",
    "### YouTube",
    "",
    f"| Key | Value |",
    "|---|---|",
    f"| Channel ID | `{external_presence['youtube']['channel_id']}` |",
    f"| Total videos | {external_presence['youtube']['total_videos']} |",
    f"| Total views | {external_presence['youtube']['total_views']:,} |",
    f"| Latest video | {(external_presence['youtube']['latest_video_date'] or '')[:10]} |",
    f"| Snapshot fetched | {(external_presence['youtube']['snapshot_fetched_at'] or '')[:10]} |",
    "",
    "### Wikidata",
    "",
    f"| Key | Value |",
    "|---|---|",
    f"| Q-IDs | {', '.join(f'`{q}`' for q in external_presence['wikidata']['q_ids'])} |",
    f"| Entity count | {external_presence['wikidata']['entity_count']} |",
    f"| Band QID | `{external_presence['wikidata']['band_qid']}` |",
    f"| Snapshot fetched | {(external_presence['wikidata']['snapshot_fetched_at'] or '')[:10]} |",
    "",
    "---",
    "",
    f"*Regenerate: `python3 _build/make_canonical_metrics.py`*",
]

out_md = ROOT / "CANONICAL_STATE.md"
with open(out_md, "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")

print(f"Written: {out_md}")
print(f"\ncanonical={counts['canonical_works']} covers={counts['covers']} "
      f"iswc={wll['iswc']['filled']}/{D} isrc={wll['isrc']['filled']}/{D} "
      f"mb_rec={wll['musicbrainz_recording_id']['filled']}/{D} "
      f"spotify={wll['spotify_track_id']['filled']}/{D}")
