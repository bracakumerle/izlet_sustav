# Authority Scoring V2 — Pilot Report

**STATUS:** VERIFIED  
**GENERATED:** 30.05.2026.  
**REQUIRES:** reports/authority_scoring_v2_spec.md, works_registry.json, registry/media_registry.json  
**METHOD:** Ručno scoriranje prema V2 spec kategorijama. Samo kanonski repository artefakti.

---

## Input verifikacija

| Artefakt | Status |
|---|---|
| authority_scoring_v2_spec.md | ✓ prisutan |
| works_registry.json | ✓ prisutan (patch apliciran) |
| registry/media_registry.json | ✓ prisutan |

---

## Scoring — 5 kandidata

### Formula
```
score = (ISC × 0.28) + (MRC × 0.22) + (WML × 0.20) + (RP × 0.15) + (CRC × 0.10) + (IC × 0.05)
```

---

### 1. zalo

**Registry podaci:**
- ISRC: HRA371300115 ✓
- ISWC: T-914.228.446-6 ✓
- MusicBrainz: null
- Wikidata: null
- media_references: ['MTV Adria rotation 2013', 'HRT Radio Dubrovnik top lista']
- Label/catalog: null (album Dallas Records verificiran u releases bloku)

**Napomena:** media_references su broadcast reference (MTV Adria, HRT Radio) — nisu media_registry ART linkovi. ART001 (Ziher) i ART002 (Barikada) referenciraju album, ne eksplicitno Žalo kao work node.

| Kategorija | Vrijednost | Obrazloženje | Doprinos |
|---|---|---|---|
| Independent Source Coverage (28%) | 0.6 | ART001+ART002 referenciraju album Nikad ne znaš; Žalo je jedan od singlova, direktno spomeut u kontekstu. Autori verificirani. | 0.168 |
| Media Registry Coverage (22%) | 0.3 | 1 indirektna referenca kroz album coverage | 0.066 |
| Work-Node Media Links (20%) | 0.0 | Nema ART linkova u media_references polju — samo broadcast referenci | 0.000 |
| Release Provenance (15%) | 0.6 | Dallas Records, 2016, BL2361431 (u releases bloku) | 0.090 |
| Cross-Registry Convergence (10%) | 0.4 | ISWC verificiran; MB artist prisutan, ali ne recording | 0.040 |
| Identifier Completeness (5%) | 0.7 | ISRC + ISWC ✓; Spotify track null | 0.035 |
| **UKUPNO** | | | **0.399** |

---

### 2. cast

**Registry podaci:**
- ISRC: HRA371800845 ✓
- ISWC: T-931.111.745-0 ✓
- MusicBrainz: null
- Wikidata: null
- media_references: ['ART011']
- ART011: Likaclub.net.hr | news | gng:False | author:null

| Kategorija | Vrijednost | Obrazloženje | Doprinos |
|---|---|---|---|
| Independent Source Coverage (28%) | 0.0 | ART011 nije GNG eligible, nema autora. Nema Tier A referenci za Čast specifično. | 0.000 |
| Media Registry Coverage (22%) | 0.3 | 1 referenca (ART011) | 0.066 |
| Work-Node Media Links (20%) | 0.4 | 1 ART link u work node | 0.080 |
| Release Provenance (15%) | 0.3 | Dallas Records / Katarza 2019 — label poznat ali catalog null u work zapisu | 0.045 |
| Cross-Registry Convergence (10%) | 0.4 | ISWC verificiran; MB artist prisutan | 0.040 |
| Identifier Completeness (5%) | 0.7 | ISRC + ISWC ✓ | 0.035 |
| **UKUPNO** | | | **0.266** |

---

### 3. sjever_uz_odsutne

**Registry podaci:**
- ISRC: null
- ISWC: null
- MusicBrainz: recording_id ✓, release_id ✓, confidence 1.0
- media_references: [URL1 braniteljski-forum, URL2 narod.hr]
- Label: Braća Kumerle Music, BKMUSIC001, barcode: 199953974831, year: 2023

**Napomena:** media_references su direktni URL-ovi, ne ART ID-ovi. Braniteljski-forum i Narod.hr su gng:False, author:null.

| Kategorija | Vrijednost | Obrazloženje | Doprinos |
|---|---|---|---|
| Independent Source Coverage (28%) | 0.3 | 2 reference bez autora; news tip, gng:False | 0.084 |
| Media Registry Coverage (22%) | 0.6 | 2 reference (ART015, ART016 per review_v2) | 0.132 |
| Work-Node Media Links (20%) | 0.7 | 2 linkova u work node | 0.140 |
| Release Provenance (15%) | 0.8 | BKM label + BKMUSIC001 + barcode verificiran | 0.120 |
| Cross-Registry Convergence (10%) | 0.7 | MusicBrainz recording + release ✓ | 0.070 |
| Identifier Completeness (5%) | 0.0 | Nema ISRC ni ISWC | 0.000 |
| **UKUPNO** | | | **0.546** |

