# iZLET Corpus Gap Report
**Date:** 2026-06-04  
**Analyst:** auto-generated from local registries  
**Status:** READ-ONLY analysis — no registry files modified

---

## ⚠ Preflight: works_registry.json not found

`registries/works_registry.json` does not exist. Analysis was performed across the three closest equivalents:

| File | Role | Entries |
|---|---|---|
| `registries/lyrics_corpus_registry.csv` | Canonical works index | 8 works |
| `registries/entity_url_registry_v1.csv` | Entity graph — Songs section | 12 MusicRecording entities |
| `registries/youtube_corpus_scored.csv` | YouTube channel crawl | 253 videos |
| `registries/youtube_covers.csv` | Cover performances extracted | 25 videos |

The gap between what is registered (8–12 works) and what is visible in the YouTube corpus (~60+ distinct original titles) is the central finding of this report.

---

## 1. Total Works Count

| Registry | Count | Scope |
|---|---|---|
| `lyrics_corpus_registry.csv` | **8** | Lyrics-layer canonical works only |
| `entity_url_registry_v1.csv` (Songs only) | **12** | MusicRecording entities with HTML pages or stubs |
| Distinct original titles in YouTube corpus | **~60–70** | Estimated from title/description analysis |

The lyrics_corpus and entity_url_registry together cover a minimum of **13 unique works** (union of both, accounting for overlap). The YouTube corpus exposes an order-of-magnitude gap.

---

## 2. Breakdown by Work Type

### lyrics_corpus_registry.csv — `work_type` field

All 8 entries carry `work_type = lyrics`. There is no type variation in this file — it is a lyrics-layer index, not a full works registry.

The meaningful classification dimension in this file is **`status`**:

| status | count | entries |
|---|---|---|
| `draft` | 4 | krijesovi-laži, frane-tente, sjever-uz-odsutne, znakovlje-hrvata |
| `planned` | 3 | čast, žalo, isuse-moj |
| `live` | 1 | moj-dinamo |

### entity_url_registry_v1.csv — `schema_tip` field (Songs section)

All 12 Songs entries carry `schema_tip = MusicRecording`. Release entities (5) carry `MusicAlbum`.

| schema_tip | count |
|---|---|
| MusicRecording | 12 |
| MusicAlbum | 5 |
| Person | 2 |
| Various (Root/WebPage) | 13 |

**Missing work types across both registries:** demos, live recordings, commissions/hymns, medleys, unreleased works. None of these categories exist as a type in any registry file.

---

## 3. Breakdown by Year

### lyrics_corpus_registry — `first_release_year`

| Year | Works |
|---|---|
| 2013 | Žalo |
| 2018 | Čast |
| 2020 | Frane Tente |
| 2021 | Znakovlje Hrvata |
| 2023 | Sjever uz odsutne |
| 2024 | Moj Dinamo |
| 2025 | Krijesovi laži |
| 2026 | Isuse moj |

**Gap years in lyrics_corpus:** 2007–2012, 2014–2017, 2019, 2022 — **13 years with zero registered works.**

### entity_url_registry — Songs, by `godina`

| Year | Works |
|---|---|
| 2009 | Ti si čudesna |
| 2016 | Žalo |
| 2019 | Čast, U svijetu bajki |
| 2021 | Znakovlje Hrvata |
| 2023 | Sjever uz odsutne |
| 2024 | Moj Dinamo |
| 2025 | Krijesovi laži, Striče Ivane, Vitez Jure |
| 2026 | Isuse moj |

**Gap years in entity_url_registry Songs:** 2007–2008, 2010–2015, 2017–2018, 2020, 2022.

### YouTube corpus — upload year distribution (all 253 videos)

