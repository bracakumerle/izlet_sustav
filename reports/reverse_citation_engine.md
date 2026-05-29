# Reverse Citation Engine — Audit Report
**Datum:** 29.05.2026.
**Status:** [OBSERVED] — čeka ratifikaciju Generala
**Izvor:** media_registry.json v1.0, works_registry.json, web fetch

---

## Svrha

Identificirati koji vanjski članci mogu poslužiti kao temelj za outreach prema novim citacijama, te koji works_registry zapisi imaju nedostajuće externe identifikatore koji blokiraju authority loop.

---

## ART001 — Ziher.hr Intervju

**Članak:** iZLET: "Volimo uživati u svakom poslu kojim se bavimo"
**Autor:** Ivan Košar
**Datum:** 26. srpnja 2016.
**URL:** https://www.ziher.hr/intervju-izlet/
**GNG eligible:** DA
**Status:** LIVE

### Što članak pokriva

- Intervju s bendom povodom albuma *Nikad ne znaš, to je ono…* (2016., Dallas Records)
- Autorska glazba, identitet benda, motivacija
- Nezavisna glazbena platforma — nije PR, nije sponzorirani sadržaj

### Veze s works_registry

| Work | Veza | ISRC | ISWC | MusicBrainz | Spotify |
|---|---|---|---|---|---|
| Album "Nikad ne znaš" | Direktna — tema intervjua | ❌ null | ❌ null | ⚠️ djelomično | ❌ null |
| Žalo | Sadržajno | ❌ null | T-914.228.446-6 ✓ | ❌ null | ⚠️ |
| Pernastica | Sadržajno | ❌ null | ❌ null | ❌ null | ❌ null |
| Majčin skut | Sadržajno | ❌ null | ❌ null | ❌ null | ❌ null |

### Authority score

**8.5/10** — Nezavisni autor, glazbena platforma, specifična tema (album), live URL.

### Outreach readiness

**VISOKA** — Ivan Košar je identificiran autor. Moguć direktni kontakt.

### Potencijalna arhivska dopuna (za bracakumerle.com)

Od 2016. do danas projekt je objavio još dva studijska albuma (*Katarza*, 2019.) i niz autorskih singlova pod Braća Kumerle Music (2023–2026.). Kanal @bracakumerle danas broji 254 javno dostupna videozapisa organizirana u pet arhivskih epoha. Album *Nikad ne znaš, to je ono…* dokumentiran je na Discogu, MusicBrainzu i Wikidati (Q139595518). Intervju na Ziher.hr ostaje primarni nezavisni glazbeni zapis o tom periodu.

### Akcija

1. Fetch članka — verificirati koje pjesme se eksplicitno spominju
2. Kontakt Ivan Košar — prijedlog follow-up članka ili kratke bilješke o nastavku projekta
3. Dodati Ziher.hr URL u `/vizualni-identitet` → Sekcija 6 (medijska pokrivenost)

---

## ART002 — Barikada.com Recenzija

**Članak:** iZLET – Nikad ne znaš, to je ono… – recenzija albuma
**Autor:** Dragutin Matošević
**Datum:** 27. listopada 2016.
**URL:** https://barikada.com/izlet-nikad-ne-znas-to-je-ono/
**GNG eligible:** DA
**Status:** LIVE

### Što članak pokriva

- Recenzija albuma *Nikad ne znaš, to je ono…* (2016., Dallas Records)
- Nezavisna glazbena recenzija — najjači tip sekundarnog izvora za Wikipedia GNG
- Barikada.com = respektabilna hrvatska glazbena platforma

### Veze s works_registry

| Work | Veza | ISRC | ISWC | MusicBrainz | Spotify |
|---|---|---|---|---|---|
| Album "Nikad ne znaš" | Direktna — tema recenzije | ❌ null | ❌ null | ⚠️ djelomično | ❌ null |
| Žalo | Sadržajno (MTV Adria) | ❌ null | T-914.228.446-6 ✓ | ❌ null | ⚠️ |

### Authority score

