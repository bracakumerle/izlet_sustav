# Authority Scoring V2 — Specifikacija

**STATUS:** VERIFIED  
**RATIFICIRAO:** General — 30.05.2026.  
**GENERATED:** 30.05.2026.  
**REQUIRES:** registry/media_registry.json, works_registry.json  

---

## Svrha

Definira kategorije i težine za rangiranje works_registry zapisa prema prioritetu za authority page deployment. Cilj: identificirati radove s najvećim potencijalom za citation loop (bracakumerle.com → Wikidata → Wikipedia → vanjski mediji).

---

## Kategorije i težine

| # | Kategorija | Težina | Rationale |
|---|---|---|---|
| 1 | Independent Source Coverage | 28% | Primarni Wikipedia GNG signal. Nezavisni autor, glazbena platforma, citabilan URL. |
| 2 | Media Registry Coverage | 22% | Ukupna pokrivenost u media_registry.json — kvantitet medijskih referenci. |
| 3 | Work-Node Media Links | 20% | Direktna veza work zapis ↔ media članak u works_registry. |
| 4 | Release Provenance | 15% | Datum objave, label (Dallas Records / BKM), catalog number, UPC. |
| 5 | Cross-Registry Convergence | 10% | Prisutnost u ≥2 vanjska registra: MusicBrainz + Wikidata + Discogs. |
| 6 | Identifier Completeness | 5% | ISRC, ISWC, Spotify track ID — nužni ali ne dovoljni signal. |

**Ukupno:** 100%

---

## Definicije kategorija

### 1. Independent Source Coverage (28%)

Mjeri postojanje nezavisnih, citabilnih medijskih referenci s identificiranim autorom.

**Maksimalni score (1.0):** 2+ nezavisne reference s autorom, glazbena platforma, live URL.

**Scoring:**
- 0 referenci: 0.0
- 1 referenca bez autora: 0.3
- 1 referenca s autorom: 0.6
- 2+ reference s autorima: 1.0

**Tier A primjeri:** Barikada.com (ART002), Ziher.hr (ART001) — autor + glazbena platforma + live URL.

---

### 2. Media Registry Coverage (22%)

Broj media_registry.json članaka koji eksplicitno referenciraju rad ili izvođača u kontekstu rada.

**Scoring:**
- 0 referenci: 0.0
- 1 referenca: 0.3
- 2 reference: 0.6
- 3+ referenci: 1.0

---

### 3. Work-Node Media Links (20%)

Direktni `media_references` linkovi unutar works_registry zapisa za taj rad.

**Scoring:**
- 0 linkova: 0.0
- 1 link: 0.4
- 2 linkova: 0.7
- 3+ linkova: 1.0

---

### 4. Release Provenance (15%)

Verificiranost izdavačkih podataka: label, datum, catalog number, UPC/barcode.

**Scoring:**
- 0 polja: 0.0
- Label + godina: 0.3
- + catalog number: 0.6
- + UPC/barcode: 0.8
- + Discogs release ID: 1.0

---

### 5. Cross-Registry Convergence (10%)

Prisutnost u vanjskim registrima kao zasebni entitet (ne samo artist).

**Scoring:**
- 0 registara: 0.0
- MusicBrainz recording ili Wikidata QID: 0.4
- 2 registra: 0.7
- 3+ registra (MB + WD + Discogs): 1.0

---

### 6. Identifier Completeness (5%)

Postojanje standardnih identifikatora.

**Scoring:**
- 0 identifikatora: 0.0
- ISRC ili ISWC: 0.4
- ISRC + ISWC: 0.7
- ISRC + ISWC + Spotify track: 1.0

---

## Formula

```
score = (ISC × 0.28) + (MRC × 0.22) + (WML × 0.20) + (RP × 0.15) + (CRC × 0.10) + (IC × 0.05)
```

Gdje su sve varijable u rasponu [0.0, 1.0].

---

## Primjer — zalo

| Kategorija | Vrijednost | Težina | Doprinos |
|---|---|---|---|
| Independent Source Coverage | 1.0 (Barikada + Ziher, autori verificirani) | 0.28 | 0.280 |
| Media Registry Coverage | 0.6 (2 reference: ART001, ART002) | 0.22 | 0.132 |
| Work-Node Media Links | 0.4 (1 link u works_registry) | 0.20 | 0.080 |
| Release Provenance | 0.6 (Dallas Records, 2016, BL2361431) | 0.15 | 0.090 |
| Cross-Registry Convergence | 0.4 (ISWC verificiran, MB artist) | 0.10 | 0.040 |
| Identifier Completeness | 0.7 (ISWC T-914.228.446-6, Spotify album) | 0.05 | 0.035 |
| **UKUPNO** | | | **0.657** |

---

## Primjer — sjever_uz_odsutne

| Kategorija | Vrijednost | Težina | Doprinos |
|---|---|---|---|
| Independent Source Coverage | 0.6 (ART015, ART016 — autori nepoznati) | 0.28 | 0.168 |
| Media Registry Coverage | 0.6 (2 reference) | 0.22 | 0.132 |
| Work-Node Media Links | 0.7 (2 linkova nakon patcha) | 0.20 | 0.140 |
| Release Provenance | 0.8 (BKM, 2023, BKMUSIC001, barcode) | 0.15 | 0.120 |
| Cross-Registry Convergence | 0.7 (MusicBrainz recording + release) | 0.10 | 0.070 |
| Identifier Completeness | 0.4 (ISRC verificiran) | 0.05 | 0.020 |
| **UKUPNO** | | | **0.650** |

---

## Napomene

- Identifier Completeness (5%) je namjerno potcijenjen u odnosu na Grok V1 model — Spotify track ID nije dokaz medijske relevantnosti.
- Independent Source Coverage (28%) je najjači signal jer direktno determinira Wikipedia GNG eligibility.
- Work-Node Media Links (20%) je odvojen od Media Registry Coverage (22%) jer razlikuje opću pokrivenost izvođača od specifičnog spomena rada.
- Ovaj model će biti revalidiran nakon što ≥5 authority stranica bude deployjano i indeksirano.

---

## Status

Pilot scoring za: `zalo`, `cast`, `sjever_uz_odsutne`, `moj_dinamo`, `frane_tente` — čeka implementaciju nakon ratifikacije spec-a.
