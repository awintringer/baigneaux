#!/usr/bin/env python3
"""Ajoute un album photo à la galerie « Notre village en images » (p325).

    python3 tools/album.py DOSSIER --titre "Fête du village" --date "20 septembre 2026"
                           [--couverture IMG_1234.jpg] [--position 0]

Pour chaque photo du dossier (ordre alphabétique, donc chronologique pour les noms WhatsApp) :
  - grande version (1600 px max, rotation EXIF appliquée) : ouverte en plein écran au clic ;
  - vignette carrée 400 px, affichée dans la grille de l'album.
Puis :
  - crée la page de l'album (copie de la structure de la galerie : en-tête, menu, fil
    d'Ariane, pied), rangée sous « Notre village en images » dans le plan du site (fil d'Ariane
    correct, mais pas d'entrée dans le menu, qui s'arrête au 2e niveau) ;
  - ajoute sa carte (couverture 4:3, titre, date, nombre de photos) au sommaire de la galerie,
    en tête par défaut (--position N pour l'insérer ailleurs, 0 = première).

Les fichiers sont nommés d'après l'album : <slug>-01.jpg (grande), <slug>-01-v.jpg (vignette),
<slug>-couverture.jpg. Le script refuse un album dont la page existe déjà.
Ensuite : vérification locale, build, import sur le dev (voir CLAUDE.md).
"""
import sys, os, re, json, glob, copy, time, unicodedata, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sitelib import Page, new_id, set_text, ent, SITE
from PIL import Image, ImageOps

SOMMAIRE = 'p325-galerie-evenements'
SOMMAIRE_URL = 'galerie-evenements.html'
IMG = os.path.join(SITE, 'data', 'images')
GRANDE, VIGNETTE, COUV = 1600, 400, (600, 450)
EXTS = ('.jpg', '.jpeg', '.png', '.webp')
CR = '\r\n'
NOW = int(time.time())

# ---------------------------------------------------------------- utilitaires
def slugify(s):
    s = s.replace('œ', 'oe').replace('Œ', 'Oe').replace('æ', 'ae').replace('Æ', 'Ae')
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')

def _load(path):
    im = ImageOps.exif_transpose(Image.open(path))
    return im.convert('RGB')

def _crop(im, ratio):
    """Recadrage au rapport largeur/hauteur demandé ; en portrait, on garde plutôt le haut
    (les visages), en paysage on centre."""
    w, h = im.size
    if w / h > ratio:
        nw = int(h * ratio); x = (w - nw) // 2
        return im.crop((x, 0, x + nw, h))
    nh = int(w / ratio); y = int((h - nh) * (0.35 if h > w else 0.5))
    return im.crop((0, y, w, y + nh))

def _save(im, name, quality):
    im.save(os.path.join(IMG, name), 'JPEG', quality=quality, optimize=True, progressive=True)
    return name

def make_images(src, base, n):
    im = _load(src)
    big = im.copy(); big.thumbnail((GRANDE, GRANDE), Image.LANCZOS)
    large = _save(big, f'{base}-{n:02d}.jpg', 82)
    thumb = _save(_crop(im, 1).resize((VIGNETTE, VIGNETTE), Image.LANCZOS), f'{base}-{n:02d}-v.jpg', 78)
    return large, thumb

def make_cover(src, base):
    return _save(_crop(_load(src), COUV[0] / COUV[1]).resize(COUV, Image.LANCZOS), f'{base}-couverture.jpg', 76)

# ---------------------------------------------------------------- éléments WebSiCo
def _base(cls, props, style=None, classes='', **extra):
    n = {'$class': cls}; n.update(extra)
    n.update({'id': new_id('Y' if cls != 'WsContainer' else 'Z'), 'properties': props,
              'owner': {'$owner': 'R'}, 'index': 0, 'user_style': style, 'more_classes': classes,
              'embedded_css_rules': ''})
    return n

def container(contents, classes='', href=''):
    n = _base('WsContainer', 8192, 0, classes, valign=None, model_id=0, contents=contents, href=href)
    Page.reindex(n); return n

