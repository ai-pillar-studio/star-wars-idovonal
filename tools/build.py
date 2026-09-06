# -*- coding: utf-8 -*-
import json, os
from data_screen import SCREEN, OFFTIMELINE
from data_books import NOVELS, COMICS

images = json.load(open('images.json'))

def default_era(y):
    if y is None: return "outside"
    if y <= -100: return "highrepublic"
    if y <= -19:  return "fall"
    if y <= -5:   return "reign"
    if y <= 4.25: return "rebellion"
    if y <= 27:   return "newrepublic"
    if y <= 35.4: return "firstorder"
    return "newjedi"

ALL = SCREEN + NOVELS + COMICS + OFFTIMELINE
out = []
for i, it in enumerate(ALL):
    era = it.get('era') or default_era(it['y'])
    img = images.get(it['wook'], {}).get('thumb')
    out.append(dict(
        id='n%d' % i, title=it['title'], hu=it.get('hu'), type=it['type'],
        canon=it['canon'], rel=it.get('rel'), y=it['y'], era=era,
        img=img, desc=it['desc'], upcoming=bool(it.get('upcoming')),
    ))

tpl = open('index_template.html').read()
assert '/*__DATA__*/[]' in tpl
html = tpl.replace('/*__DATA__*/[]', json.dumps(out, ensure_ascii=False))

dest_dir = '/Users/simonadamtamas/Documents/ClaudeCode/hobby projects/star-wars-idovonal'
os.makedirs(dest_dir, exist_ok=True)
dest = os.path.join(dest_dir, 'index.html')
open(dest, 'w').write(html)
print('items:', len(out), '| with img:', sum(1 for o in out if o['img']))
from collections import Counter
print(Counter(o['era'] for o in out))
print(Counter(o['type'] for o in out))
print('written:', dest, '(%.0f KB)' % (os.path.getsize(dest)/1024))
