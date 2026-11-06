#!/usr/bin/env python3
"""06/11/2026 — Accueil, ajustements après la refonte visuelle (retours de l'utilisateur).

  - bannière : le menu passe au-dessus de la photo (bande blanche séparée par un trait fin),
    la photo commence sous le menu ; bannière alignée sur les panneaux du dessous ;
  - colonne de menu de gauche : même hauteur que les 4 blocs d'information (rangée en flex,
    liens répartis sur toute la hauteur) ; les 4 blocs se partagent la hauteur ;
  - blocs d'information : icône et texte centrés verticalement, texte aligné à gauche ;
  - titres « À la une » / « À venir », sous-titres, boutons et rails de cartes alignés sur les bords
    des panneaux.
Ces règles ne s'appliquent qu'à partir de 641 px (colonne de menu et bannière masquées en dessous).
"""
import os, re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CSS = os.path.join(ROOT, 'site', 'css', 'default.css')
css = open(CSS, encoding='utf-8').read()
TRAIT = '#DDE2D9'
LARGE = '(min-width: 641px)'

def setp(sel, props):
    global css
    m = re.search(r'(?m)^' + re.escape(sel) + r' \{\n(.*?)\n\}', css, flags=re.S)
    assert m, sel
    lines = m.group(1).split('\n')
    for prop, val in props.items():
        lines = [l for l in lines if not re.match(r'\t' + re.escape(prop) + r'\s*:', l)]
        if val is not None: lines.append(f'\t{prop}: {val};')
    css = css[:m.start(1)] + '\n'.join(lines) + css[m.end(1):]

def media(sel, body, cond='all'):
    global css
    decl = '\n'.join(f'\t\t{k}: {v};' for k, v in body.items())
    css = css.rstrip('\n') + f'\n@media {cond} {{\n\t{sel} {{\n{decl}\n\t}}\n}}\n'

NAV_H = '92px'
# ---------------------------------------------------------------- bannière : menu au-dessus de la photo
setp('.wscontainer_Banniere', {'max-width': '1168px', 'box-sizing': 'border-box',
                               'background-position': f'30% {NAV_H}', 'background-size': f'auto calc(100% - {NAV_H})'})
media('.wscontainer_Banniere > .wssystemcontainer.H:first-child',
      {'border-bottom': f'1px solid {TRAIT}', 'padding-bottom': '6px', 'margin-bottom': '4px'})

media('.wstextarea_retour_accueil', {'padding-left': '54px', 'background-size': '46px auto'}, '(max-width: 900px)')
media('.wstextarea_retour_accueil a', {'font-size': '18px !important'}, '(max-width: 900px)')
media('.nav_rubrique > .wstextarea_Lien_header a,\n\t.wstextarea_Lien_header a', {'font-size': '15px', 'padding-left': '4px', 'padding-right': '4px'}, '(max-width: 900px)')

# ---------------------------------------------------------------- colonne de menu = hauteur des 4 blocs
RANGEE = '.wssystemcontainer.H:has(> div > .wscontainer_Subdivision .wssmenu_Main)'
media(RANGEE, {'display': 'flex !important', 'align-items': 'stretch'}, LARGE)
media(RANGEE + ' > div', {'display': 'flex !important', 'flex-direction': 'column', 'min-width': '0'}, LARGE)
media(RANGEE + ' > div:last-child', {'flex': '1 1 0'}, LARGE)
media(RANGEE + ' > div:first-child > .wscontainer_Subdivision', {'flex': '1 1 0', 'display': 'flex', 'flex-direction': 'column'}, LARGE)
media(RANGEE + ' > div:last-child > .wscontainer_Subdivision:not(.entete_mobile)', {'flex': '1 1 0'}, LARGE)
media('.wscontainer_Subdivision > .wscontainer_Bloc_menu', {'flex': '1 1 auto', 'display': 'flex', 'flex-direction': 'column'}, LARGE)
media('.wscontainer_Bloc_menu > .wssystemcontainer.H', {'flex': '1 1 auto', 'display': 'flex !important'}, LARGE)
media('.wscontainer_Bloc_menu > .wssystemcontainer.H > div:first-child', {'flex': '1 1 auto', 'display': 'flex !important', 'flex-direction': 'column'}, LARGE)
media('.wscontainer_Bloc_menu div.wssmenu_Main', {'flex': '1 1 auto', 'display': 'flex', 'flex-direction': 'column'}, LARGE)
media('.wscontainer_Bloc_menu div.wssmenu_Main > nav', {'flex': '1 1 auto', 'display': 'flex', 'flex-direction': 'column'}, LARGE)
media('.wscontainer_Bloc_menu div.wssmenu_Main > nav > ul', {'flex': '1 1 auto', 'display': 'flex', 'flex-direction': 'column',
                                                          'justify-content': 'space-between', 'margin': '0', 'padding': '6px 0'}, LARGE)

# ---------------------------------------------------------------- blocs d'information
INFO = '.wscontainer_Subdivision:has(img[src*="icone-"])'
media(INFO + ' > .wssystemcontainer.H', {'height': '100%'}, LARGE)
media(INFO + ' > .wssystemcontainer.H > div', {'vertical-align': 'middle'})
media(INFO + ' .wsstitle_Title2,\n\t' + INFO + ' .wstextarea_Texte_important_centre', {'text-align': 'left'}, LARGE)

# ---------------------------------------------------------------- en-têtes de rubrique et rails alignés sur les panneaux
setp('.wsstitle_Titre_main_page_sub', {'padding-left': '0px', 'margin-left': '0px'})
setp('.wstextarea_actus_sous_titre', {'margin-left': '0px', 'padding-left': '2px'})
media('.wscontainer:has(> .wsstitle_Titre_main_page_sub)', {'padding-left': '0 !important', 'margin-left': '5px !important'}, LARGE)
media('.wscontainer:has(> .wstextarea_liens_page_principale)', {'padding-right': '0 !important', 'margin-right': '5px !important'}, LARGE)
media('.wssystemcontainer.H:has(> div > .carte_actu),\n\t.wssystemcontainer.H:has(> div > .carte_evenement)', {'padding-left': '5px !important', 'padding-right': '5px !important', 'box-sizing': 'border-box'}, LARGE)

setp('.wstextarea_liens_page_principale', {'margin-right': '0px', 'padding-right': '0px'})
setp('.wscontainer_Bloc_menu', {'font-size': '.9em'})

open(CSS, 'w', encoding='utf-8').write(css)

# ---------------------------------------------------------------- blocs d'information : paragraphes vides retirés
import sys
sys.path.insert(0, os.path.join(ROOT, 'tools'))
from sitelib import Page, T, set_text
h = Page('home')
for t in h.find(lambda n: n.get('user_style') == 'Texte_important_centre'):
    paras = [p for p in T(t['value']).split('\r\n') if re.sub(r'<p>(&nbsp;|\s)*</p>', '', p).strip()]
    set_text(t, 'value', '\r\n'.join(paras))
h.save()
print('ok')
