import json
import sys
import os
import logging
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List

# Connectors
sys.path.insert(0, str(Path(__file__).parent))
from connectors.musicbrainz_agent import MusicBrainzAgent
from connectors.wikidata_agent import WikidataAgent

# ═══════════════════════════════════════════════════════════════════════════
# PIPELINE MANAGER v2.2: New Registry Schema + Full Link Verification
# ═══════════════════════════════════════════════════════════════════════════

ORCHESTRATOR_DIR  = Path(__file__).parent
IZLET_SUSTAV_ROOT = ORCHESTRATOR_DIR.parent
REGISTRY_PATH     = IZLET_SUSTAV_ROOT / "master_registry.json"
LOGS_DIR          = IZLET_SUSTAV_ROOT / "logs"
DATA_DIR          = IZLET_SUSTAV_ROOT / "data"
SCHEMA_OUTPUT     = DATA_DIR / "schema_org_verified.json"

LOGS_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

LOG_FILE = LOGS_DIR / f"scan_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(stream=open(sys.stdout.fileno(), mode='w', encoding='utf-8', closefd=False)),
    ]
)
logger = logging.getLogger(__name__)

# Schema.org type map
SCHEMA_TYPE = {
    "MusicGroup": "MusicGroup",
    "Person":     "Person",
    "MusicLabel": "Organization",
}


