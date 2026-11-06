#!/usr/bin/env python3
"""06/11/2026 — Refonte visuelle « plus pimpante » (dev).

Principe : un seul niveau de panneau (blanc, trait fin, sans ombre) sur un fond clair ; plus de cadres
foncés ni d'ombres vertes décalées ; titres Playfair en casse normale (fin des petites capitales et des
majuscules forcées) ; menu d'en-tête en liens plats ; cartes d'actualité avec photo pleine largeur et
catégorie en pastille ; bannière d'accueil sans ombre portée sur le titre.

Palette : fond « brume » #F1F3EE · panneau #FFFFFF · encre #1F2A23 · vigne #2F5E3E (accent) ·
trait #DDE2D9 · pierre #7A6F5F (dates, informations secondaires) · sauge #E6EEE6 (survols).

Les styles nommés (gérés par l'éditeur WebSiCo) sont modifiés en place ; les sélecteurs que l'éditeur
ne sait pas gérer sont ajoutés en blocs « @media all { … } » d'une règle chacun (tools/check_css.py).
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CSS = os.path.join(ROOT, 'site', 'css', 'default.css')
css = open(CSS, encoding='utf-8').read()

BRUME, BLANC, ENCRE, VIGNE, TRAIT, PIERRE, SAUGE = '#F1F3EE', '#FFFFFF', '#1F2A23', '#2F5E3E', '#DDE2D9', '#7A6F5F', '#E6EEE6'
TITRES = '"Playfair Display", Georgia, serif'
TEXTE = 'Inter, Arial, sans-serif'

def setp(sel, props):
    """Modifie les propriétés d'une règle gérée (en-tête exact `sel {`). None = supprimer."""
    global css
    m = re.search(r'(?m)^' + re.escape(sel) + r' \{\n(.*?)\n\}', css, flags=re.S)
    assert m, sel
    lines = m.group(1).split('\n') if m.group(1) else []
    for prop, val in props.items():
        idx = [i for i, l in enumerate(lines) if re.match(r'\t' + re.escape(prop) + r'\s*:', l)]
        for i in reversed(idx): del lines[i]
        if val is not None: lines.append(f'\t{prop}: {val};')
    css = css[:m.start(1)] + '\n'.join(lines) + css[m.end(1):]

def media(sel, body, cond='all'):
    """Ajoute un bloc @media d'une seule règle (sélecteur multiple autorisé)."""
    global css
    decl = '\n'.join(f'\t\t{k}: {v};' for k, v in body.items())
    css = css.rstrip('\n') + f'\n@media {cond} {{\n\t{sel} {{\n{decl}\n\t}}\n}}\n'

def replace_media(old_sel, body):
    global css
    m = re.search(r'@media all \{\n\t' + re.escape(old_sel) + r' \{\n(.*?)\n\t\}\n\}', css, flags=re.S)
    assert m, old_sel
    decl = '\n'.join(f'\t\t{k}: {v};' for k, v in body.items())
    css = css[:m.start(1)] + decl + css[m.end(1):]

NO_SHADOW = 'none'

# ---------------------------------------------------------------- fond, cadres de page
setp('.wsspage_Arriere_plan', {'background-color': BRUME, 'color': ENCRE})
setp('.wscontainer_BodyHome', {'border-width': '0px', 'box-shadow': NO_SHADOW, 'background-color': 'transparent',
                               'border-radius': None, 'padding': '8px', 'margin-top': '8px', 'margin-bottom': '8px'})
setp('.wscontainer_Subdivision', {'border-width': '1px', 'border-color': TRAIT, 'border-radius': '14px',
                                  'box-shadow': NO_SHADOW, 'background-color': BLANC})
# en-tête des pages intérieures : une barre blanche, le reste de la page à plat
media('.wscontainer_BodyHome:has(.nav_rubrique)',
      {'background-color': BLANC, 'border': f'1px solid {TRAIT}', 'border-radius': '14px', 'padding': '6px 10px'})

# ---------------------------------------------------------------- bannière d'accueil
setp('.wscontainer_Banniere', {'border-width': '0px', 'box-shadow': NO_SHADOW, 'border-radius': '18px',
                               'background-color': BLANC, 'padding': '10px', 'background-size': 'auto 100%',
                               'background-position': '100% 50%', 'background-repeat': 'no-repeat'})
