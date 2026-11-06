#!/usr/bin/env python3
"""06/11/2026 — Retouches après la refonte graphique (retours d'Adrien sur l'export dev du 06/11).

  1. Accueil : la barre de navigation de la bannière devient une instance du modèle Header2
     (mêmes panneaux déroulants que les autres pages, plus de copie à maintenir) ; « Baigneaux »
     aligné sur les boutons (rangée en flex centrée verticalement, partout).
  2. Menu vertical de l'accueil : sous-menus en carte (arrondi, ombre, fond blanc, sans trous).
  3. Pages de rubrique (« pages de transition ») : titre, chapô, tuiles cliquables vers chaque
     page avec une phrase de description ; la page Mairie montre en plus le maire et les adjoints.
  4. Badge « Village ambassadeur du don d'organes » : pastille posée en bas à droite de l'image.
  5. Bannière : illustration vectorielle façon affiche (site/data/images/background/banniere-affiche.svg,
     générée par tools/banniere/make_banniere.py) à la place de la photo basse définition.
  6. Fil d'Ariane : « Accueil » avec pictogramme maison, séparateurs chevrons, page courante en gras
     non soulignée, le tout dans une barre discrète.
Lancer depuis l'export du 06/11/2026 (commit « Export du 06/11/2026 (dev, après refonte graphique) »).
"""
import os, re, sys, json, copy
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
from sitelib import Page, new_id, ent, set_text, T, SITE
from album import container, textarea

ROOT = os.path.dirname(SITE)
CSS = os.path.join(SITE, 'css', 'default.css')
css = open(CSS, encoding='utf-8').read()
URL = 'https://www.baigneaux.fr'
VIGNE, ENCRE, TRAIT, SAUGE, PIERRE = '#2F5E3E', '#1F2A23', '#DDE2D9', '#E6EEE6', '#5F6B60'
LARGE = '(min-width: 641px)'


def setp(sel, props):
    """Modifie les propriétés d'une règle gérée (en-tête exact `sel {`). None = supprimer."""
    global css
    m = re.search(r'(?m)^' + re.escape(sel) + r' \{\n(.*?)\n\}', css, flags=re.S)
    assert m, sel
    lines = m.group(1).split('\n') if m.group(1) else []
    for prop, val in props.items():
        lines = [l for l in lines if not re.match(r'\t' + re.escape(prop) + r'\s*:', l)]
        if val is not None: lines.append(f'\t{prop}: {val};')
    css = css[:m.start(1)] + '\n'.join(lines) + css[m.end(1):]


def media(sel, body, cond='all'):
    """Ajoute un bloc @media d'une seule règle (sélecteur multiple autorisé)."""
    global css
    decl = '\n'.join(f'\t\t{k}: {v};' for k, v in body.items())
    css = css.rstrip('\n') + f'\n@media {cond} {{\n\t{sel} {{\n{decl}\n\t}}\n}}\n'


def drop_media(sel, cond='all'):
    """Retire un bloc @media d'une règle (sélecteur exact)."""
    global css
    pat = r'@media ' + re.escape(cond) + r' \{\n\t' + re.escape(sel) + r' \{\n.*?\n\t\}\n\}\n'
    css, n = re.subn(pat, '', css, flags=re.S)
    assert n, sel


# ================================================================ 1. accueil : en-tête = modèle Header2
home = Page('home')
ban = home.find(lambda n: n.get('user_style') == 'Banniere')[0]
nav = ban['contents'][0]
assert nav.get('name_in_model') == 'MZ156a19b6a4141f9'           # ancienne copie détachée de la rangée
model = json.load(open(os.path.join(SITE, 'models', 'Header2.json'), encoding='utf-8'))['row'][-1]['$php']
inst = Page.clone(model['contents'][0])
inst.update({'model_id': 'Header2', 'properties': 270400, 'owner': {'$owner': 'R'}, 'index': 0})
ban['contents'][0] = inst
Page.reindex(ban)

# l'en-tête posé dans la bannière perd son cadre (la bannière est déjà la carte blanche)
media('.wscontainer_Banniere > .wscontainer_BodyHome',
      {'margin': '0', 'padding': '0 0 6px', 'border': '0', 'border-bottom': f'1px solid {TRAIT}',
       'border-radius': '0', 'background-color': 'transparent', 'max-width': 'none'})
drop_media('.wscontainer_Banniere > .wssystemcontainer.H:first-child')

