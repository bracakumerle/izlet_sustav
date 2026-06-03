# ADR: Lyrics Registry Architecture

**Datum:** 2026-06-03  
**Status:** LOCKED  
**Donositelj:** General (Petar Kumerle)

---

## Odluka

```
Canonical:  registries/lyrics_corpus_registry.csv
Derived:    build/works_registry.json (generated, never manually edited)
Rule:       CSV → generator → JSON. Never reverse.
```

---

## Kontekst

`registries/lyrics_corpus_registry.csv` je jedini izvor istine za lyrics corpus podatke. Svaki JSON derivat mora biti generiran iz CSV-a putem build skripte — nikad ručno editiran.

`works_registry.json` status check ostaje otvoren — ishod određuje retire vs. generate, ne samu arhitekturu.

---

## Posljedice

- Ručne izmjene `works_registry.json` su zabranjene
- Svaki novi lyrics entry ide u CSV
- Build skripta (kad bude kreirana) čita CSV, piše JSON
- Validacija u CI: ako `works_registry.json` postoji a nije generiran — flag
