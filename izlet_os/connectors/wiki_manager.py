class WikiManager:
    def generate_draft(self, track_data):
        """Priprema kostur za Wikipediju ili medijsku objavu"""
        template = f"""
        == iZLET: {track_data['title']} ==
        Pjesma "{track_data['title']}" je dio projekta iZLET Braća Kumerle.
        Izvođač: iZLET
        Status: Službeno uvršteno u digitalni autoritet.
        """
        return template

if __name__ == "__main__":
    wm = WikiManager()
    print(wm.generate_draft({"title": "Krijesovi laži"}))