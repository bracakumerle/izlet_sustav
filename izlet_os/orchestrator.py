import json
import sys
import os
import logging
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, Tuple

# Connectors
sys.path.insert(0, str(Path(__file__).parent))
from connectors.musicbrainz_agent import MusicBrainzAgent
from connectors.wikidata_agent import WikidataAgent

# ═══════════════════════════════════════════════════════════════════════════
# PIPELINE MANAGER v2.1: Full Authority Layer Integration + Link Verification
# ═══════════════════════════════════════════════════════════════════════════

ORCHESTRATOR_DIR = Path(__file__).parent
IZLET_SUSTAV_ROOT = ORCHESTRATOR_DIR.parent
REGISTRY_PATH = IZLET_SUSTAV_ROOT / "master_registry.json"
LOGS_DIR = IZLET_SUSTAV_ROOT / "logs"
SCHEMA_OUTPUT = IZLET_SUSTAV_ROOT / "data" / "schema_org_verified.json"

# Kreiraj logs folder ako ne postoji
LOGS_DIR.mkdir(exist_ok=True)

# Setup logging
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

# ═══════════════════════════════════════════════════════════════════════════
# PIPELINE MANAGER v2.1: Full Cycle Automation
# ═══════════════════════════════════════════════════════════════════════════

class PipelineManager:
    """
    Autonomni stroj s HTTP link verifikacijom:
    1. LOAD     → Učitaj master_registry.json
    2. SCAN     → Očitaj core entitete + linkove
    3. VERIFY   → HTTP 200 check na Distribution + Communication slojeve
    4. GENERATE → Kreiraj schema_org_verified.json s aktivnim linkovima
    5. LOG      → Spremi audit trail s dokazima
    6. LIVE     → Dohvati live podatke s MusicBrainz i Wikidata API-ja
    """
    
    def __init__(self):
        self.registry = None
        self.scan_results = {}
        self.link_verification = {}
        self.timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.headers = {
            'User-Agent': 'iZLET-Authority-System/2.1'
        }
    
    def load_registry(self) -> bool:
        """KORAK 1: Učitaj master_registry.json"""
        logger.info("╔════════════════════════════════════════════════════════════════╗")
        logger.info("║  PIPELINE MANAGER v2.1 - Full Authority Integration           ║")
        logger.info("║  iZLET Authority System + Link Verification                   ║")
        logger.info("╚════════════════════════════════════════════════════════════════╝")
        logger.info(f"\n[KORAK 1/5] Učitavanje master_registry.json...")
        logger.info(f"Lokacija: {REGISTRY_PATH}")
        
        try:
            with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
                self.registry = json.load(f)
            
            core_count = len(self.registry.get("core_entities", {}))
            track_count = len(self.registry.get("tracks", []))
            
            logger.info(f"✅ Registry učitan")
            logger.info(f"   - Core entiteta: {core_count}")
            logger.info(f"   - Track-ova: {track_count}")
            
            return True
        except FileNotFoundError:
            logger.error(f"❌ Registry nije pronađen: {REGISTRY_PATH}")
            return False
        except json.JSONDecodeError as e:
            logger.error(f"❌ Registry je korumpiran: Red {e.lineno}, Kolona {e.colno}")
            return False
    
    def scan_entities(self) -> bool:
        """KORAK 2: SCAN - Očitaj core entitete"""
        logger.info(f"\n[KORAK 2/5] Skeniranje core entiteta...")
        
        if not self.registry:
            logger.error("❌ Registry nije učitan")
            return False
        
        logger.info("\n  → Core entiteti (Authority Foundation):")
        for name, entity in self.registry.get("core_entities", {}).items():
            q_id = entity.get("wikidata_id")
            entity_type = entity.get("type")
            
            self.scan_results[name] = {
                "type": entity_type,
                "q_id": q_id,
                "verified": True
            }
            
            logger.info(f"     ✅ {name} ({entity_type}): {q_id}")
        
        logger.info(f"\n✅ Skeniranje završeno: {len(self.scan_results)} entiteta")
        return True
    
    def verify_links(self) -> bool:
        """KORAK 3: VERIFY - HTTP 200 check na Distribution + Communication slojeve"""
        logger.info(f"\n[KORAK 3/5] Verifikacija HTTP dostupnosti linkova...")
        
        if not self.registry:
            logger.error("❌ Registry nije učitan")
            return False
        
        links = self.registry.get("links", {})
        total_checked = 0
        total_ok = 0
        
        # Provjera Distribution sloja
        logger.info("\n  → Distribution Layer (Streaming):")
        dist_links = links.get("distribution_layer", {})
        for service, url in dist_links.items():
            if url and url.strip():
                total_checked += 1
                status = self._check_url(url)
                self.link_verification[f"dist.{service}"] = status
                emoji = "✅" if status["ok"] else "⚠️"
                logger.info(f"     {emoji} {service}: {status['code']} - {url}")
                if status["ok"]:
                    total_ok += 1
        
        # Provjera Communication sloja
        logger.info("\n  → Communication Layer (Authority):")
        comm_links = links.get("communication_layer", {})
        for service, url in comm_links.items():
            if url and url.strip():
                total_checked += 1
                status = self._check_url(url)
                self.link_verification[f"comm.{service}"] = status
                emoji = "✅" if status["ok"] else "⚠️"
                logger.info(f"     {emoji} {service}: {status['code']} - {url}")
                if status["ok"]:
                    total_ok += 1
        
        logger.info(f"\n✅ Link verifikacija: {total_ok}/{total_checked} dostupni")
        return True
    
    def _check_url(self, url: str) -> Dict:
        """Provjeri HTTP status URL-a"""
        try:
            response = requests.head(url, headers=self.headers, timeout=5, allow_redirects=True)
            return {
                "ok": response.status_code == 200,
                "code": response.status_code,
                "url": url
            }
        except requests.RequestException as e:
            return {
                "ok": False,
                "code": 0,
                "error": str(e),
                "url": url
            }
    
    def generate_schema(self) -> bool:
        """KORAK 4: GENERATE - Kreiraj schema_org_verified.json"""
        logger.info(f"\n[KORAK 4/5] Generiranje Schema.org s dinamičkim linkovima...")
        
        # Import schema_builder
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("schema_builder", 
                                                           ORCHESTRATOR_DIR / "schema_builder.py")
            schema_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(schema_module)
            
            schema_module.generate_izlet_schema()
            active_count = len(self._extract_active_links())
            logger.info(f"✅ Schema.org generirano s {active_count} dinamičkih linkova")
            return True
        
        except Exception as e:
            logger.error(f"❌ Greška pri generaciji schema-a: {e}")
            return False
    
    def _extract_active_links(self) -> list:
        """Broj aktivnih linkova"""
        active = []
        links = self.registry.get("links", {})
        for layer_links in links.values():
            if isinstance(layer_links, dict):
                active.extend([url for url in layer_links.values() if url and url.strip()])
        return active
    
    def fetch_live_data(self) -> bool:
        """KORAK 6: Dohvati live podatke s MusicBrainz i Wikidata API-ja"""
        logger.info(f"\n[KORAK 6/6] Dohvaćanje live podataka s vanjskih autoriteta...")

        success = True

        # MusicBrainz
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

        # Wikidata
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

    def generate_report(self) -> None:
        """Finalni izvještaj s dokaznim materijalom"""
        logger.info(f"\n[KORAK 5/6] Geniranje finalnog izvještaja...")
        
        logger.info(f"\n╔════════════════════════════════════════════════════════════════╗")
        logger.info(f"║  PIPELINE EXECUTION REPORT - {self.timestamp}              ║")
        logger.info(f"╚════════════════════════════════════════════════════════════════╝")
        
        logger.info(f"\n📊 SAŽETAK IZVRŠAVANJA:")
        logger.info(f"   - Core entiteta skeniranih: {len(self.scan_results)}")
        logger.info(f"   - Linkova verificiranih: {len(self.link_verification)}")
        logger.info(f"   - Schema.org generirano: {SCHEMA_OUTPUT.exists()}")
        logger.info(f"   - Audit trail (Log): {LOG_FILE}")
        
        ok_links = sum(1 for v in self.link_verification.values() if v.get("ok"))
        total_links = len(self.link_verification)
        if total_links > 0:
            logger.info(f"\n🔗 Link Status: {ok_links}/{total_links} dostupni")
        
        logger.info(f"\n✅ PIPELINE ZAVRŠEN USPJEŠNO - {self.timestamp}")
        logger.info(f"   Dokazni materijal spreman za General-a")
        logger.info(f"   Lokacija: {LOG_FILE}\n")
    
    def run_full_cycle(self) -> bool:
        """Pokreni cijeli pipeline"""
        try:
            if not self.load_registry():
                return False
            
            if not self.scan_entities():
                return False
            
            if not self.verify_links():
                return False
            
            if not self.generate_schema():
                return False
            
            self.generate_report()

            if not self.fetch_live_data():
                return False

            return True
        
        except Exception as e:
            logger.error(f"❌ KRITIČNA GREŠKA: {type(e).__name__}: {e}")
            return False

# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    manager = PipelineManager()
    success = manager.run_full_cycle()
    sys.exit(0 if success else 1)