def textarea(html, style='Texte_normal_align_gauche', classes=''):
    n = _base('WsTextarea', 264192, style, classes, value=None)
    set_text(n, 'value', html); return n

def image(value, large, alt, size, gallery=True, classes=''):
    return _base('WsImage', 266240, None, classes, caption='', href='', tooltip=alt,
                 original_name=large, in_gallery='1' if gallery else '0', uploaded_image=large,
                 keep_format='0', width=str(size[0]), height=str(size[1]), notFlexible='0', value=value)

def carte(titre, date, nb, url, cover, slug):
    infos = ' &middot; '.join(x for x in (ent(date), f'{nb} photo{"s" if nb > 1 else ""}') if x)
    return container([
        image(cover, cover, f'{titre} : photo de couverture', COUV, gallery=False),
        textarea(f'<p><strong>{ent(titre)}</strong></p>{CR}<p>{infos}</p>'),
    ], classes='carte_album', href=url)

# ---------------------------------------------------------------- tables du site
def _json(rel):
    return json.load(open(os.path.join(SITE, rel), encoding='utf-8'))

def _save_json(obj, rel):
    with open(os.path.join(SITE, rel), 'w', encoding='utf-8') as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1); fh.write('\n')

def next_page_id():
    st = _json('tables/ws_system.6.1.json')
    used = {os.path.basename(f).split('-')[0] for f in glob.glob(f'{SITE}/pages/*.json')}
    n = int(st['row'][1]) + 1
    while f'p{n}' in used: n += 1
    st['row'][1] = str(n); _save_json(st, 'tables/ws_system.6.1.json')
    return f'p{n}'

def register(pid, path):
    """Plan du site (sous la galerie, albums les plus récents d'abord) et ordre du dump."""
    mp = _json('tables/ws_map.fr.json'); entries = mp['row'][1]['$php']
    ids = [dict(e['$arr'])['id'] for e in entries]
    if pid not in ids:
        entries.insert(ids.index(SOMMAIRE.split('-')[0]) + 1, {'$arr': [['id', pid], ['category', 'p325']]})
        _save_json(mp, 'tables/ws_map.fr.json')
    lay = _json('layout.json'); files = [e.get('file') for e in lay]
    rel = 'pages/' + os.path.basename(path)
    if rel not in files:
        lay.insert(files.index(f'pages/{SOMMAIRE}.json') + 1, {'file': rel}); _save_json(lay, 'layout.json')

# ---------------------------------------------------------------- pages
def content_column(page):
    """Colonne de contenu (à droite du menu) : parent du bloc qui porte le titre .Title."""
    t = page.find(lambda n: n.get('$class') == 'WssTitle' and n.get('user_style') == 'Title')[0]
    ps = page.parents(t)
    return ps[-2], ps[-1]                       # colonne, bloc titre

def make_album_page(pid, slug, titre, date, nodes, nom=None):
    src = Page(SOMMAIRE)
    data = copy.deepcopy(src.data)
    root = Page.clone(data['row'][-1]['$php']); root['id'] = pid
    data['row'][-1]['$php'] = root
    url_id = f'galerie-{slug}'
    nom = nom or titre                            # nom de page (fil d'Ariane) : 45 caractères max en base
    if len(nom) > 45: raise SystemExit(f'nom de page trop long ({len(nom)} > 45) : {nom!r} ; utiliser --nom')
    complet = titre if not date else f'{titre} – {date}'
    root.update({'title': '', 'url_id': url_id, 'name': nom, 'date': NOW, 'save_number': 1,
                 'description': ent(f'Photos : {complet}'), 'no_robots': '0'})
    data['row'][:-1] = [pid, 'fr', url_id, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(NOW)), nom, data['row'][5]]
    tmp = Page.__new__(Page); tmp.data, tmp.root = data, root
    col, bloc_titre = content_column(tmp)
    t = next(n for n, _ in Page._walk_static(bloc_titre) if n.get('$class') == 'WssTitle')
    t['value'] = titre                          # WssTitle : texte brut (échappé par WebSiCo)
    col['contents'] = [bloc_titre, container(nodes, classes='')]
    col['contents'][1]['user_style'] = 'Subdivision'
    Page.reindex(col)
    path = os.path.join(SITE, 'pages', f'{pid}-{url_id}.json')
    with open(path, 'w', encoding='utf-8') as fh:
        json.dump(data, fh, ensure_ascii=False, indent=1); fh.write('\n')
    return path, url_id + '.html'

