import requests

class MusicBrainzAgent:
    def __init__(self):
        self.user_agent = "iZLET_OS/1.0 (izletband@gmail.com)"
        self.base_url = "https://musicbrainz.org/ws/2/"

    def check_authority(self, title):
        """Pita svjetsku bazu: 'Znaš li ti za iZLET i pjesmu {title}?'"""
        params = {
            "query": f'recording:"{title}" AND artist:"iZLET"',
            "fmt": "json"
        }
        try:
            r = requests.get(self.base_url + "recording", params=params, headers={"User-Agent": self.user_agent})
            if r.status_code == 200:
                results = r.json().get("count", 0)
                return results > 0
            return False
        except:
            return False

if __name__ == "__main__":
    agent = MusicBrainzAgent()
    print(f"Senzor aktivan. Test za 'Krijesovi laži': {agent.check_authority('Krijesovi laži')}")