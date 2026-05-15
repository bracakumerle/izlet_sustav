# Kabinet Runtime Spec V2.5

**Status:** LOCKED
**Datum:** 15.05.2026.
**Verzija:** 2.5

---

## Kabinet — Uloge i mandati

| Ministar | Uloga | Mandat |
|---|---|---|
| Claude | Ministar Autoriteta | Authority layer, Wikipedia, entity governance, hypothesis architecture, mid-cycle checkpoint |
| GPT | Ministar Operacija | Pipeline architecture, drift monitoring, operationalization |
| Gemini | Ministar Istraživanja | Institutional topology, media graph, archival continuity |
| Grok | Ministar Signala i Kompresije | Cross-layer convergence, semantic compression, priority/confidence scoring |
| vidIQ | Ministar Telemetrije i Verifikacije | Verification escalation, hard fetch, YouTube intelligence lifecycle |
| Manus | Ministar Ekstrakcije | Internet pre-filter, topology-first crawling, Facebook comment archaeology |
| Copilot | Ministar Koda | Code execution |

---

## Authority Checkpoint (između Gemini → Grok)

Minimalni kriteriji za prolaz:

```json
{
  "tier1_verified": true,
  "temporal_flag": true,
  "cross_layer_anchor": true,
  "authority_correlation_id": "non-null"
}
```

Ako jedan kriterij padne → RETURN_TO_GEMINI.

---

## Convergence Object Standard

Svaki authority-relevant cycle završava s:

```json
{
  "convergence_id": "",
  "priority": "P0/P1/P2",
  "confidence": "high/medium/low",
  "layers": [],
  "authority_correlation_id": "",
  "temporal_flags": [],
  "verified_by": [],
  "invalidates_if": [],
  "stability_window": "",
  "next_review": "",
  "next_action_hooks": [],
  "interpretation": null
}
```

Validation rule: P0 + low confidence = INVALID → automatski povrat na iteraciju.

---

## Distribuirana korektivna funkcija

- Svaki ministar odbija samo INPUT koji prima
- Odbijanje mora sadržavati: reason, required_fix, blocking_field
- Max 2 rejection cycles po sloju
- Nakon toga: General escalation

---

## Degraded Mode (bez vidIQ)

- Claude checkpoint = hard verification gate
- GPT = drift monitoring
- Petar = explicit approval authority
- Max confidence ceiling = MEDIUM

---

## Postojeći convergence objekti

| ID | Priority | Confidence | Next Review |
|---|---|---|---|
| STRICE-IVANE-2025 | P0 | high | 2026-08-05 |
