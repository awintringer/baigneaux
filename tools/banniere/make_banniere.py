#!/usr/bin/env python3
"""Bannière d'accueil en illustration vectorielle façon affiche (en attendant une photo HD).

Motif : la tour ronde de Baigneaux sur sa colline, le grand arbre, le chemin et les rangs de vigne
de la photo d'origine (1442_banner.png), redessinés en aplats aux couleurs de la charte.
La partie gauche reste claire (titre « Bienvenue à Baigneaux » posé dessus).
Palette vérifiée pour les daltoniens : les plans se distinguent par leur clarté (du sauge très
pâle au vert vigne), la pierre de la tour est sable clair sur feuillage foncé (contraste de
luminance), aucune information ne repose sur l'opposition rouge/vert.

usage: python3 tools/banniere/make_banniere.py   -> site/data/images/background/banniere-affiche.svg
"""
import os, math, random

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, 'site', 'data', 'images', 'background', 'banniere-affiche.svg')
W, H = 1200, 330

C = dict(ciel_haut='#CFE2E6', ciel_bas='#F4F1E6', soleil='#F3E3B3', nuage='#FFFFFF',
         loin='#CBD9C4', milieu='#A3BF94', pres='#6E9A63', avant='#3F7449', vigne='#2F5E3E',
         chemin='#EFE6CF', chemin_bord='#D9CCAA', pierre='#DCC79E', pierre_ombre='#B59C6E',
         pierre_nuit='#4E4232', arbre='#2F5E3E', arbre_clair='#4E8350', tronc='#5A4A35')

def f(x): return f'{x:.1f}'.rstrip('0').rstrip('.')

def colline(points, couleur, bas=H):
    """Ligne de crête lissée (Catmull-Rom -> Bézier) fermée vers le bas."""
    p = points
    d = [f'M{f(p[0][0])},{f(p[0][1])}']
    for i in range(len(p) - 1):
        p0, p1, p2, p3 = p[max(i - 1, 0)], p[i], p[i + 1], p[min(i + 2, len(p) - 1)]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d.append(f'C{f(c1[0])},{f(c1[1])} {f(c2[0])},{f(c2[1])} {f(p2[0])},{f(p2[1])}')
    d.append(f'L{f(p[-1][0])},{bas} L{f(p[0][0])},{bas} Z')
    return f'<path d="{" ".join(d)}" fill="{couleur}"/>'

def crete(x, pts):
    """Hauteur d'une crête (interpolation linéaire) pour poser vigne et tour."""
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if x0 <= x <= x1: return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return pts[-1][1]

s = []
s.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" preserveAspectRatio="xMaxYMax slice">')
s.append('<defs>'
         f'<linearGradient id="ciel" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{C["ciel_haut"]}"/><stop offset="1" stop-color="{C["ciel_bas"]}"/></linearGradient>'
         '<linearGradient id="voile" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="1"/>'
         '<stop offset="0.30" stop-color="#fff" stop-opacity="0.92"/><stop offset="0.50" stop-color="#fff" stop-opacity="0"/></linearGradient>'
         '<filter id="grain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="7"/>'
         '<feColorMatrix values="0 0 0 0 0.18  0 0 0 0 0.25  0 0 0 0 0.2  0 0 0 0.07 0"/></filter>'
         '</defs>')
s.append(f'<rect width="{W}" height="{H}" fill="url(#ciel)"/>')
# soleil et nuages en pastilles
s.append(f'<circle cx="1050" cy="70" r="46" fill="{C["soleil"]}"/>')
for x, y, w in [(860, 58, 120), (905, 40, 70), (1090, 120, 140), (1130, 104, 70), (640, 90, 90)]:
    s.append(f'<rect x="{x}" y="{y}" width="{w}" height="22" rx="11" fill="{C["nuage"]}" opacity="0.9"/>')
# oiseaux
for x, y in [(700, 60), (722, 72), (745, 56)]:
    s.append(f'<path d="M{x},{y} q6,-6 12,0 q6,-6 12,0" fill="none" stroke="{C["vigne"]}" stroke-width="2" stroke-linecap="round" opacity="0.6"/>')
# plans de collines
loin = [(0, 215), (200, 200), (420, 190), (640, 175), (860, 180), (1050, 165), (1200, 175)]
s.append(colline(loin, C['loin']))
for x, r in [(560, 10), (1010, 8), (1024, 11), (1150, 9)]:
    s.append(f'<ellipse cx="{x}" cy="{f(crete(x, loin) - r * 0.6)}" rx="{r * 0.8}" ry="{r * 1.3}" fill="{C["pres"]}"/>')
