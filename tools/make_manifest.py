# -*- coding: utf-8 -*-
"""Generálja a ../CONTENT.md fájlt: az idővonalon szereplő összes mű pontos,
gépileg is olvasható listája. Ez a frissítési munkafolyamat bemenete —
ehhez kell hasonlítani a friss kutatás eredményét.
"""
import os
from data_screen import SCREEN, OFFTIMELINE
from data_books import NOVELS, COMICS

HERE = os.path.dirname(os.path.abspath(__file__))
DEST = os.path.join(HERE, '..', 'CONTENT.md')

TYPE_HU = {
    'film': 'Film', 'liveaction': 'Élőszereplős sorozat', 'animseries': 'Animációs sorozat',
    'miniseries': 'Minisorozat', 'tvfilm': 'TV-film', 'game': 'Videójáték',
    'novel': 'Regény', 'comic': 'Képregény',
}

def rows():
    for src, off in ((SCREEN, False), (NOVELS, False), (COMICS, False), (OFFTIMELINE, True)):
        for it in src:
            yield it, off

def iy(it):
    """In-universe év olvasható alakban."""
    y = it['y']
    if y is None:
        return '—'
    return ('%g BBY' % -y) if y < 0 else ('%g ABY' % y)

def esc(s):
    return (s or '').replace('|', '\\|')

def main():
    items = list(rows())
    lines = []
    lines.append('# Tartalomlista\n')
    lines.append('Az idővonalon szereplő összes mű. **Generált fájl — kézzel ne szerkeszd:**')
    lines.append('a forrás a `tools/data_screen.py` és a `tools/data_books.py`, ez a lista a')
    lines.append('`tools/make_manifest.py` (illetve a `build.py`) futásakor készül újra.\n')

    from collections import Counter
    c = Counter(TYPE_HU.get(it['type'], it['type']) for it, _ in items)
    lines.append('Összesen **%d** mű: ' % len(items) +
                 ', '.join('%s %d' % (k, v) for k, v in sorted(c.items())) + '.\n')

    upcoming = [it for it, _ in items if it.get('upcoming')]
    if upcoming:
        lines.append('## Még meg nem jelent / bejelentett\n')
        lines.append('| Cím | Magyar cím | Típus | Megjelenés | Wookieepedia |')
        lines.append('|---|---|---|---|---|')
        for it in sorted(upcoming, key=lambda i: i.get('rel') or ''):
            lines.append('| %s | %s | %s | %s | %s |' % (
                esc(it['title']), esc(it['hu']), TYPE_HU.get(it['type'], it['type']),
                it.get('rel') or '—', esc(it['wook'])))
        lines.append('')

    lines.append('## Teljes lista (megjelenés szerint, legújabb elöl)\n')
    lines.append('| Cím | Magyar cím | Típus | Megjelenés | In-universe | Kánon | Wookieepedia |')
    lines.append('|---|---|---|---|---|---|---|')
    for it, off in sorted(items, key=lambda p: (p[0].get('rel') or ''), reverse=True):
        jel = []
        if off: jel.append('idővonalon kívül')
        if it.get('upcoming'): jel.append('még nem jelent meg')
        cim = esc(it['title']) + (' _(%s)_' % ', '.join(jel) if jel else '')
        lines.append('| %s | %s | %s | %s | %s | %s | %s |' % (
            cim, esc(it['hu']), TYPE_HU.get(it['type'], it['type']),
            it.get('rel') or '—', iy(it), 'kánon' if it['canon'] else 'Legends',
            esc(it['wook'])))
    lines.append('')

    open(DEST, 'w').write('\n'.join(lines))
    print('CONTENT.md: %d mű, %.1f KB' % (len(items), os.path.getsize(DEST) / 1024))

if __name__ == '__main__':
    main()
