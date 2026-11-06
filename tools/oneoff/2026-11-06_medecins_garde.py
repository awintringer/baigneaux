#!/usr/bin/env python3
"""06/11/2026 — Page « Médecins de garde » (p324) : planning de novembre 2026.

Remplace le titre (« … septembre 2026 » → « … novembre 2026 ») et le bloc de texte (planning d'octobre)
en gardant la structure existante : un paragraphe `id="medgard"` par ligne, une ligne vide entre
deux gardes, emoji en tête de chaque date. Source : texte de l'application d'alerte de la commune
(« Info modifiée le 06/11/2026 »).
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from sitelib import Page, ent

MOIS = 'Novembre'
GARDES = [  # (emoji, date, médecin, commune, téléphone)
    ('💊', 'Week-end du 7 novembre', "Docteur Maud D'OLIVO", 'Sauveterre de Guyenne', '05.56.71.01.27'),
    ('🚑', 'Mercredi 11 novembre', 'Docteur Lisa PARRET', 'Rauzan', '05.33.03.00.33'),
    ('💉', 'Week-end du 14 novembre', 'Docteur Alexia RENAUD', 'Frontenac', '05.56.23.54.93'),
    ('🚒', 'Week-end du 21 novembre', 'Docteur Nicolas GOUJON', 'Targon', '05.56.23.90.17'),
    ('🩺', 'Week-end du 28 novembre', 'Docteur Emilie PALLUD', 'Rauzan', '05.33.03.00.33'),
]

SPAN = '<span style="font-size: 12.8px;">%s</span>'
def ligne(txt): return '<p id="medgard">' + SPAN % ent(txt) + '</p>'
VIDE = '<p>' + SPAN % '&nbsp;' + '</p>'

lines = [ligne(f'Médecins de garde pour le mois de {MOIS}'), VIDE]
for i, (emo, date, med, ville, tel) in enumerate(GARDES):
    lines += [ligne(f'{emo} {date} :'), ligne(f'{med} - {ville} - {tel}')]
    if i < len(GARDES) - 1: lines.append(VIDE)

p = Page('p324-medecins_de_garde')
(txt,) = p.find(lambda n: n.get('$class') == 'WsTextarea' and 'medgard' in '\n'.join(
    n['value']['$text'] if isinstance(n.get('value'), dict) else [n.get('value') or '']))
txt['value'] = {'$text': [l + '\r' for l in lines[:-1]] + [lines[-1]]}
(titre,) = p.find(lambda n: n.get('$class') == 'WssTitle' and 'garde' in n.get('value', ''))
titre['value'] = 'Médecins de garde - novembre 2026'
p.save()
print('ok :', titre['value'], '/', len(GARDES), 'gardes')
