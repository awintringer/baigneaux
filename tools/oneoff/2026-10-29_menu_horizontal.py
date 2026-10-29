#!/usr/bin/env python3
"""29/10/2026 — Menu horizontal : la colonne de menu à gauche disparaît (sauf sur l'accueil).

  - Modèle Header2 (en-tête de toutes les pages sauf l'accueil) : chacun des 5 boutons
    (Ma mairie, Ma commune, Évènements, Services, Démarches) ouvre au survol, au clic clavier
    (Tab) ou au toucher un panneau déroulant. Les panneaux sont faits de menus WebSiCo (WssMenu
    limités à une rubrique du plan du site) : une page ajoutée dans une rubrique y apparaît seule.
    Le plan du site n'est pas modifié : l'accueil garde son menu détaillé et le fil d'Ariane ses
    chemins actuels.
  - Pages (toutes sauf l'accueil) : la rangée « colonne menu | contenu » est remplacée par le fil
    d'Ariane (modèle Path, sur une ligne) suivi du contenu dans un bloc « contenu_page » pleine
    largeur ; l'affichage mobile est inchangé.
    Les autres blocs de la colonne de gauche (encart « Services publics 33 ») passent sous le
    contenu.
  - Mobile : inchangé (menu burger) ; les 6 pages qui n'avaient pas l'en-tête mobile standard
    (leur menu mobile venait de la colonne de gauche) le reçoivent.
"""
import sys, os, re, glob, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from sitelib import Page, new_id, ent, SITE
from album import container, textarea

URL = 'https://www.baigneaux.fr'

# ---------------------------------------------------------------- panneaux
# groupe : (titre, page du titre, rubrique du plan dont on liste les pages, liens fixes)
PANNEAUX = {
    'mairie.html': [(None, None, 'p207', [])],
    'vie-communale.html': [
        ('Vie communale', 'vie-communale', 'p220', []),
        ('Tourisme', 'tourisme', 'p203', []),
        ('Se repérer', None, None, [('Plan et accès', 'carte-de-la-commune')]),
    ],
    'evenements-festivites.html': [
        (None, None, None, [('Agenda des évènements', 'evenements-festivites'), ('Actualités', 'actualites'),
                            ('Notre village en images', 'galerie-evenements')]),
    ],
    'annuaire.html': [
        ('Enfance et jeunesse', 'enfance-jeunesse', 'p210', []),
        ('Santé', 'p328', 'p328', []),
        ('Assos, commerces et services', 'annuaire', 'p321', []),
        ('Intercommunalité', 'intercommunalite', 'p315', []),
    ],
    'formalites-administratives.html': [
        ('Formalités', None, None, [('Formalités administratives', 'formalites-administratives'), ('Boîte à idées', 'boite-a-idees')]),
        ('Urbanisme', 'urbanisme', 'p286', []),
    ],
}
LARGES = {'vie-communale.html', 'annuaire.html'}          # panneaux en colonnes

def lien(label, page):
    return f'<a href="{URL}/{page}.html">{ent(label)}</a>'

def menu(category):
    i = new_id('Y')
    return {'$class': 'WssMenu', 'category': category, 'depth': '0', 'value': 'vertical', 'id': i,
            'properties': 262144, 'owner': {'$owner': 'R'}, 'index': 0, 'user_style': None,
            'more_classes': 'nav_menu', 'embedded_css_rules': '', 'name_in_model': 'M' + i}

def mark(node):
    """Éléments d'un modèle : name_in_model sur chaque élément ajouté."""
    for n, _ in Page._walk_static(node):
        n.setdefault('name_in_model', 'M' + n['id'])
    return node

def groupe(titre, page, cat, liens):
    items = []
    if titre:
        items.append(textarea(f'<p>{lien(titre, page) if page else ent(titre)}</p>', style=None, classes='nav_titre'))
    if cat:
        items.append(menu(cat))
    if liens:
        items.append(textarea(''.join(f'<p>{lien(l, p)}</p>' for l, p in liens), style=None, classes='nav_liens'))
    return container(items, classes='nav_groupe')

# ---------------------------------------------------------------- modèle Header2
hf = os.path.join(SITE, 'models', 'Header2.json')
hdr = json.load(open(hf, encoding='utf-8'))
root = hdr['row'][-1]['$php']
boutons = [n for n, _ in Page._walk_static(root) if n.get('user_style') == 'Lien_header']
assert len(boutons) == 5
deja = any('nav_rubrique' in (c.get('more_classes') or '') for c, _ in Page._walk_static(root))
for b in ([] if deja else boutons):
    href = re.search(r'href="[^"]*/([^/"]+)"', b['value']).group(1)
    cell = next(n for n, _ in Page._walk_static(root) if b in (n.get('contents') or []))
    classes = 'nav_panneau' + (' nav_large' if href in LARGES else '') + \
              (' nav_droite' if href in ('annuaire.html', 'formalites-administratives.html') else '')
    panneau = container([groupe(*g) for g in PANNEAUX[href]], classes=classes)
    rub = container([b, panneau], classes='nav_rubrique')
    mark(rub)
    cell['contents'] = [rub]
    Page.reindex(cell)
