#!/usr/bin/env python3
"""28/10/2026 — page « Historique des versions » : entrées de fin septembre/octobre et du 28 octobre."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from sitelib import Page, set_text, ent

ENTRIES = [
    ('28 octobre 2026', [
        "Accueil : actualités et évènements à venir présentés en rangées défilantes (10 dernières actualités, tous les évènements à venir)",
        "Ajout des évènements de novembre : bénédiction des tombes (8/11), commémoration du 11 novembre, marche solidaire Novembre bleu (15/11) ; page Évènements mise à jour",
        "Adresse mail officielle mairie@baigneaux.fr sur tout le site, avec une actualité dédiée",
        "Nouvel en-tête et nouveau menu pour smartphone",
        "Affichage corrigé sur tablette et smartphone (en-tête, titres, menus, encadrés)",
        "Icônes vectorielles des encadrés de l'accueil",
        "Polices de caractères hébergées sur le site (plus de chargement depuis Google)",
        "Textes alternatifs sur les images (accessibilité)",
        "Corrections de liens dans les actualités",
    ]),
    ('Fin septembre - octobre 2026', [
        "Actualités : tarifs de location de la salle des fêtes, rénovation du cimetière, photos de la fête du village et de la Maïade",
        "Mise à jour de la galerie photos, des médecins de garde, des arrêtés préfectoraux, de la salle des fêtes et des demandes d'autorisation d'urbanisme",
        "Prochain conseil municipal (2 novembre) et sa convocation",
    ]),
]
p = Page('p327-historique-modifications')
tpl = [n for n in p.find(lambda n: n.get('user_style') == 'Subdivision' and n.get('contents') and n['contents'][0].get('value') == '22 septembre 2026')][-1]
parent = p.parents(tpl)[-1]; pos = parent['contents'].index(tpl)
for i, (date, lines) in enumerate(ENTRIES):
    sub = p.clone(tpl)
    sub['contents'][0]['value'] = date
    txt = next(n for n, _ in Page._walk_static(sub) if n['$class'] == 'WsTextarea')
    set_text(txt, 'value', '\r\n'.join(f'<p>- {ent(l)}</p>' for l in lines))
    p.insert(parent, sub, pos + i)
p.save(); print('ok')
