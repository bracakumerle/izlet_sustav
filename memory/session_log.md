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

---

## Sesija 005: 2026-05-12 — Site content expansion B + provenance chain

| Hash (short) | Timestamp | Event |
|---|---|---|
| ce7c7bd | 2026-05-12 ~02:00 +0200 | feat(canon): F_ORIGIN_001 — first public performance 2007-03-23 |
| 01919a1 | 2026-05-12 ~02:37 +0200 | feat(canon+works): F_CMC_001 + W_CMC_2009_001 — CMC Demo 2009 |
| 4663c1f | 2026-05-12 ~03:48 +0200 | feat(registry): AfD layer update — F_CMC_2009_VALIDATION + notability_vector |
| dc8fbcf7 | 2026-05-12 | feat(registry): audit_ledger.json v1.0 — E-001..E-005 |
| 0d35cb58 | 2026-05-12 | feat(registry): link fact_canon to audit_ledger — ledger_ref fields + E-006..E-008 |
| 29889dad | 2026-05-12 | feat(works): C1 MusicBrainz sync — partial (1/11 resolved) |
| d1644daf | 2026-05-12 | feat(works): C1 complete — 11/11 MBID resolved (manual verified) |
| e0703180 | 2026-05-12 | chore: C2-A partial — Spotify ISRC coverage limited (regional catalog) |
| cec86398 | 2026-05-12 | feat(site): add /bio + /diskografija — entity content surface B |

### Novi fajlovi (sesija 005)

| Fajl | Sadržaj |
|------|---------|
| bio.html | O bendu stranica — BreadcrumbList JSON-LD, canonical /bio |
| diskografija.html | Diskografija stranica — studijski albumi, kompilacije, singlovi |
| _redirects | Netlify rewrites: /bio → /bio.html, /diskografija → /diskografija.html |
| scripts/mb_sync.py | MusicBrainz sync skripta za rank 33-43 works |
| scripts/spotify_enrich.py | Spotify ISRC enrichment skripta (ISRC → track_id) |

### Napomene (sesija 005)

- .gitignore: dodano `izlet_sustav_v2/node_modules/` i `izlet_sustav_v2/.next/` — trajno rješenje za 130MB push blocker
- Spotify ISRC: svi HRA371... kodovi vraćaju None — regionalni katalog nije indeksiran po ISRC-u u Spotify API-ju
- MusicBrainz: 10/11 MBID-ova dostavljeno ručno (Generalom), 1/11 API resolucijom
- index.html: dodana Tidal sameAs, O bendu crawlable sekcija, footer nav linkovi (/bio, /diskografija)

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

---

## SESSION: 14-15.05.2026 — Cycle #001–#004 + Runtime V2.5

### Cycle Evolution Summary

| Cycle | Focus | Key Output |
|---|---|---|
| #001 | YouTube telemetry sweep | 10 signals, search_emergence, retention_anomaly |
| #002 | Cross-platform resonance (Meta + YT) | Hodočašće flywheel, diaspora asymmetry confirmed |
| #003 | Authority extraction | SIGCOV confirmed: 4x Tier 1 mainstream coverage |
| #004 | Memory persistence + media topology | H1-H4 verified, STRICE-IVANE-2025 convergence object |

### Architecture Changes

- signal_registry.json activated as canonical telemetry layer
- Signal Taxonomy v1.0 locked
- vidIQ Protocol v1.0 locked
- Notion operational layer activated (Operations, Signals, Research, System Map, Archive)
- Authority checkpoint introduced between Gemini → Grok
- Distributed correction model: max 2 rejections per layer → General escalation
- Convergence object standard locked (V2.5 schema)
- Degraded mode protocol: Claude = hard gate, max confidence = medium without vidIQ

### Runtime V2.5 Lock (15.05.2026)

- VidIQ = Verification Escalation Engine
- Grok = Semantic Compression & Convergence Layer
- Claude = Authority checkpoint + final validation
- Gemini = Institutional Topology & Context Mapping
- Manus = Internet pre-filter, topology-first crawling
- GPT = Pipeline architecture + drift monitoring

### EN Wikipedia Status

DEPLOYMENT READY. Sandbox update pending Petar approval.
Citation set: 4x Tier 1 + hrvatski-glasnik.com + fenix-magazin.de + maxportal.hr + tomislavcity.com + mostarski.info
Convergence anchor: STRICE-IVANE-2025 (P0, high confidence)

---

## SESSION: CMP-4 → CMP-8

**Datum:** 18–19.05.2026.
**Status:** CLOSED — ARCHIVED

**Što je riješeno:**

- Notion semantički groundiran (Root Context Block + Architecture Map)
- Runtime Context stranica kreirana (L0 orientation layer)
- iZLET Root Context rewritan
- ND Root Context dodan
- HrStud stranica kreirana
- Continuity vector definiran: Petar = runtime operator između iZLET / ND / HrStud / KABINET
- Cabinet Substitution Effect identificiran i ograničen
- PHASE A deployano: 4x YouTube naslovi, opisi (HR+EN), tagovi

**Što ostaje otvoreno:**

- Playlist arhitektura + endscreens
- External gravity / recommendation graph convergence
- Documentary authority layer

**Ključni zaključak:**
KABINET služi iZLET-u — ne obratno.
Sustav više nije bottleneck. Vanjska gravitacija jest.
