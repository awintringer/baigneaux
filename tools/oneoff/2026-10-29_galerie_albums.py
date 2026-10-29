#!/usr/bin/env python3
"""29/10/2026 — Galerie « Notre village en images » (p325) découpée en albums.

Avant : 8 événements et 66 photos sur une seule page, vignettes de tailles disparates.
Après :
  - p325 devient un sommaire : une carte par album (couverture, titre, date, nombre de photos),
    du plus récent au plus ancien ;
  - une page par album (créée par tools/album.py), vignettes carrées 400 px, photo en grand
    (1600 px max) au clic, navigation par flèches dans l'album ;
  - les liens de l'accueil, des actualités et du modèle Bulle_actu_petite vers
    galerie-evenements.html#<ancre> pointent maintenant vers la page de l'album ;
  - les anciennes images de la galerie, plus référencées nulle part, sont retirées du dépôt
    (WebSiCo les purge de toute façon à l'import).
"""
import sys, os, re, glob, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from sitelib import Page, ent, SITE
import album

IMG = os.path.join(SITE, 'data', 'images')

# Albums de la page actuelle, dans l'ordre affiché (plus récent d'abord) :
# (début du titre actuel, titre, date, ancienne ancre[, adresse, nom court si le titre dépasse 45 caractères])
ALBUMS = [
    ('Fête du village', 'Fête du village', '20 septembre 2026', 'fetevillage2026'),
    ('Maïade', 'Maïade 2026', '', 'maiade2026'),
    ('Soirée dansante', 'Soirée dansante', '19 septembre 2026', 'soiree_20260919'),
    ('Marché des producteurs - 13', 'Marché des producteurs', '13 septembre 2026', None),
    ('Fête des voisins', 'Fête des voisins 2026', '', 'fetevoisins2026'),
    ('Marché des producteurs et vide', 'Marché des producteurs et vide-grenier baigneaudais', '7 juin 2026',
     'marche_producteurs_20260607', 'marche-et-vide-grenier-juin-2026', 'Marché et vide-grenier baigneaudais'),
    ('Journée Citoyenne', 'Journée citoyenne', '10 mai 2026', None),
    ('Chasse aux Oeufs', 'Chasse aux œufs de Pâques', '6 avril 2026', None),
]

som = Page(album.SOMMAIRE)
col, bloc_titre = album.content_column(som)
ps = som.parents(col); rangee, body = ps[-1], ps[-2]          # rangée menu | contenu, BodyHome
apres = body['contents'][body['contents'].index(rangee) + 1:]   # albums en pleine largeur, sous la rangée

# ---------------------------------------------------------------- relevé des albums actuels
found = {}
old_files = set()
for sub in col['contents'] + apres:
    titres = [n for n, _ in Page._walk_static(sub) if n.get('user_style') == 'Texte_important_centre']
    imgs = [n for n, _ in Page._walk_static(sub) if n['$class'] == 'WsImage']
    if not titres or not imgs: continue
    label = Page.text(titres[0])
    key = next(a for a in ALBUMS if label.startswith(a[0]))
    found[key[1]] = [os.path.join(IMG, n['uploaded_image']) for n in imgs]
    old_files.update(n['uploaded_image'] for n in imgs); old_files.update(n['value'] for n in imgs)
assert len(found) == len(ALBUMS) and sum(map(len, found.values())) == 66, {k: len(v) for k, v in found.items()}

# ---------------------------------------------------------------- sommaire vide
intro = album.textarea('<p>' + ent('Les temps forts de la vie du village en photos. Choisissez un album '
                                   'pour voir toutes ses photos.') + '</p>', classes='albums_intro')
grille = album.container([], classes='albums_grille')
section = album.container([intro, grille]); section['user_style'] = 'Subdivision'
col['contents'] = [bloc_titre, section]
Page.reindex(col)
for sub in apres: body['contents'].remove(sub)
Page.reindex(body)
som.save()

# ---------------------------------------------------------------- albums (plus ancien d'abord, insérés en tête)
urls = {}
for _, titre, date, anchor, *court in reversed(ALBUMS):
    slug, nom = court or (None, None)
    pid, url = album.ajouter_album(found[titre], titre, date, slug=slug, nom=nom)
    urls[titre] = url
    print(f'{pid} {url} ({len(found[titre])} photos)')

# ---------------------------------------------------------------- liens entrants vers les anciennes ancres
redirect = {a[3]: urls[a[1]] for a in ALBUMS if a[3]}
for f in glob.glob(f'{SITE}/pages/*.json') + glob.glob(f'{SITE}/models/*.json'):
    txt = open(f, encoding='utf-8').read()
    new = re.sub(r'galerie-evenements\.html#(\w+)', lambda m: redirect.get(m.group(1), m.group(0)), txt)
    if new != txt:
        open(f, 'w', encoding='utf-8').write(new); print('liens mis à jour :', os.path.basename(f))

