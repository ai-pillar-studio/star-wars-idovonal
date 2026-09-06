# -*- coding: utf-8 -*-
"""Ellenőrzi az adatfájlok épségét. Nem nulla kilépési kóddal áll le, ha HIBA van.
A FIGYELMEZTETÉS-ek nem blokkolnak, de érdemes rendezni őket.
"""
import datetime, json, os, re, sys
from data_screen import SCREEN, OFFTIMELINE
from data_books import NOVELS, COMICS

HERE = os.path.dirname(os.path.abspath(__file__))
TYPES = {'film', 'liveaction', 'animseries', 'miniseries', 'tvfilm', 'game', 'novel', 'comic'}
ERAS = {'highrepublic', 'fall', 'reign', 'rebellion', 'newrepublic', 'firstorder', 'newjedi', 'outside'}
REQUIRED = ('title', 'hu', 'type', 'canon', 'rel', 'y', 'wook', 'desc')

errors, warnings = [], []

def err(m): errors.append(m)
def warn(m): warnings.append(m)

ALL = [(it, 'SCREEN') for it in SCREEN] + [(it, 'OFFTIMELINE') for it in OFFTIMELINE] \
    + [(it, 'NOVELS') for it in NOVELS] + [(it, 'COMICS') for it in COMICS]

today = datetime.date.today().isoformat()
seen_wook, seen_title = {}, {}

for it, src in ALL:
    name = it.get('title') or '<cím nélkül>'

    for k in REQUIRED:
        if k not in it:
            err('%s: hiányzó mező: %s (%s)' % (name, k, src))
    if errors and k not in it:
        continue

    if it.get('type') not in TYPES:
        err('%s: ismeretlen type: %r (érvényes: %s)' % (name, it.get('type'), ', '.join(sorted(TYPES))))
    if not isinstance(it.get('canon'), bool):
        err('%s: a canon mező True/False kell legyen, most: %r' % (name, it.get('canon')))
    if it.get('era') is not None and it.get('era') not in ERAS:
        err('%s: ismeretlen era: %r' % (name, it.get('era')))

    rel = it.get('rel')
    if rel and not re.fullmatch(r'\d{4}-\d{2}-\d{2}', rel):
        err('%s: a rel formátuma ÉÉÉÉ-HH-NN kell legyen, most: %r' % (name, rel))

    y = it.get('y')
    if y is not None and not isinstance(y, (int, float)):
        err('%s: az y szám vagy None kell legyen, most: %r' % (name, y))

    desc = it.get('desc') or ''
    if len(desc) < 60:
        err('%s: túl rövid leírás (%d karakter, minimum 60)' % (name, len(desc)))
    elif len(desc) > 320:
        warn('%s: hosszú leírás (%d karakter, a többi 76–275 között van)' % (name, len(desc)))

    w = it.get('wook')
    if w in seen_wook:
        err('%s: duplikált wook cikk (%r), már használja: %s' % (name, w, seen_wook[w]))
    seen_wook[w] = name
    # Azonos cím különböző médiumban megengedett (pl. az Ahsoka regény és sorozat),
    # a valódi egyedi kulcs a wook cikk. Csak az azonos cím + azonos típus hiba.
    key = (name, it.get('type'))
    if key in seen_title:
        err('%s: duplikált cím azonos típussal (%s és %s)' % (name, src, seen_title[key]))
    seen_title[key] = src

    if it.get('upcoming') and rel and rel <= today:
        warn('%s: upcoming=True, de a megjelenés (%s) már elmúlt — vedd ki az upcoming jelölést'
             % (name, rel))
    if not it.get('upcoming') and rel and rel > today:
        warn('%s: a megjelenés a jövőben van (%s), de nincs upcoming=True' % (name, rel))

# képek
img_path = os.path.join(HERE, 'images.json')
if os.path.exists(img_path):
    images = json.load(open(img_path))
    for it, _ in ALL:
        rec = images.get(it.get('wook'))
        if rec is None:
            warn('%s: nincs images.json bejegyzés — futtasd a fetch_images.py-t' % it.get('title'))
        elif rec.get('missing'):
            err('%s: a Wookieepedia cikk nem létezik: %r — rossz wook cím?'
                % (it.get('title'), it.get('wook')))
        elif not rec.get('local'):
            warn('%s: nincs letöltött kép — futtasd a download_images.py-t' % it.get('title'))
        elif not os.path.exists(os.path.join(HERE, '..', rec['local'])):
            err('%s: hiányzik a képfájl: %s' % (it.get('title'), rec['local']))

for w in warnings:
    print('FIGYELMEZTETÉS:', w)
for e in errors:
    print('HIBA:', e)
print('\n%d mű ellenőrizve | %d hiba | %d figyelmeztetés' % (len(ALL), len(errors), len(warnings)))
sys.exit(1 if errors else 0)
