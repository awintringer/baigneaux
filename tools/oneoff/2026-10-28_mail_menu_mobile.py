#!/usr/bin/env python3
"""28/10/2026 (soir) — adresse officielle mairie@baigneaux.fr partout, actu dédiée (accueil +
fiche Actualités), en-tête mobile refait (modèle menu_burger), ancre OTV en triple corrigée."""
import sys, os, re, glob, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from sitelib import Page, T, set_text, ent, SITE

OLD, NEW = 'communede.baigneaux@wanadoo.fr', 'mairie@baigneaux.fr'
URL, CR = 'https://www.baigneaux.fr', '\r\n'

# ---------------------------------------------------------------- 1. adresse mail partout
n_files = n_occ = 0
for f in glob.glob(f'{SITE}/*/*.json'):
    s = open(f, encoding='utf-8').read()
    if OLD in s:
        n_occ += s.count(OLD); n_files += 1
        open(f, 'w', encoding='utf-8').write(s.replace(OLD, NEW))
print(f'mail : {n_occ} occurrences remplacées dans {n_files} fichiers')

# ---------------------------------------------------------------- 2. fiche sur la page Actualités
act = Page('p304-actualites')
oct_title = act.find(lambda n: n['$class'] == 'WssTitle' and n.get('value') == 'Octobre 2026')[0]
parent = act.parents(oct_title)[-1]
tpl = [n for n in act.find(lambda n: n.get('user_style') == 'Subdivision' and 'chetterie verte' in Page.text(n)) if len(json.dumps(n)) < 30000][-1]
fiche = act.clone(tpl)
cat, date = fiche['contents'][0]['contents']          # rangée catégorie / date
cat['contents'][0]['value'] = '<p id="mail2026">Mairie</p>'
date['contents'][0]['value'] = '<p>28 octobre 2026</p>'
fiche['contents'][1]['value'] = 'Nouvelle adresse mail officielle de la mairie'
body = (f'<p>La mairie de Baigneaux dispose d&eacute;sormais d\'une adresse mail officielle&nbsp;: '
        f'<a href="mailto:{NEW}">{NEW}</a></p>{CR}<p>&nbsp;</p>{CR}'
        f'<p>Elle remplace l\'ancienne adresse en wanadoo.fr. Merci de l\'utiliser pour toutes vos demandes '
        f'et de mettre &agrave; jour vos carnets d\'adresses.</p>{CR}<p>&nbsp;</p>{CR}'
        f'<p>Le t&eacute;l&eacute;phone de la mairie ne change pas&nbsp;: <a href="tel:0556239750">05 56 23 97 50</a>.</p>')
set_text(fiche['contents'][2], 'value', body)
fiche['contents'][3]['value'] = '<p>&nbsp;&nbsp;</p>'
act.insert(parent, fiche, parent['contents'].index(oct_title) + 1)

# ancre OTV : seule la fiche « Opération Tranquilité vacances » la garde
fixed = 0
for sub in act.find(lambda n: n.get('user_style') == 'Subdivision' and len(json.dumps(n)) < 30000):
    if 'Opération Tranquilité vacances' in Page.text(sub): continue
    for n, _ in Page._walk_static(sub):
        v = T(n.get('value'))
        if '<p id="OTV">' in v:
            set_text(n, 'value', v.replace('<p id="OTV">', '<p>')); fixed += 1
print('ancres OTV retirées :', fixed)
act.save()

# ---------------------------------------------------------------- 3. carte sur l'accueil
home = Page('home')
cards = home.find(lambda n: 'carte_actu' in (n.get('more_classes') or ''))
row = home.parents(cards[0])[-2]
sdf = next(c for c in cards if 'tarifs de location' in Page.text(c))
cell = home.clone(home.parents(sdf)[-1]); card = cell['contents'][0]
for n, _ in Page._walk_static(card):
    st = n.get('user_style') or ''
    if st == 'bulle_actu_date': n['value'] = '<p>28 oct 2026</p>'
    elif st == 'titre_bulle_actu': n['value'] = '<p>Nouvelle adresse mail de la mairie</p>'
    elif st == 'Texte_normal_align_gauche':
        n['value'] = (f'<p>L\'adresse officielle de la mairie est d&eacute;sormais {NEW}.</p>{CR}<p>&nbsp;</p>{CR}'
                      f'<p><a href="{URL}/actualites.html#mail2026">Lire la suite -&gt;</a></p>')
    elif n['$class'] == 'WsImage': n['tooltip'] = 'Logo de Baigneaux'
home.insert(row, cell, 0)
oldest = row['contents'][-1]
assert 'fresque' in Page.text(oldest).lower(), Page.text(oldest)[:60]
home.remove(oldest)                                    # on garde les 10 dernières
assert len(row['contents']) == 10
home.save()

# ---------------------------------------------------------------- 4. en-tête mobile (modèle menu_burger)
mb = Page('models/menu_burger')
sub = mb.root['contents'][0]; hrow = sub['contents'][0]
c_menu, c_text, c_img = hrow['contents']
menu, text, img = c_menu['contents'][0], c_text['contents'][0], c_img['contents'][0]
c_menu['contents'], c_img['contents'] = [img], [menu]          # armoiries à gauche, menu à droite
for cell_, w in ((c_menu, 22), (c_text, 46), (c_img, 32)):
    set_text(cell_, 'embedded_css_rules', f'.id_{cell_["id"]} {{\r\n\twidth: {w}%;\r\n}}\r')
set_text(img, 'embedded_css_rules', f'.id_{img["id"]} {{\r\n\tmargin-left: 0;\r\n\tmargin-right: auto;\r\n}}\r')
text['value'] = f'<p><a href="{URL}/home.html">Baigneaux</a></p>'
text['more_classes'] = 'titre_mobile'
set_text(text, 'embedded_css_rules', '')
sub['more_classes'] = (sub.get('more_classes') or '') + ' entete_mobile'
mb.save()
print('ok')
