# Authority Acquisition Dashboard

**STATUS:** LIVE  
**GENERATED:** 30.05.2026.  
**NEXT REVIEW:** 30.06.2026.

---

## Strateški kontekst

Infrastruktura je završena. Bottleneck je isključivo External Authority.

```
Entity Consistency     ~85%  ✓ riješeno
Indexed Documentation  ~70%  ✓ riješeno
External Mentions      ~25%  ← JEDINI PREOSTALI PROBLEM
```

---

## Dashboard — 5 radova

### Žalo

| Metrika | Trenutno | Target |
|---|---|---|
| Vanjske reference | 2 (ART001, ART002) | 5+ |
| Neovisne domene | 2 (Barikada, Ziher) | 4+ |
| GNG-eligible | **2** ← jedino u sustavu | 3+ |
| Authority score V2 | ~0.619 (nakon patch) | 0.75+ |
| Authority page | ✓ live | — |

**Gap:** Jedini rad s GNG-eligible referencama. Treba lyrics platform (Genius/Musixmatch) i još jednu glazbenu recenziju.

**Target source:** Glazbeni portal s recenzentom + autor identificiran.

---

### Čast

| Metrika | Trenutno | Target |
|---|---|---|
| Vanjske reference | 1 (ART011) | 4+ |
| Neovisne domene | 1 (Likaclub) | 3+ |
| GNG-eligible | 0 | 1+ |
| Authority score V2 | 0.266 | 0.55+ |
| Authority page | ✓ live | — |

**Gap:** Najjači identifikatori (ISRC+ISWC) ali najslabija medijska pokrivenost. Jedan Tier A članak → skok na ~0.55+.

**Target source:** Muzika.hr, Ravno do dna, ili bilo koji glazbeni portal s autorom.

---

### Frane Tente

| Metrika | Trenutno | Target |
|---|---|---|
| Vanjske reference | 3 (ART012-014) | 6+ |
| Neovisne domene | 3 (Fenix, Narod, Dalmatinski) | 5+ |
| GNG-eligible | 0 | 1+ |
| Authority score V2 | 0.589 | 0.70+ |
| Authority page | ✓ live | — |

**Gap:** Tema Frane Tente kao osobe ima ekstenzivnu mainstream pokrivenost (Index, 24sata, Jutarnji, Wikipedia HR) ali bez direktne veze na iZLET pjesmu. Jedan mainstream članak koji eksplicitno veže osobu + pjesmu = veliki skok.

**Target source:** Lokalni splitski/dalmatinski portal ili kulturna institucija koja prati Marjansku tematiku.

---

### Sjever uz odsutne

| Metrika | Trenutno | Target |
|---|---|---|
| Vanjske reference | 2 (ART015-016) | 5+ |
| Neovisne domene | 2 (Braniteljski forum, Narod) | 4+ |
| GNG-eligible | 0 | 1+ |
| Authority score V2 | 0.546 | 0.65+ |
| Authority page | ✓ live | — |

**Gap:** BBB ekosustav je prirodni distribution kanal. Tekst fraze "Sjever uz odsutne" kao navijački topos → potencijal za citaciju na fan arhivama i navijačkim portalima.

**Target source:** badblueboys.hr, navijački portali, sportski mediji koji pokrivaju BBB kulturu.

---

### Moj Dinamo

| Metrika | Trenutno | Target |
|---|---|---|
| Vanjske reference | 2 (ART017-018) | 5+ |
| Neovisne domene | 2 (HOP, Zagreb.info) | 4+ |
| GNG-eligible | 0 | 1+ |
| Authority score V2 | 0.441 | 0.60+ |
| Authority page | ✓ live | — |

**Gap:** 70K YouTube pregleda = dokaz distribucije ali nema glazbeno-medijskog teksta. Shazam listing verificiran. Sportski i navijački portali su prirodni kanal.

**Target source:** Sportski portali (Goal.hr, Index sport), navijački portali, radio emisije koje pokrivaju navijačku glazbu.

---

## Prioritetni redosljed za External Authority Acquisition

| Rang | Rad | Razlog prioriteta | Najlakši put |
|---|---|---|---|
| 1 | Frane Tente | Tema već medijski pokrivena, treba samo veza | Lokalni/kulturni portal |
| 2 | Moj Dinamo | 70K YT views, BBB ekosustav, discovery potencijal | Sportski/navijački portal |
| 3 | Sjever uz odsutne | Isti razlog + BBB kontekst aktivan | Navijački arhivi |
| 4 | Žalo | GNG-eligible već — treba lyrics platform | Genius/Musixmatch |
| 5 | Čast | Najteži — treba glazbeni Tier A | Glazbeni portal |

---

## Akcijski plan — 30 dana

### Tjedan 1-2: Discovery
- Perplexity: scouting potencijalnih izvora za svaku pjesmu
- Gemini: authority gap mapping (current vs desired evidence)
- Grok: ROI prioritizacija (koje 5 URL-ova najviše podiže cijeli sustav)

### Tjedan 3-4: Execution
- Lyrics platforms: Genius i Musixmatch za sve 5 pjesama
- Wikipedia HR: dodati links na authority pages u diskografiji
- Wikidata: dodati `bracakumerle.com/pjesme/*` URL-ove kao references

---

## Što se NE radi

- ❌ Novi HTML deployment ciklusi
- ❌ Novi scoring modeli
- ❌ Infrastrukturni radovi
- ❌ Governance dokumenti

Sve je riješeno. Jedino što podiže authority su **vanjski, neovisni, indeksirani izvori**.

---

*Generirano: 30.05.2026. — Claude (Ministar Autoriteta)*  
*Sljedeći review: 30.06.2026. — mjeriti promjenu u External Mentions %*
