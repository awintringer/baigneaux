#!/usr/bin/env python3
"""06/11/2026 — Actualité « Travaux et entretien de notre commune ».

  - page Actualités (p304) : nouvelle fiche en tête de « Novembre 2026 » (ancre #travaux06112026),
    avec 3 photos (poutre de l'ancienne salle des fêtes, désherbage du cimetière, jeu pour enfants
    du city stade) ;
  - accueil : nouvelle carte en tête (catégorie Mairie, vignette 400x180) ; la plus ancienne carte
    (25 juil., feux de forêt) sort des « 10 dernières » ; sa fiche reste sur la page Actualités ;
  - page « Historiques des versions » (p327) : entrée du 6 novembre.

Photos : copies de travail dans PHOTOS (3 fichiers poutre/cimetiere/jeu .jpg), recadrées en 3:4 ;
l'original recadré est `uploaded_image`, la variante affichée (`-m`, 2x) est `value`.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from sitelib import Page, ent, set_text, SITE
from PIL import Image, ImageOps

PHOTOS = sys.argv[1] if len(sys.argv) > 1 else '.'
IMG = os.path.join(SITE, 'data', 'images')
URL = 'https://www.baigneaux.fr'
ANCRE = 'travaux06112026'
TITRE = 'Travaux et entretien de notre commune'
CR = '\r\n'

def load(name): return ImageOps.exif_transpose(Image.open(os.path.join(PHOTOS, name))).convert('RGB')
def save(im, name, q):
    im.save(os.path.join(IMG, name), 'JPEG', quality=q, optimize=True, progressive=True); return name
def crop(im, ratio, y0):                      # recadrage pleine largeur, `y0` = haut en pixels
    w, h = im.size; nh = int(round(w / ratio)); y0 = max(0, min(y0, h - nh)); return im.crop((0, y0, w, y0 + nh))

# (fichier, haut du recadrage 3:4, nom, texte alternatif)
PHOTOS_FICHE = [
    ('poutre.jpg', 0, 'travaux-novembre-2026-01', "Poutre descellée de l'ancienne salle des fêtes"),
    ('cimetiere.jpg', 230, 'travaux-novembre-2026-02', 'Désherbage des allées du cimetière'),
    ('jeu.jpg', 380, 'travaux-novembre-2026-03', 'Jeu pour enfants du city stade après réparation'),
]
fiche_imgs = []
for f, y0, nom, alt in PHOTOS_FICHE:
    c = crop(load(f), 3 / 4, y0)
    c.thumbnail((1200, 1600), Image.LANCZOS)
    big = save(c, nom + '.jpg', 84)
    med = save(c.resize((600, 800), Image.LANCZOS), nom + '-m.jpg', 80)
    fiche_imgs.append((big, med, alt))
vign = 'vignette-travaux-novembre-2026.jpg'
c = crop(load('cimetiere.jpg'), 400 / 180, int(2048 * .14))
save(c.resize((400, 180), Image.LANCZOS), vign, 80)

# ------------------------------------------------------------------ page Actualités
a = Page('p304-actualites')
(h_nov,) = a.find(lambda n: n.get('$class') == 'WssTitle' and a.text(n) == 'Novembre 2026')
(modele,) = a.find(lambda n: n.get('id') == 'Z916aeb7780f1fb2')                 # fiche du 4 novembre
(photos_modele,) = a.find(lambda n: n.get('id') == 'Z436ad37171a718c')          # rangée de photos (cimetière)
fiche = a.clone(modele)
textes = [n for n, _ in a.walk(fiche) if n.get('$class') == 'WsTextarea']
cat, date, corps, vide = textes
set_text(cat, 'value', f'<p id="{ANCRE}">Mairie</p>')
set_text(date, 'value', '<p>6 novembre 2026</p>')
titre = next(n for n, _ in a.walk(fiche) if n.get('$class') == 'WssTitle')
titre['value'] = TITRE
p = lambda t: f'<p>{t}</p>'
set_text(corps, 'value', CR.join([
    p('Le point sur les interventions r&eacute;alis&eacute;es ou en cours dans la commune&nbsp;:'),
    p('&nbsp;'),
    p('<strong>Ancienne salle des f&ecirc;tes</strong>&nbsp;: une poutre descell&eacute;e est en cours de r&eacute;paration par l\'EURL Bois &agrave; Vivre.'),
    p('&nbsp;'),
    p('<strong>Cimeti&egrave;re</strong>&nbsp;: la 2e phase de d&eacute;sherbage a &eacute;t&eacute; effectu&eacute;e. L\'ensemencement aura lieu jeudi 12 novembre.'),
    p('&nbsp;'),
    p('<strong>City stade</strong>&nbsp;: les montants rouill&eacute;s ont &eacute;t&eacute; repeints et le jeu pour enfants endommag&eacute; (poign&eacute;e disparue) a &eacute;t&eacute; r&eacute;par&eacute;. '
      'La pelouse a &eacute;t&eacute; tondue et les haies qui entourent le city stade sont en cours d\'&eacute;lagage.'),
]))
rangee = a.clone(photos_modele)
cols = rangee['contents']
del cols[3:]
for col, (big, med, alt) in zip(cols, fiche_imgs):
    im = next(n for n, _ in a.walk(col) if n.get('$class') == 'WsImage')
    im.update(tooltip=alt, uploaded_image=big, value=med, width='300', height='400')
    if 'original_name' in im: im['original_name'] = big
    col['embedded_css_rules'] = '.id_%s {\r\n\twidth: 33.3%%;\r\n}\r' % col['id']
    im['embedded_css_rules'] = '.id_%s {\r\n\tmargin-left: auto;\r\n\tmargin-right: auto;\r\n}\r' % im['id']
a.reindex(rangee)
# la fiche : en-tête, titre, texte, [photos], ligne vide
fiche['contents'].insert(3, rangee); a.reindex(fiche)
(parent,) = [a.parents(h_nov)[-1]]
a.insert(parent, fiche, parent['contents'].index(h_nov) + 1)
a.save()

# ------------------------------------------------------------------ accueil
h = Page('home')
cartes = h.find(lambda n: n.get('more_classes') == 'carte_actu')
enveloppe = h.parents(cartes[0])[-1]; rail = h.parents(cartes[0])[-2]
neuve = h.clone(enveloppe)
carte = next(n for n, _ in h.walk(neuve) if n.get('more_classes') == 'carte_actu')
img = next(n for n, _ in h.walk(carte) if n.get('$class') == 'WsImage')
img.update(tooltip='Désherbage des allées du cimetière', uploaded_image=vign, value=vign)
if 'original_name' in img: img['original_name'] = vign
tx = [n for n, _ in h.walk(carte) if n.get('$class') == 'WsTextarea']
ccat, cdate, ctitre, ctexte = tx
ccat['user_style'] = 'bulle_actu_categorie_mairie'; set_text(ccat, 'value', '<p>Mairie</p>')
set_text(cdate, 'value', '<p>6 nov 2026</p>')
set_text(ctitre, 'value', '<p>Travaux et entretien de notre commune</p>')
set_text(ctexte, 'value', CR.join([
    '<p>Poutre de l\'ancienne salle des f&ecirc;tes en cours de r&eacute;paration, d&eacute;sherbage du cimeti&egrave;re, entretien du city stade&nbsp;: le point sur les travaux.</p>',
    '<p>&nbsp;</p>',
    f'<p><a href="{URL}/actualites.html#{ANCRE}">Lire la suite -&gt;</a></p>']))
h.insert(rail, neuve, 0)
anciennes = [c for c in rail['contents'] if c is not neuve]
h.remove(anciennes[-1])
assert len(rail['contents']) == 10
h.save()

# ------------------------------------------------------------------ historique des versions
v = Page('p327-historique-modifications')
(t28,) = v.find(lambda n: n.get('$class') == 'WssTitle' and v.text(n) == '28 octobre 2026')
bloc = v.parents(t28)[-1]
nouveau = v.clone(bloc)
nt = next(n for n, _ in v.walk(nouveau) if n.get('$class') == 'WssTitle'); nt['value'] = '6 novembre 2026'
nx = next(n for n, _ in v.walk(nouveau) if n.get('$class') == 'WsTextarea')
set_text(nx, 'value', CR.join([
    '<p>- Actualit&eacute;s&nbsp;: travaux et entretien de notre commune (poutre de l\'ancienne salle des f&ecirc;tes, cimeti&egrave;re, city stade)</p>',
    '<p>- Mise &agrave; jour des m&eacute;decins de garde (novembre 2026)</p>']))
par = v.parents(bloc)[-1]
v.insert(par, nouveau, par['contents'].index(bloc))
v.save()
print('ok')
