# iZLET Operating System v3.0 — Operativni okvir (disciplina, ne funkcionalnost)
## Status: OPERATIONAL TRIAL — službeni operativni okvir U UPORABI (nije eksperiment); prikupljaju se podaci za evoluciju. Prozor 2026-07-12 → 2026-08-11. SMJER ratificiran, dokument NE. Ne širiti okvir; situacije koje ne pokriva → `OS_v3_CHANGELOG.md`; v3.1 tek nakon mjesec dana stvarnog rada (proof-through-practice). Agent ne samo-amandira (001I §7).
## Autor: Claude (Ministar autoriteta) · 2026-07-12 · sinteza postojećeg + 3 stvarno nedostajuća dijela. Companion: `SYSTEM_INDEX.md`.

> v3.0 ne dodaje funkcionalnost — dodaje **operativnu disciplinu** da auditi/implementacije/istraživanja počinju iz istog, provjerenog konteksta.

---

## §0. FALSE-GAP DEFENCE PRIMIJENJENA NA OVAJ PRIJEDLOG
(Prije pisanja provjereno postoji li već — po vlastitom zakonu.)

| Tražena komponenta | Već postoji? | Gdje | v3.0 dodaje |
|---|---|---|---|
| Mutation Rules | ✅ uglavnom | `MUTATION_IR_SPEC_v1.0` (FROZEN) + `PUBLICATION_GATE` + OP §4 | generalizacija na svih 12 slojeva |
| NO DIRECT EDIT | ✅ implicitno | Mutation IR route (MANUAL/HOLD) + 001I §7 + „General executes" | eksplicitno imenovan zakon |
| LIVE STATUS view | ✅ | `dashboard.html` (žive snapshotove + Netlify fn po platformi) | designacija + staleness flag |
| Ownership | ⚠ djelom. | `runtime_spec_v2_5` (mandati Kabineta) | per-LAYER matrica (izvedena) |
| Dependency propagation | ❌ | — | **stvarno novo (§5)** |
| 6 principa / v3.0 okvir | ❌ (kao jedan okvir) | rasuto | **sinteza (§1)** |

→ Genuinely novo = **§5 Dependency propagation** + **per-layer Ownership (§2)** + **generalizirani lifecycle (§3)**. Ostalo referira postojeće.

---

## §1. TEMELJNI PRINCIPI
**NAČELO 0 (spine): „Sustav evoluira dokazom, ne idejom."** *(General/GPT, 2026-07-12.)* Iz njega izviru svi ostali — False Gap Defence, Phase 0, Acceptance Criteria, Operational Trial, 30-day validation, Changelog, „v3.1 tek nakon Field Loga". Sve je ista filozofija.

