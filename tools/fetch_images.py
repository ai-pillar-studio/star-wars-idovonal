# -*- coding: utf-8 -*-
import json, os, urllib.request, urllib.parse, time

HERE = os.path.dirname(os.path.abspath(__file__))
from data_screen import SCREEN, OFFTIMELINE
from data_books import NOVELS, COMICS

ALL = SCREEN + OFFTIMELINE + NOVELS + COMICS

def default_era(y):
    if y is None: return "outside"
    if y <= -100: return "highrepublic"
    if y <= -19:  return "fall"
    if y <= -5:   return "reign"
    if y <= 4.25: return "rebellion"
    if y <= 27:   return "newrepublic"
    if y <= 35.4: return "firstorder"
    return "newjedi"

for it in ALL:
    it.setdefault('era', default_era(it['y']))

titles = [it['wook'] for it in ALL]
print('items:', len(ALL), 'unique wook titles:', len(set(titles)))

def fandom_images(batch):
    q = urllib.parse.quote('|'.join(batch))
    url = f"https://starwars.fandom.com/api.php?action=query&titles={q}&prop=pageimages&piprop=thumbnail&pithumbsize=480&pilicense=any&format=json&redirects=1"
    req = urllib.request.Request(url, headers={'User-Agent':'hobby-timeline/1.0'})
    d = json.load(urllib.request.urlopen(req, timeout=45))
    # map: queried title -> final title (normalized + redirects)
    mapping = {}
    for n in d.get('query',{}).get('normalized',[]): mapping[n['from']] = n['to']
    for r in d.get('query',{}).get('redirects',[]):  mapping[r['from']] = r['to']
    imgs = {}
    for p in d.get('query',{}).get('pages',{}).values():
        t = p.get('title')
        thumb = p.get('thumbnail',{}).get('source')
        missing = 'missing' in p
        imgs[t] = (thumb, missing)
    out = {}
    for t in batch:
        final = t
        while final in mapping: final = mapping[final]
        thumb, missing = imgs.get(final, (None, True))
        out[t] = {'thumb': thumb, 'missing': missing, 'final': final}
    return out

result = {}
uniq = list(dict.fromkeys(titles))
for i in range(0, len(uniq), 50):
    batch = uniq[i:i+50]
    result.update(fandom_images(batch))
    time.sleep(0.5)

# A meglévő borítók RÖGZÍTETTEK. A Fandom időnként lecseréli egy cikk fő képét
# (jellemzően plakátról sorozatlogóra), és e nélkül minden futás átírná az addigi
# borítókat — az oldal kinézete magától, észrevétlenül romlana. Ezért amelyik
# műnek már van letöltött képe, azt érintetlenül hagyjuk; csak az új művek
# borítója jön a friss API-válaszból.
#
# Szándékos frissítéshez:  python3 fetch_images.py --refresh
import sys as _sys
refresh = '--refresh' in _sys.argv

try:
    prev = json.load(open('images.json'))
except (IOError, ValueError):
    prev = {}

pinned = 0
for title, rec in result.items():
    old_rec = prev.get(title) or {}
    local = old_rec.get('local')
    if local and not refresh and os.path.exists(os.path.join(HERE, '..', local)):
        # a régi rekord marad, a friss thumb URL-t eldobjuk
        result[title] = dict(old_rec)
        pinned += 1

json.dump(result, open('images.json','w'), ensure_ascii=False, indent=1)
print('rögzített (változatlanul hagyott) borító:', pinned,
      '| friss URL:', len(result) - pinned,
      '| --refresh' if refresh else '')
nf = [t for t,v in result.items() if v['missing']]
noimg = [t for t,v in result.items() if not v['missing'] and not v['thumb']]
print('MISSING PAGES (%d):' % len(nf));  [print('  -', t) for t in nf]
print('PAGE OK BUT NO IMAGE (%d):' % len(noimg)); [print('  -', t) for t in noimg]
print('with image:', sum(1 for v in result.values() if v['thumb']))
