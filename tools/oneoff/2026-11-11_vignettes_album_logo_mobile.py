#!/usr/bin/env python3
"""11/11/2026 — deux corrections après reprise de l'état du dev.

  1. Album « Cérémonie du 11 novembre » : ses vignettes avaient été créées carrées (outil album.py
     d'avant le correctif du 01/11, cf. 2026-11-01_galerie_ratios.py) -> vignettes au format de la photo.
  2. Vue mobile : le modèle `menu_burger` affichait encore le vieux blason (armoiries.png) au lieu du
     logo « Baigneaux » de l'en-tête ordinateur. Le modèle ET toutes les copies stockées dans les pages
     sont mis à jour (à l'affichage public, c'est la copie de la page qui est rendue, cf. docs/FORMAT.md).
"""
import sys, os, glob
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from sitelib import Page, SITE
import album
from PIL import Image

IMG = os.path.join(SITE, 'data', 'images')

# ------------------------------------------------------------------ 1. vignettes de l'album
p = Page('p342-galerie-ceremonie-du-11-novembre-novembre-2026')
n = 0
for im in p.find(lambda x: x.get('$class') == 'WsImage' and 'photo_album' in (x.get('more_classes') or '')):
    thumb, size = album.make_thumb(os.path.join(IMG, im['uploaded_image']), im['uploaded_image'][:-4])
    old = im['value']; im['value'] = thumb; im['width'], im['height'] = str(size[0]), str(size[1])
    if old != thumb and old.endswith('-v.jpg') and os.path.exists(os.path.join(IMG, old)): os.remove(os.path.join(IMG, old))
    n += 1
p.save(); print(n, 'vignettes')

# ------------------------------------------------------------------ 2. logo de la vue mobile
src = Image.open(os.path.join(IMG, 'logosite.png')).convert('RGBA')        # logo 1024x1024, fond transparent
logo = src.crop(src.getchannel('A').getbbox())
h = 120; w = round(logo.width * h / logo.height)
NOM = 'logo-baigneaux-mobile.png'
logo.resize((w, h), Image.LANCZOS).save(os.path.join(IMG, NOM), optimize=True)
dw, dh = round(w / 2), 60                                                   # affichage 60 px de haut (retina x2)
fichiers = glob.glob(f'{SITE}/pages/*.json') + glob.glob(f'{SITE}/models/menu_burger.json')
tot = 0
for f in sorted(fichiers):
    rel = os.path.relpath(f, SITE)[:-5]
    pg = Page(rel if rel.startswith('models/') else os.path.basename(rel))
    ch = 0
    for im in pg.find(lambda x: x.get('$class') == 'WsImage' and 'armoiries' in str(x.get('uploaded_image')) + str(x.get('value'))):
        im.update(value=NOM, uploaded_image=NOM, tooltip='Logo de Baigneaux', width=str(dw), height=str(dh))
        if 'original_name' in im: im['original_name'] = NOM
        ch += 1
    if ch: pg.save(); tot += ch
print(tot, 'images remplacées (modèle + copies)')
# (entrée de l'historique des versions complétée à la main : « Vue mobile : le logo de Baigneaux remplace l'ancien blason »)
