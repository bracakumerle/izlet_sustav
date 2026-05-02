import requests

class DiscogsAgent:
    def __init__(self):
        self.base_url = "https://api.discogs.com/database/search"
        # Koristimo privremeni user-agent
        self.headers = {"User-Agent": "iZLET_OS_Bot/1.0"}

    def check_artist(self, artist_name):
        """Provjerava postoji li iZLET na Discogsu"""
        params = {"q": artist_name, "type": "artist"}
        try:
            r = requests.get(self.base_url, params=params, headers=self.headers)
            data = r.json()
            return len(data.get("results", [])) > 0
        except:
            return False

if __name__ == "__main__":
    ds = DiscogsAgent()
    print(f"Discogs Senzor aktivan. Status: {ds.check_artist('iZLET')}")