import requests

class WikidataAgent:
    def __init__(self):
        self.url = "https://www.wikidata.org/w/api.php"

    def check_entity(self, name):
        """Provjerava postoji li entitet iZLET ili određena pjesma na Wikidati"""
        params = {
            "action": "wbsearchentities",
            "search": name,
            "language": "hr",
            "format": "json"
        }
        try:
            r = requests.get(self.url, params=params)
            data = r.json()
            # Ako postoji rezultat koji u opisu ima 'glazbenik', 'band' ili 'pjesma'
            return len(data.get("search", [])) > 0
        except:
            return False

if __name__ == "__main__":
    wd = WikidataAgent()
    print(f"Wikidata Senzor aktivan. Status za 'iZLET': {wd.check_entity('iZLET')}")