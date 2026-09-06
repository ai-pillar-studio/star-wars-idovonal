---
name: star-wars-frissites
description: A Star Wars galaktikus idővonal weboldal frissítése. Felkutatja az új Star Wars tartalmakat (filmek, sorozatok, évadok, regények, képregények, játékok), összeveti a projekt aktuális listájával, hozzáadja az újakat leírással és borítóképpel, majd GitHubra pusholja, hogy az élő oldal frissüljön. Használd, ha a felhasználó a Star Wars idővonal/projekt frissítését kéri, új tartalmak kereséséről vagy az oldal aktualizálásáról beszél.
---

# Star Wars idővonal frissítése

Az idővonal-oldal (`index.html`) generált fájl. **Soha ne szerkeszd közvetlenül** —
mindig az adatfájlokat módosítsd, és futtasd újra a pipeline-t.

## 0. A projekt megkeresése

Alapértelmezett hely:
`/Users/simonadamtamas/Documents/ClaudeCode/hobby projects/star-wars-idovonal`

Ha nincs ott, klónozd egy munkakönyvtárba, és ott dolgozz:
`git clone https://github.com/ai-pillar-studio/star-wars-idovonal.git`

Ha létezik, előbb `git pull`, hogy ne egy elavult állapotra dolgozz.

## 1. A jelenlegi állapot beolvasása

Olvasd el a repo gyökerében a **`CONTENT.md`** fájlt — ez a mérvadó, generált
lista mind a ~150 műről (cím, magyar cím, típus, megjelenés, in-universe év,
kánon/Legends, Wookieepedia-cikk). Ez a kutatás kiindulópontja.

Jegyezd meg külön a „Még meg nem jelent / bejelentett" szakaszt: ezeknél lehet,
hogy időközben megjelentek, vagy csúszott a dátumuk.

## 2. Kutatás

Keress rá, mi történt a legutóbbi frissítés óta. Használható források:

- Wookieepedia: „Timeline of canon media" — az idővonal hivatalos rendezése
- StarWars.com hírek, Lucasfilm / Disney bejelentések
- Wookieepedia „Upcoming media" és az egyes művek cikkei

Mit keress:
- **új megjelenések**: film, sorozat vagy évad, regény, képregény-sorozat, játék
- **bejelentések**: még meg nem jelent, de datált vagy datálatlan projektek
- **állapotváltozás**: a `CONTENT.md` „még meg nem jelent" tételei közül
  megjelent-e valamelyik, illetve csúszott-e a dátum
- **idővonal-változás**: átsorolták-e valaminek az in-universe évét
- **kánon-változás**: bekerült-e Legends-anyag a kánonba vagy fordítva

Ha nincs semmi új, **ne találj ki semmit** — jelentsd, hogy nincs változás,
és állj meg. Üres commitot ne csinálj.

## 3. Ellenőrzés hozzáadás előtt — `lookup.py`

Minden jelöltet a Wookieepedia infoboxából ellenőrizz, ne a keresési találatok
szövegéből és **soha ne emlékezetből**:

```bash
python3 tools/lookup.py "Eyes Like Stars" "Star Wars Zero Company"
```

Kiírja a cikk tényadatait: `release date`, **`timeline`** (ebből jön az in-universe
év), `author`/`writer`/`director`/`developer`, `publisher`, `media type`, és a kiadói
ismertetőt, amiből a magyar `desc` írható. Ha a cikk nem létezik, azt is megmondja —
ilyenkor rossz a `wook` cím, keresd meg a pontosat.

Szabályok:

- **az in-universe évet a `timeline` mezőből vedd**, ne becsüld meg. Ha a mező hiányzik
  vagy nem egyértelmű, a mű az `OFFTIMELINE` listába kerül, és jelezd a felhasználónak
- tartományt (`19 BBY–18 BBY`) a kezdetéhez közeli értékkel vegyél fel, és a `desc`-ben
  utalj rá, hogy a cselekmény átível
- a `release date`-et is innen vedd, ne a hírportálokról

**A `WebFetch` a starwars.fandom.com-on nem működik** (a Fandom 402-t ad rá), ezért a
cikkek tartalmához a `lookup.py`-t használd. A `WebSearch` arra jó, hogy *megtaláld*,
mi az új — az ellenőrzés viszont mindig a `lookup.py`.

## 4. Az adat felvétele

A megfelelő listába vedd fel, a meglévő tételek stílusát követve:

- `tools/data_screen.py` → `SCREEN` (film, liveaction, animseries, miniseries, tvfilm, game)
  és `OFFTIMELINE` (in-universe évhez nem köthető művek)
- `tools/data_books.py` → `NOVELS` (novel) és `COMICS` (comic)

Mezők:

