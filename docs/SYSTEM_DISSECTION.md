# SYSTEM DISSECTION — iZLET_sustav (jedinstveni radni dokument)
## Anatomija implementacije iz stvarnog koda. Ministar autoriteta · 2026-07-12.
### Konsolidira Track A–E (bivše zasebne datoteke). **Pravilo: nova `.md` samo ako NE može biti poglavlje ovdje.**
### Format nalaza: **NALAZ → HIPOTEZA → DOKAZ → POUZDANOST → UTJECAJ.**

## TRACK STATUS
| Track | Domena | Status |
|---|---|---|
| A | Automation (`izlet_os`) | ✅ COMPLETE |
| B | Registry | ✅ COMPLETE |
| C | Web (schema) | ✅ COMPLETE |
| D | Publication Pipeline (Netlify/build/scripts) | ✅ COMPLETE |
| E | Criticality / Risk / Health | ⬜ NOT STARTED |
| — | **ARCHITECTURAL INCIDENT 001** | 🔴 OPEN (Publication Drift) |

*Trajni docs: `SYSTEM_INDEX` (arhitektura) · ovaj `SYSTEM_DISSECTION` (implementacija) · `IZLET_OS_v3_OPERATING_FRAMEWORK` · `OS_v3_CHANGELOG` · budući `SYSTEM_ATLAS` (tek kad dissekcija završi).*

---

## CANONICAL DATA FLOW — dva toka (Entity / Rights / Discovery)
```
① DISCOVERY (ingest): Spotify·YouTube·Discogs·MB ─ scripts/{spotify_ingest,apple_ingest,mb_sync}+connectors+census
     ─► data/*snapshots + works_census_v2.csv ─► registries/works_registry.json (76 CANDIDATE)
        ─► [REVIEW / reconciliation — RUČNO, PENDING] ─┐
② AUTHORITATIVE (canon): HDS-ZAMP·ISWCNet·CISAC ─► works_registry.json ROOT (44 CANON) ◄┘
     ─► _build/make_canonical_metrics.py ─► CANONICAL_STATE.md + data/canonical_metrics.json ─► Web ─► KG ─► YouTube ─► Discovery
③ ENTITY spine: master_registry.json ─► orchestrator (verify+schema) ─► schema_org_verified.json [AUDIT, ne web]
LIFECYCLE: Discovery → Candidate(76) → Review → Canonical(44) → Publication → Verification
```

---