Šest izvedenih principa (svaki s postojećom implementacijom):
1. **Repository-first** — repo je primarni operativni izvor. *(identity-canon: „Repo wins"; 4. SYSTEM MAP: Data Layer=GitHub kanon.)*
2. **Phase 0 obvezan** — nijedan veći zadatak bez orijentacije. *(`SYSTEM_INDEX §3` + `PROPOSAL_Phase0`; nadograđuje 001I + OP §1.)*
3. **False Gap Defence** — nijedan prijedlog prije provjere postojećeg. *(`SYSTEM_INDEX §4`.)*
4. **Layer ownership** — svaki sloj ima vlasnika i pravila izmjene. *(§2 ovdje, izvedeno iz `runtime_spec_v2_5`.)*
5. **Dependency awareness** — svaka promjena zna koje slojeve zahvaća. *(§5 ovdje.)*
6. **Canonical over derived** — izvedeni dokumenti ne nadjačavaju kanonske registre. *(identity-canon; MUTATION_IR provenance; „edit source + regen, nikad derived".)*

---

## §2. OWNERSHIP MATRIX (PROPOSED — izvedeno iz runtime_spec_v2_5, čeka ratifikaciju)
| Layer | Owner | Secondary | General approval |
|---|---|---|:--:|
| L0 Governance | **General** | Claude | DA |
| L1 Repository | **General** | Claude | DA |
| L2 Registry | **General** | Claude (executor) | DA |
| L3 Web | **Claude** | GPT | DA (publish) |
| L4 YouTube | **Claude** | vidIQ | DA (publish) |
| L5 Authority | **Claude** | Gemini | DA (external write) |
| L6 Knowledge Graph | **Claude** | Gemini | DA (WD write) |
| L7 Signal | **Grok** | vidIQ | NE (read-only) |
| L8 Operations | **GPT** | Claude | DA (WS change) |
| L9 Research | **Gemini** | Perplexity | NE (unvalidated) |
| L10 Automation/MCP | **GPT** | Copilot (kod) | DA (deploy) |
| L11 Memory | **Claude** | — | NE |

Pravilo: „Tko smije dirati ovaj sloj?" = Owner predlaže/izvršava dopušteno; Secondary asistira; ako „General approval = DA" → nijedna mutacija ne postaje trajna bez General GO.

> **Korekcija (GPT, 2026-07-12) — „Owner" ovdje = EXECUTION OWNER. DOMAIN OWNER svih DA-slojeva = General.** Web/YouTube/Registry su Generalovi; Claude ih ODRŽAVA/izvršava, ne posjeduje. Split kolone (Domain vs Execution) = v3.1 kandidat (`OS_v3_CHANGELOG.md`).

---

## §3. MUTATION LIFECYCLE (generalizirano na sve slojeve)
```
READ → ANALYZE → PROPOSE → RATIFY → IMPLEMENT → VERIFY → PUBLISH
```
Tko izvršava koji korak (po sloju, izvedeno iz postojećih gate-ova):

| Korak | Tko | Postojeća implementacija |
|---|---|---|
| READ / ANALYZE | Owner (agent) | Phase 0 (SYSTEM_INDEX) |
| PROPOSE | Owner | proposal doc / Mutation IR (route odlučuje compiler) |
| RATIFY | **General** (za DA-slojeve) | decision_log / Notion ratifikacija |
| IMPLEMENT | Owner/executor; **General za MANUAL/irreverzibilno** | `executor/execute.js`; Mutation IR route AUTO/REVIEW/MANUAL |
| VERIFY | Owner + vidIQ | `executor/verify.js`; Convergence Object |
| PUBLISH | Owner; General GO za javno | `PUBLICATION_GATE` (Gate 1–5) |

Konkretne implementacije lifecyclea koje VEĆ postoje:
- **Registry/Wikidata mutacije** → `MUTATION_IR_SPEC_v1.0` (route AUTO/REVIEW/MANUAL/HOLD/BLOCKED; rollback batch).
- **YouTube/objava** → `PUBLICATION_GATE` (Gate 1 Registry → 2 Entity → 3 Produkcija → 4 YT metadata → 5 QA).
- **Canon/identity/runtime** → proposal → review → ratifikacija (nema automatike).

---

## §4. ZAKON: NO DIRECT EDIT
**Nijedan agent ne mijenja `registry` · `runtime` · `canon` · `identity` bez:**
```
proposal → review → ratification
```
- Registry/WD: mutacija ide kroz Mutation IR + Gate (nikad ručni direktni edit).
- Runtime/Canon/Identity (runtime_spec, identity-canon, CANON_v1.0): samo General ratificira; agent predlaže (001I §7 — no self-amend).
- Derived (web copy, JSON-LD, YT opisi): **uređuje se izvor + regen**, nikad se ne „krpa" derived mimo izvora (Princip 6).

Ovo je većinom već praksa (Mutation IR, gate-ovi, „General executes MANUAL") — v3.0 je samo imenuje kao zakon.

---

## §5. DEPENDENCY PROPAGATION MAP (stvarno novo)
Ako promijeniš izvor, ovo se mora regenerirati/provjeriti:

```
works_registry.json  (L2 izvor istine)
   ↓ regen: _build/make_canonical_metrics.py
CANONICAL_STATE.md + data/canonical_metrics.json
   ↓
Web (/pjesme/, diskografija.html, data/schema_org_verified.json)
   ↓
Google KG (Wikidata/schema.org)  ←→  MusicBrainz (via Mutation IR)
   ↓
YouTube (About + video opisi — canonical footer)
   ↓
Discovery (search / KP cross-link)
```

Ostali lanci:
- **identity-canon.md** → web copy (bio/about), JSON-LD `about`, naming standard, E-001 trailer, YT opis. *(Canon mijenja narativ svugdje — zato „mijenja se rijetko".)*
- **runtime_spec (uloge)** → Ownership Matrix (§2) → tko izvršava mutacije.
- **MB/WD edit (Mutation IR)** → `wikidata_state.json` / `mb_snapshot.json` → `dashboard.html` + CANONICAL_STATE „External presence" + KG.

**Zakon propagacije:** promjena L2 (Registry) = obavezan regen svih nizvodnih (CANONICAL_STATE → Web → KG → YouTube). Nikad ne mijenjaj nizvodni derived bez regeneracije iz izvora.

---

## §6. LIVE STATUS (postoji — designacija, ne novi build)
**SYSTEM_INDEX = što postoji (statično). LIVE STATUS = u kakvom je stanju (živo).**
- Kanonski LIVE STATUS view = **`dashboard.html`** (repo root, noindex) — povlači žive snapshotove (`/data/mb_snapshot.json`, `wikidata_snapshot.json`) + Netlify funkcije (spotify/youtube/discogs/wikipedia/system/facebook) s `fetched_at`.
- Dopunski izvori: `data/system_status.json`, `data/canonical_metrics.json`, Notion „Platform Completion Tracker" (Presence/Status/What is done/What is missing).
- **⚠ Staleness (mora se regenerirati):** `system_status.json` (last_run 2026-05-02) · `CANONICAL_STATE.md` (2026-06-04). Live view je star ~5–10 tjedana.

---

## §7. ZA GENERALA — ratifikacija
1. **Ratificiraj v3.0 principe (§1)** kao operativni okvir.
2. **Ratificiraj Ownership Matrix (§2)** — ili korigiraj vlasnike.
3. **Ratificiraj NO DIRECT EDIT (§4)** + Mutation Lifecycle (§3) kao formalizaciju postojećih gate-ova.
4. **Dependency propagation (§5)** — potvrdi lance ili dopuni.
5. **Refresh staleness (§6)** — regen `CANONICAL_STATE` + `system_status` (zaseban zadatak, uz GO).
6. Zakači pointer na `SYSTEM_INDEX` + ovaj okvir u `CLAUDE.md` (auto-loaded) da Phase 0 bude obvezan.

Ministar autoriteta preporučuje 1–4 (formalizacija postojećeg, nizak rizik). 5–6 su izvršni koraci uz tvoj GO.

---
*iZLET OS v3.0 · PROPOSED · 2026-07-12 · sinteza postojećeg + dependency/ownership/lifecycle · ne mijenja protokole, ne stvara module · „canonical over derived".*
