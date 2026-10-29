#!/usr/bin/env python3
"""29/10/2026 — Page « Commissions communales » (p322) remise au propre.

Avant : 13 cadres « Cadre-rose » (bordure bleue, titres en petites capitales avec ombre orange,
noms centrés en gras), répartis à la main en 3 colonnes de hauteurs inégales ; intro centrée avec
des paragraphes vides comme espacement.
Après :
  - une carte par commission (titre sur bandeau vert clair, liste de membres), mise en colonnes
    fluides par le CSS (3, 2 ou 1 selon la largeur), même présentation pour les délégations externes ;
  - chaque membre a sa petite photo ronde à côté du nom (portraits de la page Conseil municipal,
    silhouette neutre pour les élues sans photo) ;
  - intitulés harmonisés (minuscules, « Église », « Salle des fêtes » au singulier) ;
  - intro alignée à gauche, sans paragraphes vides.
L'ordre des membres de chaque commission est conservé.
"""
import sys, os, re
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from sitelib import Page, T, plain, set_text, ent, SITE
from album import container, textarea, image

INTITULES = {
    'Bâtiments Communaux': 'Bâtiments communaux',
    'Communication et Numérique': 'Communication et numérique',
    'Décoration et Jardins': 'Décoration et jardins',
    'Salles des Fêtes': 'Salle des fêtes',
    'Responsables Agents Communaux': 'Responsables des agents communaux',
    "Appels d'Offres": 'Appels d’offres',
    'Correspondants Tempêtes': 'Correspondants tempêtes',
    'Animaux dangereux et errants - Protection des animaux': 'Animaux dangereux et errants, protection des animaux',
    'église et cimetière': 'Église et cimetière',
}

# ---------------------------------------------------------------- portraits (page Conseil municipal)
conseil = Page('p208-conseil-municipal')
PORTRAIT = {}
for card in conseil.find(lambda n: 'carte_elu' in (n.get('more_classes') or '')):
    img = next(c for c in card['contents'] if c['$class'] == 'WsImage')
    nom = re.search(r'<strong>(.*?)</strong>', T(next(c for c in card['contents'] if c['$class'] == 'WsTextarea')['value'])).group(1)
    PORTRAIT[plain(nom)] = img['value']
assert len(PORTRAIT) == 11, PORTRAIT

def membre(nom):
    prenom, famille = nom.split(' ', 1)
    alt = f'Portrait de {prenom} {famille.capitalize()}'
    return container([image(PORTRAIT[nom], PORTRAIT[nom], alt, (80, 80), gallery=False),
                      textarea(f'<p>{ent(nom)}</p>', style=None)], classes='membre')

def carte(titre_tpl, intitule, noms):
    t = Page.clone(titre_tpl)
    t.update({'value': intitule, 'user_style': None, 'more_classes': ''})
    return container([t, container([membre(n) for n in noms], classes='membres')], classes='carte_commission')

def section(titre_tpl2, titre, cartes):
    t = Page.clone(titre_tpl2); t['value'] = titre
    s = container([t, container(cartes, classes='commissions_grille')]); s['user_style'] = 'Subdivision'
    return s

# ---------------------------------------------------------------- relevé de la page actuelle
p = Page('p322-commissions')
titres = p.find(lambda n: n.get('user_style') == 'COMMISSIONS')
tpl_titre, tpl_titre2 = titres[0], p.find(lambda n: n.get('user_style') == 'Title2')[0]

def lire(t):
    """(intitulé, [noms]) pour un titre de commission : la liste est le WsTextarea qui le suit."""
    parent = p.parents(t)[-1]
    if parent['$class'] == 'WsContainer' and parent['contents'] == [t]:   # titre emballé (Finances)
        parent = p.parents(parent)[-1]
    liste = next(n for n, _ in Page._walk_static(parent) if n['$class'] == 'WsTextarea')
    noms = [plain(x) for x in re.split(r'</p>|<br\s*/?>', T(liste['value'])) if plain(x)]   # un nom par paragraphe ou par ligne
    return INTITULES.get(t['value'], t['value']), noms

internes, externes = [], []
sec_int, sec_ext = None, None
for t in titres:
    ps = p.parents(t)
    (externes if any(n.get('user_style') == 'Subdivision' and any(
        c.get('user_style') == 'Title2' for c in n.get('contents', [])) for n in ps) else internes).append(lire(t))
for n, _ in p.walk():
    if n.get('user_style') == 'Subdivision' and any('Cadre-rose' == (c.get('user_style')) for c, _ in Page._walk_static(n)) \
            and not any(c.get('user_style') == 'Title' for c, _ in Page._walk_static(n)):
        sec_int = n
    if n.get('user_style') == 'Subdivision' and any(c.get('user_style') == 'Title2' for c in n.get('contents', [])):
        sec_ext = n
