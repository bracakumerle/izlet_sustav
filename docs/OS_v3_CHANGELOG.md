# OS v3.0 — CHANGELOG (proof-through-practice)
## Pravilo: OS v3.0 se NE širi tijekom probe. Situacije koje okvir ne pokriva bilježe se ovdje. v3.1 tek nakon 30 dana stvarnog rada.
### OPERATIONAL TRIAL prozor: 2026-07-12 → 2026-08-11 · v3.1 review: ~2026-08-11

> Zašto: okvir je dosegao zrelost gdje svaka nova ideja lako postaje novi false gap. Isti princip koji uvodimo za sustav — **prvo dokaz kroz praksu, zatim ratifikacija** — primjenjuje se i na sam okvir.

---

## CHANGE ACCEPTANCE CRITERIA (v3.1 gate)
Promjena ulazi u v3.1 SAMO ako zadovoljava **najmanje jedan** kriterij:
- [ ] Spriječila bi stvarni incident zabilježen u Field Logu (§B).
- [ ] Uklanja dokazanu redundanciju.
- [ ] Smanjuje broj koraka u operativnom tijeku.
- [ ] Rješava ponavljajući problem u ≥2 različita subsystema.
- [ ] Usklađuje okvir s već ratificiranim kanonom.

**Ako nijedan kriterij nije zadovoljen → promjena se ODBACUJE.** (Sprječava da v3.1 postane zbroj dobrih ideja koje nikad nisu bile stvarno potrebne.)

---

## A. v3.1 KANDIDATI (zabilježeni, NE implementirani — GPT review 2026-07-12)
Ne graditi tijekom probe. Svaki se validira stvarnom potrebom u 30 dana.

1. **Owner split — Domain vs Execution.** „Owner" = Execution Owner; Domain Owner svih DA-slojeva = General. *(Djelomično već korigirano inline u OS v3.0 §2; puna dvokolonska matrica = v3.1.)* — **prioritet (ispravak, ne proširenje).**
2. **Capability Matrix.** Layer × {Read · Analyze · Propose · Execute · Publish} × agent (✅/⚠/❌). Rješava „tko što SMIJE", ne samo „tko je owner". Primjer: Claude/Registry = Read✅ Analyze✅ Propose✅ Execute⚠ Publish❌.
3. **Confidence per subsystem** u SYSTEM_INDEX. Uz „status: implemented" dodati „confidence: X% (razlog)". Npr. Repository 98% · Research 60% (not fully inspected). Pokazuje slijepe točke.
4. **Evidence Chain (nacrtan).** Observation → Evidence → Decision → Implementation → Verification. Već se radi (Mutation IR/gate), ali nije dijagram.
5. **Dependency network (šire).** Trenutni lanac je linearan; proširiti u mrežu: Registry → Automation → Schema → Web → MusicBrainz → Wikidata → Google → YouTube → Signals → Research → Dashboard → Discovery.
6. **SYSTEM HEALTH KPI** (≠ SYSTEM STATUS). Per-layer % (Registry 97 · Authority 82 · Signal 74 · Research 91 · Automation 88 · YouTube 79) + ukupni SYSTEM HEALTH %. Postaje KPI cijelog sustava.

---

## B. FIELD LOG — situacije koje okvir NE pokriva (puni se tijekom rada)
| Datum | Situacija koju okvir ne pokriva | Sloj | Predloženo pravilo (v3.1) | Status |
|---|---|---|---|---|
| 2026-07-12 | Naziv `works_registry.json` koristi se za DVIJE različite datoteke (root=rights-kanon 44; `registries/`=census-candidate 76) → dugoročno zbunjuje | L2 Registry | Nakon reconciliationa preimenovati `registries/works_registry.json` → `works_census_registry.json` (ili `_candidate_`). Naming-collision guard u dissekciji. | TECH DEBT (ne hitno) — otkriveno u Dissection Track B |
| 2026-07-12 | Dependency Validation nalaz nema „Canonical Source" (odakle „Expected") → za 6 mj neće biti očito | Metodologija (BETA) | Dodati stupac u finding format: Evidence · **Canonical Source** · Expected · Observed · Severity · Action | v3.1 KANDIDAT — validirano u BETA-01 (GPT) |
| 2026-07-12 | Rizik parcijalne izmjene tijekom validacije (kontaminira analizu; gubi se jedinstven paket) | Metodologija (BETA) | **PRAVILO: „Validation Phase is READ-ONLY."** Implementacija = zasebna faza tek nakon: full validation → Validation Report → klasifikacija → jedinstveni Implementation Plan → ratifikacija → kontrolirani Implementation | GENERAL RATIFICIRAO 2026-07-12 |

---

## C. PROTOKOL PROBE
- Ne mijenjati OS v3.0 §1–§6 tijekom prozora (osim čistih ispravaka netočnosti).
- Svaki „framework ne pokriva ovo" trenutak → redak u §B (ne odmah pravilo).
- Na kraju prozora (~2026-08-11): pregled §B → koji kandidati iz §A su se DOKAZALI potrebom → tek tada v3.1.
- Kandidat koji se u 30 dana nije pojavio u §B = NE ulazi u v3.1 (dokaz kroz praksu, ne pretpostavka).

---
*OS v3.0 CHANGELOG · otvoren 2026-07-12 · proof-through-practice · ne širi okvir tijekom probe.*
