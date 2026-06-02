# Member Identity Validation — Braća Kumerle
**Datum:** 2026-06-03  
**Metodologija:** Live API fetch (MusicBrainz, Discogs, Wikidata)  
**Status:** VERIFIED

---

## KORAK 1 — MusicBrainz: band member relations

Endpoint: `https://musicbrainz.org/ws/2/artist/b973e6f2-c282-473a-b2fb-ffb4466b312f?inc=artist-rels&fmt=json`

| artist.name | artist.id (puni UUID) | begin | end | direction |
|---|---|---|---|---|
| Petar Kumerle | 9ab299e2-499b-4abc-8585-e09dee7990e3 | 2007 | NULL (aktivan) | backward |
| Toni Kumerle | b134ce50-d8fa-4180-8734-76cbbcc820f3 | 2007 | NULL (aktivan) | backward |

**Napomena:** MB vraća 5 dupliciranih relacija za svakog člana (10 ukupno). Isti UUID — data quality issue u MusicBrainz bazi, ne utječe na valjanost MBID-a.

---

## KORAK 2 — MusicBrainz: puni artist records

### Petar Kumerle
- **name:** Petar Kumerle
- **id:** 9ab299e2-499b-4abc-8585-e09dee7990e3
- **disambiguation:** Member of Croatian rock band iZLET
- **life-span.begin:** 1990-08-15
- **ipis:** (prazno u MB — nije uneseno)

### Toni Kumerle
- **name:** Toni Kumerle
- **id:** b134ce50-d8fa-4180-8734-76cbbcc820f3
- **disambiguation:** Member of Croatian rock band iZLET
- **life-span.begin:** 1985-07-09
- **ipis:** (prazno u MB — nije uneseno)

---

## KORAK 3 — Discogs validation

Endpoint: `https://api.discogs.com/artists/6610944`

Band name na Discogsu: **Izlet (2)**

Members array:

| name | id | resource_url |
|---|---|---|
| Toni Kumerle | 3364223 | https://api.discogs.com/artists/3364223 |
| Petar Kumerle | 17042197 | https://api.discogs.com/artists/17042197 |

### Toni Kumerle (Discogs 3364223)
- **namevariations:** (prazno)
- **profile (EN):** Croatian songwriter, vocalist, multi-instrumentalist, and producer. Co-founder of the rock band iZLET and the independent label Braća Kumerle Music.

### Petar Kumerle (Discogs 17042197)
- **namevariations:** (prazno)
- **profile (EN):** Croatian vocalist, multi-instrumentalist, and producer. Co-founder of the rock band iZLET and the independent label Braća Kumerle Music.

---

## KORAK 4 — Wikidata cross-check

### Q139595619 — Petar Kumerle
- **labels.hr:** Petar Kumerle ✓
- **labels.en:** Petar Kumerle ✓
- **P434 (MusicBrainz ID):** 9ab299e2-499b-4abc-8585-e09dee7990e3 ✓ (podudaranje potvrđeno)
- **P1816 (Discogs artist ID):** NULL ← GAP (Discogs ID = 17042197 poznat, nije upisano)
- **P27 (citizenship):** Q224 (Hrvatska) ✓

### Q139595627 — Toni Kumerle
- **labels.hr:** Toni Kumerle ✓
- **labels.en:** Toni Kumerle ✓
- **P434 (MusicBrainz ID):** b134ce50-d8fa-4180-8734-76cbbcc820f3 ✓ (podudaranje potvrđeno)
- **P1816 (Discogs artist ID):** NULL ← GAP (Discogs ID = 3364223 poznat, nije upisano)
- **P27 (citizenship):** NULL ← GAP (Petar ima Q224, Toni nema)

---

## KORAK 5 — Kanonska tablica

| entity | wikidata | musicbrainz (puni UUID) | discogs_id | ipi |
|---|---|---|---|---|
| Petar Kumerle | Q139595619 | 9ab299e2-499b-4abc-8585-e09dee7990e3 | 17042197 | 00772816513 |
| Toni Kumerle | Q139595627 | b134ce50-d8fa-4180-8734-76cbbcc820f3 | 3364223 | 00638706326 |

**IPI izvor:** HDS-ZAMP / works_registry.json (nije dostupan kroz MB ili Wikidata API)

---

## Findings & Gaps

### Potvrđeno ✓
- Oba MBID-a su potvrđena kroz 3 neovisna izvora (MB relations, MB artist record, Wikidata P434)
- Discogs ID-ovi potvrđeni kroz band members array
- Wikidata Q-brojevi ispravni, oba imaju P434 koji se podudaraju s MB

### Gaps ← akcija potrebna
| gap | entitet | preporučena akcija |
|---|---|---|
| Wikidata P1816 null | Petar Kumerle (Q139595619) | Dodati Discogs artist ID = 17042197 |
| Wikidata P1816 null | Toni Kumerle (Q139595627) | Dodati Discogs artist ID = 3364223 |
| Wikidata P27 null | Toni Kumerle (Q139595627) | Dodati P27 = Q224 (Hrvatska) |
| MB ipis prazno | oba | MB IPIs nisu uneseni (opciono) |
| MB duplikati | oba | 5x duplicirane member-of-band relacije — MB cleanup |
| master_registry.json | oba | MB UUID upisani skraćeno (9ab299e2, b134ce50) — ažurirati na pune UUID-ove |

### master_registry.json korekcija
Trenutno upisano: `"musicbrainz": "9ab299e2"` i `"musicbrainz": "b134ce50"`  
Ispravno: pune UUID vrijednosti iz ove validacije
