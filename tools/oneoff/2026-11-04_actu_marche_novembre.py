#!/usr/bin/env python3
"""04/11/2026 — actu « Nouveauté au marché des producteurs » (dimanche 8 novembre, 9h, traiteur
Antonio) : fiche sous un nouveau titre « Novembre 2026 » de la page Actualités (ancre
#marche08112026) et carte en tête de l'accueil (la plus ancienne sort, 10 cartes)."""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from sitelib import Page, set_text, ent

URL, CR, ANCHOR = 'https://www.baigneaux.fr', '\r\n', 'marche08112026'

PARAS = [
    "🍽️ NOUVEAUTÉ AU MARCHÉ DES PRODUCTEURS DE BAIGNEAUX ! 🧺",
    "Le marché des producteurs de Baigneaux revient bientôt ! L'occasion de retrouver nos producteurs locaux, "
    "ou de découvrir leurs bons produits et de partager un moment convivial au cœur de notre commune.",
    "🌟 Et pour cette édition, une nouveauté de taille : nous accueillerons pour la toute première fois un traiteur ! "
    "Antonio nous rejoint à partir de ce dimanche 😍",
    "Au menu : des plats chauds, préparés pour l'occasion, à déguster sur place pour profiter pleinement du marché "
    "ou à emporter à la maison. 😋",
    "Que vous veniez faire vos emplettes, découvrir les produits de nos producteurs ou simplement passer un bon moment "
    "entre habitants, nous vous attendons nombreux !",
    "📍 <strong>Rendez-vous à Baigneaux ce dimanche 8 novembre à partir de 9h !</strong>",
    "N'hésitez pas à partager l'information autour de vous et à venir accompagnés !",
    "À très bientôt sur le marché ! 😊",
]

def html_para(p):  # ent() sur le texte, balises <strong> conservées
    return ent(p.replace('<strong>', '\0').replace('</strong>', '\1')).replace('\0', '<strong>').replace('\1', '</strong>')

# ---------------------------------------------------------------- fiche sur la page Actualités
act = Page('p304-actualites')
assert not act.find(lambda n: ANCHOR in json.dumps(n.get('value') or '')), 'actu déjà présente'
oct_title = act.find(lambda n: n['$class'] == 'WssTitle' and n.get('value') == 'Octobre 2026')[0]
parent = act.parents(oct_title)[-1]
pos = parent['contents'].index(oct_title)
nov_title = act.clone(oct_title); nov_title['value'] = 'Novembre 2026'
tpl = [n for n in act.find(lambda n: n.get('user_style') == 'Subdivision'
                           and 'Nouvelle adresse mail officielle' in Page.text(n)) if len(json.dumps(n)) < 30000][-1]
fiche = act.clone(tpl)
cat, date = fiche['contents'][0]['contents']
cat['contents'][0]['value'] = f'<p id="{ANCHOR}">Vie communale</p>'
date['contents'][0]['value'] = '<p>4 novembre 2026</p>'
fiche['contents'][1]['value'] = 'Nouveauté au marché des producteurs'
set_text(fiche['contents'][2], 'value', f'{CR}<p>&nbsp;</p>{CR}'.join(f'<p>{html_para(p)}</p>' for p in PARAS))
act.insert(parent, nov_title, pos)
act.insert(parent, fiche, pos + 1)
act.save()

# ---------------------------------------------------------------- carte sur l'accueil
home = Page('home')
cards = home.find(lambda n: 'carte_actu' in (n.get('more_classes') or ''))
row = home.parents(cards[0])[-2]
ref = next(c for c in cards if 'Rétrospective sur notre marché' in Page.text(c))
cell = home.clone(home.parents(ref)[-1]); card = cell['contents'][0]
for n, _ in Page._walk_static(card):
    st = n.get('user_style') or ''
    if st == 'bulle_actu_date': n['value'] = '<p>4 nov 2026</p>'
    elif st == 'titre_bulle_actu': n['value'] = f'<p>{ent("Marché des producteurs ce dimanche")}</p>'
    elif st == 'Texte_normal_align_gauche':
        n['value'] = (f'<p>{ent("Dimanche 8 novembre dès 9h, et pour la première fois un traiteur : Antonio et ses plats chauds !")}</p>'
                      f'{CR}<p>&nbsp;</p>{CR}<p><a href="{URL}/actualites.html#{ANCHOR}">Lire la suite -&gt;</a></p>')
    elif n['$class'] == 'WsImage': n['tooltip'] = 'Stand du marché des producteurs de Baigneaux'
home.insert(row, cell, 0)
oldest = row['contents'][-1]
assert 'Prieuré' in Page.text(oldest), Page.text(oldest)[:60]
home.remove(oldest)                                    # on garde les 10 dernières
assert len(row['contents']) == 10
home.save()
print('ok')