## TRACK A — AUTOMATION (`izlet_os`)
**Execution graph:** `orchestrator.py` (PipelineManager v2.2, entry=`__main__`, ručno) → 7 KORAK: load `master_registry.json` → scan → verify_links (HTTP HEAD) → **generate `data/schema_org_verified.json`** (sameAs=samo 200) → report (`logs/scan_report_*`) → MB+WD snapshot → YouTube snapshot.
**Moduli:** connectors/{musicbrainz,wikidata,youtube,discogs}_agent (snapshot→data/*.json; WD ima hashlib change-detect), authority_builder (master→WD brief), schema_builder (→`data/schema_org.json`), reporter (master→report), enrichers/spotify_works_enricher (**jedini mutira works_registry**, preview→apply).
**Siročad (pozivatelj nepoznat):** discogs_agent, wiki_manager, network_agent.
**Failure/Recovery:** registry JSON korupcija=HARD (KORAK 1 abort)→restore git; vanjski API=SOFT (non-fatal)→retry next cycle; **scheduler NIJE u izlet_os** (trigger ručni/nepoznat).

---

## TRACK B — REGISTRY
**Model = HUB + SPOKE (ne dva konkurenta):** `master_registry.json` = ENTITY hub (5 entiteta: izlet/petar/toni/BKM/**braca_kumerle=Alias**) + `registries:{works,events,metrics}` pointer.

**NALAZ: dvije `works_registry.json` datoteke (RAZLIČITA svrha).**
- HIPOTEZA (početna): dva konkurentska korijena → **ODBAČENA.**
- DOKAZ: root (44) meta source=ISWCNet/CISAC/HDS-ZAMP (IPI/ISWC); `registries/` (76) meta source=works_census_v2.csv, role=DERIVED_CANDIDATE, reconciliation=PENDING.
- POUZDANOST: 99% (oba pročitana). UTJECAJ: MEDIUM (staging tech-debt, ne divergencija).

| Datoteka | # | Uloga |
|---|--|---|
| root `works_registry.json` | 44 | CANON — rights (ZAMP/ISWC) → CANONICAL_STATE |
| `registries/works_registry.json` | 76 | CANDIDATE — census; reconciliation PENDING (2026-06-04) |

**Writers:** root works ← spotify_works_enricher(apply), scripts/{mb_sync,spotify_enrich}; metrics ← scripts/{apple_ingest,spotify_ingest}; master ← ručno/setup.py.
**Otkriveno (SYSTEM_INDEX L10 nije imao):** cijeli `scripts/` sloj + `_build/`.
**Failure/Recovery:** master korupcija=HARD→git; 76 vs 44=SOFT (nezavršen merge)→dovrši reconciliation.
**TECH DEBT (Field Log):** preimenovati `registries/works_registry.json` → `works_census_registry.json`.

---

## TRACK C — WEB (schema)
**NALAZ: objavljena web schema je INLINE i NIJE iz generatora.**
- HIPOTEZA: web koristi `schema_org_verified.json` → **ODBAČENA** (bila i moja ranija kriva pretpostavka).
- DOKAZ: grep — svaka `.html` ima vlastiti `<script application/ld+json>`; `schema_org_verified.json` čita samo orchestrator(piše)+1 audit-report; `schema_org.json` (schema_builder) = **0 čitatelja = orphan**.
- POUZDANOST: 98%. UTJECAJ: **HIGH** (izvor istine za Google je ručni HTML).

| Schema | Generator | Čitatelj | Status |
|---|---|---|---|
| inline JSON-LD (HTML) | ručno / (lyrics: skripta) | Google/KG | ŽIVI objavljeni izvor |
| `schema_org_verified.json` | orchestrator | audit-report | verifikacija (ne web) |
| `schema_org.json` | schema_builder | nitko | LEGACY/ORPHAN |

---

## TRACK D — PUBLICATION PIPELINE (odgovori na 6 pitanja)
1. **Kako HTML nastaje?** Netlify `publish="."` = **statično, BEZ build-stepa.** Repo se servira kakav jest. `netlify/functions` = live-data API (čita `data/*.json`, GET/CORS) — hrani `dashboard.html`.
2. **Tko uređuje inline JSON-LD?** index/bio/pjesme/people/en = **ručno**; `lyrics/*` = `scripts/build_lyrics_pages.py` (template `lyrics-template.html`).
3. **Zašto nije generator?** Generator-pattern POSTOJI (lyrics), ali `build_lyrics_pages.py` ima **hardkodiran `SONGS` popis** (isrc/mb/spotify/youtube u skripti) — NIJE iz `works_registry`. Glavne stranice = ručno kurirane (bogatiji schema).
4. **Svjesna odluka ili dug?** MJEŠOVITO: lyrics=generator (ali hardkodiran); index/entity=kurirano/dug.
5. **Može li se regenerirati?** Kapacitet postoji (template+skripta), ali **ništa nije spojeno na kanonski registry.**
6. **Zašto se ne regenerira danas?** Nijedan generator ne čita `works_registry`/`master_registry`; podaci se ručno prepisuju.

**Failure/Recovery:** deploy pad=HARD→Netlify redeploy; inline drift=SOFT (tiho do re-crawla)→ručni fix / budući registry→HTML generator.

---

## 🔴 ARCHITECTURAL INCIDENT 001 — PUBLICATION DRIFT
- **NALAZ:** objavljeni sloj (web schema) NIJE izveden iz kanonskog registra — krši načelo **„canonical over derived".**
- **HIPOTEZA:** master_registry → (auto) → objavljeno → **ODBAČENA.** Stvarnost: master_registry → (RUČNI copy) → inline JSON-LD; lyrics → (hardkodiran copy) → HTML.
- **DOKAZ:** `netlify.toml publish="."` (nema builda); grep 0 generatora spojenih na registry; `index.html` 7 sameAs vs `master_registry` 17 urls vs `schema_org_verified` (provjereni podskup) = **≥3 verzije istine za „službeni sameAs".**
- **POUZDANOST:** 95%. **UTJECAJ:** HIGH (entity-authority projekt ovisi o konzistentnom sameAs).
- **STATUS:** OPEN. **NE popravljati** dok se ne potvrdi je li ručno namjerno (Track D pokazuje: djelomično kurirano) — kandidat za **STATE RECONCILIATION** (published ↔ registry), poslije uz General GO (NO DIRECT EDIT).

---

## TRACK E — CRITICALITY / RISK / HEALTH ⬜ NOT STARTED

## OTVORENO → DEPENDENCY VALIDATION / STATE RECONCILIATION
1. 76→44 reconciliation (PENDING). 2. schema_builder deprecation (proposal→ratify). 3. events_registry nije seciran. 4. STATE RECONCILIATION: published inline schema ↔ master_registry (≥3 verzije sameAs) = Incident 001. 5. scheduler/trigger orchestratora.

---
*SYSTEM DISSECTION · konsolidirano 2026-07-12 · iz koda · ne mijenja sustav. Zamjenjuje bivše `SYSTEM_DISSECTION_01_izlet_os` / `_TRACK_B_` / `_TRACK_C_` (obrisane, sadržaj ovdje).*