class PipelineManager:
    """
    Autonomni stroj s HTTP link verifikacijom:
    1. LOAD     → Učitaj master_registry.json (entities schema v2)
    2. SCAN     → Iteriraj entitete, čitaj ids + urls
    3. VERIFY   → HTTP HEAD check na svim URL-ovima svakog entiteta
    4. GENERATE → Kreiraj schema_org_verified.json s verified sameAs linkovima
    5. LOG      → Spremi audit trail s dokazima
    6. LIVE     → Dohvati live podatke s MusicBrainz i Wikidata API-ja
    """

    def __init__(self):
        self.registry          = None
        self.entities          = {}   # parsed entities dict
        self.scan_results      = {}   # entity_key → {name, type, ids, url_count}
        self.link_verification = {}   # "entity.service" → {ok, code, url}
        self.timestamp         = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.headers           = {'User-Agent': 'iZLET-Authority-System/2.2'}

    # ── KORAK 1 ────────────────────────────────────────────────────────────

    def load_registry(self) -> bool:
        """KORAK 1: Učitaj master_registry.json"""
        logger.info("╔════════════════════════════════════════════════════════════════╗")
        logger.info("║  PIPELINE MANAGER v2.2 - Full Authority Integration           ║")
        logger.info("║  iZLET Authority System + Link Verification                   ║")
        logger.info("╚════════════════════════════════════════════════════════════════╝")
        logger.info(f"\n[KORAK 1/6] Učitavanje master_registry.json...")
        logger.info(f"Lokacija: {REGISTRY_PATH}")

        try:
            with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
                self.registry = json.load(f)

            self.entities = self.registry.get("entities", {})
            entity_count  = len(self.entities)
            total_urls    = sum(
                len([v for v in e.get("urls", {}).values() if v])
                for e in self.entities.values()
            )

            logger.info(f"✅ Registry učitan")
            logger.info(f"   - Entiteta: {entity_count}")
            logger.info(f"   - URL-ova ukupno: {total_urls}")
            return True

        except FileNotFoundError:
            logger.error(f"❌ Registry nije pronađen: {REGISTRY_PATH}")
            return False
        except json.JSONDecodeError as e:
            logger.error(f"❌ Registry je korumpiran: Red {e.lineno}, Kolona {e.colno}")
            return False

    # ── KORAK 2 ────────────────────────────────────────────────────────────

    def scan_entities(self) -> bool:
        """KORAK 2: SCAN - Iteriraj entitete, čitaj ids + urls"""
        logger.info(f"\n[KORAK 2/6] Skeniranje entiteta iz registra...")

        if not self.entities:
            logger.error("❌ Nema entiteta u registru")
            return False

        logger.info(f"\n  → Entiteti ({len(self.entities)}):")
        for key, entity in self.entities.items():
            name      = entity.get("name", key)
            etype     = entity.get("type", "Unknown")
            ids       = entity.get("ids", {})
            urls      = entity.get("urls", {})
            url_count = len([v for v in urls.values() if v])

            self.scan_results[key] = {
                "name":      name,
                "type":      etype,
                "ids":       ids,
                "url_count": url_count,
            }

            id_summary = " | ".join(f"{k}: {v}" for k, v in ids.items())
            logger.info(f"     ✅ {name} ({etype})")
            logger.info(f"        IDs    → {id_summary}")
            logger.info(f"        URL-ovi→ {url_count} platformi")

        logger.info(f"\n✅ Skeniranje završeno: {len(self.scan_results)} entiteta")
        return True

    # ── KORAK 3 ────────────────────────────────────────────────────────────

    def verify_links(self) -> bool:
        """KORAK 3: VERIFY - HTTP HEAD check na svim URL-ovima"""
        logger.info(f"\n[KORAK 3/6] Verifikacija HTTP dostupnosti linkova...")

        if not self.entities:
            logger.error("❌ Nema entiteta za verifikaciju")
            return False

        total_checked = 0
        total_ok      = 0

        for key, entity in self.entities.items():
            name = entity.get("name", key)
            urls = entity.get("urls", {})
            active_urls = {svc: url for svc, url in urls.items() if url}

            if not active_urls:
                continue

            logger.info(f"\n  → {name}:")
            for service, url in active_urls.items():
                total_checked += 1
                status = self._check_url(url)
                vkey   = f"{key}.{service}"
                self.link_verification[vkey] = status
                emoji  = "✅" if status["ok"] else "⚠️ "
                logger.info(f"     {emoji} {service:<20} {status['code']}  {url}")
                if status["ok"]:
                    total_ok += 1

        logger.info(f"\n✅ Link verifikacija: {total_ok}/{total_checked} dostupni")
        return True

    def _check_url(self, url: str) -> Dict:
        try:
            r = requests.head(url, headers=self.headers, timeout=8, allow_redirects=True)
            return {"ok": r.status_code == 200, "code": r.status_code, "url": url}
        except requests.RequestException as e:
            return {"ok": False, "code": 0, "error": str(e), "url": url}

    # ── KORAK 4 ────────────────────────────────────────────────────────────

    def generate_schema(self) -> bool:
        """KORAK 4: GENERATE - Kreiraj schema_org_verified.json s verified sameAs"""
        logger.info(f"\n[KORAK 4/6] Generiranje Schema.org s verificiranim linkovima...")

        try:
            graph = []

            for key, entity in self.entities.items():
                name   = entity.get("name", key)
                etype  = entity.get("type", "Thing")
                ids    = entity.get("ids", {})
                urls   = entity.get("urls", {})

                # sameAs = only URLs that passed HTTP 200
                same_as: List[str] = []
                for service, url in urls.items():
                    if not url:
                        continue
                    vkey   = f"{key}.{service}"
                    status = self.link_verification.get(vkey, {})
                    if status.get("ok"):
                        same_as.append(url)

                node: Dict = {
                    "@type": SCHEMA_TYPE.get(etype, etype),
                    "name":  name,
                }

                if ids.get("wikidata"):
                    node["@id"] = f"https://www.wikidata.org/wiki/{ids['wikidata']}"

                if urls.get("website"):
                    node["url"] = urls["website"]

                if same_as:
                    node["sameAs"] = same_as

                # MusicGroup extras
                if etype == "MusicGroup":
                    if ids.get("musicbrainz"):
                        node["musicBrainzID"] = ids["musicbrainz"]
                    if ids.get("spotify"):
                        node["spotifyArtistID"] = ids["spotify"]

                graph.append(node)

            schema = {
                "@context":    "https://schema.org",
                "@graph":      graph,
                "_generated":  self.timestamp,
                "_verified_links": sum(1 for v in self.link_verification.values() if v.get("ok")),
                "_total_links":    len(self.link_verification),
            }

            with open(SCHEMA_OUTPUT, "w", encoding="utf-8") as f:
                json.dump(schema, f, ensure_ascii=False, indent=2)

            verified_count = schema["_verified_links"]
            logger.info(f"✅ Schema.org generirano: {len(graph)} entiteta, {verified_count} verified sameAs linkova")
            logger.info(f"   Saved → {SCHEMA_OUTPUT}")
            return True

        except Exception as e:
            logger.error(f"❌ Greška pri generaciji schema-a: {e}")
            return False

    def _extract_active_links(self) -> List[str]:
        active = []
        for entity in self.entities.values():
            active.extend(url for url in entity.get("urls", {}).values() if url)
        return active

    # ── KORAK 5 ────────────────────────────────────────────────────────────

    def generate_report(self) -> None:
        """KORAK 5: Finalni izvještaj"""
        logger.info(f"\n[KORAK 5/6] Generiranje finalnog izvještaja...")

        ok_links    = sum(1 for v in self.link_verification.values() if v.get("ok"))
        total_links = len(self.link_verification)

        logger.info(f"\n╔════════════════════════════════════════════════════════════════╗")
        logger.info(f"║  PIPELINE EXECUTION REPORT - {self.timestamp}              ║")
        logger.info(f"╚════════════════════════════════════════════════════════════════╝")
        logger.info(f"\n📊 SAŽETAK IZVRŠAVANJA:")
        logger.info(f"   - Entiteta skeniranih:   {len(self.scan_results)}")
        logger.info(f"   - Linkova verificiranih: {total_links}")
        logger.info(f"   - Linkova dostupnih:     {ok_links}/{total_links}")
        logger.info(f"   - Schema.org generirano: {SCHEMA_OUTPUT.exists()}")
        logger.info(f"   - Audit trail:           {LOG_FILE}")

        if total_links > 0:
            pct = round(ok_links / total_links * 100)
            logger.info(f"\n🔗 Link Health: {ok_links}/{total_links} ({pct}%)")

        logger.info(f"\n✅ PIPELINE ZAVRŠEN USPJEŠNO - {self.timestamp}")
        logger.info(f"   Lokacija: {LOG_FILE}\n")

    # ── KORAK 6 ────────────────────────────────────────────────────────────

    def fetch_live_data(self) -> bool:
        """KORAK 6: Dohvati live podatke s MusicBrainz i Wikidata API-ja"""
        logger.info(f"\n[KORAK 6/6] Dohvaćanje live podataka s vanjskih autoriteta...")

        success = True

        try:
            logger.info("  → MusicBrainz API...")
            mb = MusicBrainzAgent()
            snapshot, path = mb.snapshot()
            artist = snapshot["artist"]
            stats  = snapshot["stats"]
            logger.info(f"     ✅ Artist: {artist['name']} ({artist['type']})")
            logger.info(f"     ✅ Release groups: {stats['release_group_count']}")
            logger.info(f"     ✅ Recordings: {stats['recording_count']}")
            logger.info(f"     ✅ Saved → {path}")
        except Exception as e:
            logger.error(f"     ❌ MusicBrainz greška: {e}")
            success = False

        try:
            logger.info("  → Wikidata API...")
            wd = WikidataAgent()
            snapshot, snap_path, state_path, changed = wd.snapshot()
            for qid, ent in snapshot["entities"].items():
                label = ent["labels"].get("hr") or ent["labels"].get("en", qid)
                desc  = ent["descriptions"].get("hr") or ent["descriptions"].get("en", "")
                logger.info(f"     ✅ {qid}: {label} — {desc}")
            logger.info(f"     ✅ Snapshot → {snap_path}")
            logger.info(f"     ✅ State    → {state_path} (changed: {changed})")
        except Exception as e:
            logger.error(f"     ❌ Wikidata greška: {e}")
            success = False

        return success

    # ── FULL CYCLE ─────────────────────────────────────────────────────────

    def run_full_cycle(self) -> bool:
        try:
            if not self.load_registry():   return False
            if not self.scan_entities():   return False
            if not self.verify_links():    return False
            if not self.generate_schema(): return False
            self.generate_report()
            if not self.fetch_live_data(): return False
            return True
        except Exception as e:
            logger.error(f"❌ KRITIČNA GREŠKA: {type(e).__name__}: {e}")
            return False


# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    manager = PipelineManager()
    success = manager.run_full_cycle()
    sys.exit(0 if success else 1)
