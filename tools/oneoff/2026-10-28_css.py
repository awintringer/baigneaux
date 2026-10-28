#!/usr/bin/env python3
"""28/10/2026 — nettoyage CSS sans changement visuel voulu, polices auto-hébergées.
- feuille de style : déclarations invalides supprimées, style mort retiré, polices de secours
- CSS embarqué : déclarations « undefined » supprimées, largeurs de colonnes > 100 % normalisées
- en-tête HTML des pages : @font-face Google (1 graisse) -> polices locales data/fonts (vraies graisses)"""
import sys, os, re, glob
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from sitelib import Page, T, set_text, SITE

# ---------------------------------------------------------------- default.css
p = os.path.join(SITE, 'css', 'default.css'); css = open(p, encoding='utf-8').read(); before = css
for bad in (r'\tundefined: [^;]*;\n', r'\tborder-color: aa8a8f;\n', r'\ttext-shadow: #000000;\n', r'\tfont-variant: bold;\n'):
    css, n = re.subn(bad, '', css); assert n, bad
css = css.replace('color : #000091;', 'color: #000091;')
css, n = re.subn(r'\.wscontainer_Main \{[^}]*\}\n', '', css); assert n == 1
FONTS = {
    'Playfair Display': '"Playfair Display", Georgia, serif',
    'Inter': 'Inter, Arial, sans-serif',
    'Manrope': 'Manrope, Arial, sans-serif',
    '"Manrope"': 'Manrope, Arial, sans-serif',
    'Calibri': 'Calibri, Inter, Arial, sans-serif',
}
def fam(m):
    v = m.group(1).strip()
    return f'font-family: {FONTS.get(v, v)};'
css = re.sub(r'font-family: ([^;,]+);', fam, css)
open(p, 'w', encoding='utf-8').write(css)
print('default.css:', len(before), '->', len(css), 'octets')

# ---------------------------------------------------------------- polices locales
FACES = [('Inter', 'inter', w, 'normal') for w in (400, 500, 600, 700)] + \
        [('Manrope', 'manrope', w, 'normal') for w in (400, 500, 600, 700)] + \
        [('Playfair Display', 'playfair-display', w, 'normal') for w in (400, 700)] + \
        [('Playfair Display', 'playfair-display', 400, 'italic')]
FONT_BLOCK = '<style>\r\n/* Polices hébergées sur le site (data/fonts, licence SIL OFL) */\r\n' + ''.join(
    f"@font-face {{ font-family: '{f}'; font-style: {s}; font-weight: {w}; font-display: swap; "
    f"src: url(data/fonts/{slug}-latin-{w}-{s}.woff2) format('woff2'); }}\r\n" for f, slug, w, s in FACES) + '</style>'
for name in ('Inter', 'Manrope', 'Playfair'):
    assert any(f.startswith(name) for f, *_ in FACES)

# ---------------------------------------------------------------- pages, modèles, brouillons
def norm_widths(parent):
    cells = parent.get('contents') or []
    ws = []
    for c in cells:
        m = re.search(r'width:\s*([\d.]+)%', T(c.get('embedded_css_rules'))); ws.append(float(m.group(1)) if m else None)
    known = [w for w in ws if w is not None]
    if not known or sum(known) <= 100.5 or None in ws: return 0
    # Le navigateur (tableau) honore les premières colonnes et donne le reste à la dernière :
    # 60/60 s'affiche 60/40, 75/30 -> 75/25, 50/70 -> 50/50 (mesuré). On écrit ce qui s'affiche.
    acc = 0.0
    for i, (c, w) in enumerate(zip(cells, ws)):
        new = round(100 - acc, 1) if i == len(cells) - 1 else round(min(w, 100 - acc), 1)
        acc += new
        set_text(c, 'embedded_css_rules', re.sub(r'width:\s*[\d.]+%', f'width: {new:g}%', T(c['embedded_css_rules'])))
    return 1

stats = {'hdr': 0, 'undefined': 0, 'widths': 0}
for f in sorted(glob.glob(f'{SITE}/pages/*.json') + glob.glob(f'{SITE}/models/*.json') + glob.glob(f'{SITE}/drafts/*.json')):
    pg = Page(os.path.relpath(f, SITE)[:-5]); changed = False
    h = T(pg.root.get('hdr_html'))
    if 'fonts.gstatic.com' in h:
        h2, n = re.subn(r'<style>(?:(?!</style>).)*fonts\.gstatic\.com(?:(?!</style>).)*</style>', lambda m: FONT_BLOCK, h, count=1, flags=re.S)
        assert n == 1 and 'gstatic' not in h2, f
        set_text(pg.root, 'hdr_html', h2); stats['hdr'] += 1; changed = True
    for n, ps in pg.walk():
        e = T(n.get('embedded_css_rules'))
        if 'undefined:' in e:
            set_text(n, 'embedded_css_rules', re.sub(r'\s*undefined:[^;]*;', '', e)); stats['undefined'] += 1; changed = True
        if 'pages' in f and not any(a.get('model_id') for a in ps + (n,)) and norm_widths(n):
            stats['widths'] += 1; changed = True
    if changed: pg.save()
print(stats)
