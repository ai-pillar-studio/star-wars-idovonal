# Star Wars – Galaktikus idővonal

Magyar nyelvű, egyfájlos rajongói oldal: ~150 Star Wars-mű (filmek, sorozatok,
videójátékok, regények, képregények) kígyózó, korszakonként témázott idővonalon,
in-universe (BBY/ABY) sorrendben, kánon/Legends és típus szerinti szűrőkkel.

**Élő oldal:** https://ai-pillar-studio.github.io/star-wars-idovonal/

## Felépítés

- `index.html` – maga a weboldal, egyetlen önálló fájl (nincs build, nincs függőség)
- `tools/` – az adat-pipeline, ami az `index.html`-t generálja; részletek: [tools/README.md](tools/README.md)

## Bővítés

```bash
cd tools
python3 fetch_images.py && python3 build.py
```

## Jogi megjegyzés

Nem hivatalos rajongói projekt, semmilyen kapcsolatban nem áll a Lucasfilm Ltd.-vel
vagy a The Walt Disney Company-val. A Star Wars és a kapcsolódó nevek a jogtulajdonosok
védjegyei. A borítóképek a Wookieepedia/Wikipedia felől hivatkozottak, ismertető céllal.
