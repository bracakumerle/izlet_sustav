import json
from datetime import datetime

def generate_status_report():
    print("--- Generiranje iZLET Status Izvještaja ---")
    
    try:
        with open("master_registry.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except:
        print("Greška: Registar nije pronađen.")
        return

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    filename = f"logs/izvjestaj_{timestamp}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"IZVJEŠTAJ O DIGITALNOM AUTORITETU - iZLET\n")
        f.write(f"Datum: {datetime.now().strftime('%d.%m.%2026. %H:%M')}\n")
        f.write("-" * 40 + "\n\n")

        for track in data.get("tracks", []):
            f.write(f"PJESMA: {track['title']}\n")
            f.write(f"  - Status: {track.get('status', 'unknown')}\n")
            f.write(f"  - YouTube ID: {track.get('youtube_id', 'NEDOSTAJE')}\n\n")

    print(f"✅ Izvještaj spremljen u: {filename}")

if __name__ == "__main__":
    generate_status_report()