#!/usr/bin/env python3
"""06/11/2026 — Casse des titres après la refonte visuelle.

Les anciens styles de titre forçaient la casse (minuscules + petites capitales pour Title et
Titre_main_page_sub, petites capitales pour Title2). Ils affichent désormais le texte tel quel :
les titres saisis tout en capitales ou sans majuscule initiale sont remis en casse normale
(accents rétablis sur les capitales).
"""
import sys, os, glob
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from sitelib import Page, plain, SITE

TITRES = {
    'FRANCE SERVICES': 'France Services',
    'LA CARTE COMMUNALE': 'La carte communale',
    'LA MISSION LOCALE DES DEUX RIVES': 'La Mission locale des Deux Rives',
    'LES ACCUEILS DE LOISIRS SANS HEBERGEMENT 3 A 11 ANS': 'Les accueils de loisirs sans hébergement (3 à 11 ans)',
    "LES DIFFÉRENTES DEMANDES D'AUTORISATION D'URBANISME": "Les différentes demandes d'autorisation d'urbanisme",
    'MULTI ACCUEIL 0 A 3 ANS': 'Multi-accueil (0 à 3 ans)',
    'OFFICE DE TOURISME': 'Office de tourisme',
    'RELAIS DE LA PETITE ENFANCE': 'Relais de la petite enfance',
    'chemins de randonnées': 'Chemins de randonnées',
    "l'aire de jeux": "L'aire de jeux",
    'notre pôle ADS': 'Notre pôle ADS',
    'évènements et Festivités à venir': 'Évènements et festivités à venir',
    "CONDITIONS GÉNÉRALES D'UTILISATION DU SITE": "Conditions générales d'utilisation du site",
    'HÉBERGEMENT DU SITE': 'Hébergement du site',
    'IDENTIFICATION': 'Identification',
    "boucles dans l'entre-deux-mers": "Boucles dans l'Entre-deux-Mers",
    'les randonnées partout en France': 'Les randonnées partout en France',
    'à la une': 'À la une',
    'à venir à baigneaux': 'À venir à Baigneaux',
}
n = 0
for f in sorted(glob.glob(os.path.join(SITE, 'pages', '*.json'))):
    p = Page(os.path.basename(f)[:-5]); changed = False
    for node, _ in p.walk():
        if node.get('$class') == 'WssTitle' and plain(node.get('value')) in TITRES:
            node['value'] = TITRES[plain(node['value'])]; changed = True; n += 1
    if changed: p.save()
print(n, 'titres corrigés'); assert n == len(TITRES), 'titre introuvable'
