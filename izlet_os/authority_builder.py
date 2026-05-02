import json

class AuthorityBuilder:
    def __init__(self, registry_path="master_registry.json"):
        with open(registry_path, "r", encoding="utf-8") as f:
            self.data = json.load(f)

    def generate_wikidata_brief(self):
        print("--- NACRT ZA WIKIDATA INJEKCIJU ---")
        for entity in self.data["entities"]:
            name = entity["name"]
            e_type = entity["type"]
            
            print(f"\n[ENTITET]: {name}")
            print(f"  Opis (HR): {'Glazbeni sastav' if e_type == 'Band' else 'Hrvatski glazbenik'}")
            print(f"  Poveznica: Potrebno kreirati novi Q-broj (Item)")
            
            # Automatizirano dodavanje referenci
            if name in ["Petar Kumerle", "Toni Kumerle"]:
                print(f"  Referenca: Koristiti postojeći Discogs profil kao izvor autoriteta.")
            else:
                print(f"  Referenca: Potreban vanjski medijski članak ili službena stranica.")

if __name__ == "__main__":
    ab = AuthorityBuilder()
    ab.generate_wikidata_brief()