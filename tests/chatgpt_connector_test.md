# Connector Benchmark — Test A2 + B

Agent: Perplexity (Claude Sonnet 4.6)
Run: 2026-06-04 14:43 CEST
Test: A2 — GitHub.create_file

## Status
- fetch_file (pre-create): 404 — file did not exist ✅
- create_file: ✅ PASS (blob SHA: baebe4d7c98d4930cb2f235aba8332aac0cfc73c)
- read-back A2: ✅ PASS (content match, SHA match)

## Test B — Update Integrity
- update_file run: 2026-06-04 14:45 CEST
- pre-update SHA: baebe4d7c98d4930cb2f235aba8332aac0cfc73c
- post-update SHA: PENDING read-back

## Purpose
Verifying optimistic locking: blob SHA must change after update.

## Next
Test C: stale SHA rejection (409 expected)
