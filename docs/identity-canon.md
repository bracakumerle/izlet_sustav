# iZLET — Identity Canon (v1.0)

Status: APPROVED (Petar/Toni, 2026-06-11) — spreman za commit kao
`docs/identity-canon.md`. Multi-model audit (Claude/GPT/Gemini/Grok/Perplexity)
zatvoren. Daljnje dopune organske, ne čekaju vanjski review.
Izvor: KAB-OPS-001, multi-model konvergencija (Claude/GPT/Gemini/Grok/Perplexity), 2026-06-11

## Svrha

Jezgra identiteta projekta — minimalni skup činjenica koji mora preživjeti
svaku buduću kompresiju (web redesign, AI sažetak, Wikipedia, knowledge panel).
Stabilan dokument, mijenja se rijetko. Sve izvedeno (web copy, JSON-LD `about`,
E-001 trailer script, E-002 epizode) referencira ovaj dokument kao source of
truth za narativ. Repo wins.

Prijelazi i njihovi razlozi ("zašto") žive u zasebnom živom dokumentu —
vidi `docs/transitions.md`. Ne miješati: ovaj dokument je jezgra, transitions.md
raste s vremenom.

---

```yaml
people:
  - name: Petar Kumerle
    role: autor teksta i glazbe, izvođač
  - name: Toni Kumerle
    role: autor teksta i glazbe, izvođač
  # relacija (Petar ↔ Toni = Braća Kumerle) već je strukturno kodirana:
  # /people/petar-kumerle i /people/toni-kumerle međusobno linkaju kao
  # "Član sastava" unutar MusicGroup entiteta — nema potrebe za zasebnim
  # "Brotherhood" poljem, odnos je topološki, ne samo tekstualan.

purpose: >
  Kontinuirani autorski rad Petra i Tonija Kumerlea kroz koji se iskustva,
  vrijednosti i sjećanja prirodno pretaču u pjesme i dokumentaciju.

continuity:
  start: 2007
  end: present
  creative_identity: iZLET
  publishing_identity: Braća Kumerle (autorsko/publishing ime, DistroKid)

themes:
  - identitet i pamćenje (povijesna/domoljubna tematika)
  - vjera
  - kontinuitet kroz generacije
  - osobno i kolektivno iskustvo

# works_reference NAMJERNO izostavljen iz jezgre (v0.4 odluka):
# popis ključnih/sekundarnih djela je operativni izbor (end-screen klaster,
# /pjesme/ stranice) koji se može promijeniti do 2040. bez utjecaja na
# people/continuity/themes/eras. Source of truth ostaje web registry
# (/pjesme/ + end-screen mapping), ne ovaj dokument — izbjegava duplikat/drift.

eras:   # izvor: bracakumerle.com/bio + /people/ (Web layer, objavljeno — zamjenjuje raniju GPT rekonstrukciju)
  - "2007-2012: Formacija i demo era — 7 demo izdanja (uklj. CMC Demo 2009 na Croatia Records kompilaciji), prvi nastup 23.3.2007. (III. gimnazija Zagreb)"
  - "2013-2015: Singl proboj — Žalo, Maša, Pernastica, Svemir"
  - "2016-2019: Dallas Records — albumi 'Nikad ne znaš, to je ono…' (2016) i 'Katarza' (2019), live circuit"
  - "2020-2024: Tranzicija — Frane Tente originalna snimka, priprema neovisne faze"
  - "2025-: Braća Kumerle Music era — neovisna distribucija, arhiv aktivan, corpus u izgradnji"
```

---

## Napomena o "kompresiji"

Ovo NIJE "Canonical Story Object" u GPT/Grok smislu (ne modelira
"rekonstruktibilnost za 2050"). Ovo je obična biografska/uredbena referenca —
ulazni podatak za E-001 (trailer script) i E-002 (Priče iza pjesama).
Apstraktniji slojevi (Compression, Reconstructibility) nisu polja u dokumentu;
oni su posljedica toga da ovaj dokument postoji i da se redovito održava.

## Otvoreno za potvrdu (Petar/Toni)

- [x] Eras — potvrđeno (Petar, 2026-06-11): tranzicija 2020-2024, Braća Kumerle Music era od 2025.
- [ ] Themes — dopuniti iz stvarne tag taksonomije (interna taksonomija živi u registry, ne ovdje)
- [ ] Purpose — odobriti formulaciju ili predložiti vlastitu

Prijelazi i njihovi razlozi: vidi `transitions-draft.md` (zaseban, ACTIVE DRAFT, raste s vremenom).
Popis djela (primary/secondary): vidi web registry (/pjesme/ + end-screen mapping) — izvan ovog dokumenta.
