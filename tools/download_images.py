# -*- coding: utf-8 -*-
"""Letölti az images.json-ben hivatkozott borítókat az ../images/ mappába,
és minden bejegyzésbe beírja a 'local' relatív útvonalat, hogy a build.py
külső hotlink helyett a repóban tárolt fájlra hivatkozhasson.

Idempotens: a már meglévő fájlokat nem tölti le újra.
"""
import json, os, re, time, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(HERE, '..', 'images')
UA = {'User-Agent': 'hobby-timeline/1.0 (personal fan project)'}

EXT_BY_CTYPE = {
    'image/jpeg': '.jpg', 'image/png': '.png', 'image/gif': '.gif',
    'image/webp': '.webp', 'image/svg+xml': '.svg',
}

def wiki_filename(url):
    """A wiki eredeti fájlneve az URL-ből, pl. .../images/7/75/EPI_TPM_poster.png/revision/... """
    path = urllib.parse.urlparse(url).path
    for seg in reversed(path.split('/')):
        if re.search(r'\.(jpe?g|png|gif|webp|svg)$', seg, re.I):
            return urllib.parse.unquote(seg)
    return None

def slugify(name):
    stem, ext = os.path.splitext(name)
    stem = re.sub(r'[^A-Za-z0-9]+', '-', stem).strip('-').lower()
    return (stem or 'kep')[:80] + ext.lower().replace('.jpeg', '.jpg')

def existing_file(fname):
    """Visszaadja a már letöltött fájl nevét, tetszőleges kiterjesztéssel."""
    stem = os.path.splitext(fname)[0]
    for ext in ('.webp', '.jpg', '.png', '.gif', '.svg'):
        cand = stem + ext
        path = os.path.join(IMG_DIR, cand)
        if os.path.exists(path) and os.path.getsize(path) > 0:
            return cand
    return None


def main():
    os.makedirs(IMG_DIR, exist_ok=True)
    images = json.load(open(os.path.join(HERE, 'images.json')))

    taken = {}   # fájlnév -> forrás URL (ütközésfigyeléshez)
    downloaded = skipped = failed = 0

    for title, rec in images.items():
        url = rec.get('thumb')
        if not url:
            rec.pop('local', None)
            continue

        base = wiki_filename(url) or (title + '.jpg')
        fname = slugify(base)
        # névütközés eltérő forrásokkal -> sorszámozás
        n = 2
        while taken.get(fname, url) != url:
            stem, ext = os.path.splitext(slugify(base))
            fname = f'{stem}-{n}{ext}'
            n += 1
        taken[fname] = url

        # A Fandom .png/.jpg URL-en is webp-et szolgálhat ki, ilyenkor a fájl más
        # kiterjesztéssel mentődött -> a stem alapján keressük a meglévő példányt.
        existing = existing_file(fname)
        if existing:
            rec['local'] = 'images/' + existing
            taken[existing] = url
            skipped += 1
            continue
        dest = os.path.join(IMG_DIR, fname)

        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=45) as r:
                data = r.read()
                ctype = (r.headers.get('Content-Type') or '').split(';')[0].strip().lower()
        except Exception as e:
            print('  HIBA:', title, '->', e)
            failed += 1
            continue

        # kiterjesztés korrekció a tényleges tartalom alapján
        want = EXT_BY_CTYPE.get(ctype)
        if want and not fname.lower().endswith(want):
            stem = os.path.splitext(fname)[0]
            fname = stem + want
            dest = os.path.join(IMG_DIR, fname)
            taken[fname] = url

        with open(dest, 'wb') as f:
            f.write(data)
        rec['local'] = 'images/' + fname
        downloaded += 1
        print('  ok: %-60s %6.1f KB' % (fname, len(data) / 1024))
        time.sleep(0.15)

    json.dump(images, open(os.path.join(HERE, 'images.json'), 'w'),
              ensure_ascii=False, indent=1)

    total = sum(os.path.getsize(os.path.join(IMG_DIR, f)) for f in os.listdir(IMG_DIR))
    print('\nletöltve: %d | már megvolt: %d | sikertelen: %d' % (downloaded, skipped, failed))
    print('images/ mérete: %d fájl, %.1f MB' % (len(os.listdir(IMG_DIR)), total / 1024 / 1024))

if __name__ == '__main__':
    main()
