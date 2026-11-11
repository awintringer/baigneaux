#!/usr/bin/env python3
"""01/11/2026 — Galeries : photos déformées dans la visionneuse (rapport largeur/hauteur faux).

Cause : la visionneuse de WebSiCo (`$Gallery`, ws_lib/ws_core/ws_jglobal.js) ne lit pas la taille
de la grande photo : elle reprend la largeur et la hauteur *affichées* de la vignette cliquée
(`img.width`, `img.height`) et agrandit la grande photo dans ce rapport. Deux modifications récentes
ont donné aux vignettes un cadre qui n'a plus la forme de la photo :
  - 28/10 (7e069cf), cartes d'événements de l'accueil : image forcée à 100 % x 260 px
    (`object-fit: contain`) -> affiches étirées en largeur ;
  - 29/10 (8960d71), albums : vignettes recadrées en carré (fichier 400x400 + `aspect-ratio: 1/1`)
    -> toutes les photos d'album écrasées en carré au clic.
Les grandes versions (<slug>-NN.jpg) ont gardé leur format d'origine ; les originaux 2000 px sont
dans l'historique git (commit 8960d71^, champ uploaded_image de l'ancienne page p325).

Correctif :
  - nouvelles vignettes au format de la photo (400 px de haut, <slug>-NN-m.jpg, nouveau nom pour
    ne pas resservir l'ancienne vignette carrée en cache), largeur/hauteur exactes dans le WsImage ;
  - grille d'album en « mur de photos » : rangées de hauteur fixe, chaque vignette à sa largeur
    naturelle (aucun recadrage) ;
  - cartes d'événements : cadre de 260 px conservé, mais l'image y est centrée à sa taille propre
    (max-width / max-height) au lieu d'être étirée.
Règle à retenir (CLAUDE.md) : une image « En galerie » ne doit jamais être recadrée ou forcée par le
CSS (object-fit, aspect-ratio, width + height fixes) : la boîte de l'<img> doit garder sa forme.
"""
import sys, os, glob, re
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from sitelib import Page, SITE
import album

IMG = os.path.join(SITE, 'data', 'images')

# ---------------------------------------------------------------- vignettes des albums
retirees = 0
for f in sorted(glob.glob(f'{SITE}/pages/p*-galerie-*.json')):
    name = os.path.basename(f)[:-5]
    if name == album.SOMMAIRE: continue
    p = Page(name)
    imgs = p.find(lambda n: n.get('$class') == 'WsImage' and 'photo_album' in (n.get('more_classes') or ''))
    for n in imgs:
        large = n['uploaded_image']
        thumb, size = album.make_thumb(os.path.join(IMG, large), large[:-4])
        old = n['value']
        n['value'] = thumb
        n['width'], n['height'] = str(size[0]), str(size[1])
        if old != thumb and old.endswith('-v.jpg') and os.path.exists(os.path.join(IMG, old)):
            os.remove(os.path.join(IMG, old)); retirees += 1
    p.save()
    print(f'{name} : {len(imgs)} vignettes')
print(retirees, 'vignettes carrées retirées')

# ---------------------------------------------------------------- CSS
cssf = os.path.join(SITE, 'css/default.css')
css = open(cssf, encoding='utf-8').read()

def bloc(media, sel, decl):
    return '@media %s {\n\t%s {\n%s\t}\n}\n' % (media, sel, ''.join(f'\t\t{d.strip()};\n' for d in decl.split(';') if d.strip()))

def remplace(media, sel, decl):
    global css
    pat = re.compile(r'@media %s \{\n\t%s \{\n[^}]*\}\n\}\n' % (re.escape(media), re.escape(sel)))
    assert len(pat.findall(css)) == 1, (media, sel)
    css = pat.sub(lambda m: bloc(media, sel, decl), css)

remplace('all', '.wscontainer.album_grille',
         'display: flex; flex-wrap: wrap; justify-content: center; align-items: flex-start; gap: 10px; padding: 4px 6px 6px; margin: 0; border-width: 0;')
remplace('all', '.album_grille .wsimage',
         'float: none !important; flex: 0 0 auto; width: auto !important; max-width: 100% !important; margin: 0 !important; padding: 0 !important;')
remplace('all', '.album_grille .wsimage img',
         'display: block; width: auto; max-width: 100%; height: 190px; border-radius: 8px; transition: transform .2s ease, box-shadow .2s ease;')
remplace('(max-width: 640px)', '.wscontainer.album_grille', 'gap: 6px;')
remplace('(max-width: 640px)', '.album_grille .wsimage img', 'height: 110px; border-radius: 4px;')
remplace('all', '.carte_evenement > .wsimage',
         'order: -1; display: flex; align-items: center; justify-content: center; height: 260px; margin: 0 0 14px !important; max-width: none !important; width: 100%; padding: 0; box-sizing: border-box; background: #e8efe9; border-radius: 10px; overflow: hidden;')
remplace('all', '.carte_evenement > .wsimage img',
         'display: block; width: auto; height: auto; max-width: 100%; max-height: 260px;')
open(cssf, 'w', encoding='utf-8').write(css)
print('css ok')
