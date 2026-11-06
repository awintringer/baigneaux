#!/usr/bin/env python3
"""06/11/2026 (soir) — Deuxième série de retouches (retours d'Adrien), après 2026-11-06_retouches_refonte.py.

  1. Bannière : retour à la photo (l'illustration n'a pas convaincu ; une photo HD viendra).
  2. Page Mairie : maire et adjoints en colonne à gauche des tuiles (cartes compactes).
  3. Accueil : cartes d'évènements refaites sur le modèle des cartes d'actualité (image pleine
     largeur recadrée, date en pastille posée sur l'image, titre en Playfair, horaires et lieu dessous).
  4. Pied de page (modèle Footer) : panneau blanc en trois colonnes (mairie, contact, liens).
  5. Historique des versions complété à partir de l'historique du dépôt (29/10 → 06/11).
"""
import os, re, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
from sitelib import Page, new_id, ent, set_text, T, SITE
from album import container, textarea

CSS = os.path.join(SITE, 'css', 'default.css')
css = open(CSS, encoding='utf-8').read()
URL = 'https://www.baigneaux.fr'
VIGNE, ENCRE, TRAIT, SAUGE, PIERRE = '#2F5E3E', '#1F2A23', '#DDE2D9', '#E6EEE6', '#5F6B60'
LARGE = '(min-width: 641px)'
CR = '\r\n'


def setp(sel, props):
    global css
    m = re.search(r'(?m)^' + re.escape(sel) + r' \{\n(.*?)\n\}', css, flags=re.S)
    assert m, sel
    lines = m.group(1).split('\n') if m.group(1) else []
    for prop, val in props.items():
        lines = [l for l in lines if not re.match(r'\t' + re.escape(prop) + r'\s*:', l)]
        if val is not None: lines.append(f'\t{prop}: {val};')
    css = css[:m.start(1)] + '\n'.join(lines) + css[m.end(1):]


def media(sel, body, cond='all'):
    global css
    decl = '\n'.join(f'\t\t{k}: {v};' for k, v in body.items())
    css = css.rstrip('\n') + f'\n@media {cond} {{\n\t{sel} {{\n{decl}\n\t}}\n}}\n'


def drop_media(sel, cond='all'):
    global css
    pat = r'@media ' + re.escape(cond) + r' \{\n\t' + re.escape(sel) + r' \{\n.*?\n\t\}\n\}\n'
    css, n = re.subn(pat, '', css, flags=re.S)
    assert n, sel


# ================================================================ 1. bannière photo
NAV = '84px'
setp('.wscontainer_Banniere', {'background-image': 'url(data/images/background/1442_banner.png)',
                               'background-position': f'30% {NAV}', 'background-size': f'auto calc(100% - {NAV})',
                               'min-height': '410px'})
svg = os.path.join(SITE, 'data', 'images', 'background', 'banniere-affiche.svg')
if os.path.exists(svg): os.remove(svg)

# ================================================================ 2. Mairie : élus à gauche des tuiles
m = Page('p207-mairie')
rub = m.find(lambda n: 'rubrique' == (n.get('more_classes') or '').strip())[0]
kids = rub['contents']
cls = lambda n: (n.get('more_classes') or '').strip()
tuiles = next(n for n in kids if cls(n) == 'tuiles_rubrique')
elus = [n for n in kids if cls(n) in ('rubrique_soustitre', 'apercu_elus', 'rubrique_bouton')]
assert len(elus) == 3
for n in elus: kids.remove(n)
set_text(elus[2], 'value', f'<p><a href="{URL}/conseil-municipal.html">Tout le conseil &rarr;</a></p>')
colonne = container(elus, classes='colonne_elus')
corps = container([colonne, tuiles], classes='mairie_corps')
kids[kids.index(tuiles)] = corps
Page.reindex(rub)
m.save()

media('.wscontainer.mairie_corps',
      {'display': 'grid', 'grid-template-columns': '230px minmax(0, 1fr)', 'gap': '18px', 'align-items': 'start',
       'margin': '0', 'padding': '0', 'border-width': '0'}, LARGE)
