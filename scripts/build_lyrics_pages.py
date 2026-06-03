"""
build_lyrics_pages.py
Generates 5 lyrics pages from lyrics-template.html
"""
import io, sys, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = os.path.join(ROOT, "lyrics-template.html")

SONGS = [
    {
        "slug": "moj-dinamo",
        "title": "Moj Dinamo",
        "year": "2024",
        "isrc": "QT6F32530626",
        "mb_rec": "08a4c06f-f83f-4d88-ac3a-b3ac6160d7d6",
        "mb_work": "d89204a8-e68d-42e6-b719-8be781132800",
        "spotify": "5gfjKvC0yxasJd0hafXTwx",
        "youtube": "xp-f5vjciCk",
        "genius": "https://genius.com/Izlet-moj-dinamo-lyrics",
        "label": "Braća Kumerle Music",
        "about": ["Dinamo Zagreb", "navijačka kultura", "lojalnost", "identitet"],
        "desc": "Navijačka himna posvećena GNK Dinamo Zagreb i kulturi Bad Blue Boysa.",
    },
    {
        "slug": "krijesovi-lazi",
        "title": "Krijesovi laži",
        "year": "2025",
        "isrc": "QT6F32539173",
        "mb_rec": "94dd1837-6977-4937-a02e-b8258b932b2a",
        "mb_work": None,
        "spotify": None,
        "youtube": "gk5AHkbyLVU",
        "genius": "https://genius.com/Izlet-krijesovi-lazi-lyrics",
        "label": "Braća Kumerle Music",
        "about": ["domovinska povijest", "antikomunizam", "memorija", "krijesovi"],
        "desc": "Pjesma o povijesnoj memoriji i sukobljenim narativima domovinske prošlosti.",
    },
    {
        "slug": "frane-tente",
        "title": "Frane Tente",
        "year": "2020",
        "isrc": "QT6F32536381",
        "mb_rec": "0999a678-4586-48c5-a1f1-598ffaa69977",
        "mb_work": "48601b97-cff8-4346-af89-987de31bcfa1",
        "spotify": "1Vg4lIa8nKwoJGgsJt0X99",
        "youtube": "sAWssQ-lNtk",
        "genius": "https://genius.com/Izlet-frane-tente-lyrics",
        "label": "Braća Kumerle Music",
        "about": ["Frane Tente", "domovinski rat", "sjećanje", "žrtva"],
        "desc": "Posveta Frani Tenti, mladom domoljubu koji je umro u komunističkom zatvoru.",
    },
    {
        "slug": "sjever-uz-odsutne",
        "title": "Sjever uz odsutne",
        "year": "2023",
        "isrc": "QT6EX2529331",
        "mb_rec": "87cf4afb-efbf-4627-a8b1-170725fa7807",
        "mb_work": "7d41efc4-76e3-4b5b-80ed-ffddddbb0cd0",
        "spotify": "546tgpxlqS3GsLPEo13BP2",
        "youtube": "o02z8L8gOn0",
        "genius": "https://genius.com/Izlet-sjever-uz-odsutne-lyrics",
        "label": "Braća Kumerle Music",
        "about": ["solidarnost", "Bad Blue Boys", "zatvoreni navijači", "sjever"],
        "desc": "Pjesma podrške Bad Blue Boysima zatočenima u grčkim zatvorima (2023).",
    },
    {
        "slug": "znakovlje-hrvata",
        "title": "Znakovlje Hrvata",
        "year": "2021",
        "isrc": None,
        "mb_rec": None,
        "mb_work": None,
        "spotify": None,
        "youtube": "AltC9RZWsd4",
        "genius": None,
        "label": "Braća Kumerle Music",
        "about": ["hrvatska simbolika", "baština", "kulturni identitet", "domoljublje"],
        "desc": "Himna hrvatskog kulturnog identiteta i narodnih simbola.",
    },
]


def build_about_json(items):
    return ",\n        ".join(f'"{a}"' for a in items)


def build_about_li(items):
    return "\n        ".join(f"<li>{a}</li>" for a in items)


with open(TEMPLATE, encoding="utf-8") as f:
    base = f.read()

for s in SONGS:
    slug    = s["slug"]
    title   = s["title"]
    year    = s["year"]
    isrc    = s["isrc"] or "NULL"
    mb_rec  = s["mb_rec"]
    mb_work = s["mb_work"]
    spotify = s["spotify"]
    youtube = s["youtube"]
    genius  = s["genius"]
    label   = s["label"]
    about   = s["about"]
    desc    = s["desc"]

    html = base

    # --- slug & title substitutions ---
    html = html.replace("moj-dinamo", slug)
    html = html.replace("Moj Dinamo", title)

    # --- year ---
    html = html.replace('datetime="2024">2024<', f'datetime="{year}">{year}<')
    html = html.replace('"datePublished": "2024"', f'"datePublished": "{year}"')

    # --- description ---
    html = html.replace(
        "Kanonski tekst pjesme Moj Dinamo — iZLET (Braća Kumerle). Autorski zapis, teme i kontekst.",
        f"Kanonski tekst pjesme {title} — iZLET (Braća Kumerle). {desc}"
    )

    # --- ISRC ---
    html = html.replace("QT6F32530626", isrc)

    # --- about array in JSON-LD ---
    html = html.replace(
        '"Dinamo Zagreb",\n        "navijačka kultura",\n        "lojalnost",\n        "identitet"',
        build_about_json(about)
    )

    # --- about <li> in HTML ---
    html = html.replace(
        "<li>Dinamo Zagreb</li>\n        <li>navijačka kultura</li>\n        <li>lojalnost</li>\n        <li>identitet</li>",
        build_about_li(about)
    )

    # --- Spotify ---
    sp_link = f'<a href="https://open.spotify.com/track/{spotify}">Spotify →</a>' if spotify else "(nije dostupno na Spotifyu)"
    html = html.replace('<a href="https://open.spotify.com/track/">→</a>', sp_link)

    # --- MusicBrainz recording link ---
    mb_rec_html = (
        f'<li>MusicBrainz recording: <a href="https://musicbrainz.org/recording/{mb_rec}">{mb_rec}</a></li>'
        if mb_rec else
        "<li>MusicBrainz recording: NULL</li>"
    )
    # Insert after ISRC line
    html = html.replace(
        f"<li>ISRC: {isrc}</li>",
        f"<li>ISRC: {isrc}</li>\n        {mb_rec_html}"
    )

    # --- Genius ---
    if genius:
        html = html.replace(
            "</ul>\n    </section>\n\n    <section>\n      <h2>Kronološki kontekst</h2>",
            f'<li>Genius: <a href="{genius}">Genius →</a></li>\n      </ul>\n    </section>\n\n    <section>\n      <h2>Kronološki kontekst</h2>'
        )

    out_dir = os.path.join(ROOT, "lyrics", slug)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "index.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    size = os.path.getsize(out_path)
    print(f"  OK: lyrics/{slug}/index.html  ({size} B)")

print(f"\nDone. 5 lyrics pages generated in lyrics/")
