# iZLET_sustav — Session Log

## Sesija: 2026-05-04 / 2026-05-06 / 2026-05-11

### Kompletni zadaci

| ID | Opis | Status | Output |
|----|------|--------|--------|
| WORKS-ENRICH-01 | Spotify enrichment — 27 EXACT + 1 AMBIGUOUS match | done | works_registry.json (27 spotify_track_id + isrc) |
| WIKI-ARCH-01 | Wikipedia arhivska struktura | done | wikipedia/ (README, _status, u_izradi, arhiva) |
| WIKI-DRAFT-01 | EN Wikipedia draft placeholder | done | wikipedia/u_izradi/en_izlet.wikitext |
| REG-EVENTS-01 | events_registry.json — inicijalna struktura | done | events_registry.json (2 eventi) |
| REG-METRICS-01 | metrics_registry.json — unified telemetry layer | done | metrics_registry.json (YouTube, Spotify, Facebook) |
| DISCOGS-FETCH-01 | Discogs API fetch — artist + release data | done | terminal output (nije perzistiran) |
| SCRIPT-AUTH-01 | spotify_auth.py — Client Credentials flow | done | scripts/spotify_auth.py |
| SCRIPT-INGEST-01 | spotify_ingest.py — metrics pull + null-safe | done | scripts/spotify_ingest.py |
| SCRIPT-APPLE-01 | apple_ingest.py — CSV ingestion pipeline | done | scripts/apple_ingest.py |
| SCRIPT-YT-01 | youtube_tag_update.py — OAuth2 tag enrichment | done | scripts/youtube_tag_update.py |
| YT-TAGS-01 | YouTube tag update — 5 videa (domovinski rat tags) | done | 5/5 OK (new_only / merged mode) |
| SCHEMA-01 | Schema.org alternateName array na bracakumerle.com | done | index.html |
| METRICS-FIX-01 | Spotify blok reklasificiran (API deprecated Feb 2026) | done | metrics_registry.json |
| GBP-01 | GBP identifikatori u master_registry.json | done | master_registry.json + CL-GBP-01 cluster |
| ENV-FIX-01 | .env uklonjen iz git trackinga | done | .gitignore |
| PETAR-DISCOGS | Petar Kumerle Discogs ID (17042197) u master_registry | done | master_registry.json petar_kumerle.ids + url |
| ARCH-2007 | Web arhiva III. gimnazija — potvrda 2007. osnivanja | done | urllib fetch, iso-8859-2, 24.3.2007 članak |

### Otvorene stavke

| ID | Opis | Prioritet | Napomena |
|----|------|-----------|----------|
| AUTH-002 | EN Wikipedia objava | P1 | Status UNKNOWN — rok 09.05.2026. prošao, objava nije potvrđena |
| HOD2026-REG | events_registry.json — hodočašće eventi | P2 | HOD2026_D01 dodaje se u ovoj sesiji |
| YT-DESC-FIX | YouTube About: "founded in 2009" → "2007" | P2 | Manualno u YouTube Studio |
| DATA-005 | MusicBrainz singlovi (11 singlova 2025-26) | P3 | Ručni unos |
| SEO-002 | Google Rich Results Test | P3 | — |
| DISCOGS-FIX | Katarza format: ukloniti "CD-ROM" | P3 | Submission note pripremljen |
| HOD2026-CONT | Dodavati daljnje HOD2026 etape u events_registry | P3 | Toni pješači Zagreb→Međugorje |

---

## Sesija 004: 2026-05-12 — Schema hardening + A1 works expansion

| Hash (short) | Timestamp | Event |
|---|---|---|
| 2f405c7 | 2026-05-12 17:52:24 +0200 | fix(schema): foundingDate 2007 + correct Apple Music/Deezer IDs + alternateName array[4] |
| 4959fe2 | 2026-05-12 17:59:47 +0200 | fix(schema): @id + description — canonical KG node |
| 5c48524 | 2026-05-12 18:03:04 +0200 | fix(schema): image array + logo — visual entity anchoring |
| 4df5b46 | 2026-05-12 18:15:32 +0200 | feat(works): BKM singles 2025-26 — work graph expansion A1 (total_works 33→44) |
| 1ea2416 | 2026-05-12 18:24:26 +0200 | chore: remove izlet_sustav_v2 artifacts |

### Novi registri (sesija 004)

| Fajl | Sadržaj |
|------|---------|
| registry/fact_canon.json | F_ORIGIN_001 + F_CMC_001 + F_CMC_2009_VALIDATION |
| registry/afd_registry.json | AfD state snapshot — borderline_KEEP, action_mode ACTIVE |
| registry/audit_ledger.json | Deterministički provenance graph — E-2026-05-12-001..004 |

### Aktivni registri

```
master_registry.json     — entiteti, ID-ovi, source clusters, notability_vector, wikipedia_survival_rule v2
works_registry.json      — 44 works (32 ISWC + W_CMC_2009_001 + 11 BKM singlova)
events_registry.json     — eventi (live, incidents, hodočašće)
metrics_registry.json    — YouTube + Spotify + Facebook metrike
registry/fact_canon.json — 3 canonical facts (F_ORIGIN_001, F_CMC_001, F_CMC_2009_VALIDATION)
registry/afd_registry.json — Wikipedia HR AfD snapshot
registry/audit_ledger.json — provenance ledger v1.0
```

### Ključni vanjski ID-ovi

| Entitet | Platforma | ID |
|---------|-----------|-----|
| iZLET | Wikidata | Q139595518 |
| iZLET | MusicBrainz | b973e6f2-c282-473a-b2fb-ffb4466b312f |
| iZLET | Spotify | 11wCFDSyZy0LfWkgllak6d |
| iZLET | Discogs | 6610944 |
| iZLET | Google Business | 8283358399340898051 |
| iZLET | Google MID | /g/11bt_5d27r |
| Toni Kumerle | Discogs | 3364223 |
| Petar Kumerle | Discogs | 17042197 |
