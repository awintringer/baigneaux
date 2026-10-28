#!/usr/bin/env python3
"""Génère les icônes vectorielles des tuiles de l'accueil (site/data/images/icone-*.svg).
Libellés en Manrope 600 convertis en tracés (rendu identique partout, sans police installée).
usage: python3 tools/icons/make_icons.py   (requiert fonttools + brotli)"""
import os
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FONT = TTFont(os.path.join(ROOT, 'site', 'data', 'fonts', 'manrope-latin-600-normal.woff2'))
GS, CMAP, UPM = FONT.getGlyphSet(), FONT.getBestCmap(), FONT['head'].unitsPerEm
HMTX = FONT['hmtx']
GREEN, DARK, BG, BORDER = '#2f5e3e', '#1f2937', '#ffffff', '#d6e6d9'

def text_path(s, size, cx, baseline):
    scale = size / UPM
    width = sum(HMTX[CMAP[ord(c)]][0] for c in s) * scale
    x = cx - width / 2; d = []
    for c in s:
        g = CMAP[ord(c)]
        pen = SVGPathPen(GS)
        GS[g].draw(TransformPen(pen, (scale, 0, 0, -scale, x, baseline)))
        d.append(pen.getCommands()); x += HMTX[g][0] * scale
    return f'<path d="{" ".join(d)}" fill="{DARK}"/>'

STROKE = f'fill="none" stroke="{GREEN}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"'
ICONS = {
    'horaires': (['Horaires', 'd’ouverture'],
        f'<circle cx="80" cy="58" r="32" {STROKE}/><path d="M80 38 V58 L94 67" {STROKE}/>'),
    'contact': (['Nous', 'contacter'],
        f'<rect x="44" y="34" width="72" height="50" rx="7" {STROKE}/><path d="M47 39 L80 63 L113 39" {STROKE}/>'),
    'conseil': (['Conseil', 'municipal'],
        f'<circle cx="58" cy="38" r="7" {STROKE}/><circle cx="80" cy="33" r="8" {STROKE}/><circle cx="102" cy="38" r="7" {STROKE}/>'
        f'<path d="M47 60 Q58 46 69 60 M68 56 Q80 41 92 56 M91 60 Q102 46 113 60" {STROKE}/>'
        f'<rect x="42" y="60" width="76" height="12" rx="3" {STROKE}/><path d="M50 72 V88 M110 72 V88" {STROKE}/>'),
    'lecteur-puce': (['Lecteur de', 'puce électronique'],
        f'<rect x="40" y="32" width="80" height="54" rx="7" {STROKE}/><path d="M40 46 H120" {STROKE}/>'
        f'<rect x="50" y="58" width="18" height="12" rx="2.5" {STROKE}/><path d="M78 60 H106 M78 69 H98" {STROKE}/>'),
}

# Affichée en petit (mobile), l'icône masque son libellé et agrandit le pictogramme (un seul fichier)
SMALL = ('@media (max-width: 110px) { .label { display: none; } '
         '.ico { transform-origin: 80px 59px; transform: translate(0px, 21px) scale(1.3); } '
         '.ico * { stroke-width: 6px; } }')

def svg(name, lines, body):
    size = 15 if max(len(l) for l in lines) <= 12 else 13.5
    labels = ''.join(text_path(l, size, 80, 118 + i * (size + 4)) for i, l in enumerate(lines))
    title = ' '.join(lines).replace('’', "'")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 160 160" width="160" height="160" role="img" aria-label="{title}">'
            f'<title>{title}</title><style>{SMALL}</style>'
            f'<rect x="2" y="2" width="156" height="156" rx="22" fill="{BG}" stroke="{BORDER}" stroke-width="2"/>'
            f'<g class="ico">{body}</g><g class="label">{labels}</g></svg>\n')

for name, (lines, body) in ICONS.items():
    out = os.path.join(ROOT, 'site', 'data', 'images', f'icone-{name}.svg')
    open(out, 'w', encoding='utf-8').write(svg(name, lines, body))
    print(out, os.path.getsize(out), 'octets')
