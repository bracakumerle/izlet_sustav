# ZAMP Catalogue Reconciliation
**Datum:** 2026-06-04  
**Izvor:** ZAMP baza autora (live), works_registry.json (canonical, 44 radova)  
**Metoda:** P+T intersection — iZLET kandidati = djelo registrirano na oba autora

> **Napomena o terminologiji:** P+T intersection ≠ automatski iZLET corpus.  
> Presjek dokazuje da su Petar i Toni koautori, ali ne dokazuje izvođača.  
> Svih 17 radova u delta skupu klasificirani su kao UNCLASSIFIED pending performer verification.

---

## Rezultati

| Kategorija | Broj |
|---|---|
| Toni Kumerle ZAMP ukupno | 67 |
| Petar Kumerle ZAMP ukupno | 61 |
| P+T intersection (oba autora) | **60** |
| Već u works_registry.json | 39 |
| Normalizacijski mismatch (u registru, drugačiji naslov) | 4 |
| **Delta skup — unclassified Petar/Toni shared works** | **17** |
| Toni-only (vjerojatno ne iZLET) | 7 |
| Petar-only | 1 |

---

## Normalizacijski mismatches (u registru, drugačiji naslov)

| ZAMP naslov | Registry naslov | Napomena |
|---|---|---|
| Noćima - Here I am | Noćima (Here I Am) | Identičan rad |
| Topim se i gubim | Topim se i gubim se | Nedostaje "se" |
| XIX bojna HOS Vitez Jure Francetić | Vitez Jure | Skraćen u registru |
| Frane Tente pjesma o domoljubu | Frane Tente | Skraćen u registru |

---

## 17 unclassified Petar/Toni shared works (delta skup)

**Status:** UNCLASSIFIED — awaiting performer verification  
**Dozvoljene klasifikacije:** `IZLET_CORE` / `EARLY_IZLET` / `LETECI_MAJMUNI` / `VISKI_STRIP` / `OTHER` / `UNKNOWN`  
**Izvor klasifikacije:** ZAMP registration details ili osobna potvrda autora — ne godina registracije

| Godina | Naslov | Klasifikacija | Napomena |
|---|---|---|---|
| 2007 | Autori nalaze smisao | UNCLASSIFIED | Rana era — izvođač nepoznat |
| 2009 | Tvoje je pitanje totalno suvišno | UNCLASSIFIED | Rana era — izvođač nepoznat |
| 2013 | Postoji samo jedan Bog | UNCLASSIFIED | — |
| 2014 | Konji od žada | UNCLASSIFIED | — |
| 2018 | Htio bi samo ostati tamo | UNCLASSIFIED | Katarza era po godini — izvođač nepoznat |
| 2018 | Ljubav liječi sve | UNCLASSIFIED | Katarza era po godini — izvođač nepoznat |
| 2018 | Neka slatko boli | UNCLASSIFIED | Katarza era po godini — izvođač nepoznat |
| 2018 | Nema mjesta | UNCLASSIFIED | Katarza era po godini — izvođač nepoznat |
| 2018 | Obale se tope | UNCLASSIFIED | Katarza era po godini — izvođač nepoznat |
| 2018 | Samo tamo | UNCLASSIFIED | Katarza era po godini — izvođač nepoznat |
| 2018 | Trag koji ostavlja | UNCLASSIFIED | Katarza era po godini — izvođač nepoznat |
| 2018 | Tužni odlazak | UNCLASSIFIED | Katarza era po godini — izvođač nepoznat |
| 2019 | Hrabrost | UNCLASSIFIED | Post-Katarza — izvođač nepoznat |
| 2019 | Hrvatski trolist | UNCLASSIFIED | Post-Katarza — izvođač nepoznat |
| 2019 | Koza u velegradu | UNCLASSIFIED | Post-Katarza — izvođač nepoznat |
| 2019 | Starčevićeva himna | UNCLASSIFIED | Post-Katarza — izvođač nepoznat |
| 2020 | Njedra | UNCLASSIFIED | — |

---

## Toni-only (7 — vjerojatno ne iZLET)

Cupilajac (2012) · Dok me diraš rukama (2011) · Filter boy (2010) · Kajla (2007)  
Ljeto ide majko (2012) · Možda je to (2011) · So sweet (2010)

---

## Petar-only (1)

Odlazak (2018) — potencijalno isti rad kao Tužni odlazak (Toni)? Requires cross-check.

---

## Tok klasifikacije

```
reports/zamp_catalogue_reconciliation_2026-06-04.md  ← ovaj dokument
         ↓
   Classification Sprint (za svih 17)
         ↓
   IZLET_CORE | EARLY_IZLET | LETECI_MAJMUNI | VISKI_STRIP | OTHER | UNKNOWN
         ↓
   works_registry.json  ← tek nakon klasifikacije
```

**works_registry.json se ne mijenja dok klasifikacija nije potvrđena.**

---

## Napomene

- P+T intersection ≠ automatski iZLET (braća mogu zajednički pisati za druge izvođače)
- Za svaki od 17: verificirati na Spotify/MusicBrainz/Discogs/ZAMP detalji pod kojim izvođačem
- 2007-2009 radovi: rana era — potencijalno Leteći Majmuni, ali bez dokaza
- 2018 cluster (8 radova): Katarza era po godini registracije — izvođač nepoznat, ne pretpostavljati B-sides
- Katarza album (2019) u registru ima 13 trackova — provjeri preklapanje s ovim listom
- Petar-only Odlazak (2018) vs Toni-registrirani Tužni odlazak (2018): visoko sumnjiv split registration