# Works Authority Graph

Sources used: `works_registry.json`, `registry/media_registry.json`, `data/youtube_archive.json`, `registries/youtube_corpus_raw.csv`, `events_registry.json`, `master_registry.json`.

## Work ↔ Media Reference Relationships

| Work | Media references |
|---|---|
| Žalo | MTV Adria rotation 2013; HRT Radio Dubrovnik top lista |
| Čast | ART011, Likaclub.net.hr, "Pogledajte glazbeni spot grupe iZLET za pjesmu Čast" |
| U svijetu bajki | ART003 Mixeta.net; ART008 Likaclub.net.hr |
| Zašto šutim | ART004 Mixeta.net |
| Čaroban otok | ART005 Likaclub.net.hr |
| Tko si ti | ART006 Likaclub.net.hr |
| Kokosovo mlijeko | ART010 Likaclub.net.hr |
| Sjever uz odsutne | ART015 Portal Braniteljski forum; ART016 Narod.hr |
| Moj Dinamo | ART017 HOP.com.hr; ART018 Zagreb.info |
| Krijesovi laži | ART019 HOP.com.hr; work-node media URL |
| Striče Ivane | event registry node; mainstream incident notes in ART023-ART029 mention STRICE-IVANE-2025 signal but are not music-authority sources |

## Work ↔ YouTube Relationships

| Work | YouTube relationships found in repository |
|---|---|
| Čast | `K90ntS9oIEM` official video; `1gPfgO3daPk` album video; `V8Jw0Letyyo` live/related performance; `pwUEL73aQ4U` live/related performance |
| Sjever uz odsutne | `o02z8L8gOn0` official video |
| Moj Dinamo | `xp-f5vjciCk` official video; `Lr_3YjBUHrw` premiere clip; one short-form archive reference mentioning the song |
| Striče Ivane | `S04QjTS23KU`, `zOVPy32dfIg`, `3wsqpwuWEMM`, `l4g11KCitN0`, `NaScwMlnNQg` |
| Žalo | `HrpRU2tpg2I`; `hviyXdTsKLM`; additional title match in archive |
| Majčin skut | `3ZGoz2pm8ug`; `LryxvBJBUuU`; Facebook post reference |
| Znakovlje Hrvata | multiple live/archive title matches in YouTube archive |
| Frane Tente | multiple title matches in media and YouTube archive |

## Work ↔ Registry Relationships

| Work | Registry relationships |
|---|---|
| Žalo | ISWC, ISRC, Spotify track, existing `/pjesme/zalo.html`, iZLET master registry entity |
| Čast | ISWC, ISRC, Spotify track, media registry ART011 |
| Sjever uz odsutne | MusicBrainz recording, MusicBrainz release, artist ID, barcode `199953974831`, catalog number `BKMUSIC001`, media registry ART015/ART016 |
| Moj Dinamo | MusicBrainz recording, media registry ART017/ART018 |
| Krijesovi laži | ISRC, MusicBrainz recording, media registry ART019 |
| Striče Ivane | event registry `event_strice_ivane_performance_2025`; Facebook post references ISWC `T-900.869.775-4`; no canonical works registry entry |
| W_CMC_2009_001 / Ti Si Čudesna | Discogs release ID `12309194`, release URL, CMC Demo 2009 appearance |

## Strongest Authority Clusters

1. **Žalo cluster**: work identifiers plus broadcast/media references plus an existing authority page.
2. **Čast cluster**: ISWC, ISRC, Spotify, media registry article, and four YouTube references.
3. **Sjever uz odsutne cluster**: MusicBrainz release/recording, barcode/catalog number, two media articles, official YouTube video.
4. **Moj Dinamo cluster**: MusicBrainz recording, two media articles, official YouTube video and performance/premiere clips.
5. **Striče Ivane performance cluster**: event registry plus high-coverage YouTube archive nodes; canonical work registry entry is missing.

## Graph Gaps

- Several high-visibility 2023-2026 works have MusicBrainz data but no ISRC/ISWC in `works_registry.json`.
- Many Dallas/Katarza works have ISWC/ISRC/Spotify but no MusicBrainz/Wikidata work-level identifiers.
- Existing cross-links between generated work pages are sparse because most authority pages do not yet exist.
