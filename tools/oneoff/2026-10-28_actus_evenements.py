#!/usr/bin/env python3
"""28/10/2026 — rangées défilantes sur l'accueil (10 dernières actus, événements),
ajout des événements de novembre, mise à jour de la page Événements, ancre en double."""
import sys, os, json, re
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from sitelib import Page, T, set_text, ent

IMG = json.load(open('/tmp/newimgs.json'))
URL = 'https://www.baigneaux.fr'
CR = '\r\n'

def strip_width(cell):
    css = T(cell.get('embedded_css_rules'))
    if css:
        css2 = re.sub(r'\s*width:\s*[\d.]+%;', '', css)
        if re.fullmatch(r'\s*\.id_\w+\s*\{\s*\}\s*', css2): css2 = ''
        set_text(cell, 'embedded_css_rules', css2)

def clean_css(node):
    css = T(node.get('embedded_css_rules'))
    if 'undefined:' in css: set_text(node, 'embedded_css_rules', re.sub(r'\s*undefined:[^;]*;', '', css))

def add_class(node, cls):
    mc = node.get('more_classes') or ''
    if cls not in mc.split(): node['more_classes'] = (mc + ' ' + cls).strip()

def by_style(card, style_prefix):
    return [n for n, _ in Page._walk_static(card) if (n.get('user_style') or '').startswith(style_prefix)]

home = Page('home')

# ---------------------------------------------------------------- actus row
ref_card = home.find(lambda n: n.get('user_style') == 'Subdivision' and 'novation du cimeti' in json.dumps(n, ensure_ascii=False) and len(json.dumps(n)) < 20000)[0]
ps = home.parents(ref_card); ref_cell, actus_row = ps[-1], ps[-2]
assert len(actus_row['contents']) == 4

NEW_ACTUS = [  # (catégorie, style, date, titre, résumé, ancre, vignette, alt)
    ('Vie communale', 'vie_communale', '22 sept 2026', 'Rétrospective sur notre marché des producteurs',
     "Retour sur notre 3ème marché des producteurs du 13 septembre et sa baguette « la Baigneaudaise ».",
     'marche13092026', 'marche-producteurs-sept2026', 'Stand du marché des producteurs'),
    ('Sécurité', 'securite', '15 sept 2026', 'Incendie sur la commune',
     "Un incendie s'est déclaré à l'entrée du bourg, direction Bellebat. Retour sur l'intervention.",
     'incendie20260915', 'incendie-20260915', "Fumée de l'incendie au-dessus du bourg"),
    ('Vie communale', 'vie_communale', '27 juil 2026', 'Collecte de dons pour les évacués des incendies',
     "Notre collecte pour les évacués des incendies de l'ouest de la Gironde est terminée : merci à tous !",
     'donsincendies2026', 'collecte-dons-incendies-2026', 'Dons collectés à la salle des fêtes'),
    ('Santé', 'sante', '25 juil 2026', 'Feux de forêt en Gironde',
     "Passage en vigilance noire feux de forêt : mesures de restriction et conseils face aux fumées.",
     'feux072026', 'feux-foret-juillet-2026', 'Arrêté de vigilance noire feux de forêt'),
    ('Mairie', 'mairie', '21 juil 2026', 'Avancement des travaux route du Prieuré',
     "La première phase des travaux route du Prieuré est terminée, avec l'installation des caniveaux.",
     'prieure22026', 'travaux-route-prieure-2026', 'Travaux de caniveaux route du Prieuré'),
    ('Vie communale', 'vie_communale', '23 juin 2026', "Réalisation d'une fresque murale à l'école",
     "Les enfants de l'école ont réalisé une magnifique fresque sur le mur récemment repeint.",
     'fresque23062026', 'fresque-ecole-2026', "Fresque murale réalisée par les enfants de l'école"),
]

for cell in actus_row['contents']:
    strip_width(cell)
    add_class(cell['contents'][0], 'carte_actu')

