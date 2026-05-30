# Authority Page Deployment Pipeline — Top 5

**STATUS:** DRAFT  
**GENERATED:** 30.05.2026.  
**REQUIRES:** authority_scoring_v2_pilot.md, works_registry.json, registry/media_registry.json  

---

## 1. Frane Tente — `/pjesme/frane-tente`

**V2 Score:** 0.589 | **Rang:** #1

### Raspoloživi metadata

| Polje | Vrijednost | Status |
|---|---|---|
| Naslov | Frane Tente | ✓ |
| Godina | 2025 | ✓ |
| Label | Braća Kumerle Music | ✓ |
| MusicBrainz recording | 0999a678-4586-48c5-a1f1-598ffaa69977 | ✓ |
| ISRC | null | ❌ gap |
| ISWC | null | ❌ gap |
| Spotify track | null | ❌ gap |
| Catalog number | null | ❌ gap |
| Media refs | ART012, ART013, ART014 | ✓ |

### Evidence sources za stranicu

- ART012: Fenix Magazin — news, bez autora
- ART013: Dalmatinskiportal.hr — news, bez autora
- ART014: Narod.hr — news, bez autora
- MusicBrainz recording ID verificiran

### Preporučena page struktura

```
Hero: "Frane Tente" | Braća Kumerle Music · 2025.
Sekcija 1: Osnovni podaci (tablica)
Sekcija 2: Kontekst (Frane Tente — hrvatska domovinska tema)
Sekcija 3: Registri i identifikatori
Sekcija 4: Medijske reference (3 članka)
Sidebar: Slušaj (Spotify album) + Registri (MusicBrainz)
Footer: shared nav
```

### Schema.org

```json
{
  "@type": "MusicRecording",
  "name": "Frane Tente",
  "byArtist": { "@type": "MusicGroup", "name": "iZLET" },
  "datePublished": "2025",
  "recordingOf": {
    "@type": "MusicComposition",
    "composer": [
      { "@type": "Person", "name": "Toni Kumerle" },
      { "@type": "Person", "name": "Petar Kumerle" }
    ]
  },
  "sameAs": ["https://musicbrainz.org/recording/0999a678-4586-48c5-a1f1-598ffaa69977"]
}
```

### Missing authority signals

- ISRC — potreban za IFPI verification
- ISWC — potreban za Wikipedia citation
- Spotify track ID — potreban za streaming sidebar

### Deploy readiness: 7/10 — može se deployati bez ISRC/ISWC

---

## 2. Žalo — `/pjesme/zalo` ✓ DEPLOYED

**V2 Score:** 0.399 (→ ~0.619 nakon data gap korekcije) | **Rang:** #4 → potencijalni #1

### Status

Stranica postoji: `bracakumerle.com/pjesme/zalo`

### Kritični data gap

`works_registry.json → zalo.media_references` ne sadrži ART001 i ART002 — jedine GNG-eligible reference u cijelom sustavu.

**Ispravak potreban:**
```json
"media_references": ["ART001", "ART002", "MTV Adria rotation 2013", "HRT Radio Dubrovnik top lista"]
```

### Što stranica nema a treba

- ART001 (Ziher) i ART002 (Barikada) vidljivi kao medijske reference
- `year: 2016` dodat u work node
- MusicBrainz recording ID za Žalo specifično

### Deploy readiness: 8/10 — deployed, treba data gap korekciju

---

## 3. Sjever uz odsutne — `/pjesme/sjever-uz-odsutne`

**V2 Score:** 0.546 | **Rang:** #2

### Raspoloživi metadata

| Polje | Vrijednost | Status |
|---|---|---|
| Naslov | Sjever uz odsutne | ✓ |
| Godina | 2023 | ✓ |
| Label | Braća Kumerle Music | ✓ |
| Catalog | BKMUSIC001 | ✓ |
| Barcode | 199953974831 | ✓ |
| MusicBrainz recording | 87cf4afb-efbf-4627-a8b1-170725fa7807 | ✓ |
| MusicBrainz release | 8b675ac0-7ab0-40e3-b8a1-a2a6c2bab553 | ✓ |
| ISRC | null | ❌ gap |
| ISWC | null | ❌ gap |
| Media refs | 2 URL-a (braniteljski-forum, narod.hr) | ✓ |

### Preporučena page struktura