| Year | Videos | Notes |
|---|---|---|
| 2009 | 1 | Ti si čudesna official — earliest upload |
| 2010 | 3 | Pernastica, Ljeto u Maximiru, Žalo (official videos) |
| 2011 | 2 | Spasi me, So Sweet/VISKI STRIP |
| 2012 | 14 | Leteći majmuni release batch + Pink Floyd cover |
| 2013 | 2 | Oo da sa krilima, Ježeva molitva |
| 2014 | 2 | Live Ne žurim, live Urota duhova |
| **2015** | **0** | **Gap — only year with zero YouTube activity** |
| 2016 | 4 | Himna VK Zagreb, i Migranti, Susjedova vila, Ćelavi škembići |
| 2017 | 15 | Nikad ne znaš album batch upload + standalone |
| 2018 | 12 | Live sessions, Tužni odlazak, Obale se tope |
| 2019 | 26 | Katarza album batch + official videos + live sets |
| 2020 | 16 | Official video burst + covers |
| 2021 | 22 | Large original upload batch |
| 2022 | 4 | Pod ovim nebom, Džomba, Čovjek moli Boga, Dotepenci |
| 2023 | 3 | Sjever uz odsutne official, Božićna idila, Bogdanovci moji |
| 2024 | 25 | Moj Dinamo official, U svijetu bajki re-release, Igraj Donna + heavy live |
| 2025 | ~100 | Growth phase — shorts dominant, multiple originals |
| 2026 | 17 | Jan–May only |

**Earliest work:** Ti si čudesna — YouTube upload 2009-05-25 (CMC Demo 2009).  
**Latest registered work:** Isuse moj — 2026 (BKM singl).  
**Only upload gap in YouTube:** 2015.

---

## 4. Breakdown by Source / Confidence

### lyrics_corpus_registry — `source_verified` field

| value | count |
|---|---|
| YES | 8 |
| (other) | 0 |

The `source_verified` field is boolean — no source name is recorded. It indicates that all 8 entries were manually verified, but **the verification source is not captured anywhere in the registry schema**.

No `confidence` or equivalent field exists in lyrics_corpus_registry.

### entity_url_registry — `status` field (proxy for confidence)

| status | count (all entity types) |
|---|---|
| Live | 16 |
| Stub | 10 |
| (blank) | 6 |

For Songs specifically:

| status | songs |
|---|---|
| Live | 7 (čast, frane-tente, krijesovi-laži, moj-dinamo, sjever-uz-odsutne, u-svijetu-bajki, žalo) |
| Stub | 5 (isuse-moj, strice-ivane, ti-si-cudesna, vitez-jure, znakovlje-hrvata) |

### youtube_corpus_scored — `probable_tier` field

| tier | count | meaning |
|---|---|---|
| A | 14 | Highest authority — official videos, high engagement |
| B | 47 | Strong signal — official-adjacent or strong performance |
| C | 192 | Raw / unprocessed / lower signal |

`authority_score` range: 39.03 – 80 (Ti si čudesna scores 80, the highest in the corpus).

---

## 5. Covered Sources Audit

| Source domain | Status | Evidence |
|---|---|---|
| **DistroKid** | NOT COVERED | No DistroKid IDs or references in any registry. ISRCs present but source not attributed. |
| **Spotify** | PARTIAL | SP: track IDs present for 6 works (čast, frane-tente, moj-dinamo, sjever-uz-odsutne, u-svijetu-bajki, žalo) + artist ID. ~6 of 12 songs covered. |
| **MusicBrainz** | PARTIAL | MB: recording IDs for 8 works (čast, frane-tente, krijesovi-laži, moj-dinamo, sjever-uz-odsutne, u-svijetu-bajki, vitez-jure-partial, žalo). Missing for: znakovlje-hrvata (noted "MB:multiple refs"), strice-ivane, isuse-moj, ti-si-cudesna. No MB release IDs for any album. |
| **Discogs** | PARTIAL | Release IDs for 2 albums (Katarza: 35923165; Nikad ne znaš: 12898284), label (4368922), 1 person (17042197). No track-level Discogs data. |
| **YouTube** | COVERED | Full 253-video channel crawl scored and categorised in `youtube_corpus_scored.csv`. |
| **Facebook** | NOT COVERED | No Facebook IDs, post links, or references in any registry file. |
| **Physical releases (CD/booklet/liner notes)** | NOT COVERED | CMC Demo and Dallas Records releases confirmed in entity_url_registry, but no physical-media-derived metadata (track lists, liner notes, catalogue numbers). |
| **Personal archive / oral history** | NOT COVERED | No field for this source type exists in any registry. |
| **Press / media articles** | NOT COVERED | One HOP.com.hr article referenced in HTML (krijesovi-laži), but no media citations appear in any registry file. |