for cat, style, date, title, summary, anchor, thumb, alt in NEW_ACTUS:
    cell = home.clone(ref_cell); card = cell['contents'][0]
    img = next(n for n, _ in Page._walk_static(card) if n['$class'] == 'WsImage')
    img.update({'value': IMG[thumb], 'uploaded_image': IMG[thumb], 'original_name': IMG[thumb],
                'tooltip': alt, 'width': '200', 'height': '90', 'in_gallery': '0'})
    c = by_style(card, 'bulle_actu_categorie_')[0]
    c['user_style'] = f'bulle_actu_categorie_{style}'; c['value'] = f'<p>{ent(cat)}</p>'
    by_style(card, 'bulle_actu_date')[0]['value'] = f'<p>{ent(date)}</p>'
    by_style(card, 'titre_bulle_actu')[0]['value'] = f'<p>{ent(title)}</p>'
    body = by_style(card, 'Texte_normal_align_gauche')[0]
    body['value'] = f'<p>{ent(summary)}</p>{CR}<p>&nbsp;</p>{CR}<p><a href="{URL}/actualites.html#{anchor}">Lire la suite -&gt;</a></p>'
    home.insert(actus_row, cell)

# ---------------------------------------------------------------- events row
noel_card = home.find(lambda n: n.get('user_style') == 'Subdivision' and 'March&eacute; de No&euml;l' in json.dumps(n, ensure_ascii=False) and len(json.dumps(n)) < 15000)[0]
ps = home.parents(noel_card); noel_cell, events_row = ps[-1], ps[-2]
assert len(events_row['contents']) == 3

NEW_EVENTS = [  # (jour, mois, titre, horaire, lieu, image, alt)
    ('8', 'NOV', 'Bénédiction des tombes', '14h30', 'Cimetière, suivi d’un café', 'benediction-tombes-2026',
     'Affiche de la bénédiction des tombes du 8 novembre 2026'),
    ('11', 'NOV', 'Commémoration du 11 novembre', '10h30 devant l’école', '11h au monument aux morts', 'armistice-11-novembre-2026',
     'Invitation à la commémoration de l’Armistice du 11 novembre 2026'),
    ('15', 'NOV', 'Marche solidaire Novembre bleu', '9h', 'Devant la salle des fêtes', 'marche-novembre-bleu-2026',
     'Affiche de la marche solidaire Novembre bleu du 15 novembre 2026'),
]
for cell in events_row['contents']:
    strip_width(cell)
    add_class(cell['contents'][0], 'carte_evenement')
    for n, _ in Page._walk_static(cell): clean_css(n)

for pos, (day, month, title, hour, place, poster, alt) in enumerate(NEW_EVENTS, start=1):
    cell = home.clone(noel_cell); card = cell['contents'][0]
    by_style(card, 'bulle_agenda')[0]['value'] = (f'<p><span style="font-size: 35px;">{day}</span></p>{CR}'
                                                 f'<p><span style="font-size: 25px;">{month}</span></p>')
    txt = by_style(card, 'Texte_normal_align_gauche')[0]
    txt['value'] = (f'<p><strong>{ent(title)}</strong></p>{CR}<p><span>&nbsp;</span></p>{CR}'
                    f'<p><span>🕒 {ent(hour)}</span></p>{CR}<p><span>&nbsp;📍&nbsp;{ent(place)}</span></p>')
    img = next(n for n, _ in Page._walk_static(card) if n['$class'] == 'WsImage')
    f, w, h = IMG[poster]['home']
    img.update({'value': f, 'uploaded_image': IMG[poster]['orig'], 'original_name': IMG[poster]['orig'],
                'tooltip': alt, 'width': str(w), 'height': str(h), 'in_gallery': '1'})
    home.insert(events_row, cell, pos)
home.save()

# ---------------------------------------------------------------- page Événements
ev = Page('p319-evenements-festivites')
t = ev.find(lambda n: n['$class'] == 'WssTitle' and n.get('value') == 'Octobre 2026')[0]
t['value'] = 'Novembre 2026'
marche = ev.find(lambda n: n.get('user_style') == 'Subdivision' and n.get('contents') and n['contents'][0].get('value') == 'Marché des producteurs - 11 octobre 2026')[0]
marche['contents'][0]['value'] = 'Marché des producteurs - 8 novembre 2026'
txt = next(n for n, _ in Page._walk_static(marche) if n['$class'] == 'WsTextarea')
v = T(txt['value'])
v = v.replace('Notre 4&egrave;me march&eacute; des producteurs vous attend le 11 octobre 2026',
              'Notre prochain march&eacute; des producteurs vous attend le dimanche 8 novembre 2026')