| mező | kötelező | leírás |
|---|---|---|
| `title` | igen | eredeti cím |
| `hu` | igen | magyar cím; ha nincs hivatalos magyar cím, üres string |
| `type` | igen | `film`, `liveaction`, `animseries`, `miniseries`, `tvfilm`, `game`, `novel`, `comic` |
| `canon` | igen | `True` = kánon, `False` = Legends |
| `rel` | igen | megjelenés `ÉÉÉÉ-HH-NN`; ha nincs dátum, üres string |
| `y` | igen | in-universe év, BBY = negatív, ABY = pozitív, tört szám is lehet; `None` ha nem köthető |
| `era` | nem | korszak-felülbírálás, ha az `y`-ból számolt alapérték nem stimmel: `highrepublic`, `fall`, `reign`, `rebellion`, `newrepublic`, `firstorder`, `newjedi`, `outside` |
| `wook` | igen | a Wookieepedia-cikk **pontos** címe (ebből jön a borítókép) |
| `desc` | igen | magyar leírás, 2–3 mondat, **100–250 karakter** |
| `upcoming` | nem | `True`, ha még nem jelent meg |

A `desc` a meglévők hangnemét kövesse: tárgyilagos, spoilermentes ismertető,
ami elhelyezi a művet a történetben. Nézd meg néhány szomszédos tétel leírását
mintának, mielőtt írsz.

Ha egy korábban `upcoming=True` mű időközben megjelent, vedd ki az `upcoming`
jelölést, és pontosítsd a `rel` dátumot.

## 5. A pipeline futtatása

A `tools/` mappából, ebben a sorrendben:

```bash
python3 fetch_images.py && python3 download_images.py && python3 build.py && python3 validate.py
```

- `fetch_images.py` — borító-URL-ek a Fandom API-ból. A kimenetében a
  **MISSING PAGES** szakasz a hibás `wook` címeket jelenti: ezeket javítsd, ne hagyd benne
- `download_images.py` — a képeket az `images/` mappába tölti (idempotens)
- `build.py` — újragenerálja az `index.html`-t **és** a `CONTENT.md`-t
- `validate.py` — épségellenőrzés. **Ha hibát jelez, ne pushold**: javítsd, majd futtasd újra

## 6. Ellenőrzés

- `git diff --stat` — csak a várt fájlok változtak?
- nyisd meg a helyi `index.html`-t, és nézd meg, hogy az új tételek a jó helyen,
  képpel jelennek meg

## 7. Publikálás

Két mód van. **Ha a futás felügyelet nélküli** (havi routine, ütemezett futás),
mindig a PR-mód a helyes — kivéve, ha a felhasználó kifejezetten mást kér.

### PR-mód (felügyelet nélküli futásnál ez a kötelező)

```bash
git checkout -b frissites-$(date +%Y-%m)
git add -A && git commit
git push -u origin frissites-$(date +%Y-%m)
gh pr create --title "..." --body "..."
```

A PR leírása tartalmazza tételenként: mi került be, milyen **forrás** alapján,
mi az in-universe éve, és mit hagytál ki és miért. A main-re **ne** pusholj.

### Közvetlen mód (csak ha a felhasználó jelen van és ezt kéri)

```bash
git add -A && git commit && git push origin main
```

A commit üzenete sorolja fel, mi került be. Utána várd meg a GitHub Pages buildet,
és ellenőrizd az élő oldalt:

```bash
gh api /repos/ai-pillar-studio/star-wars-idovonal/pages/builds/latest --jq .status
curl -s -o /dev/null -w '%{http_code}\n' https://ai-pillar-studio.github.io/star-wars-idovonal/
```

## 8. Jelentés

Foglald össze a felhasználónak:
- mi került be (cím, típus, in-universe év), és milyen forrás alapján
- mi változott meg (dátum, kánon-státusz, upcoming→megjelent)
- **mit hagytál ki és miért** (pl. nincs megbízható in-universe év, nincs Wookieepedia-cikk)
- az élő oldal állapota

## Amit soha ne csinálj

- ne szerkeszd kézzel az `index.html`-t vagy a `CONTENT.md`-t — mindkettő generált
- ne találj ki művet, dátumot vagy in-universe évet forrás nélkül
- ne pushold, ha a `validate.py` hibát jelez
- **soha ne futtass `rm -rf`-et** takarításra. Ha egy szkript rossz helyre írt fájlt,
  a szkriptet javítsd, a szemetet pedig néven nevezve, egyesével töröld — abszolút
  útvonalra menő rekurzív törlés tilos
- ne csinálj üres commitot vagy üres PR-t, ha nincs változás
- felügyelet nélküli futásnál soha ne pushold közvetlenül a main-re