milieu = [(0, 250), (260, 232), (520, 220), (700, 190), (820, 172), (950, 185), (1200, 205)]
s.append(colline(milieu, C['milieu']))
# rangs de vigne sur la colline du milieu (à droite de la tour)
for i, x in enumerate(range(880, 1200, 22)):
    y0 = crete(x, milieu) + 6
    s.append(f'<path d="M{x},{f(y0)} l-38,{f(140)}" stroke="{C["vigne"]}" stroke-width="9" stroke-linecap="round" opacity="0.85"/>')
    s.append(f'<path d="M{x},{f(y0 - 4)} v10" stroke="{C["tronc"]}" stroke-width="2.5"/>')
pres = [(0, 290), (300, 272), (560, 262), (760, 250), (980, 262), (1200, 250)]
s.append(colline(pres, C['pres']))
# tour ronde (cylindre en ruine) sur la crête du milieu
tx, tw, th = 800, 70, 124
ty = crete(tx + tw / 2, milieu) + 4
top = ty - th
s.append(f'<path d="M{tx},{f(ty)} V{f(top + 10)} l8,-6 l10,4 l9,-8 l12,5 l11,-4 l14,6 V{f(ty)} Z" fill="{C["pierre"]}"/>')
s.append(f'<path d="M{tx + tw * 0.62},{f(ty)} V{f(top + 4)} l9,-2 l{f(tw * 0.38 - 9)},4 V{f(ty)} Z" fill="{C["pierre_ombre"]}"/>')
for k in range(1, 6):                      # assises de pierre
    yy = top + 10 + k * 17
    s.append(f'<path d="M{tx},{f(yy)} q{tw / 2},6 {tw},0" fill="none" stroke="{C["pierre_ombre"]}" stroke-width="1.4" opacity="0.7"/>')
s.append(f'<rect x="{tx + 40}" y="{f(top + 26)}" width="8" height="16" rx="4" fill="{C["pierre_nuit"]}"/>')
s.append(f'<rect x="{tx + 16}" y="{f(top + 58)}" width="7" height="13" rx="3.5" fill="{C["pierre_nuit"]}"/>')
s.append(f'<path d="M{tx + 22},{f(ty)} c2,-14 10,-20 12,-34 c6,8 2,22 8,34 Z" fill="{C["arbre_clair"]}" opacity="0.9"/>')  # lierre
s.append(f'<ellipse cx="{tx + tw / 2}" cy="{f(ty)}" rx="{tw / 2 + 6}" ry="5" fill="{C["avant"]}" opacity="0.5"/>')
# grand arbre à gauche de la tour
ax, ay = 640, crete(640, milieu) + 30
s.append(f'<path d="M{ax - 6},{f(ay)} l3,-60 h7 l3,60 Z" fill="{C["tronc"]}"/>')
for dx, dy, r, c in [(-38, -78, 40, 'arbre'), (30, -84, 42, 'arbre'), (-6, -118, 48, 'arbre'),
                     (-50, -110, 30, 'arbre_clair'), (36, -128, 32, 'arbre_clair'), (0, -150, 30, 'arbre_clair')]:
    s.append(f'<circle cx="{ax + dx}" cy="{f(ay + dy)}" r="{r}" fill="{C[c]}"/>')
# premier plan et chemin qui monte vers la tour
avant = [(0, 318), (360, 300), (600, 296), (820, 290), (1200, 284)]
s.append(colline(avant, C['avant']))
s.append(f'<path d="M520,{H} C560,300 640,280 700,262 C740,250 770,240 800,{f(ty + 2)} '
         f'L806,{f(ty + 2)} C790,248 760,262 726,276 C680,294 640,312 620,{H} Z" fill="{C["chemin"]}"/>')
s.append(f'<path d="M560,{H} C600,312 650,292 700,276" fill="none" stroke="{C["chemin_bord"]}" stroke-width="3" stroke-linecap="round"/>')
# herbes hautes au premier plan
random.seed(4)
for i in range(46):
    x = 440 + i * 17 + random.uniform(-5, 5)
    y = H - random.uniform(0, 6)
    h = random.uniform(10, 22)
    s.append(f'<path d="M{f(x)},{f(y)} q{f(random.uniform(-6, 6))},{f(-h / 2)} {f(random.uniform(-8, 8))},{f(-h)}" '
             f'fill="none" stroke="{C["vigne"]}" stroke-width="2" stroke-linecap="round" opacity="0.6"/>')
s.append(f'<rect width="{W}" height="{H}" filter="url(#grain)"/>')
s.append(f'<rect width="{W}" height="{H}" fill="url(#voile)"/>')
s.append('</svg>')
open(OUT, 'w', encoding='utf-8').write('\n'.join(s) + '\n')
print(OUT, os.path.getsize(OUT), 'octets')