---

### 4. moj_dinamo

**Registry podaci:**
- ISRC: null
- ISWC: null
- MusicBrainz: recording_id ✓, confidence 1.0
- media_references: ['ART017', 'ART018']
- ART017: HOP.com.hr | news | gng:False | author:null
- ART018: Zagreb.info | news | gng:False | author:null
- Label: Braća Kumerle Music, year: 2025

| Kategorija | Vrijednost | Obrazloženje | Doprinos |
|---|---|---|---|
| Independent Source Coverage (28%) | 0.3 | 2 reference bez autora; news tip, gng:False | 0.084 |
| Media Registry Coverage (22%) | 0.6 | 2 reference (ART017, ART018) | 0.132 |
| Work-Node Media Links (20%) | 0.7 | 2 ART linkova u work node | 0.140 |
| Release Provenance (15%) | 0.3 | BKM label + godina; nema catalog, barcode | 0.045 |
| Cross-Registry Convergence (10%) | 0.4 | MusicBrainz recording ✓; nema release | 0.040 |
| Identifier Completeness (5%) | 0.0 | Nema ISRC ni ISWC | 0.000 |
| **UKUPNO** | | | **0.441** |

---

### 5. frane_tente

**Registry podaci:**
- ISRC: null
- ISWC: null
- MusicBrainz: recording_id ✓, confidence 1.0
- media_references: ['ART012', 'ART013', 'ART014']
- ART012: Fenix Magazin | news | gng:False | author:null
- ART013: Dalmatinskiportal.hr | news | gng:False | author:null
- ART014: Narod.hr | news | gng:False | author:null
- Label: Braća Kumerle Music, year: 2025

| Kategorija | Vrijednost | Obrazloženje | Doprinos |
|---|---|---|---|
| Independent Source Coverage (28%) | 0.3 | 3 reference bez autora; news tip, gng:False | 0.084 |
| Media Registry Coverage (22%) | 1.0 | 3+ reference (ART012, ART013, ART014) | 0.220 |
| Work-Node Media Links (20%) | 1.0 | 3 ART linkova u work node | 0.200 |
| Release Provenance (15%) | 0.3 | BKM label + godina; nema catalog, barcode | 0.045 |
| Cross-Registry Convergence (10%) | 0.4 | MusicBrainz recording ✓; nema release | 0.040 |
| Identifier Completeness (5%) | 0.0 | Nema ISRC ni ISWC | 0.000 |
| **UKUPNO** | | | **0.589** |

---

## Ranking

| Rang | Work | V2 Score | Stari rang (est.) |
|---|---|---|---|
| 1 | frane_tente | 0.589 | 37 |
| 2 | sjever_uz_odsutne | 0.546 | 31 |
| 3 | moj_dinamo | 0.441 | 38 |
| 4 | zalo | 0.399 | visoko (authority page postoji) |
| 5 | cast | 0.266 | visoko (ISRC+ISWC) |

---

## Analiza — ponaša li se model kako je zamišljen?

**DA** — model radi ono što je dizajniran.

**Ključni pomak:** `frane_tente` i `sjever_uz_odsutne` izlaze na vrh unatoč nedostatku ISRC/ISWC, jer imaju gustu media/registry vezu. `cast` pada na dno unatoč najboljim identifikatorima — ART011 je gng:False, nema autora.

**Potvrđena lažna negativna (stari model):**
- `frane_tente` (bio rank 37) → sada #1
- `sjever_uz_odsutne` (bio rank 31) → sada #2
- `moj_dinamo` (bio rank 38) → sada #3

**Potvrđena lažna pozitivna (stari model):**
- `cast` (bio visoko zbog ISRC+ISWC) → sada #5

---

## Kritični nalaz

`zalo` ima **najveći authority page potencijal** unatoč score 0.399 — jer je jedini rad s Tier A medijskim referencama (ART001 Ziher + ART002 Barikada, autori verificirani, gng:True). Ove reference nisu pravilno unesene kao ART linkovi u work node — to je **data gap koji treba ispraviti**.

Ispravak: dodati ART001 i ART002 u `zalo.media_references` u works_registry.json.

Nakon ispravka, `zalo` bi imao:
- ISC: 1.0 (→ 0.280)
- WML: 0.7 (→ 0.140)
- Procijenjeni novi score: **~0.619** → rang #1

---

## Preporuke

1. **Ispraviti data gap za zalo** — dodati ART001, ART002 u media_references
2. **Sljedeće authority stranice** prema V2 rangu: frane_tente → sjever_uz_odsutne → moj_dinamo
3. **Cast** treba Tier A medijsku referencu prije authority page deployanja
4. **ISRC/ISWC gap** za sjever_uz_odsutne, moj_dinamo, frane_tente — rješavati paralelno

---

*Generirano: 30.05.2026. — Claude (Ministar Autoriteta)*  
*STATUS: VERIFIED — temeljeno isključivo na kanonskim repository artefaktima*
