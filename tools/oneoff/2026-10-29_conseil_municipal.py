#!/usr/bin/env python3
"""29/10/2026 — Page « Conseil municipal » (p208) : trombinoscope.

Avant : maire et adjoints dans des cadres imbriqués, conseillers en 2 colonnes de grandes cartes
(photo 150x200 à gauche, nom en haut à droite, beaucoup de vide), icônes « appareil photo »
bleues pour les élues sans photo, deux zones (colonne de droite + pleine largeur).

Après :
  - tout le contenu dans la colonne de droite, à côté du menu ;
  - deux sections : « Maire et adjoint·e·s » (3 cartes) et « Conseillers municipaux »
    (8 cartes, ordre alphabétique) ;
  - cartes verticales identiques : portrait rond, nom, fonction ; grille fluide (CSS
    `carte_elu`, voir default.css) ;
  - portraits recadrés en carré 400 px à partir des originaux 1200x1600 (les fichiers originaux
    restent référencés par `uploaded_image`, donc recadrables dans l'éditeur) ;
  - élues sans photo : silhouette neutre aux couleurs du site (`portrait-a-venir.png`) ;
  - lien vers les procès-verbaux et les commissions en bas de page.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from sitelib import Page, ent, SITE
from PIL import Image, ImageDraw

IMG = os.path.join(SITE, 'data', 'images')
URL = 'https://www.baigneaux.fr'
CR = '\r\n'
W = 'whatsapp-image-2026-01-11-at-09-58-'

# (nom affiché, fonction, original, (centre x, haut, côté) du recadrage, nouveau fichier)
def crop(face_y, side=900): return (600, face_y - int(side * .42), side)
BUREAU = [
    ('Sandrine ALLAIN', 'Maire depuis 2020', W + '58--2-.jpg', crop(714), 'portrait-sandrine-allain.jpg'),
    ('Sophie BASSAN', '1<sup>re</sup> adjointe', W + '57--2-.jpg', crop(734), 'portrait-sophie-bassan.jpg'),
    ('Christophe GUILHON', '2<sup>e</sup> adjoint', 'cg.png', (470, 200, 939), 'portrait-christophe-guilhon.jpg'),
]
CONSEIL = [
    ('Lucas BERTHOMIEU', W + '53.jpg', crop(652), 'portrait-lucas-berthomieu.jpg'),
    ('Valérie BRUNET', None, None, None),
    ('Pascale CRUCHON', W + '57.jpg', crop(693), 'portrait-pascale-cruchon.jpg'),
    ('Thierry DONVAL', W + '54--2-.jpg', crop(652), 'portrait-thierry-donval.jpg'),
    ('Magali PALACIN', None, None, None),
    ('Stéphanie PARCELLIER', W + '56--7-.jpg', crop(734), 'portrait-stephanie-parcellier.jpg'),
    ('Sandrine PONDARRE', W + '56--2-.jpg', crop(734), 'portrait-sandrine-pondarre.jpg'),
    ('Adrien WINTRINGER', W + '56--1-.jpg', crop(693), 'portrait-adrien-wintringer.jpg'),
]
PLACEHOLDER = 'portrait-a-venir.png'
SIZE = 400

# ---------------------------------------------------------------- images
def make_portrait(orig, box, out):
    cx, top, s = box
    im = Image.open(os.path.join(IMG, orig)).convert('RGB')
    top = max(0, min(top, im.size[1] - s)); left = max(0, min(cx - s // 2, im.size[0] - s))
    im.crop((left, top, left + s, top + s)).resize((SIZE, SIZE), Image.LANCZOS) \
      .save(os.path.join(IMG, out), 'JPEG', quality=82, optimize=True, progressive=True)

def make_placeholder(out):
    k = 4; n = SIZE * k
    im = Image.new('RGB', (n, n), '#e7f1e8'); d = ImageDraw.Draw(im)
    c = '#b9d6c0'
    d.ellipse((n * .34, n * .2, n * .66, n * .52), fill=c)                 # tête
    d.ellipse((n * .16, n * .58, n * .84, n * 1.18), fill=c)               # épaules
    im.resize((SIZE, SIZE), Image.LANCZOS).save(os.path.join(IMG, out), 'PNG', optimize=True)

for _, _, orig, box, out in BUREAU: make_portrait(orig, box, out)
for _, orig, box, out in CONSEIL:
    if orig: make_portrait(orig, box, out)
make_placeholder(PLACEHOLDER)

# ---------------------------------------------------------------- page
p = Page('p208-conseil-municipal')
by_id = {n['id']: n for n, _ in p.walk() if 'id' in n}
right_col = by_id['Z2069cafaed6feb6']          # colonne de droite (burger, titre, maire, adjoints)
body = by_id['Z582b7f3ac75cd']                  # BodyHome : [rangée menu/contenu, conseillers]
sec_maire, sec_adj, sec_cons = by_id['Z1869cafc5269c58'], by_id['Z515b6ad572ae1c0'], by_id['Z515b6ad59d104e3']
tpl_title = by_id['Y515b6ad487aecd2']           # WssTitle FORMALITES
tpl_row = by_id['Z1869caff44edeba']             # rangée H (2 cellules)
tpl_card = by_id['Z1869caff48d0365']            # carte bloc_conseil_perso
tpl_img, tpl_txt = by_id['Y1869caff4f0d0c5'], by_id['Y515b6ad45dc6581']

def image(name, file, orig):
    img = Page.clone(tpl_img)
    alt = 'Portrait de ' + name.split()[0] + ' ' + name.split()[1].capitalize() if file else \
          'Pas encore de photo de ' + name.split()[0] + ' ' + name.split()[1].capitalize()
    img.update({'value': file or PLACEHOLDER, 'tooltip': alt,
                'uploaded_image': orig or PLACEHOLDER, 'original_name': orig or PLACEHOLDER,
                'width': '200', 'height': '200', 'notFlexible': '0', 'keep_format': '0',
                'in_gallery': '0', 'user_style': None, 'more_classes': '', 'embedded_css_rules': ''})
    return img

def card(name, role, file, orig):
    c = Page.clone(tpl_card)
    t = Page.clone(tpl_txt)
    t['value'] = f'<p><strong>{ent(name)}</strong></p>' + (f'{CR}<p>{role}</p>' if role else '')
    t['user_style'] = 'Texte_normal_align_gauche'
    c.update({'contents': [image(name, file, orig), t], 'properties': 8192,
              'user_style': 'bloc_conseil_perso', 'more_classes': 'carte_elu', 'embedded_css_rules': ''})
    Page.reindex(c)
    return c

def row(cards):
    r = Page.clone(tpl_row)
    cell_tpl = r['contents'][0]
    cells = []
    for cd in cards:
        cell = Page.clone(cell_tpl); cell['contents'] = [cd]; cell['embedded_css_rules'] = ''
        Page.reindex(cell); cells.append(cell)
    r['contents'] = cells; Page.reindex(r)
    return r

def section(title, cards, extra=()):
    s = Page.clone(sec_cons)                     # Subdivision, ids neufs
    t = Page.clone(tpl_title); t['value'] = title
    s['contents'] = [t, row(cards), *extra]; Page.reindex(s)
    return s

bureau = [card(n, r, f, o) for n, r, o, _, f in BUREAU]
conseil = [card(n, '', f, o) for n, o, _, f in CONSEIL]

voir = Page.clone(tpl_txt)
voir['user_style'] = 'Texte_normal_align_gauche'
voir['more_classes'] = 'conseil_voir_aussi'
voir['value'] = (f'<p>{ent("Voir aussi : ")}<a href="{URL}/pv-conseil.html">{ent("procès-verbaux des conseils")}</a>'
                 f' &middot; <a href="{URL}/commissions.html">{ent("commissions communales")}</a></p>')

new_sections = [section('Maire et adjoint·e·s', bureau),
                section('Conseillers municipaux', conseil, [voir])]

# colonne de droite : burger + bloc titre, puis les deux sections
keep = [n for n in right_col['contents'] if n is not sec_maire and n is not sec_adj]
right_col['contents'] = keep + new_sections
Page.reindex(right_col)
p.remove(sec_cons)
p.save()

# anciennes vignettes 150x200 : plus référencées, supprimées par la purge WebSiCo à l'import
print('ok :', len(bureau) + len(conseil), 'cartes')