def album_nodes(titre, date, photos):
    nb = len(photos)
    infos = ' &middot; '.join(x for x in (ent(date), f'{nb} photo{"s" if nb > 1 else ""}') if x)
    retour = f'<a href="{SOMMAIRE_URL}">&larr; {ent("Toutes les galeries")}</a>'
    grille = container([image(v, g, alt, (VIGNETTE, VIGNETTE), classes='photo_album') for g, v, alt in photos],
                       classes='album_grille')
    return [textarea(f'<p>{retour} <span class="album_infos">&nbsp;&middot; {infos}</span></p>', classes='album_nav'),
            textarea(f'<p>{ent("Cliquez sur une photo pour l’agrandir, puis utilisez les flèches pour faire défiler l’album.")}</p>',
                     classes='album_aide'),
            grille,
            textarea(f'<p>{retour}</p>', classes='album_nav album_nav_bas')]

def sommaire_grid(page):
    return page.find(lambda n: 'albums_grille' in (n.get('more_classes') or ''))[0]

def ajouter_album(sources, titre, date='', couverture=None, position=0, slug=None, alts=None, nom=None):
    """sources : chemins des photos, dans l'ordre d'affichage. Renvoie (pid, url)."""
    if not slug:                                  # « Marché des producteurs » + « 13 septembre 2026 »
        periode = re.sub(r'^\s*\d{1,2}(er)?\s+', '', date)     # -> marche-des-producteurs-septembre-2026
        slug = slugify(titre if re.search(r'\d{4}', titre) or not periode else f'{titre} {periode}')
    if len(nom or titre) > 45: raise SystemExit(f'titre trop long pour un nom de page ({len(titre)} > 45) : utiliser --nom')
    if glob.glob(f'{SITE}/pages/p*-galerie-{slug}.json'):
        raise SystemExit(f'album déjà présent : galerie-{slug}')
    photos = []
    for i, src in enumerate(sources, 1):
        large, thumb = make_images(src, slug, i)
        alt = alts[i - 1] if alts else f'{titre} – photo {i}'
        photos.append((large, thumb, alt))
    cover = make_cover(couverture or sources[0], slug)
    pid = next_page_id()
    path, url = make_album_page(pid, slug, titre, date, album_nodes(titre, date, photos), nom)
    register(pid, path)
    som = Page(SOMMAIRE); grid = sommaire_grid(som)
    som.insert(grid, carte(titre, date, len(photos), url, cover, slug), position)
    som.save()
    return pid, url

# ---------------------------------------------------------------- CLI
if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('dossier'); ap.add_argument('--titre', required=True); ap.add_argument('--date', default='')
    ap.add_argument('--couverture', help='nom du fichier de couverture (défaut : la première photo)')
    ap.add_argument('--position', type=int, default=0, help='place de la carte dans le sommaire (0 = première)')
    ap.add_argument('--nom', help='nom court de la page (fil d’Ariane, 45 caractères max ; défaut : le titre)')
    a = ap.parse_args()
    srcs = sorted(f for f in glob.glob(os.path.join(a.dossier, '*')) if f.lower().endswith(EXTS))
    if not srcs: raise SystemExit('aucune photo dans ' + a.dossier)
    cov = os.path.join(a.dossier, a.couverture) if a.couverture else None
    pid, url = ajouter_album(srcs, a.titre, a.date, cov, a.position, nom=a.nom)
    print(f'{pid} {url} : {len(srcs)} photos ; carte ajoutée au sommaire en position {a.position}')
