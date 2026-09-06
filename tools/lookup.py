# -*- coding: utf-8 -*-
"""Egy Wookieepedia-cikk tényadatainak kiírása az infoboxból.

Használat:  python3 lookup.py "Eyes Like Stars" ["Másik cím" ...]

A frissítési munkafolyamat ellenőrző lépése: a `timeline` mezőből jön az
in-universe év, a `release date`-ből a megjelenés — így egyiket sem kell
megbecsülni. Ha a cikk nem létezik, azt is jelzi (rossz `wook` cím).
"""
import html, json, re, sys, urllib.error, urllib.parse, urllib.request

UA = {'User-Agent': 'hobby-timeline/1.0 (personal fan project)'}
FIELDS = ('release date', 'released', 'publication date', 'timeline', 'author',
          'writer', 'artist', 'director', 'developer', 'publisher', 'media type',
          'season', 'episodes', 'pages', 'series', 'preceded by', 'followed by')

def api(**p):
    p.setdefault('format', 'json')
    url = 'https://starwars.fandom.com/api.php?' + urllib.parse.urlencode(p)
    return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30))

def clean(v):
    v = re.sub(r'<ref[^>]*?/>', '', v)
    v = re.sub(r'<ref.*?</ref>', '', v, flags=re.S)
    v = re.sub(r'\{\{[^{}]*\}\}', '', v)
    v = re.sub(r'\[\[(?:[^|\]]*\|)?([^\]]*)\]\]', r'\1', v)
    v = v.replace("'''", '').replace("''", '').replace('<br />', ' / ').replace('*', ' ')
    return html.unescape(re.sub(r'\s+', ' ', v)).strip(' /,')

def fields(ib):
    """Az infobox legfelső szintű mezői. A beágyazott sablonok és hivatkozások
    belsejében lévő | jeleket nem tekinti mezőhatárnak."""
    body = ib[2:-2] if ib.endswith('}}') else ib[2:]
    out, depth, buf = {}, 0, ''

    def add(chunk):
        if '=' in chunk:
            k, v = chunk.split('=', 1)
            k = k.strip().lower()
            if k:
                out[k] = v

    k = 0
    while k < len(body):
        two = body[k:k + 2]
        if two in ('{{', '[['):
            depth += 1; buf += two; k += 2; continue
        if two in ('}}', ']]'):
            depth -= 1; buf += two; k += 2; continue
        if body[k] == '|' and depth == 0:
            add(buf); buf = ''; k += 1; continue
        buf += body[k]; k += 1
    add(buf)
    return out


def top_templates(wt):
    """A cikk legfelső szintű {{...}} sablonjai, kiegyensúlyozott párokat követve."""
    out, i = [], 0
    while True:
        i = wt.find('{{', i)
        if i < 0:
            return out
        depth, j = 0, i
        while j < len(wt) - 1:
            if wt[j:j + 2] == '{{':
                depth += 1; j += 2; continue
            if wt[j:j + 2] == '}}':
                depth -= 1; j += 2
                if depth == 0:
                    break
                continue
            j += 1
        out.append(wt[i:j])
        i = j


def infobox(wt):
    """A cikk élén több sablon is állhat (era-sáv, karbantartási bannerek).
    Azt választjuk, amelyik a legtöbb keresett mezőt tartalmazza."""
    best, best_score = '', 0
    for tpl in top_templates(wt)[:12]:
        score = sum(1 for k in fields(tpl) if k in FIELDS)
        if score > best_score:
            best, best_score = tpl, score
    return best


def summary(wikitext):
    m = re.search(r"==\s*Publisher's summary\s*==\s*(.+?)(?:\n==|\Z)", wikitext, re.S)
    if not m:
        m = re.search(r"==\s*Official description\s*==\s*(.+?)(?:\n==|\Z)", wikitext, re.S)
    return clean(m.group(1))[:600] if m else ''

def lookup(title):
    print('=' * 70)
    print(title)
    print('=' * 70)
    try:
        d = api(action='parse', page=title, prop='wikitext', redirects=1)
    except Exception as e:
        print('  ✗ HIBA:', e)
        return
    # a hiányzó lapot a Fandom JSON-hibaként adja vissza, nem HTTP 404-ként
    if 'error' in d or 'parse' not in d:
        print('  ✗ NINCS ILYEN CIKK — rossz wook cím, keress rá a pontos címre')
        print('   ', d.get('error', {}).get('info', ''))
        return

    real = d['parse'].get('title', title)
    if real != title:
        print('  átirányítva ide:', real)
    wt = d['parse']['wikitext']['*']

    fs = fields(infobox(wt))
    for key in FIELDS:
        if key in fs:
            val = clean(fs[key])
            if val:
                print('  %-16s %s' % (key + ':', val[:150]))

    s = summary(wt)
    if s:
        print('\n  Kiadói ismertető:\n   ', s)
    print()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    for t in sys.argv[1:]:
        lookup(t)