media('.wscontainer.colonne_elus',
      {'margin': '0 0 0 8px', 'padding': '14px 14px 16px', 'background': '#F6F8F4', 'border': f'1px solid {TRAIT}',
       'border-radius': '14px', 'box-sizing': 'border-box'})
media('.colonne_elus > .wstextarea.rubrique_soustitre', {'margin': '0 0 10px', 'font-size': '1.35em'})
media('.colonne_elus > .wscontainer.apercu_elus',
      {'display': 'flex', 'flex-direction': 'column', 'gap': '8px', 'padding': '0'})
media('.colonne_elus .apercu_elus > .wscontainer.carte_elu',
      {'flex': 'none', 'display': 'flex', 'align-items': 'center', 'gap': '12px', 'padding': '8px 10px !important',
       'text-align': 'left', 'box-shadow': 'none', 'border-radius': '12px'})
media('.colonne_elus .carte_elu .wsimage',
      {'width': '58px !important', 'flex': '0 0 58px', 'margin': '0 !important'})
media('.colonne_elus .carte_elu .wstextarea',
      {'font-size': '0.95em', 'text-align': 'left', 'margin': '0', 'padding': '0', 'min-width': '0'})
media('.colonne_elus > .wstextarea.rubrique_bouton', {'margin': '14px 0 0', 'max-width': 'none'})
media('.colonne_elus .rubrique_bouton a', {'font-size': '15px !important', 'padding': '8px 12px !important'})
media('.wscontainer.colonne_elus', {'margin': '0 8px 18px'}, '(max-width: 640px)')

# ================================================================ 3. cartes d'évènements de l'accueil
EV = '.carte_evenement'
for sel in ['.carte_evenement > .wsimage', '.carte_evenement > .wsimage img', '.carte_evenement > .wscontainer',
            '.carte_evenement .wssystemcontainer.H', '.carte_evenement .wssystemcontainer.H > div:first-child']:
    drop_media(sel)
media('.wssystemcontainer.H > div > .wscontainer.carte_evenement',
      {'position': 'relative', 'padding': '0 !important', 'overflow': 'hidden'})
media(EV + ' > .wsimage',
      {'order': '-1', 'width': '100% !important', 'max-width': 'none !important', 'height': '170px',
       'margin': '0 !important', 'padding': '0 !important', 'background': SAUGE, 'overflow': 'hidden'})
media(EV + ' > .wsimage img',
      {'display': 'block', 'width': '100% !important', 'height': '100% !important', 'max-width': 'none',
       'object-fit': 'cover', 'object-position': 'center 22%'})
media(EV + ' > .wscontainer',
      {'flex': '1 1 auto', 'width': 'auto', 'padding': '14px 16px 16px !important', 'margin': '0 !important',
       'box-sizing': 'border-box', 'border-width': '0 !important'})
media(EV + ' .wssystemcontainer.H',
      {'display': 'block !important', 'width': '100%', 'padding': '0 !important', 'margin': '0 !important'})
media(EV + ' .wssystemcontainer.H > div:first-child',
      {'position': 'absolute', 'top': '12px', 'left': '12px', 'z-index': '2', 'width': 'auto !important'})
media(EV + ' .wstextarea_bulle_agenda',
      {'min-width': '52px', 'padding': '6px 8px 7px', 'margin': '0', 'background-color': '#FFFFFF', 'color': VIGNE,
       'border-radius': '10px', 'box-shadow': '0 4px 12px rgba(31, 42, 35, 0.25)', 'line-height': '1.05',
       'font-family': 'Manrope, Arial, sans-serif', 'text-align': 'center'})
media(EV + ' .wstextarea_bulle_agenda p', {'margin': '0'})
media(EV + ' .wstextarea_bulle_agenda span', {'font-size': 'inherit !important'})
media(EV + ' .wstextarea_bulle_agenda p:first-child', {'font-size': '24px', 'font-weight': '800'})
media(EV + ' .wstextarea_bulle_agenda p + p',
      {'font-size': '12px', 'font-weight': '700', 'letter-spacing': '0.08em', 'text-transform': 'uppercase'})