with open(hf, 'w', encoding='utf-8') as fh:
    json.dump(hdr, fh, ensure_ascii=False, indent=1); fh.write('\n')

# ---------------------------------------------------------------- pages : plus de colonne de gauche
def contains(node, target):
    return any(n is target for n, _ in Page._walk_static(node))

done = 0
for f in sorted(glob.glob(os.path.join(SITE, 'pages', '*.json'))):
    name = os.path.basename(f)[:-5]
    if name == 'home': continue
    p = Page(name)
    menus = p.find(lambda n: n.get('model_id') == 'MENU')
    if not menus: continue                                 # déjà traitée
    m = menus[0]; ps = p.parents(m)
    left_sub, left_cell, row, body = ps[-1], ps[-2], ps[-3], ps[-4]
    assert row['contents'][0] is left_cell and left_sub.get('user_style') == 'Subdivision', name
    path = p.find(lambda n: n.get('model_id') == 'Path')[0]
    # bloc qui contient le fil d'Ariane hors colonne (p313) : on le retire
    if not contains(left_sub, path):
        holder = p.parents(path)[-1]
        if holder['contents'] == [path] and holder is not body:
            p.remove(holder)
        else:
            p.remove(path)
    extras = [c for c in left_sub['contents'] if not contains(c, m) and not contains(c, path)]
    autres = [c for c in left_cell['contents'] if c is not left_sub]
    avant = [c for c in autres if c.get('model_id') == 'menu_burger']   # en-tête mobile rangé dans la colonne
    extras = extras + [c for c in autres if c.get('model_id') != 'menu_burger']
    # le contenu de la colonne de droite passe dans un bloc « contenu_page » (pleine largeur) ;
    # ses rangées remontent d'un niveau d'imbrication, la règle CSS contenu_page leur garde
    # sur mobile leur comportement d'avant (voir RULES)
    rest = row['contents'][1:]
    if len(rest) == 1:
        nouveau = [container(rest[0]['contents'], classes='contenu_page')]
    else:                                                  # plusieurs colonnes : on garde la rangée
        for c in rest: c['embedded_css_rules'] = ''
        row['contents'] = rest; Page.reindex(row)
        nouveau = [row]
    i = body['contents'].index(row)
    entete = [container(avant, classes='contenu_page')] if avant else []   # même règle mobile que le contenu
    body['contents'][i:i + 1] = entete + [path] + nouveau + extras
    Page.reindex(body)
    p.save(); done += 1
print(done, 'pages sans colonne de gauche')

# pages qui n'avaient pas d'en-tête mobile (leur menu mobile venait de la colonne de gauche) :
# on leur ajoute celui des autres pages (modèle menu_burger), en tête de page
ref = Page('p208-conseil-municipal').find(lambda n: n.get('model_id') == 'menu_burger')[0]
ajouts = []
for f in sorted(glob.glob(os.path.join(SITE, 'pages', '*.json'))):
    name = os.path.basename(f)[:-5]
    if name == 'home': continue
    p = Page(name)
    if p.find(lambda n: n.get('model_id') == 'menu_burger'): continue
    path = p.find(lambda n: n.get('model_id') == 'Path')[0]
    body = p.parents(path)[-1]
    p.insert(body, container([Page.clone(ref)], classes='contenu_page'), body['contents'].index(path))
    p.save(); ajouts.append(name)
print('en-tête mobile ajouté :', ', '.join(ajouts))