---

## 6. Corpus Size Estimation

### Source material for estimation

- lyrics_corpus_registry: 8 works
- entity_url_registry Songs: 12 works
- YouTube corpus: distinct original titles visible across 253 videos
- Albums with known tracklists visible on YouTube:
  - *Leteći majmuni* (2012): ~10 tracks in 2012-06-18 batch upload
  - *Nikad ne znaš, to je ono…* (2016): ~14 tracks in 2017-12-18/19 batch upload
  - *Katarza* (2019): ~14 tracks in 2019-08-23 batch upload
  - BKM era singles (2020–2026): ~12 confirmed originals

### Conservative estimate — author originals only, no covers, no commissions

**Range: 45–55 distinct original works**

Basis: Albums (10 + 14 + 14 = ~38) + BKM era confirmed originals (~12) + pre-album standalone singles (Ti si čudesna, Pernastica, Ljeto u Maximiru, Žalo, Spasi me, Zetovac = ~6) = ~56, with some deduplication likely. Only works with YouTube upload evidence or registry confirmation counted.

### Realistic estimate — includes probable unreleased, demos, early period originals

**Range: 70–90 distinct works**

Basis: Conservative base (~55) + estimated early period material 2007–2009 not on YouTube (~5–10 originals) + probable standalone singles not yet appearing in any registry (~10–15 known from live setlists in YouTube descriptions). Commissions (Himna VK Zagreb, Himna 124. Brigada) counted as originals.

### Upper bound — all candidates including covers, live-only, fragments

**Range: 110–140 total**

Basis: Realistic (~80) + 25 documented covers (youtube_covers.csv) + undocumented covers visible in corpus (~10–15 more) + live-only premieres not yet in registry (Striče Ivane pre-studio, Nezavisna Država live) + probable 2007–2009 pre-YouTube fragments.

---

## 7. Gap Hypothesis

### GAP-1 — Entire early period missing (2007–2012)

**Severity: CRITICAL**

lyrics_corpus_registry has nothing before 2013. entity_url_registry Songs has only Ti si čudesna (2009) for this window. Yet the YouTube corpus shows:
- *Leteći majmuni* (2012): ~10 tracks uploaded as a batch
- 2010–2011 official videos: Pernastica, Ljeto u Maximiru, Žalo, Spasi me
- 2008 live video referenced in YouTube description (Svemir Live 2008)
- CMC Demo 2009: only Ti si čudesna formally registered, but demo likely had 2–4 tracks

**Likely missing:** 15–25 original works from 2007–2012 with zero registry coverage.

---

### GAP-2 — Dallas Records era undertracks (2016–2018)

**Severity: HIGH**

*Nikad ne znaš, to je ono…* (2016): ~14 tracks visible on YouTube but only **Žalo** appears in entity_url_registry, and only in lyrics_corpus as `planned` status. The other ~13 album tracks (Pernastica, Dva gemišta, Ne žurim, Majčin skut, Svemir, Maša, Noćima, Topim se i gubim se, Kako da se smijem, Oni spavaju, Imam, Vlak, Sadašnji Trenutak) have zero registry entries.

Similarly, 2017–2018 standalone originals (Obale se tope, Tužni odlazak, Hrabrost) are in the YouTube corpus but absent from all registries.

**Likely missing:** 15–18 works from 2016–2018 Dallas Records era.