# ---------------------------------------------------------------- ménage des anciennes images
refs = ''.join(open(f, encoding='utf-8').read() for f in [f for f in glob.glob(f'{SITE}/**/*.json', recursive=True) if not f.endswith('zipmeta.json')]
               + glob.glob(f'{SITE}/css/*.css'))
gone = [f for f in sorted(old_files) if f not in refs and os.path.exists(os.path.join(IMG, f))]
for f in gone: os.remove(os.path.join(IMG, f))
print(len(gone), 'anciennes images retirées')

# ---------------------------------------------------------------- styles (un bloc @media par règle, cf. check_css.py)
RULES = [
    ('all', '.wscontainer.albums_grille', 'display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 18px; padding: 4px 6px 14px; margin: 0; border-width: 0;'),
    ('all', '.wscontainer.carte_album', 'display: block; height: 100%; box-sizing: border-box; overflow: hidden; padding: 0 !important; margin: 0 !important; background: #ffffff; border: 1px solid #cfe3d4; border-radius: 14px; box-shadow: 0 3px 10px rgba(47, 94, 62, 0.12); color: inherit; text-decoration: none; transition: box-shadow .2s ease, transform .2s ease;'),
    ('(hover: hover)', '.wscontainer.carte_album:hover', 'transform: translateY(-3px); box-shadow: 0 10px 22px rgba(47, 94, 62, 0.2);'),
    ('all', '.carte_album .wsimage', 'float: none !important; width: 100% !important; max-width: none !important; margin: 0 !important; padding: 0 !important;'),
    ('all', '.carte_album .wsimage img', 'display: block; width: 100%; height: auto; aspect-ratio: 4 / 3; object-fit: cover;'),
    ('all', '.carte_album .wstextarea', 'float: none; font-size: 1.1em; line-height: 1.35; text-align: left; padding: 12px 14px 14px; margin: 0;'),
    ('all', '.carte_album .wstextarea p', 'margin: 0;'),
    ('all', '.carte_album .wstextarea strong', 'font-family: Manrope, Arial, sans-serif; font-weight: 700; font-size: 1.05em; color: #2f5e3e;'),
    ('all', '.carte_album .wstextarea p + p', 'margin-top: 4px; font-size: 0.88em; color: #4d6b56;'),
    ('all', '.wstextarea.albums_intro', 'float: none; font-size: 1.15em; text-align: center; margin: 6px 10px 18px;'),
    ('all', '.wscontainer.album_grille', 'display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 10px; padding: 4px 6px 6px; margin: 0; border-width: 0;'),
    ('all', '.album_grille .wsimage', 'float: none !important; width: 100% !important; max-width: none !important; margin: 0 !important; padding: 0 !important;'),
    ('all', '.album_grille .wsimage img', 'display: block; width: 100%; height: auto; aspect-ratio: 1 / 1; object-fit: cover; border-radius: 8px; transition: transform .2s ease, box-shadow .2s ease;'),
    ('(hover: hover)', '.album_grille .wsimage a:hover img', 'transform: scale(1.03); box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);'),
    ('all', '.wstextarea.album_nav', 'float: none; font-size: 1.25em; margin: 6px 8px 4px;'),
    ('all', '.wstextarea.album_nav a', 'color: #2f5e3e; font-weight: 600; text-decoration: none;'),
    ('all', '.wstextarea.album_nav a:hover', 'text-decoration: underline;'),
    ('all', '.album_nav .album_infos', 'color: #4d6b56; font-weight: normal;'),
    ('all', '.wstextarea.album_aide', 'float: none; font-size: 1.1em; color: #4d6b56; margin: 0 8px 12px;'),
    ('all', '.wstextarea.album_nav_bas', 'margin-top: 18px;'),
    ('(max-width: 640px)', '.wscontainer.albums_grille', 'grid-template-columns: repeat(2, 1fr); gap: 10px; padding: 2px 0 10px;'),
    ('(max-width: 640px)', '.carte_album .wstextarea', 'font-size: 0.95em; padding: 8px 10px 10px;'),
    ('(max-width: 640px)', '.wscontainer.album_grille', 'grid-template-columns: repeat(3, 1fr); gap: 6px;'),
    ('(max-width: 640px)', '.album_grille .wsimage img', 'border-radius: 4px;'),
]
cssf = os.path.join(SITE, 'css/default.css')
css = open(cssf, encoding='utf-8').read()
if '.albums_grille' not in css:
    css = css.rstrip('\n') + '\n' + ''.join(
        '@media %s {\n\t%s {\n%s\t}\n}\n' % (m, sel, ''.join(f'\t\t{d.strip()};\n' for d in decl.split(';') if d.strip()))
        for m, sel, decl in RULES)
    open(cssf, 'w', encoding='utf-8').write(css)
print('css ok')