v = v.replace('Et nous rejoindra en novembre notre traiteur J&eacute;r&ocirc;me', 'Nous rejoindra &eacute;galement notre traiteur J&eacute;r&ocirc;me')
assert 'novembre 2026' in v and 'en novembre notre traiteur' not in v
set_text(txt, 'value', v)

noel_sub = ev.find(lambda n: n.get('user_style') == 'Subdivision' and n.get('contents') and n['contents'][0].get('value') == 'Marché de Noël - 5 décembre 2026')[0]
parent = ev.parents(marche)[-1]
PAGE_EVENTS = [
    ('Bénédiction des tombes - 8 novembre 2026', 'benediction-tombes-2026',
     ["À l'occasion de la Toussaint, l'équipe paroissiale de Targon-Cadillac procédera à la bénédiction des tombes "
      "au cimetière de Baigneaux le dimanche 8 novembre 2026, à partir de 14h30.",
      "La cérémonie sera suivie d'un café."],
     'Affiche de la bénédiction des tombes du 8 novembre 2026'),
    ("Commémoration de l'Armistice - 11 novembre 2026", 'armistice-11-novembre-2026',
     ["Un hommage sera rendu le mercredi 11 novembre 2026 à nos soldats morts pour la France.",
      "Le conseil municipal invite toutes les Baigneudaises et tous les Baigneudais à se rendre à 10h30 devant l'école, "
      "où un café sera offert, puis à 11h au monument aux morts.",
      "Le Maire énoncera les noms des anciens combattants, une minute de silence sera respectée et une gerbe sera déposée, "
      "en présence des pompiers de Targon et de la Gendarmerie de Créon.",
      "Un verre de l'amitié sera ensuite offert à la salle des fêtes."],
     "Invitation à la commémoration de l'Armistice du 11 novembre 2026"),
    ('Marche solidaire Novembre bleu - 15 novembre 2026', 'marche-novembre-bleu-2026',
     ["La mairie de Baigneaux organise une marche solidaire pour Novembre bleu, ensemble contre le cancer de la prostate, "
      "le dimanche 15 novembre 2026.",
      "Rendez-vous à 9h devant la salle des fêtes, pour un parcours de 8 km maximum."],
     'Affiche de la marche solidaire Novembre bleu du 15 novembre 2026'),
]
pos = parent['contents'].index(marche)
for i, (title, poster, paras, alt) in enumerate(PAGE_EVENTS, start=1):
    sub = ev.clone(noel_sub)
    sub['contents'][0]['value'] = title
    txt = next(n for n, _ in Page._walk_static(sub) if n['$class'] == 'WsTextarea')
    set_text(txt, 'value', CR.join(f'<p>{ent(p)}</p>' for p in paras))
    img = next(n for n, _ in Page._walk_static(sub) if n['$class'] == 'WsImage')
    f, w, h = IMG[poster]['page']
    img.update({'value': f, 'uploaded_image': IMG[poster]['orig'], 'original_name': IMG[poster]['orig'],
                'tooltip': alt, 'width': {'$d': str(w)}, 'height': {'$d': str(h)}})
    ev.insert(parent, sub, pos + i)
ev.save()

# ---------------------------------------------------------------- ancre en double (Actualités)
act = Page('p304-actualites')
retro = act.find(lambda n: n.get('user_style') == 'Subdivision' and 'Retrospective sur notre march' in Page.text(n) and len(json.dumps(n)) < 40000)[0]
fixed = 0
for n, _ in Page._walk_static(retro):
    v = T(n.get('value'))
    if 'id="fresque23062026"' in v:
        set_text(n, 'value', v.replace('id="fresque23062026"', 'id="marche13092026"')); fixed += 1
assert fixed == 1, fixed
act.save()
print('ok: actus', len(actus_row['contents']), '| événements', len(events_row['contents']))