setp('.wstextarea_Titre_accueil', {'text-shadow': None, 'letter-spacing': '-0.01em', 'color': ENCRE,
                                   'padding-top': '48px', 'line-height': '1.05em', 'font-size': '4.6em'})
setp('.wstextarea_Sous_titre_accueil', {'font-family': TEXTE, 'font-size': '1.6em', 'color': '#3c4a41'})

# ---------------------------------------------------------------- titres
setp('.wsstitle_Title', {'text-transform': 'none', 'font-variant': 'normal', 'border-bottom-width': '0px',
                         'border-radius': None, 'font-size': '3.2em', 'padding': '24px 30px', 'letter-spacing': '-0.01em',
                         'color': ENCRE, 'line-height': '1.1em'})
setp('.wsstitle_Title2', {'font-variant': 'normal', 'color': ENCRE, 'font-size': '1.8em'})
setp('.wsstitle_Title3', {'text-transform': 'none', 'color': ENCRE, 'font-size': '2.1em'})
setp('.wsstitle_FORMALITES', {'font-variant': 'normal', 'font-family': TITRES, 'font-weight': 'bold', 'font-size': '2em',
                              'text-align': 'left', 'letter-spacing': '0em', 'border-bottom-width': '1px',
                              'border-bottom-right-radius': None, 'border-color': TRAIT, 'color': ENCRE,
                              'padding': '6px 10px 10px', 'margin': '6px 10px 10px'})
setp('.wsstitle_COMMISSIONS', {'font-variant': 'normal', 'box-shadow': NO_SHADOW, 'border-width': '0px'})

# ---------------------------------------------------------------- en-tête : liens plats
setp('.wstextarea_Lien_header', {'gap': '6px', 'font-family': TEXTE})
setp('.wstextarea_Lien_header a', {'background': 'transparent', 'border': '1px solid transparent', 'box-shadow': NO_SHADOW,
                                   'border-radius': '10px', 'font-size': '17px', 'font-weight': '600', 'padding': '14px 10px'})
setp('.wstextarea_Lien_header a:hover, .wstextarea_Lien_header a.hover',
     {'transform': None, 'box-shadow': NO_SHADOW, 'border-color': 'transparent', 'background': SAUGE})
setp('.wstextarea_retour_accueil a', {'background': 'transparent', 'border': '0px', 'box-shadow': NO_SHADOW})
setp('.wstextarea_retour_accueil a:hover, .wstextarea_retour_accueil a.hover',
     {'transform': None, 'box-shadow': NO_SHADOW, 'border-color': 'transparent', 'background': 'transparent'})
setp('.wstextarea_retour_accueil', {'letter-spacing': '0em'})
replace_media('.nav_rubrique:has(a.selected) > .wstextarea_Lien_header a',
              {'border-color': 'transparent', 'box-shadow': f'inset 0 -2px 0 {VIGNE}', 'border-radius': '10px 10px 2px 2px'})

# ---------------------------------------------------------------- menu de l'accueil (colonne) et sous-menus
setp('.wssmenu_Main', {'background': 'transparent', 'box-shadow': NO_SHADOW, 'border': '0px', 'backdrop-filter': None,
                       '-webkit-backdrop-filter': None, 'margin': '0px', 'padding': '4px 6px'})
setp('.wssmenu_Main .submenu a', {'text-transform': 'none', 'font-weight': '500'})
setp('.wscontainer_Bloc_menu', {'text-transform': 'none'})
setp('.wssmenu_Sous-menus', {'background': BLANC, 'box-shadow': NO_SHADOW, 'border': f'1px solid {TRAIT}', 'border-radius': '14px',
                             'backdrop-filter': None, '-webkit-backdrop-filter': None})
setp('.wssmenu_Sous-menus .submenu', {'background': 'transparent', 'box-shadow': NO_SHADOW, 'border': '0px',
                                      'backdrop-filter': None, '-webkit-backdrop-filter': None})
setp('.wssmenu_Sous-menus a', {'background-color': 'transparent', 'border-radius': '10px'})
setp('.wssmenu_Sous-menus a:hover, .wssmenu_Sous-menus a.hover', {'transform': None, 'color': VIGNE})
setp('.wssmenu_Sous-menus .submenu a:hover, .wssmenu_Sous-menus .submenu a.hover', {'transform': None, 'color': VIGNE})
media('.wssmenu_Sous-menus a',
      {'font-variant': 'normal', 'text-transform': 'none'})