# « Baigneaux » et les 5 boutons sur une même ligne médiane
RANGEE = '.wssystemcontainer.H:has(> div > .wstextarea_retour_accueil)'
media(RANGEE, {'display': 'flex !important', 'align-items': 'center', 'justify-content': 'space-between'}, LARGE)
media(RANGEE + ' > div', {'display': 'block !important', 'flex': '0 1 auto', 'width': 'auto !important'}, LARGE)
setp('.wstextarea_retour_accueil', {'padding-top': '0px', 'margin-top': '0px', 'line-height': '1'})
setp('.wstextarea_retour_accueil a', {'min-height': '56px', 'line-height': '1'})
setp('.wstextarea_Lien_header', {'margin-top': '0px'})

# ================================================================ 2. sous-menus du menu vertical de l'accueil
media('.wssmenu_Main ul.submenu',
      {'background-color': '#FFFFFF', 'border': f'1px solid {TRAIT}', 'border-radius': '12px',
       'box-shadow': '0 10px 28px rgba(31, 42, 35, 0.18), 0 2px 6px rgba(31, 42, 35, 0.08)',
       'padding': '6px !important', 'margin-left': '6px', 'overflow': 'hidden'}, LARGE)
media('.wssmenu_Main ul.submenu a',
      {'margin': '0 !important', 'border-radius': '8px', 'background-color': 'transparent !important',
       'padding': '9px 14px !important', 'font-size': '0.95em'}, LARGE)
media('.wssmenu_Main ul.submenu a:hover,\n\t.wssmenu_Main ul.submenu a:focus-visible',
      {'background-color': f'{SAUGE} !important', 'color': f'{VIGNE} !important', 'transform': 'none'}, LARGE)
media('.wssmenu_Main ul.submenu a::after', {'display': 'none'}, LARGE)

setp('.wssmenu_Main a.hover', {'background-color': SAUGE})

# ================================================================ 4. badge « Village ambassadeur du don d'organes »
badge = home.find(lambda n: n.get('$class') == 'WsImage' and 'ambassadeur' in (n.get('value') or ''))[0]
assert badge in ban['contents']
badge['embedded_css_rules'] = ''
badge['more_classes'] = 'badge_ambassadeur'
media('.wscontainer_Banniere', {'position': 'relative'})
media('.wscontainer_Banniere > .wsimage.badge_ambassadeur',
      {'position': 'absolute', 'right': '22px', 'bottom': '20px', 'z-index': '2'}, LARGE)
media('.wsimage.badge_ambassadeur',
      {'background-color': '#FFFFFF', 'border-radius': '12px', 'padding': '6px 8px', 'max-width': 'none !important',
       'box-shadow': '0 6px 18px rgba(31, 42, 35, 0.22)', 'margin': '0', 'line-height': '0'})
media('.wsimage.badge_ambassadeur img', {'width': '170px', 'height': 'auto', 'display': 'block'})

# ================================================================ 5. bannière en illustration (tools/banniere/make_banniere.py)
import subprocess
subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'banniere', 'make_banniere.py')], check=True)
NAV = '84px'
setp('.wscontainer_Banniere', {'background-image': 'url(data/images/background/banniere-affiche.svg)',
                               'background-position': f'0px {NAV}', 'background-size': f'100% calc(100% - {NAV})',
                               'min-height': '400px'})

# ================================================================ 6. fil d'Ariane
MAISON = os.path.join(SITE, 'data', 'images', 'background', 'icone-maison.svg')
open(MAISON, 'w', encoding='utf-8').write(
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" '
    f'stroke="{VIGNE}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">'
    '<path d="M3 11.5 12 4l9 7.5"/><path d="M5.5 10v9.5h4.5v-5.5h4v5.5h4.5V10"/></svg>\n')
pf = os.path.join(SITE, 'models', 'Path.json')
pm = json.load(open(pf, encoding='utf-8'))
for n, _ in Page._walk_static(pm['row'][-1]['$php']):
    if n.get('$class') == 'WsTextarea' and n.get('user_style') == 'Path':
        n['value'] = f'<p><a href="{URL}/home.html">Accueil</a></p>'
with open(pf, 'w', encoding='utf-8') as fh:
    json.dump(pm, fh, ensure_ascii=False, indent=1); fh.write('\n')
# le bloc qui contient ce texte est « contenu libre dans le modèle » (bit 7) : chaque page garde sa copie
import glob
nb = 0
for f in sorted(glob.glob(os.path.join(SITE, 'pages', '*.json'))):
    pg = Page(os.path.basename(f)[:-5])
    cibles = pg.find(lambda n: n.get('name_in_model') == 'MY557f20acc196b')
    for n in cibles:
        n['value'] = f'<p><a href="{URL}/home.html">Accueil</a></p>'
    if cibles: pg.save(); nb += 1
