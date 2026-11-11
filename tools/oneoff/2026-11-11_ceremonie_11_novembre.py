#!/usr/bin/env python3
"""11/11/2026 — Cérémonie du 11 novembre.

  - album photo : créé avant ce script avec
      python3 tools/album.py PHOTOS --titre "Cérémonie du 11 novembre" --date "11 novembre 2026" \
          --couverture IMG_20261111_111152.jpg      (page p342, 14 photos)
  - accueil : nouvelle carte d'actu en tête (Vie communale, lien direct vers l'album, comme les
    actus « Fête du village » et « Maïade » : pas de fiche sur la page Actualités) ; la plus ancienne
    carte (27 juil., collecte de dons) sort des « 10 dernières », sa fiche reste sur Actualités ;
    les cartes d'événements du 8 novembre (×2) et du 11 novembre sont retirées ;
  - page Évènements (p319) : les trois rubriques correspondantes (8 nov ×2, 11 nov) sont retirées ;
  - page « Historiques des versions » (p327) : entrée du 11 novembre.

Usage : python3 tools/oneoff/2026-11-11_ceremonie_11_novembre.py DOSSIER_PHOTOS
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from sitelib import Page, set_text, SITE
from PIL import Image, ImageOps

PHOTOS = sys.argv[1]
URL = 'https://www.baigneaux.fr'
ALBUM = f'{URL}/galerie-ceremonie-du-11-novembre-novembre-2026.html'
CR = '\r\n'

# vignette 400x180 de la carte (bande du haut de la photo d'ensemble)
vign = 'vignette-ceremonie-11-novembre-2026.jpg'
im = ImageOps.exif_transpose(Image.open(os.path.join(PHOTOS, 'IMG_20261111_111152.jpg'))).convert('RGB')
w, h = im.size; nh = int(round(w / (400 / 180))); y0 = int(h * .18)
im.crop((0, y0, w, y0 + nh)).resize((400, 180), Image.LANCZOS).save(
    os.path.join(SITE, 'data', 'images', vign), 'JPEG', quality=80, optimize=True, progressive=True)

# ------------------------------------------------------------------ accueil
home = Page('home')
cartes = home.find(lambda n: n.get('more_classes') == 'carte_actu')
enveloppe = home.parents(cartes[0])[-1]; rail = home.parents(cartes[0])[-2]
neuve = home.clone(enveloppe)
carte = next(n for n, _ in home.walk(neuve) if n.get('more_classes') == 'carte_actu')
img = next(n for n, _ in home.walk(carte) if n.get('$class') == 'WsImage')
img.update(tooltip="Cérémonie du 11 novembre devant le monument aux morts", uploaded_image=vign, value=vign)
if 'original_name' in img: img['original_name'] = vign
ccat, cdate, ctitre, ctexte = [n for n, _ in home.walk(carte) if n.get('$class') == 'WsTextarea']
ccat['user_style'] = 'bulle_actu_categorie_vie_communale'; set_text(ccat, 'value', '<p>Vie communale</p>')
set_text(cdate, 'value', '<p>11 nov 2026</p>')
set_text(ctitre, 'value', '<p>C&eacute;r&eacute;monie du 11 novembre</p>')
set_text(ctexte, 'value', CR.join([
    "<p>Retrouvez les photos de la c&eacute;r&eacute;monie de comm&eacute;moration de l'Armistice.</p>",
    '<p>&nbsp;</p>',
    f'<p><a href="{ALBUM}">Lire la suite&nbsp;-&gt;</a></p>']))
home.insert(rail, neuve, 0)
anciennes = [c for c in rail['contents'] if c is not neuve]
home.remove(anciennes[-1])
assert len(rail['contents']) == 10

evts = home.find(lambda n: n.get('more_classes') == 'carte_evenement')
a_retirer = [e for e in evts if any(home.text(x).strip().startswith(('8 NOV', '11 NOV'))
                                    for x, _ in home.walk(e) if x.get('$class') == 'WsTextarea')]
assert len(a_retirer) == 3, len(a_retirer)
for e in a_retirer: home.remove(e)
home.save()

# ------------------------------------------------------------------ page Évènements
ev = Page('p319-evenements-festivites')
sections = [n for n in ev.find(lambda n: n.get('user_style') == 'Subdivision' and n.get('$class') == 'WsContainer')
            if any(ev.text(x).startswith(('Marché des producteurs - 8 novembre', 'Bénédiction des tombes - 8 novembre',
                                          "Commémoration de l'Armistice - 11 novembre"))
                   for x, _ in ev.walk(n) if x.get('$class') == 'WssTitle')]
# ne garder que les conteneurs les plus internes (un seul titre)
sections = [s for s in sections if sum(1 for x, _ in ev.walk(s) if x.get('$class') == 'WssTitle') == 1]
assert len(sections) == 3, len(sections)
for s in sections: ev.remove(s)
ev.save()

# ------------------------------------------------------------------ historique des versions
v = Page('p327-historique-modifications')
(t,) = v.find(lambda n: n.get('$class') == 'WssTitle' and v.text(n) == '6 novembre 2026')
bloc = v.parents(t)[-1]
nouveau = v.clone(bloc)
nt = next(n for n, _ in v.walk(nouveau) if n.get('$class') == 'WssTitle'); nt['value'] = '11 novembre 2026'
nx = next(n for n, _ in v.walk(nouveau) if n.get('$class') == 'WsTextarea')
set_text(nx, 'value', CR.join([
    '<p>- Galerie&nbsp;: nouvel album &laquo;&nbsp;C&eacute;r&eacute;monie du 11 novembre&nbsp;&raquo; (14 photos) et actualit&eacute; correspondante sur l\'accueil</p>',
    '<p>- &Eacute;v&egrave;nements&nbsp;: retrait des &eacute;v&egrave;nements pass&eacute;s du 8 et du 11 novembre</p>']))
par = v.parents(bloc)[-1]
v.insert(par, nouveau, par['contents'].index(bloc))
v.save()
print('ok')