# ---------------------------------------------------------------- cartes d'actualité (accueil)
for cat, couleur in (('mairie', VIGNE), ('vie_communale', '#a1307f'), ('securite', '#a34700'), ('sante', '#005fae'), ('emploi', '#4A00B3')):
    setp(f'.wstextarea_bulle_actu_categorie_{cat}', {'text-transform': 'none', 'font-family': TEXTE, 'font-size': '1.05em',
                                                    'font-weight': '600', 'color': couleur, 'padding-left': None})
    media(f'.wstextarea_bulle_actu_categorie_{cat} p',
          {'display': 'inline-block', 'margin': '0', 'padding': '3px 10px', 'border-radius': '999px',
           'background-color': f'color-mix(in srgb, {couleur} 12%, white)'})
setp('.wstextarea_bulle_actu_date', {'font-variant': 'normal', 'font-family': TEXTE, 'font-weight': '500', 'font-size': '1.05em', 'color': PIERRE})
setp('.wstextarea_titre_bulle_actu', {'font-family': TITRES, 'font-size': '1.75em', 'line-height': '1.2em', 'color': ENCRE})
setp('.wstextarea_titre_grosse_bulle_actu', {'border-bottom-width': '0px', 'border-bottom-right-radius': None, 'font-size': '1.3em',
                                            'font-weight': '600', 'color': VIGNE})
media('.wscontainer.carte_actu', {'padding': '0 !important', 'overflow': 'hidden'})
media('.carte_actu > .wsimage',
      {'margin': '0 0 6px !important', 'width': '100% !important', 'max-width': 'none !important', 'height': '150px', 'padding': '0 !important'})
media('.carte_actu > .wsimage img',
      {'display': 'block', 'width': '100% !important', 'height': '100% !important', 'object-fit': 'cover'})
media('.carte_actu > .wssystemcontainer,\n\t.carte_actu > .wstextarea',
      {'margin-left': '12px !important', 'margin-right': '12px !important'})

# ---------------------------------------------------------------- cartes d'événement
setp('.wstextarea_bulle_agenda', {'background-color': VIGNE, 'color': BLANC, 'border-radius': '12px'})

# ---------------------------------------------------------------- accueil : en-têtes de rubrique, boutons, icônes
setp('.wsstitle_Titre_main_page_sub', {'text-transform': 'none', 'font-variant': 'normal', 'font-size': '3em', 'color': ENCRE,
                                       'letter-spacing': '-0.01em', 'border-radius': None})
setp('.wstextarea_actus_sous_titre', {'border-bottom-width': '0px', 'border-radius': None, 'border-bottom-right-radius': None,
                                      'color': '#3c4a41', 'font-size': '1.35em'})
media('.wscontainer:has(> .wsstitle_Titre_main_page_sub),\n\t.wscontainer:has(> .wstextarea_actus_sous_titre),\n\t.wscontainer:has(> .wstextarea_liens_page_principale)',
      {'border-width': '0 !important', 'background': 'transparent !important', 'box-shadow': 'none !important'})
setp('.wstextarea_liens_page_principale', {'font-family': TEXTE})
setp('.wstextarea_liens_page_principale a', {'background': 'transparent', 'border': f'1.5px solid {VIGNE}', 'border-radius': '999px',
                                             'box-shadow': NO_SHADOW, 'font-size': '16px', 'font-weight': '600', 'padding': '10px 18px'})
setp('.wstextarea_liens_page_principale a:hover, .wstextarea_liens_page_principale a.hover',
     {'transform': None, 'box-shadow': NO_SHADOW, 'background': SAUGE, 'border-color': VIGNE})
setp('.wssmenu_Main a', {'font-variant': 'normal', 'padding': '12px 14px'})
media('.wsimage:has(> img[src*="icone-"])', {'background-color': 'transparent !important'})
media('.carte_actu > .wssystemcontainer', {'width': 'auto !important', 'box-sizing': 'border-box'})

open(CSS, 'w', encoding='utf-8').write(css)
print('ok')
