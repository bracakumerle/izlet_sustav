import os

# Definicija strukture operativnog sustava iZLET
folders = ["izlet_os", "logs", "data"]
files = {
    "izlet_os/orchestrator.py": "# Glavni mozak sustava",
    "izlet_os/.env": "OPENAI_API_KEY=\nGEMINI_API_KEY=\nANTHROPIC_API_KEY=",
    "master_registry.json": "{\n  \"project\": \"iZLET_Core\",\n  \"tracks\": []\n}",
    "requirements.txt": "python-dotenv\nrequests"
}

def build():
    print("--- Pokretanje izgradnje sustava iZLET ---")
    for f in folders:
        if not os.path.exists(f):
            os.makedirs(f)
            print(f"✔ Kreirana mapa: {f}")
    
    for path, content in files.items():
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"  ✔ Kreirana datoteka: {path}")
    print("\n[USPJEH]: Sustav je spreman za rad.")

if __name__ == "__main__":
    build()