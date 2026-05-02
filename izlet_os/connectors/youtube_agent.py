import requests

class YouTubeAgent:
    def __init__(self):
        # Za sada koristimo public scrap/oembed metodu (bez API ključa za start)
        self.base_url = "https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v="

    def check_video(self, video_id):
        """Provjerava je li video iZLET-a aktivan na YouTubeu"""
        if not video_id:
            return False
        try:
            r = requests.get(f"{self.base_url}{video_id}")
            return r.status_code == 200
        except:
            return False

if __name__ == "__main__":
    yt = YouTubeAgent()
    # Test (primjer ID-a, zamijeni sa svojim ako želiš)
    test_id = "dQw4w9WgXcQ" 
    print(f"YouTube Senzor aktivan. Video status: {yt.check_video(test_id)}")