print(nb, "pages : fil d'Ariane")

setp('.wscontainer_Path', {'font-size': '14px', 'color': PIERRE})
setp('.wstextarea_Path', {'font-size': '1em', 'font-weight': '500'})
setp('.wstextarea_Path a', {'color': VIGNE, 'text-decoration': 'none', 'font-weight': '500'})
setp('.wsspagepath_Path', {'font-size': '0px', 'color': PIERRE})
setp('.wsspagepath_Path a', {'font-size': '14px', 'text-decoration': 'none', 'padding-left': '0px', 'color': VIGNE,
                             'font-weight': '500'})
setp('.wsspagepath_Path a:hover, .wsspagepath_Path a.hover', {'text-decoration': 'underline'})
drop_media('.wscontainer_Path')
media('.wscontainer_Path',
      {'display': 'inline-block', 'width': 'auto !important', 'margin': '10px 14px 2px', 'padding': '7px 16px 7px 12px',
       'background-color': '#FFFFFF', 'border': f'1px solid {TRAIT}', 'border-radius': '999px', 'box-sizing': 'border-box'})
media('.wscontainer_Path .wscontainer', {'padding': '0 !important', 'margin': '0 !important', 'border-width': '0 !important'})
media('.wscontainer_Path .wssystemcontainer.H',
      {'align-items': 'center !important', 'gap': '0 !important'})
media('.wscontainer_Path .wssystemcontainer.H > div,\n\t.wsspagepath_Path',
      {'display': 'flex !important', 'align-items': 'center', 'height': '20px'})
media('.wscontainer_Path .wstextarea_Path,\n\t.wstextarea_Path p,\n\t.wsspagepath_Path', {'margin': '0 !important', 'padding': '0 !important', 'line-height': '20px'})
media('.wstextarea_Path a::before',
      {'content': '""', 'display': 'inline-block', 'width': '17px', 'height': '17px', 'margin-right': '6px',
       'vertical-align': '-3px', 'background-image': 'url(data/images/background/icone-maison.svg)',
       'background-size': '17px 17px'})
media('.wstextarea_Path p::after,\n\t.wsspagepath_Path a + a::before',
      {'content': '""', 'display': 'inline-block', 'width': '6px', 'height': '6px', 'margin': '0 12px 0 10px',
       'border-right': f'1.6px solid {PIERRE}', 'border-top': f'1.6px solid {PIERRE}', 'transform': 'rotate(45deg)',
       'vertical-align': '2px'})
media('.wsspagepath_Path a:last-child',
      {'color': ENCRE, 'font-weight': '600', 'pointer-events': 'none'})

