# Works Authority Review v2

Reconstructed from:

- `reports/works_authority_candidates.md`
- `reports/works_authority_gaps.md`
- `reports/works_authority_graph.md`

## Candidate Ranking Audit

The ranking is internally consistent with its stated scoring model, but it is not fully aligned with authority-page priority.

The model strongly rewards identifier completeness: ISWC, ISRC, Spotify track, and other registry fields. This pushes many Dallas/Katarza-era works into the Top 10 even when their media-reference base is thin.

The graph report identifies stronger authority clusters for some lower-ranked works, especially `sjever_uz_odsutne`, `moj_dinamo`, and `strice_ivane_cover`. These have clearer media and YouTube relationships than several Top 10 works.

`zalo` is a justified high-priority candidate because it combines identifiers, media/broadcast references, YouTube coverage, and an existing authority page.

`cast` is also justified as a high-priority candidate because it has ISWC, ISRC, Spotify, media registry ART011, and four YouTube references.

`u_svijetu_bajki` has a reasonable Top 10 position because it has identifiers plus two media registry references.

`zasto_sutim`, `caroban_otok`, `kokosovo_mlijeko`, and `tko_si_ti` are plausible but weaker Top 10 items because each has only one media reference in the candidate table.

`pernastica`, `majcin_skut`, and `princeza_tea` look over-ranked as authority-page candidates because their media reference count is zero in the candidates report.

## Likely False Positives

- `pernastica`: High score driven by ISWC, ISRC, ZAMP work code, Spotify, and YouTube coverage, but no media references.
- `majcin_skut`: Identifier and YouTube coverage are present, but media references are absent in the candidate table.
- `princeza_tea`: Identifier and YouTube coverage are present, but media references are absent in the candidate table.
- Generic Dallas/Katarza album tracks with one YouTube match and no media references may be overvalued for authority-page sequencing.

## Likely False Negatives

- `sjever_uz_odsutne`: Ranked 31 despite a strong graph cluster: MusicBrainz recording/release, barcode, catalog number, ART015, ART016, and official YouTube video.
- `moj_dinamo`: Ranked 38 despite MusicBrainz recording, ART017, ART018, official YouTube video, and premiere clip.
- `strice_ivane_cover`: Ranked 30 and not canonical in `works_registry.json`, but graph shows event registry, five YouTube references, and Facebook ISWC reference.
- `frane_tente`: Ranked 37 despite multiple media references in the graph/media relationship section.
- `krijesovi_lazi`: Ranked 29 despite ISRC, MusicBrainz recording, and media reference evidence.
- `znakovlje_hrvata`: Ranked 36 despite multiple YouTube title matches and a MusicBrainz recording.

## Registry Gaps

- `strice_ivane_cover` is not a canonical `works_registry.json` work, even though it appears in event, YouTube, and Facebook-derived evidence.
- Several 2023-2026 works have MusicBrainz data but no ISRC or ISWC in `works_registry.json`.
- `sjever_uz_odsutne` lacks ISRC and ISWC despite having MusicBrainz release/recording, barcode, catalog number, media references, and official YouTube coverage.
- `moj_dinamo` lacks ISRC and ISWC despite MusicBrainz recording and media references.
- `frane_tente` has media registry coverage but is not surfaced as a strong candidate in the candidate ranking.
- Many Dallas/Katarza works have ISWC, ISRC, and Spotify track IDs but lack MusicBrainz work ID, MusicBrainz recording ID, Discogs master ID, and Wikidata QID.
- Work nodes often do not include media references even when `registry/media_registry.json` has matching subject entries.
- Dedicated authority assets are missing or not identified for all Top 10 gap-report works.
- Cross-links are sparse because most candidate work pages do not yet exist.

## Scoring-Model Weaknesses

- Identifier completeness is overweighted compared with media-source density.
- A Spotify track ID is treated as a strong external signal even when the work lacks media references.
- YouTube coverage count does not distinguish official video, album upload, live clip, short, or loose title match.
- Media references are counted, but source status and tier are not clearly weighted.
- Existing authority page status adds points, which can entrench already-created pages instead of identifying the next best candidate.
- The model does not sufficiently reward multi-source clusters: registry plus media plus YouTube plus event evidence.
- The model penalizes newer works with missing ISRC/ISWC even when they have stronger repository evidence elsewhere.
- It does not separate canonical works from performance/event nodes, which makes `strice_ivane_cover` difficult to place.
- It does not distinguish work-level identifiers from artist-level identifiers inherited from `master_registry.json`.

## Summary

The generated ranking is useful as an identifier-completeness audit, but it should not be treated as the final authority-page priority order.

The strongest evidence clusters in the generated reports are:

- `zalo`
- `cast`
- `sjever_uz_odsutne`
- `moj_dinamo`
- `strice_ivane_cover`

The clearest mismatch is that `sjever_uz_odsutne` and `moj_dinamo` appear as strong graph clusters but are ranked low because they lack ISRC/ISWC.