```
Hero: "Sjever uz odsutne" | BKM · BKMUSIC001 · 2023.
Sekcija 1: Osnovni podaci
Sekcija 2: Kontekst (podrška Bad Blue Boysima — jasna tema)
Sekcija 3: Registri (MusicBrainz recording + release verificirani)
Sekcija 4: Medijske reference (2 portala)
Sidebar: Registri (MusicBrainz release page direktni link)
```

### Schema.org

```json
{
  "@type": "MusicRecording",
  "name": "Sjever uz odsutne",
  "byArtist": { "@type": "MusicGroup", "name": "iZLET" },
  "datePublished": "2023",
  "isrcCode": null,
  "sameAs": [
    "https://musicbrainz.org/recording/87cf4afb-efbf-4627-a8b1-170725fa7807",
    "https://musicbrainz.org/release/8b675ac0-7ab0-40e3-b8a1-a2a6c2bab553"
  ]
}
```

### Missing authority signals

- ISRC — gap (DistroKid ima, treba ekstrahirati)
- ISWC — gap

### Deploy readiness: 8/10 — najjači MusicBrainz profil, može deployati odmah

---

## 4. Moj Dinamo — `/pjesme/moj-dinamo`

**V2 Score:** 0.441 | **Rang:** #3

### Raspoloživi metadata

| Polje | Vrijednost | Status |
|---|---|---|
| Naslov | Moj Dinamo | ✓ |
| Godina | 2025 | ✓ |
| Label | Braća Kumerle Music | ✓ |
| MusicBrainz recording | 08a4c06f-f83f-4d88-ac3a-b3ac6160d7d6 | ✓ |
| ISRC | null | ❌ gap |
| ISWC | null | ❌ gap |
| Catalog | null | ❌ gap |
| Media refs | ART017 (HOP), ART018 (Zagreb.info) | ✓ |

### Napomena o temi

Moj Dinamo je navijačka / sportska tema (GNK Dinamo Zagreb). Medijska pokrivenost vezana uz specifičan kontekst — ne glazbeni press. To ograničava GNG eligibility ali ne i authority page deployment.

### Deploy readiness: 6/10 — može deployati, slabiji external signal od Frane Tente i Sjever

---

## 5. Čast — `/pjesme/cast`

**V2 Score:** 0.266 | **Rang:** #5

### Raspoloživi metadata

| Polje | Vrijednost | Status |
|---|---|---|
| Naslov | Čast | ✓ |
| ISRC | HRA371800845 | ✓ |
| ISWC | T-931.111.745-0 | ✓ |
| Label | Dallas Records (Katarza 2019) | ✓ (indirektno) |
| MusicBrainz | null | ❌ gap |
| Media refs | ART011 (Likaclub, gng:False) | ⚠️ slabo |

### Kritični gap

Čast ima najbolje identifikatore ali najslabiju medijsku pokrivenost. ART011 je jedina referenca i nije GNG eligible.

**Authority page za Čast ima smisla tek nakon** jedne od:
- Tier A medijske reference (glazbena platforma, identificirani autor)
- MusicBrainz recording ID

### Deploy readiness: 4/10 — odgoditi do Tier A reference

---

## Deployment redosljed

| Prioritet | Work | Action |
|---|---|---|
| P1 | frane_tente | Kreirati `/pjesme/frane-tente` odmah |
| P2 | sjever_uz_odsutne | `/pjesme/sjever-uz-odsutne` postoji — verificirati sadržaj |
| P3 | zalo | Deployed — ispraviti data gap (ART001, ART002) |
| P4 | moj_dinamo | `/pjesme/moj-dinamo` postoji — verificirati sadržaj |
| P5 | cast | Odgoditi — čeka Tier A referencu |

---

## Shared zahtjevi za sve stranice

1. `global.css` link u `<head>`
2. Shared nav (`.bk-site-header`) iz `docs/shared-nav.html`
3. Schema.org `MusicRecording` s `byArtist` → `MusicGroup` → `sameAs` Wikidata + MusicBrainz
4. Canonical URL: `https://bracakumerle.com/pjesme/[slug]`
5. `og:type: music.song`
6. Breadcrumb nav: bracakumerle.com › Diskografija › [Naziv]

---

*Generirano: 30.05.2026. — Claude (Ministar Autoriteta)*  
*STATUS: DRAFT — čeka ratifikaciju redosljeda od Generala*