# ================================================================ 3. pages de rubrique : tuiles au lieu du simple menu
# (titre de tuile, page, description) ; une page ajoutée plus tard dans une rubrique apparaît dans le
# menu du haut automatiquement, mais sa tuile est à ajouter ici (voir docs/RUBRIQUES.md).
RUBRIQUES = {
    'p207-mairie': ("Ma mairie", "Le conseil municipal, ses décisions et vos démarches auprès de la mairie.", [
        ("Conseil municipal", 'conseil-municipal', "Le maire, les adjoints et les conseillers municipaux."),
        ("Commissions communales", 'commissions', "Les commissions de travail du conseil et leurs membres."),
        ("Procès-verbaux des conseils", 'pv-conseil', "Le compte rendu de chaque séance du conseil municipal."),
        ("Délibérations", 'deliberations', "Les décisions adoptées par le conseil, classées par année."),
        ("Arrêtés municipaux", 'arretes', "Les arrêtés du maire : circulation, sécurité, chasse…"),
        ("Arrêtés préfectoraux", 'arretes-prefectoraux', "Les arrêtés du préfet qui concernent la commune."),
        ("Formalités administratives", 'formalites-administratives', "Carte d'identité, passeport, élections, recensement militaire…"),
        ("Boîte à idées", 'boite-a-idees', "Une idée, une remarque, un problème à signaler ? Écrivez à la mairie."),
    ]),
    'p220-vie-communale': ("Vie communale", "Les lieux, les équipements et les souvenirs partagés du village.", [
        ("Notre village en images", 'galerie-evenements', "Les albums photo des fêtes et des rendez-vous du village."),
        ("Salle des fêtes", 'salle-fetes', "Tarifs et conditions de location de la salle des fêtes."),
        ("Aire de jeux et city stade", 'aire-jeux', "City stade, terrain de pétanque et jeux d'enfants, dans le bourg."),
        ("Patrimoine", 'patrimoine', "Histoire, chiffres clés et patrimoine de la commune."),
        ("Plateforme déchets verts", 'p320', "Le dépôt de déchets verts de l'impasse de Racaud, ouvert 24 h/24."),
    ]),
    'p210-enfance-jeunesse': ("Enfance et jeunesse", "De la petite enfance à l'adolescence : écoles, modes de garde et loisirs.", [
        ("Écoles (RPI)", 'RPI', "Le regroupement pédagogique de Frontenac et ses cinq communes."),
        ("Petite enfance et périscolaire", 'asmat', "Assistantes maternelles, relais petite enfance, multi-accueil et centres de loisirs."),
        ("Jeunesse", 'jeunesse', "Les espaces jeunes pour les 11-17 ans autour de Baigneaux."),
    ]),
    'p328': ("Santé", "Se soigner près de chez soi et rester informé.", [
        ("Médecins de garde", 'medecins_de_garde', "Les médecins de garde du mois, week-ends et jours fériés."),
        ("Professionnels de santé à proximité", 'p329', "Pharmacies, médecins et autres professionnels de santé des environs."),
        ("Infos santé publique", 'comsante', "Prévention et bons gestes, comme la lutte contre le moustique tigre."),
    ]),
    'p321-annuaire': ("Assos, commerces et services", "Les associations, les commerces et les services utiles aux habitants.", [
        ("Associations", 'associations', "Les associations du village et leurs contacts."),
        ("Commerces", 'commerces', "Commerces, entreprises et artisans de la commune."),
        ("Annuaire des services", 'annuaires-services', "Communauté de communes, collecte des déchets et autres services publics."),
        ("Mobilité", 'mobilite', "Covoiturage, prêt de vélos électriques et transport solidaire."),
        ("Emplois", 'emplois', "Les offres d'emploi relayées par la mairie."),
        ("Formations", 'formations', "Accompagnement des jeunes vers la formation et l'emploi."),
        ("Sécurité", 'securite', "Opération Tranquillité vacances, plainte en ligne et bons réflexes."),
    ]),
    'p203-tourisme': ("Tourisme", "Découvrir Baigneaux et l'Entre-Deux-Mers.", [
        ("Hébergeurs", 'Domaines', "Où dormir à Baigneaux et aux alentours."),
        ("Chemins de randonnée", 'chemins-randonnees', "Des boucles à pied autour du village et dans l'Entre-Deux-Mers."),
        ("Office de tourisme", 'p314', "L'office de tourisme pour préparer votre visite."),
    ]),
    'p286-urbanisme': ("Urbanisme", "Construire, agrandir, aménager : les règles et les démarches.", [
        ("Carte communale", 'carte-communale', "Le document d'urbanisme qui fixe les zones constructibles."),
        ("Demandes d'autorisation", 'demandes-autorisations', "Permis, déclaration préalable, certificat d'urbanisme : formulaires et dépôt en ligne."),
    ]),
    'p315-intercommunalite': ("Intercommunalité", "Les services que Baigneaux partage avec les communes voisines.", [
        ("Communauté de communes", 'CDC', "La Communauté de communes rurales de l'Entre-Deux-Mers et ses compétences."),
        ("Espace France Services", 'p317', "Des permanences à Targon pour vous aider dans vos démarches."),
    ]),
}
CR = '\r\n'
titre_modele = Page('p325-galerie-evenements').find(lambda n: n.get('$class') == 'WssTitle' and n.get('user_style') == 'Title')[0]
cm = Page('p208-conseil-municipal')
elus = [c for c in cm.find(lambda n: 'carte_elu' in (n.get('more_classes') or ''))][:3]
assert 'ALLAIN' in Page.text(elus[0])
for nom, (titre, chapo, tuiles) in RUBRIQUES.items():
    pg = Page(nom)
    menu = pg.find(lambda n: n.get('user_style') == 'Sous-menus')[0]
    for _, cible, _ in tuiles:
        fichiers = [f for f in os.listdir(os.path.join(SITE, 'pages')) if f.endswith(f'-{cible}.json') or f == f'{cible}.json']
        assert fichiers, cible
    t = Page.clone(titre_modele); t['value'] = titre                # WssTitle : texte brut
    blocs = [t, textarea(f'<p>{ent(chapo)}</p>', classes='rubrique_intro')]
    cartes = [container([textarea(f'<p><strong>{ent(tt)}</strong></p>{CR}<p>{ent(d)}</p>', style=None)],
                        classes='tuile_rubrique', href=f'{URL}/{u}.html') for tt, u, d in tuiles]
    blocs.append(container(cartes, classes='tuiles_rubrique'))
    if nom == 'p207-mairie':
        blocs.append(textarea('<p>Vos élus</p>'.replace('é', '&eacute;'), style=None, classes='rubrique_soustitre'))
        blocs.append(container([Page.clone(e) for e in elus], classes='apercu_elus'))
        blocs.append(textarea(f'<p><a href="{URL}/conseil-municipal.html">Tout le conseil municipal &rarr;</a></p>',
                              style='liens_page_principale', classes='rubrique_bouton'))
    hub = container(blocs, classes='rubrique')
    parent = pg.parents(menu)[-1]
    parent['contents'][parent['contents'].index(menu)] = hub
    Page.reindex(parent)
    pg.save()