media(EV + ' .wstextarea_Texte_normal_align_gauche',
      {'float': 'none', 'font-size': '15px', 'line-height': '1.45', 'color': '#3C4A41', 'margin': '0', 'padding': '0'})
media(EV + ' .wstextarea_Texte_normal_align_gauche p', {'margin': '0 0 3px'})
media(EV + ' .wstextarea_Texte_normal_align_gauche p:first-child strong',
      {'display': 'block', 'margin-bottom': '8px', 'font-family': '"Playfair Display", Georgia, serif',
       'font-size': '1.45em', 'line-height': '1.2', 'color': ENCRE})
media(EV + ' .wstextarea_Texte_normal_align_gauche p:nth-child(2)', {'display': 'none'})

# ================================================================ 4. pied de page
fp = os.path.join(SITE, 'models', 'Footer.json')
fm = json.load(open(fp, encoding='utf-8'))
froot = fm['row'][-1]['$php']
inner = froot['contents'][0]['contents'][0]
old = inner['contents'][0]
assert old.get('user_style') == 'Texte-centre'
cols = [
    '<p><strong>Mairie de Baigneaux</strong></p>' + CR +
    '<p>116 rue Yvonne de la Seigli&egrave;re<br />33760 Baigneaux</p>',
    '<p>Contact</p>' + CR +
    '<p><a href="tel:+33556239750">05 56 23 97 50</a></p>' + CR +
    '<p><a href="mailto:mairie@baigneaux.fr">mairie@baigneaux.fr</a></p>' + CR +
    '<p>Lundi et vendredi 13h-18h<br />Mercredi 8h30-11h30</p>',
    '<p>&Agrave; suivre</p>' + CR +
    '<p><a href="https://www.facebook.com/lesbaignaudais/">Facebook : Les Baignaudais</a></p>' + CR +
    f'<p><a href="{URL}/boite-a-idees.html">Bo&icirc;te &agrave; id&eacute;es</a></p>' + CR +
    f'<p><a href="{URL}/mentions-legales.html">Mentions l&eacute;gales</a></p>' + CR +
    f'<p><a href="{URL}/historique-modifications.html">Historique des versions</a></p>',
]
klass = ['pied_mairie', 'pied_col', 'pied_col']
pied = container([textarea(c, style=None, classes=k) for c, k in zip(cols, klass)], classes='pied_colonnes')
for n, _ in Page._walk_static(pied):
    n['name_in_model'] = 'M' + n['id']
inner['contents'][0] = pied
Page.reindex(inner)
with open(fp, 'w', encoding='utf-8') as fh:
    json.dump(fm, fh, ensure_ascii=False, indent=1); fh.write('\n')

setp('.wscontainer_fred1', {'color': ENCRE, 'max-width': '1168px', 'margin-top': '28px', 'margin-bottom': '18px',
                            'background-color': '#FFFFFF', 'border': f'1px solid {TRAIT}', 'border-radius': '14px',
                            'border-width': '1px', 'padding': '26px 30px 14px', 'box-sizing': 'border-box'})
media('.wscontainer.pied_colonnes',
      {'display': 'grid', 'grid-template-columns': '1.3fr 1fr 1fr', 'gap': '28px', 'margin': '0', 'padding': '0 0 18px',
       'border-width': '0', 'border-bottom': f'1px solid {TRAIT}'})
media('.wscontainer.pied_colonnes', {'grid-template-columns': '1fr', 'gap': '18px'}, '(max-width: 640px)')
media('.wscontainer_fred1', {'margin-left': '8px', 'margin-right': '8px', 'padding': '20px 18px 12px'}, '(max-width: 640px)')
media('.pied_colonnes .wstextarea',
      {'float': 'none', 'margin': '0', 'padding': '0', 'font-family': 'Inter, Arial, sans-serif', 'font-size': '14px',
       'line-height': '1.55', 'color': '#3C4A41', 'text-align': 'left'})
