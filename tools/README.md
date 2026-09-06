# Star Wars idővonal – build eszközök

A weboldal maga egyetlen fájl: `../index.html`. Ezek a szkriptek csak akkor kellenek,
ha bővíteni szeretnéd az adatbázist (pl. Legends regények/képregények pótlása).

- `data_screen.py` – filmek, sorozatok, játékok (kurált lista magyar leírásokkal)
- `data_books.py` – regények és képregények
- `images.json` – borítókép-URL-ek gyorsítótára (Wookieepedia/Wikipedia)
- `fetch_images.py` – borítók lekérése a Fandom API-ból az adatfájlok `wook` mezője alapján
- `index_template.html` – a weboldal sablonja (a `/*__DATA__*/[]` helyére kerül az adat)
- `build.py` – összefűzi az adatokat a sablonnal → `../index.html`

Új elem hozzáadása: vedd fel a megfelelő data_*.py listába, futtasd:
`python3 fetch_images.py && python3 build.py`