media('.wscontainer.rubrique', {'margin': '0', 'padding': '6px 10px 18px', 'border-width': '0'})
media('.wscontainer.rubrique > .wsstitle_Title', {'padding': '14px 8px 4px', 'margin': '0'})
media('.wstextarea.rubrique_intro', {'float': 'none', 'font-size': '1.15em', 'color': '#3c4a41', 'margin': '0 8px 20px', 'padding': '0'})
media('.wscontainer.tuiles_rubrique',
      {'display': 'grid', 'grid-template-columns': 'repeat(auto-fill, minmax(240px, 1fr))', 'gap': '14px',
       'margin': '0', 'padding': '0 8px', 'border-width': '0'})
media('.wscontainer.tuile_rubrique',
      {'display': 'block', 'position': 'relative', 'box-sizing': 'border-box', 'height': '100%', 'margin': '0 !important',
       'padding': '16px 40px 16px 18px !important', 'background': '#F6F8F4', 'border': f'1px solid {TRAIT}',
       'border-radius': '14px', 'color': 'inherit', 'text-decoration': 'none', 'font-weight': '400',
       'transition': 'border-color .2s ease, box-shadow .2s ease, transform .2s ease'})
media('.wscontainer.tuile_rubrique::after',
      {'content': '""', 'position': 'absolute', 'right': '18px', 'top': '50%', 'width': '8px', 'height': '8px',
       'margin-top': '-5px', 'border-right': f'2px solid {VIGNE}', 'border-top': f'2px solid {VIGNE}',
       'transform': 'rotate(45deg)', 'transition': 'right .2s ease'})
media('.wscontainer.tuile_rubrique:hover,\n\t.wscontainer.tuile_rubrique:focus-visible',
      {'background': '#FFFFFF', 'border-color': VIGNE, 'box-shadow': '0 8px 20px rgba(31, 42, 35, 0.12)', 'transform': 'translateY(-2px)'})
media('.wscontainer.tuile_rubrique:hover::after', {'right': '14px'})
media('.tuile_rubrique .wstextarea', {'float': 'none', 'margin': '0', 'padding': '0', 'font-size': '1em', 'line-height': '1.4', 'text-align': 'left'})
media('.tuile_rubrique .wstextarea p', {'margin': '0'})
media('.tuile_rubrique .wstextarea strong',
      {'display': 'block', 'margin-bottom': '4px', 'font-family': 'Manrope, Arial, sans-serif', 'font-size': '1.12em',
       'font-weight': '700', 'color': VIGNE})
media('.tuile_rubrique .wstextarea p + p', {'font-size': '0.92em', 'color': '#4A5A4F'})
media('.wstextarea.rubrique_soustitre',
      {'float': 'none', 'margin': '30px 8px 12px', 'padding': '0', 'font-family': '"Playfair Display", Georgia, serif',
       'font-size': '1.7em', 'font-weight': '700', 'color': ENCRE})
media('.wscontainer.apercu_elus',
      {'display': 'flex', 'flex-wrap': 'wrap', 'gap': '14px', 'margin': '0', 'padding': '0 8px', 'border-width': '0'})
media('.apercu_elus > .wscontainer.carte_elu', {'flex': '0 1 200px', 'min-width': '0', 'margin': '0 !important'})
media('.wstextarea.rubrique_bouton', {'display': 'block', 'margin': '18px 8px 0', 'max-width': '300px'})
media('.wstextarea.rubrique_bouton p', {'margin': '0'})

home.save()
open(CSS, 'w', encoding='utf-8').write(css)
print('ok')