media('.pied_colonnes .wstextarea p', {'margin': '0 0 4px'})
media('.wstextarea.pied_mairie',
      {'padding-left': '64px !important', 'min-height': '54px', 'background-image': 'url(data/images/background/1231_logositepetit.png)',
       'background-repeat': 'no-repeat', 'background-position': '0 2px', 'background-size': '52px auto'})
media('.wstextarea.pied_mairie strong',
      {'font-family': '"Playfair Display", Georgia, serif', 'font-size': '1.45em', 'color': VIGNE})
media('.wstextarea.pied_col p:first-child',
      {'margin-bottom': '8px', 'font-family': 'Manrope, Arial, sans-serif', 'font-size': '0.85em', 'font-weight': '700',
       'letter-spacing': '0.06em', 'text-transform': 'uppercase', 'color': VIGNE})
media('.pied_colonnes .wstextarea a', {'color': VIGNE, 'text-decoration': 'none', 'font-weight': '500'})
media('.pied_colonnes .wstextarea a:hover,\n\t.pied_colonnes .wstextarea a:focus-visible', {'text-decoration': 'underline'})
media('.wscontainer_fred1 .wssbadge', {'margin': '12px auto 0', 'opacity': '0.75'})

# ================================================================ 5. historique des versions
H = Page('p327-historique-modifications')
bloc = H.find(lambda n: n.get('user_style') == 'Bloc-titre')[0]
ref = next(n for n in bloc['contents'] if n.get('user_style') == 'Subdivision' and '6 novembre 2026' in Page.text(n))

def entree_set(node, date, lignes):
    for n, _ in Page._walk_static(node):
        if n.get('$class') == 'WssTitle': n['value'] = date
        if n.get('$class') == 'WsTextarea': set_text(n, 'value', CR.join(f'<p>- {ent(l)}</p>' for l in lignes))

ENTREES = [
    ('6 novembre 2026', [
        "Nouvelle présentation : design plus clair et plus actuel, menu en haut de page avec panneaux déroulants, aussi sur l'accueil",
        "Pages de rubrique (Ma mairie, Vie communale, Santé…) : une tuile par page avec sa description, les élus sur la page Mairie",
        "Accueil : nouvelles cartes d'évènements, sous-menus plus lisibles, badge « Village ambassadeur du don d'organes » repositionné",
        "Nouveau fil d'Ariane et nouveau pied de page",
        "Actualités : travaux et entretien de notre commune (poutre de l'ancienne salle des fêtes, cimetière, city stade)",
        "Mise à jour des médecins de garde (novembre 2026)",
    ]),
    ('4 et 5 novembre 2026', [
        "Actualité : un traiteur au marché des producteurs du 8 novembre",
        "Relecture complète du site : prochain conseil municipal (14 décembre), arrêtés terminés signalés, orthographe harmonisée",
        "Titres d'onglet des pages, liens mail et menus déroulants corrigés",
    ]),
    ('1er novembre 2026', [
        "Galeries photos : photos non déformées dans la visionneuse, vignettes au format d'origine",
        "Couleurs des étiquettes de catégorie plus contrastées, lisibles aussi par les personnes daltoniennes",
    ]),
    ('29 octobre 2026', [
        "Menu horizontal à 5 rubriques (Ma mairie, Ma commune, Évènements, Services, Démarches)",
        "Galerie « Notre village en images » : un album par évènement",
        "Conseil municipal : trombinoscope ; commissions communales : cartes avec les portraits des membres",
        "Boîte à idées : formulaire pour écrire directement à la mairie",
    ]),
]
entree_set(ref, *ENTREES[0])
pos = bloc['contents'].index(ref)
for i, (date, lignes) in enumerate(ENTREES[1:], 1):
    e = Page.clone(ref); entree_set(e, date, lignes)
    bloc['contents'].insert(pos + i, e)
Page.reindex(bloc)
H.save()

open(CSS, 'w', encoding='utf-8').write(css)
print('ok')
