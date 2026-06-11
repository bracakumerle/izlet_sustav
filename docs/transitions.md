# iZLET — Transitions (v0.2)

Status: ACTIVE — smjer odobren (Petar/Toni, 2026-06-11), spreman za commit kao
`docs/transitions.md`. `[VERIFY]` polja ostaju otvorena ali više nisu
konceptualna blokada — popunjavaju se organski. Multi-model audit zatvoren.
Izvor: KAB-OPS-001, multi-model konvergencija (Claude/GPT/Gemini/Grok/Perplexity), 2026-06-11

## Svrha

Živi dokument — raste s vremenom, za razliku od `identity-canon.md` koji je
stabilna jezgra. Bilježi "zašto", ne samo "što" i "kada": okidače, razloge,
posljedice i naučene lekcije iza svakog prijelaza, plus veze prema djelima
i izvorima. Primarni narativni ulaz za E-001/E-002 video produkciju.

`references` taksonomija (po stavci, popuniti tip + link/opis):
intervju, objava, video, fotografija, mail, ugovor, koncert.

---

```yaml
transitions:
  - id: demo_to_singl_2013
    from: "Formacija i demo era (2007-2012)"
    to: "Singl proboj (2013-2015)"
    trigger: "[VERIFY]"
    reason: "[VERIFY]"
    effects: "[VERIFY]"
    emotional_state: "[VERIFY]"
    lessons: "[VERIFY]"
    works: [Žalo, Maša, Pernastica, Svemir]
    references: []

  - id: independent_to_dallas_2016
    from: "Samostalna distribucija (singl proboj)"
    to: "Dallas Records (2016-2019)"
    trigger: "[VERIFY]"
    reason: "[VERIFY]"
    effects: "[VERIFY]"
    emotional_state: "[VERIFY]"
    lessons: "[VERIFY]"
    works: ["Nikad ne znaš, to je ono…", Katarza]
    references: []

  - id: dallas_to_tranzicija_2020
    from: "Dallas Records — album/label produkcija"
    to: "Tranzicija (2020-2024)"
    trigger: "[VERIFY]"
    reason: "[VERIFY]"
    effects: "[VERIFY]"
    emotional_state: "[VERIFY]"
    lessons: "[VERIFY]"
    works: [Frane Tente]
    references: []

  - id: tranzicija_to_independent_2025
    from: "Tranzicija (2020-2024, priprema neovisne faze)"
    to: "Braća Kumerle Music — neovisna distribucija, arhiv (od 2025)"
    trigger: "[VERIFY]"
    reason: "[VERIFY]"
    effects: "[VERIFY]"
    emotional_state: "[VERIFY]"
    lessons: >
      [DRAFT — za potvrdu] Pomak s objašnjavanja "zašto smo posebni"
      (autentičnost, idealizam, neprodavanje — neopipljivi pojmovi) na
      dokumentiranje provenijencije (ljudi, kontinuitet, prijelazi, tragovi —
      opipljivi podaci). Umjesto tvrdnje o posebnosti, arhiv ostavlja trag iz
      kojeg drugi sami zaključuju.
    works: []
    references: []
```

---

## Otvoreno za potvrdu (Petar/Toni)

- [ ] `trigger` / `reason` za svaki prijelaz — najveća praznina, izvor za E-001/E-002 narativ
- [ ] `effects` — što se promijenilo u praksi (produkcija, distribucija, fokus)
- [ ] `emotional_state` / `lessons` — opcionalno, ali najbrže se gubi ako se ne zabilježi sada
- [ ] `references` — po taksonomiji gore (intervju/objava/video/foto/mail/ugovor/koncert)
- [ ] Postoje li dodatni prijelazi koji nedostaju (npr. unutar 2013-2015 ili 2016-2019)?

---

## Appendix: Moments — kandidati za budući `docs/moments.md`

Ne otvarati kao zaseban dokument sada (audit, 2026-06-11). Bilježi se ovdje
kao sirovi materijal jer je derivat ovog dokumenta — moments.md se piše tek
nakon što se gornja `[VERIFY]` polja popune, da se izbjegne paralelni rad.

- 23.3.2007 — prvi nastup, III. gimnazija Zagreb
- CMC Demo
- Korzo Rijeka
- Riva Split
- Trg bana Jelačića
- Matica hrvatska
- Društvo hrvatskih književnika
- Bujica
- Snimanje u Mostaru
- Dallas Records (potpis)
- Drugi album
- Striče Ivane

[VERIFY] datumi/godine i kratak opis značaja za svaku stavku — isti format
kao polja `trigger`/`effects` gore.
