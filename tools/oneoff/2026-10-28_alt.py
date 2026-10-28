#!/usr/bin/env python3
"""28/10/2026 — textes alternatifs des images (champ « info-bulle » de WebSiCo, rendu en alt + title).
Règles : logos et icônes connus, puis corrections par fichier, puis titre de section le plus proche
(ou nom de la page), numéroté quand plusieurs images partagent le même contexte."""
import sys, os, re, glob, collections
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from sitelib import Page, plain, SITE

FIXED = [
    (r'^logosite', 'Logo de Baigneaux'), (r'^armoiries', 'Armoiries de Baigneaux'),
    (r'^horaires', 'Horaires d’ouverture'), (r'^contact', 'Nous contacter'),
    (r'^conseil', 'Conseil municipal'), (r'^lecteur_puce', 'Lecteur de puce électronique'),
    (r'^village-ambassadeur', 'Baigneaux, village ambassadeur du don d’organes'),
    (r'^805936917_.*-e8f7', 'Marché des producteurs devant la salle des fêtes'),
    (r'^march--noel2026', 'Affiche du marché de Noël 2026'),
    (r'^flyer_noel_2026', 'Affiche du spectacle de Noël 2026'),
    (r'^noel-f338', 'Affiche du spectacle de Noël 2026'),
    (r'^assistante', 'Assistantes maternelles'),
    (r'^relais', 'Relais de la petite enfance'),
    (r'^multi-accueil', 'Multi-accueil 0 à 3 ans'),
    (r'^loisirs', 'Accueils de loisirs sans hébergement 3 à 11 ans'),
    (r'^moulin', 'Moulin sur la boucle de Soulignac'),
    (r'^entre_deux_mers_balades', 'Balades et randonnées dans l’Entre-deux-Mers'),
    (r'^logo_visorando', 'Visorando, randonnées partout en France'),
    (r'^randogps', 'RandoGPS, randonnées partout en France'),
    (r'^odyssee2m', 'L’Odyssée de l’Entre-Deux-Mers'),
    (r'^ape\.', 'APE entre 3 écoles, association de parents d’élèves'),
    (r'^service-civique-cdc', 'Service civique à la CdC Rurales de l’Entre-Deux-Mers'),
    (r'^mission-locale', 'Garantie Jeunes avec la Mission locale des 2 Rives'),
    (r'^erip', 'ERIP Sud Gironde, espace régional d’information et de proximité'),
    (r'^emploi-jeunes-1', '1 jeune 1 solution : 16-18 ans sans école, formation ni emploi'),
    (r'^emploi-jeunes-2', '1 jeune 1 solution : appelez le 0 800 122 500'),
    (r'^donna-libera', 'Atelier Retouches Donna Libera'),
    (r'^tl-plomberie', 'Flyer de TL Plomberie'),
    (r'^lam-btp', 'L.A.M BTP'),
    (r'^3\.jpg$', 'Mobilité solidaire : covoiturage, vélos électriques et transport solidaire'),
    (r'^1-4906', 'Le TUS, transport d’utilité sociale'),
    (r'^2-87ff', 'Prêt de vélos électriques par la CdC'),
    (r'^fetebaigneaux2026flyer', 'Affiche de la fête du village 2026'),
    (r'^674619328_', 'Affiche de la journée citoyenne du 10 mai 2026'),
    (r'^marche-producteur-7-juin-2026', 'Affiche du marché des producteurs du 7 juin 2026'),
    (r'^paque2026', 'Affiche de Pâques 2026'),
    (r'^noel2025', 'Affiche de Noël 2025'),
    (r'^fete2025', 'Affiche de la fête du village 2025'),
    (r'^11nov', 'Affiche de la commémoration du 11 novembre'),
    (r'^otv', 'Opération Tranquillité Vacances'),
    (r'^porter-plainte', 'Porter plainte en ligne'),
    (r'^servicespublics33', 'Services publics 33'),
    (r'^bouton_annuaire', 'Annuaire des services'),
    (r'^cdc\.png', 'CdC Rurales de l’Entre-Deux-Mers'),
    (r'^menu_sept2026', 'Menu de la cantine, septembre 2026'),
    (r'^menu_oct2026', 'Menu de la cantine, octobre 2026'),
]
MONTH = r'(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)'
TITLE_STYLES = {'titre_bulle_actu', 'titre_grosse_bulle_actu'}

def sentence(t):
    t = t.strip(' :')
    if t.isupper() and len(t) > 4: t = t[0] + t[1:].lower()
    return t[0].upper() + t[1:] if t else t

def is_title(c, gallery):
    if c['$class'] == 'WssTitle': return True
    st = c.get('user_style') or ''
    return c['$class'] == 'WsTextarea' and (st in TITLE_STYLES or (gallery and st == 'Texte_important_centre'))

done = collections.Counter()
for f in sorted(glob.glob(f'{SITE}/pages/*.json') + glob.glob(f'{SITE}/models/*.json')):
    p = Page(os.path.relpath(f, SITE)[:-5]); pname = p.data['row'][4] or ''
    gallery = 'galerie' in f
    pending = []
    def visit(n, titles):
        titles = list(titles)
        for c in n.get('contents') or []:
            if is_title(c, gallery):
                t = plain(c.get('value'))
                if t and not re.fullmatch(MONTH + r'? ?\d{4}', t.lower()) and t.lower() != 'historique': titles.append(sentence(t))
            if c['$class'] == 'WsImage':
                if not (c.get('tooltip') or c.get('caption')) and c.get('value') not in (None, '', '0'):
                    pending.append((c, titles[-1] if titles else sentence(pname or 'Baigneaux')))
            else:
                visit(c, titles)
    visit(p.root, [])
    seen = collections.Counter(); totals = collections.Counter(ctx for c, ctx in pending if not any(re.search(rx, c['value']) for rx, _ in FIXED))
    for c, ctx in pending:
        alt = next((a for rx, a in FIXED if re.search(rx, c['value'])), None)
        if alt is None:
            seen[ctx] += 1
            alt = ctx if totals[ctx] == 1 else f'{ctx} – photo {seen[ctx]}'
        c['tooltip'] = alt; done[os.path.basename(f)] += 1
    if pending: p.save()
print(sum(done.values()), 'images renseignées sur', len(done), 'fichiers')