assert len(internes) == 13 and len(externes) == 2 and sec_int and sec_ext, (len(internes), len(externes))
for _, noms in internes + externes:
    for nom in noms: assert nom in PORTRAIT, nom

# ---------------------------------------------------------------- nouvelle présentation
body = p.parents(sec_int)[-1]
i = body['contents'].index(sec_int)
body['contents'][i] = section(tpl_titre2, 'Commissions du conseil municipal', [carte(tpl_titre, a, b) for a, b in internes])
body['contents'][body['contents'].index(sec_ext)] = section(tpl_titre2, 'Commissions externes',
                                                             [carte(tpl_titre, a, b) for a, b in externes])
Page.reindex(body)

intro = p.find(lambda n: 'instances internes' in T(n.get('value')))[0]
paras = [x for x in re.findall(r'<p>(.*?)</p>', T(intro['value']), re.S) if plain(x)]
set_text(intro, 'value', '\r\n'.join(f'<p>{x}</p>' for x in paras))
intro['more_classes'] = 'commissions_intro'
p.save()
print(len(internes), 'commissions,', len(externes), 'externes')

# ---------------------------------------------------------------- styles (un bloc @media par règle)
RULES = [
    ('all', '.wscontainer.commissions_grille', 'columns: 3 250px; column-gap: 18px; padding: 6px 6px 0; margin: 0; border-width: 0;'),
    ('all', '.wscontainer.carte_commission', 'display: block; break-inside: avoid; margin: 0 0 18px !important; padding: 0 0 8px !important; overflow: hidden; background: #ffffff; border: 1px solid #cfe3d4; border-radius: 14px; box-shadow: 0 3px 10px rgba(47, 94, 62, 0.12);'),
    ('all', '.carte_commission .wsstitle', "margin: 0; padding: 12px 16px; background: #e7f1e8; border: 0; border-bottom: 1px solid #cfe3d4; border-radius: 0; box-shadow: none; font-family: Manrope, Arial, sans-serif; font-size: 1.15em; font-weight: 700; font-variant: normal; text-transform: none; letter-spacing: 0; line-height: 1.3; color: #2f5e3e; text-align: left;"),
    ('all', '.wscontainer.membres', 'margin: 0; padding: 6px 10px 0; border-width: 0;'),
    ('all', '.wscontainer.membre', 'display: flex; align-items: center; margin: 0; padding: 3px 6px; border-width: 0;'),
    ('all', '.membre .wsimage', 'flex: 0 0 44px; float: none !important; width: 44px !important; max-width: 44px !important; margin: 0 !important; padding: 0 !important;'),
    ('all', '.membre .wsimage img', 'display: block; width: 44px; height: 44px; object-fit: cover; border-radius: 50%; border: 2px solid #ffffff; box-shadow: 0 0 0 1px #6baa7a;'),
    ('all', '.membre .wstextarea', 'float: none; margin: 0 0 0 12px; padding: 0; font-family: Inter, Arial, sans-serif; font-size: 1.1em; font-weight: 500; color: #1d2b21; text-align: left;'),
    ('all', '.membre .wstextarea p', 'margin: 0;'),
    ('all', '.wstextarea.commissions_intro', 'text-align: left; line-height: 1.55;'),
    ('all', '.wstextarea.commissions_intro p + p', 'margin-top: 0.8em;'),
    ('(max-width: 640px)', '.wssystemcontainer.H:has(> div > .commissions_intro) > div', 'display: block !important; width: 100% !important;'),
    ('(max-width: 640px)', '.wssystemcontainer.H:has(> div > .commissions_intro) > div > .wsimage', 'max-width: 200px !important; margin: 0 auto 10px !important;'),
    ('(max-width: 640px)', '.membre .wsimage', 'flex-basis: 38px; width: 38px !important; max-width: 38px !important;'),
    ('(max-width: 640px)', '.membre .wsimage img', 'width: 38px; height: 38px;'),
    ('(max-width: 640px)', '.wscontainer.membres', 'padding: 4px 6px 0;'),
]
cssf = os.path.join(SITE, 'css/default.css')
css = open(cssf, encoding='utf-8').read()
if '.carte_commission' not in css:
    css = css.rstrip('\n') + '\n' + ''.join(
        '@media %s {\n\t%s {\n%s\t}\n}\n' % (m, sel, ''.join(f'\t\t{d.strip()};\n' for d in decl.split(';') if d.strip()))
        for m, sel, decl in RULES)
    open(cssf, 'w', encoding='utf-8').write(css)
print('css ok')
