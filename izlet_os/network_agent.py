import requests

class NetworkAgent:
    def __init__(self):
        # Svi tvoji verificirani podaci na jednom mjestu
        self.targets = {
            "Authority": {
                "iZLET": "https://www.wikidata.org/wiki/Q139595518",
                "Petar Kumerle": "https://www.wikidata.org/wiki/Q139595619",
                "Toni Kumerle": "https://www.wikidata.org/wiki/Q139595627",
                "Braća Kumerle": "https://www.wikidata.org/wiki/Q139595609",
                "Braća Kumerle Music": "https://www.wikidata.org/wiki/Q139595640",
                "Sjever uz odsutne": "https://www.wikidata.org/wiki/Q139595589"
            },
            "Streaming": {
                "Spotify": "https://open.spotify.com/artist/06i5vP8K0l9E1mZ27I6B2Y",
                "YouTube": "https://www.youtube.com/@bracakumerle"
            }
        }

    def check_node(self, category, name):
        url = self.targets.get(category, {}).get(name)
        if not url: return "❌ (Missing URL)"
        try:
            r = requests.get(url, timeout=5)
            # Ako vrati 200, entitet je "živ" na webu
            return "✅" if r.status_code == 200 else f"❌ ({r.status_code})"
        except:
            return "⚠️ (Connection Error)"

if __name__ == "__main__":
    na = NetworkAgent()
    print("--- BRZA PROVJERA IDENTITETA ---")
    for name in na.targets["Authority"]:
        print(f"{name}: {na.check_node('Authority', name)}")