---

### GAP-3 — Katarza album undertracks (2019)

**Severity: HIGH**

*Katarza* (2019): ~14 tracks visible on YouTube. Of these, only **Čast** and **U svijetu bajki** are registered in entity_url_registry. 12 Katarza tracks (Uredi se, Tko si ti, Urota duhova, Oceana, Siluete, Zaklopi moje oči, Zašto šutim, Čaroban otok, Poslije svega, Princeza Tea, Ponekad, Kokosovo mlijeko, Osmijeh je bitan) have no registry entry despite official YouTube uploads with captions and full metadata.

**Likely missing:** 12 confirmed Katarza tracks + 2019 non-album singles (Gori Oluja, Nema mjesta, Nezavisna Država).

---

### GAP-4 — BKM era standalone originals (2020–2022)

**Severity: MEDIUM**

The BKM era is better covered in the registry but still incomplete. YouTube shows originals not in any registry:
- 2020: Tvoja njedra, Tko si ti (standalone), Bogdanovačka Kalvarija (collab Ivica Jurčan)
- 2021: Vitez Jure (in entity_url_registry as Stub), Zašto šutim (official), Samo tamo (official), Koza u velegradu, Neka slatko boli, Autori nalaze smisao, Doživljaj, Konji od žada, Tvoje je pitanje totalno suvišno, Oltar spasa, Postoji samo jedan Bog, Hrvatski Trolist, Himna 124. brigada
- 2022: Džomba, Pod ovim nebom, Čovjek moli Boga, Dotepenci

**Likely missing:** 18–22 original works from 2020–2022.

---

### GAP-5 — No work type beyond "lyrics" / "MusicRecording"

**Severity: MEDIUM**

Neither registry tracks:
- Demos / work-in-progress versions
- Live-exclusive premieres (Striče Ivane was performed dozens of times on YouTube before any studio release)
- Commissions and hymns (Himna VK Zagreb, Himna 124. brigada — these are original compositions but not categorised)
- Collaborative works (Bogdanovačka Kalvarija feat. Ivica Jurčan; Gori Oluja feat. Marko Jurič; VISKI STRIP feat. Toni Kumerle)
- Cover arrangements (25 documented, only in youtube_covers.csv — not linked to any works registry)

---

### GAP-6 — source_verified has no attribution

**Severity: LOW (schema)**

All 8 lyrics_corpus entries mark `source_verified = YES` but the verification source is not recorded. When a future maintainer reads the file, there is no way to know whether "verified" means: confirmed from Spotify metadata, from MusicBrainz, from physical booklet, or from personal memory. This is a schema gap, not a coverage gap.

---

### GAP-7 — 2015 blackout

**Severity: LOW (informational)**

2015 is the only year with zero YouTube uploads in the entire 2009–2026 timeline. This could indicate:
- A hiatus in public activity
- Content removed or unlisted
- Entirely private or venue-only activity

No registry file addresses this. Worth noting as an unexplained gap in the public record.

---

## Summary Table

| # | Gap | Estimated missing works | Severity |
|---|---|---|---|
| GAP-1 | Early period 2007–2012 | 15–25 | CRITICAL |
| GAP-2 | Nikad ne znaš album + 2017–2018 standalones | 15–18 | HIGH |
| GAP-3 | Katarza album + 2019 standalones | 14–17 | HIGH |
| GAP-4 | BKM era 2020–2022 standalones | 18–22 | MEDIUM |
| GAP-5 | Work types not tracked (demos, collabs, commissions, covers) | unknown | MEDIUM |
| GAP-6 | source_verified has no attribution field | schema only | LOW |
| GAP-7 | 2015 blackout — no explanation | unknown | LOW |

**Total estimated unregistered original works: 62–82**  
Against a registered base of 8–12, the corpus is undercounted by a factor of **5–8×**.

---

*End of report — 2026-06-04*  
*Sources: local registry files only — no external APIs consulted*
