# AI Repository Benchmark — izlet_sustav
**Datum:** 2026-06-04  
**Repozitorij:** bracakumerle/izlet_sustav  
**Svrha:** Verifikacija capabilityja Perplexity GitHub MCP connektora kao independent execution domene u Kabinet arhitekturi.

---

## Rezultati testova

| Test | Capability | Rezultat | Artefakt |
|------|-----------|---------|----------|
| A | `repository_read` | ✅ PASS | — |
| B | `create_file` (main) | ✅ PASS | — |
| B | `readback_verification` | ✅ PASS | — |
| C | `stale_sha_protection` | ✅ PASS | greška na namjerno krivom SHA |
| D | `branch_create` | ✅ PASS | `benchmark/test-d-workflow` |
| D | `create_file_on_branch` | ✅ PASS | `benchmark/test_d_result.md` |
| D | `pull_request_create` | ✅ PASS | PR #1 |
| E | `update_file` (correct SHA) | ✅ PASS | GitHub Write Test #002 |
| — | `delete_file` | ⬜ UNVERIFIED | nije testirano |
| — | `merge_execution` | ⬜ UNVERIFIED | nije testirano |
| — | `conflict_resolution` | ⬜ UNVERIFIED | nije testirano |

**Neovisna verifikacija PR #1:** GPT je potvrdio da PR postoji, state=open, mergeable=true, commit `6b080e8ae4a3e556fef1f6ab75e58fa4f2c01f66`.

---

## Capability model (finalni)

```yaml
PERPLEXITY_GITHUB_CONNECTOR:

  repository_observation:
    status: VERIFIED

  repository_mutation:
    create_file: VERIFIED
    update_file: VERIFIED
    delete_file: UNVERIFIED

  consistency_controls:
    stale_sha_protection: VERIFIED

  workflow_capabilities:
    branch_create: VERIFIED
    create_file_on_branch: VERIFIED
    pull_request_create: VERIFIED
    review_cycle: UNVERIFIED
    merge_execution: UNVERIFIED

  trust_level:
    repository_operator: HIGH
    workflow_operator: PROVISIONAL
```

### Precizna terminološka distinkcija

Ono što je verificirano **nije** `autonomous_git_workflow`.  
Ono što je verificirano jest:

> **branch_automation + review_artifact_submission**

Pattern:
```
read → mutate → isolate_on_branch → submit_for_review
```

Merge odluka ostaje na ljudskom operatoru.

---

## Arhitekturna implikacija za Kabinet

Ključna novost nije GitHub write capability sam po sebi.  
Ključna novost je uspostava **independent execution domene**:

```
Domain A — Claude Code:
  lokalni filesystem + lokalni git
  verified: lokalni commit, push

Domain B — Perplexity:
  GitHub REST API (remote)
  verified: read, create, branch, PR, stale_sha_protection, update_file

Domain C — GPT:
  audit + cross-verification
  verified: nezavisno čitanje stanja repozitorija
```

### Triangulacija

```
Claude Code: izvrši promjenu lokalno + push
     ↓
Perplexity: provjeri SHA na originu
     ↓
GPT: usporedi očekivano i stvarno stanje
     ↓
→ nikad ne ovisiš o self-reporting jednog agenta
```

Ovo je kvalitativni pomak od modela **povjerenja u izvještaj** prema modelu **verifikacije stanja**.

---

## Status benchmark artefakta

```yaml
PR_1:
  url: https://github.com/bracakumerle/izlet_sustav/pull/1
  state: open
  benchmark_artifact: KEEP
  action_after_documentation: close (ne merge, ne delete branch odmah)
  razlog: commit nema poslovnu vrijednost za main
```

---

## Perplexity Notion Write — naknadno dodan

| Test | Result | Page ID |
|---|---|---|
| TEST-NOTION-WRITE-001 | ✅ VERIFIED | 37528908-2d7e-81c8-9081-ecf61799dab2 |
| TEST-NOTION-WRITE-002 | ✅ VERIFIED | 37528908-2d7e-8177-b1e0-e779f7d2fb5f |

**Verification method:** create → return page_id → fetch(page_id) → content match confirmed  
**Timestamp:** 2026-06-04T18:40 CEST  
**GitHub Write #002 SHA:** [this commit]

---

## Sljedeći koraci (opcionalno)

1. ~~`update_file(correct_SHA)` — zatvoriti positive path test~~ ✅ DONE (GitHub Write #002)
2. Ažurirati Notion: Kabinet arhitektura → dodati execution domain model
3. Zatvoriti PR #1 nakon potvrde da je ovaj dokument na mainu