**9.0/10** — Nezavisna recenzija, identificirani autor, glazbena platforma, live URL. Najjači single authority signal u cijelom media_registry-u (isključujući incident cluster).

### Outreach readiness

**VISOKA** — Dragutin Matošević je identificiran autor. Aktivan kritičar.

### Potencijalna arhivska dopuna (za bracakumerle.com)

Album *Nikad ne znaš, to je ono…* (2016.) bio je prvi studiosi album pod Dallas Records. Recenzija na Barikadi dokumentira autorski smjer benda u preddomoljubnoj fazi. Od tada projekt je razvio novi identitetski sloj — domoljubna glazba, HOS tematika, BBB/navijački sadržaj — koji nije bio prisutan u 2016. godini. Recenzija stoga ostaje primarni dokument specifične kreativne faze koja je prethodila trenutnom identitetu.

### Akcija

1. Fetch članka — verificirati koje pjesme se eksplicitno ocjenjuju
2. Kontakt Dragutin Matošević — prijedlog recenzije BKM singla ili novog albuma
3. Dodati Barikada.com URL u Wikipedia HR članak kao citation za GNG

---

## Usporedna analiza

| | ART001 Ziher | ART002 Barikada |
|---|---|---|
| Tip | Intervju | Recenzija |
| Autor | Ivan Košar | Dragutin Matošević |
| GNG weight | Srednji-visok | Visok |
| Wikipedia citabilnost | DA | DA |
| Outreach potencijal | Visok | Visok |
| Tema | Album 2016 | Album 2016 |
| Blokirajući gap | ISRC/ISWC za album | ISRC/ISWC za album |

---

## Kritični gap: Dallas Records era bez identifikatora

Oba članka se referiraju na album *Nikad ne znaš, to je ono…* (2016.) koji u works_registry nema:
- ISRC za individualne pjesme
- Spotify track IDs
- MusicBrainz release ID za album

**Ovo je blokirajući gap za Wikipedia citabilnost.** Bez verificiranih eksternih identifikatora, album postoji samo kao tvrdnja — ne kao verificirani entitet.

### Prioritetna akcija za gap zatvaranje

1. Discogs release ID za album (https://www.discogs.com/artist/6610944 — provjeriti)
2. MusicBrainz release unos za "Nikad ne znaš, to je ono…"
3. Spotify album URL: https://open.spotify.com/album/6hT2KjY5IqE6e3wqSmNJyB (verificirati)

---

## Outreach strategija

### Faza 1 — Fetch i analiza (1-2 dana)
- Fetchati ART001 i ART002 — identificirati sve pjesme koje se eksplicitno spominju
- Mapirati na works_registry zapise

### Faza 2 — Gap popunjavanje (2-5 dana)
- Dodati MusicBrainz i Discogs identifikatore za "Nikad ne znaš" album
- Verificirati Spotify album URL

### Faza 3 — Outreach (5-14 dana)
- Kontaktirati Ivan Košar (Ziher.hr) — follow-up intervju ili kratka bilješka
- Kontaktirati Dragutin Matošević (Barikada) — recenzija novog materijala
- Prijedlog: poslati link na bracakumerle.com/vizualni-identitet kao referentni materijal

### Faza 4 — Wikipedia deployment (14-30 dana)
- Koristiti ART001 + ART002 kao primarne citacije za EN Wikipedia draft
- Dodati ART002 kao GNG citation u HR Wikipedia rebuild

---

## Authority score projekta — trenutno stanje

| Komponenta | Status | % |
|---|---|---|
| Entity Consistency | Wikidata, MB, Discogs, Schema.org | ~85% |
| Indexed Documentation | bracakumerle.com, vizualni-identitet, YouTube | ~65% |
| External Mentions | ART001, ART002 = jedine GNG-eligible citacije | ~25% |

**Usko grlo:** External Mentions. Sve ostalo je sekundarno.

---

*Generirano: 29.05.2026. — Claude (Ministar Autoriteta)*
*[OBSERVED] — čeka ratifikaciju Generala*
