# Star Wars – Galaktikus idővonal

Magyar nyelvű, egyfájlos rajongói oldal: ~150 Star Wars-mű (filmek, sorozatok,
videójátékok, regények, képregények) kígyózó, korszakonként témázott idővonalon,
in-universe (BBY/ABY) sorrendben, kánon/Legends és típus szerinti szűrőkkel.

**Élő oldal:** https://ai-pillar-studio.github.io/star-wars-idovonal/

## Felépítés

- `index.html` – maga a weboldal, egyetlen önálló fájl (nincs build, nincs futásidejű függőség)
- `images/` – a borítóképek; az oldal relatív útvonalon hivatkozik rájuk
- `CONTENT.md` – az összes szereplő mű generált listája (a frissítés kiindulópontja)
- `tools/` – az adat-pipeline, ami az `index.html`-t generálja; részletek: [tools/README.md](tools/README.md)

## Bővítés

```bash
cd tools
python3 fetch_images.py && python3 download_images.py && python3 build.py && python3 validate.py
```

A teljes frissítési munkafolyamat — friss tartalmak felkutatása, felvétele, publikálás —
a `star-wars-frissites` skillben van leírva:
[.claude/skills/star-wars-frissites/SKILL.md](.claude/skills/star-wars-frissites/SKILL.md).
Claude Code sessionben elég annyi, hogy *„frissítsd a Star Wars projektet"*.

## Jogi megjegyzés

Nem hivatalos rajongói projekt, semmilyen kapcsolatban nem áll a Lucasfilm Ltd.-vel
vagy a The Walt Disney Company-val. A Star Wars és a kapcsolódó nevek a jogtulajdonosok
védjegyei. A borítóképek kis felbontású részletek a Wookieepedia/Wikipedia anyagaiból, ismertető céllal.