# ---------------------------------------------------------------- styles (un bloc @media par règle)
RULES = [
    ('all', '.wscontainer.nav_rubrique', 'position: relative; margin: 0; padding: 0; border-width: 0;'),
    ('all', '.wscontainer.nav_panneau', 'display: none; position: absolute; top: calc(100% + 12px); left: 0; z-index: 50; min-width: 260px; margin: 0; padding: 0; border-width: 0; border-radius: 14px; background: #ffffff; box-shadow: 0 12px 28px rgba(31, 61, 41, 0.2);'),
    ('all', '.wscontainer.nav_panneau::before', 'content: ""; position: absolute; left: 0; right: 0; top: -14px; height: 14px;'),
    ('all', '.nav_panneau.nav_droite', 'left: auto; right: 0;'),
    ('all', '.nav_rubrique:hover > .nav_panneau, .nav_rubrique:focus-within > .nav_panneau', 'display: flex;'),
    ('all', '.nav_panneau > .wscontainer.nav_groupe', 'flex: 1 1 0; min-width: 210px; margin: 0; padding: 14px 18px 16px; border-width: 0; background: transparent;'),
    ('all', '.nav_panneau > .nav_groupe + .nav_groupe', 'border-left: 1px solid #e3eee5;'),
    ('all', '.nav_panneau.nav_large', 'width: max-content; max-width: min(900px, 92vw);'),
    ('all', '.wstextarea.nav_titre', 'float: none; margin: 0 0 6px; padding: 0 0 6px; border-bottom: 2px solid #e7f1e8; font-family: Manrope, Arial, sans-serif; font-size: 0.95em; font-weight: 700; letter-spacing: 0.03em; text-transform: uppercase; color: #2f5e3e; text-align: left;'),
    ('all', '.wstextarea.nav_titre a', 'color: #2f5e3e; text-decoration: none;'),
    ('all', '.wstextarea.nav_titre p, .wstextarea.nav_liens p', 'margin: 0;'),
    ('all', '.wssmenu.nav_menu .button', 'display: none;'),
    ('all', '.wssmenu.nav_menu ul', 'list-style: none; margin: 0 !important; padding: 0 !important;'),
    ('all', '.wssmenu.nav_menu li, .wssmenu.nav_menu a', 'display: block; float: none; width: auto; background: none; border: 0; box-shadow: none; margin: 0;'),
    ('all', '.wssmenu.nav_menu a, .wstextarea.nav_liens a', 'display: block; padding: 6px 8px !important; border-radius: 8px; font-family: Inter, Arial, sans-serif; font-size: 15px; font-weight: 500; margin: 0 !important; line-height: 1.3; color: #1d2b21; text-decoration: none; text-align: left; text-transform: none; font-variant: normal; letter-spacing: 0; white-space: normal;'),
    ('all', '.wssmenu.nav_menu a:hover, .wstextarea.nav_liens a:hover, .wssmenu.nav_menu a:focus-visible, .wstextarea.nav_liens a:focus-visible', 'background: #e7f1e8; color: #2f5e3e;'),
    ('all', '.wssmenu.nav_menu a.selected', 'background: #2f5e3e; color: #ffffff;'),
    ('all', '.wstextarea.nav_liens', 'float: none; margin: 0; padding: 0;'),
    ('all', '.wssmenu.nav_menu li', 'padding: 0 !important;'),
    ('all', '.wscomponent.wssmenu.nav_menu', 'margin: 0; padding: 0; border-width: 0; background: none;'),
    ('all', '.wscontainer_Path', 'margin: 6px 14px 0;'),
    ('all', '.wscontainer.contenu_page', 'margin: 0; padding: 0; border-width: 0;'),
    ('all', '.wssystemcontainer.H:has(> div > .carte_elu)', 'max-width: 860px; margin-left: auto; margin-right: auto;'),
    # sans la colonne de gauche, les rangées du contenu remontent d'un niveau d'imbrication (hDepth2 -> 1) ;
    # on leur garde sur mobile le comportement qu'elles avaient (WebSiCo empile les hDepth1 sous 640 px)
    ('(min-width: 321px) and (max-width: 640px)', '.contenu_page .wssystemcontainer.H.hDepth1 > div', 'display: table-cell;'),
    ('(max-width: 640px)', '.contenu_page .wssystemcontainer.H.hDepth1:has(> div > .wscontainer_Subdivision)', 'display: flex !important; flex-wrap: wrap;'),
    ('(max-width: 640px)', '.contenu_page .wssystemcontainer.H.hDepth1:has(> div > .wscontainer_Subdivision) > div', 'display: block !important; flex: 1 1 260px; width: auto !important; min-width: 0;'),
    ('all', '.wscontainer_Path .wssystemcontainer.H', 'display: flex !important; align-items: baseline; flex-wrap: wrap; gap: 6px;'),
    ('all', '.wscontainer_Path .wssystemcontainer.H > div', 'width: auto !important; flex: 0 1 auto;'),
    ('all', '.nav_rubrique:has(a.selected) > .wstextarea_Lien_header a', 'border-color: #2f5e3e; box-shadow: inset 0 -3px 0 #6baa7a;'),
    ('all', '.wssystemcontainer.H:has(.nav_rubrique), .wssystemcontainer.H:has(.nav_rubrique) > div', 'overflow: visible;'),
    ('all', '.wscontainer:has(> .wssystemcontainer.H .nav_rubrique)', 'position: relative; z-index: 40; overflow: visible;'),
]
cssf = os.path.join(SITE, 'css/default.css')
css = open(cssf, encoding='utf-8').read()
if '.nav_rubrique' not in css:
    css = css.rstrip('\n') + '\n' + ''.join(
        '@media %s {\n\t%s {\n%s\t}\n}\n' % (m, sel.replace(', ', ',\n\t'), ''.join(f'\t\t{d.strip()};\n' for d in decl.split(';') if d.strip()))
        for m, sel, decl in RULES)
    open(cssf, 'w', encoding='utf-8').write(css)
print('css ok')
