import json
import os

def generate_izlet_schema():
    # Osiguravamo da mapa 'data' postoji
    if not os.path.exists('data'):
        os.makedirs('data')

    # Definiramo strukturu za Google Knowledge Graph
    schema = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "MusicGroup",
                "@id": "https://bracakumerle.com/#iZLET",
                "name": "iZLET",
                "genre": "Rock",
                "member": [
                    {"@type": "Person", "name": "Petar Kumerle"},
                    {"@type": "Person", "name": "Toni Kumerle"}
                ]
            },
            {
                "@type": "Person",
                "@id": "https://bracakumerle.com/#PetarKumerle",
                "name": "Petar Kumerle",
                "jobTitle": "Product Manager",
                "sameAs": [
                    "https://www.discogs.com/artist/Petar+Kumerle",
                    "https://www.linkedin.com/in/petarkumerle"
                ]
            },
            {
                "@type": "Organization",
                "name": "Braća Kumerle Music",
                "@id": "https://bracakumerle.com/#Label"
            }
        ]
    }
    
    # Zapisivanje u datoteku
    with open("data/schema_org.json", "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=4, ensure_ascii=False)
    
    print("✅ USPJEH: Schema.org kod je generiran u mapi 'data/schema_org.json'")

if __name__ == "__main__":
    generate_izlet_schema()