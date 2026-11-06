#!/usr/bin/env python3
"""06/11/2026 — Vignettes des cartes d'actualité de l'accueil pour la photo pleine largeur.

Depuis la refonte visuelle, l'image d'une carte occupe toute la largeur (environ 290 x 150 px).
Les cartes qui affichaient une miniature 200 x 90 ou le petit logo 90 x 90 reçoivent une vignette
580 x 300 tirée de la photo d'origine (ou le logo centré sur fond sauge pour les annonces de la mairie).
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from sitelib import Page, SITE
from PIL import Image, ImageOps

IMG = os.path.join(SITE, 'data', 'images')
W, H = 580, 300

def cover(src, fy=0.5):
    im = ImageOps.exif_transpose(Image.open(os.path.join(IMG, src))).convert('RGB')
    w, h = im.size; r = W / H
    if w / h > r:
        nw = int(h * r); x = (w - nw) // 2; im = im.crop((x, 0, x + nw, h))
    else:
        nh = int(w / r); y = int((h - nh) * fy); im = im.crop((0, y, w, y + nh))
    return im.resize((W, H), Image.LANCZOS)

def logo():
    fond = Image.new('RGB', (W, H), (230, 238, 230))
    lg = Image.open(os.path.join(IMG, 'logosite.png')).convert('RGBA'); lg.thumbnail((210, 210), Image.LANCZOS)
    fond.paste(lg, ((W - lg.width) // 2, (H - lg.height) // 2), lg); return fond

VIGNETTES = {  # titre de la carte (début) -> (fichier, image)
    'Nouvelle adresse mail': ('vignette-mairie.jpg', logo),
    'Evolution des tarifs': ('vignette-mairie.jpg', logo),
    'Début de la rénovation du cimetière': ('vignette-cimetiere-oct2026.jpg', lambda: cover('whatsapp-image-2026-10-16-at-11-11-05--3-.jpg', .1)),
    'Fête du village 2026': ('vignette-fete-village-2026.jpg', lambda: cover('fete-du-village-septembre-2026-04.jpg')),
    'Photos de la Maïade': ('vignette-maiade-2026.jpg', lambda: cover('maiade-2026-01.jpg', .45)),
}
faits = set()
h = Page('home')
for carte in h.find(lambda n: n.get('more_classes') == 'carte_actu'):
    t = Page.text(carte)
    for debut, (nom, fabrique) in VIGNETTES.items():
        if debut in t:
            if nom not in faits:
                fabrique().save(os.path.join(IMG, nom), 'JPEG', quality=82, optimize=True, progressive=True); faits.add(nom)
            img = next(n for n, _ in h.walk(carte) if n.get('$class') == 'WsImage')
            img.update(value=nom, uploaded_image=nom, width=str(W // 2), height=str(H // 2))
            if 'original_name' in img: img['original_name'] = nom
            print(debut, '->', nom)
h.save()
