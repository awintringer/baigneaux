#!/usr/bin/env python3
"""05/11/2026 — Suites de la passe de cohérence (docs/COHERENCE.md), choix d'Adrien :

  - Accueil : prochain conseil municipal le 14 décembre ; lien vers la convocation d'octobre retiré
    (élément « Convocation » supprimé, à rajouter avec la nouvelle convocation).
  - Arrêtés : historique conservé, arrêtés échus marqués « terminé » ; titre « Arrêtés municipaux ».
  - Traiteur du marché : Jérôme, « Antonio pour les intimes » (accueil, actualités, évènements).
  - Habitants : Baigneaudais, Baigneaudaises. « Évènements » partout (bouton du menu, nom de page).
  - Orthographe (relevé de docs/COHERENCE.md §5 et quelques autres).
  - Annuaire des services : polices et couleurs de la charte (vert #2f5e3e, Manrope / Inter).
  - Menus déroulants : chevron sur les 5 boutons du modèle Header2 pour signaler le panneau.
Idempotent.
"""
import sys, os, glob, json, html
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from sitelib import Page, SITE, ent

# ------------------------------------------------------------------ remplacements de texte
# (ancien, nouveau) en texte brut ; appliqués aussi sous forme d'entités HTML (ent()).
TEXTES = [
    # traiteur
    ("notre traiteur Jérôme, qui", "notre traiteur Jérôme (Antonio pour les intimes), qui"),
    ("Antonio nous rejoint à partir de ce dimanche", "Jérôme, Antonio pour les intimes, nous rejoint à partir de ce dimanche"),
    ("un traiteur : Antonio et ses plats chauds", "un traiteur : Jérôme (Antonio pour les intimes) et ses plats chauds"),
    # gentilé
    ("les Baigneudaises et tous les Baigneudais", "les Baigneaudaises et tous les Baigneaudais"),
    ("Habitants : les Baignaudais", "Habitants : les Baigneaudais"),
    ("Habitants&nbsp;: les Baignaudais", "Habitants&nbsp;: les Baigneaudais"),
    # évènements
    ("Evènements", "Évènements"),
    ("Evenements de notre commune", "Évènements de notre commune"),
    # arrêtés
    ("Arrêtés en vigueur", "Arrêtés municipaux"),
    ("Arrêté du 25 juillet 2026", "Arrêté du 25 juillet 2026 (terminé)"),
    ("Arreté circulation 6 octobre 2026", "Arrêté de circulation du 6 octobre 2026 (travaux du 8 octobre, terminé)"),
    ("ARRETE DU CONSEIL DEPARTEMENTAL : Interdiction", "ARRÊTÉ DU CONSEIL DÉPARTEMENTAL (terminé) : interdiction"),
    ("la 19èmet et 20ème étape du Tour", "les 19e et 20e étapes du Tour"),
    ("la commune de baigneaux", "la commune de Baigneaux"),
    # orthographe
    ("Tranquilité", "Tranquillité"),
    ("accesible", "accessible"),
    ("nationnal", "national"),
    ("janiver", "janvier"),
    ("ultèrieurement", "ultérieurement"),
    ("S'y ajouterons", "S'y ajouteront"),
    ("vous serons communiqués", "vous seront communiquées"),
    ("pensant cette période", "pendant cette période"),
    ("que nous avons choisi pour", "que nous avons choisie pour"),
    ("notemment", "notamment"),
    ("des plats chaud,", "des plats chauds,"),
    ("se sont arrêté à", "se sont arrêtés à"),
    ("ont évoluées en 2017", "ont évolué en 2017"),
    ("rendre rendez-vous", "prendre rendez-vous"),
    ("ou nos élus", "où nos élus"),
    ("Les differentes demandes", "Les différentes demandes"),
    ("LES DIFFERENTES DEMANDES", "LES DIFFÉRENTES DEMANDES"),
    ("location de la SdF", "location de la salle des fêtes"),
    ("Nous avait rejoint à partir de ce marché un stand d'olives et tapenades qui nous ont également régalé",
     "Nous a rejoints à partir de ce marché un stand d'olives et tapenades, qui nous a également régalés"),
    ("brosses à dent enfants", "brosses à dents enfants"),
    ("réhausseurs", "rehausseurs"),
    ("ainsi qu'en témoigne les vestiges", "ainsi qu'en témoignent les vestiges"),
    ("des informations qu'il délivre", "des informations qu'elle délivre"),
    ("lecteur du site et de la Mairie de", "lecteur du site et la Mairie de"),
    ("ne pourra être tenu pour responsable", "ne pourra être tenue pour responsable"),
    ("professionnels de santé à proximités", "professionnels de santé à proximité"),
]
PAIRES = []
for a, b in TEXTES:
    PAIRES.append((a, b))
    if ent(a) != a: PAIRES.append((ent(a), ent(b)))

compte = {a: 0 for a, _ in TEXTES}

def fix(s):
    if s.startswith(('http', 'mailto:', 'data/')): return s
    for a, b in PAIRES:
        if a in s and not (a in b and b in s):
            n = s.count(a); s = s.replace(a, b)
            for x, y in TEXTES:
                if a in (x, ent(x)): compte[x] += n
    return s

def walk(o):
    if isinstance(o, dict):
        if '$text' in o and isinstance(o['$text'], list):
            joined = fix('\n'.join(o['$text']))
            o['$text'] = joined.split('\n'); return o
        for k in list(o): o[k] = walk(o[k])
        return o
    if isinstance(o, list): return [walk(x) for x in o]
    if isinstance(o, str): return fix(o)
    return o

for f in sorted(glob.glob(f'{SITE}/pages/*.json') + glob.glob(f'{SITE}/models/*.json')):
    t = open(f, encoding='utf-8').read()
    data = walk(json.loads(t))
    new = json.dumps(data, ensure_ascii=False, indent=1) + '\n'
    if new != t: open(f, 'w', encoding='utf-8').write(new)
for a, n in compte.items():
    if not n: print('déjà fait ou absent :', a)

# ------------------------------------------------------------------ accueil : prochain conseil
p = Page('home')
for n, _ in p.walk():
    v = n.get('value')
    if isinstance(v, str) and 'Le 2 novembre &agrave; 18h30' in v:
        n['value'] = v.replace('Le 2 novembre &agrave; 18h30', 'Le 14 d&eacute;cembre &agrave; 18h30')
conv = p.find(lambda n: n.get('$class') == 'WssDownload' and 'octobre' in json.dumps(n.get('data_filename')))
for n in conv: p.remove(n)
p.save()

# ------------------------------------------------------------------ CSS
CSS = os.path.join(SITE, 'css', 'default.css')
css = open(CSS, encoding='utf-8').read()
REMPL = [
    (""".wstextarea_Nom-endroti {
	font-family: Inter, Arial, sans-serif;
	font-weight: bold;
	font-style: normal;
	border-right-color: #555555;
	border-right-width: 0px;
	text-transform: uppercase;
	padding-top: 0px;
	color: #C95559;
	font-size: 1.84em;
	text-align: center;
	float: none;
}""", """.wstextarea_Nom-endroti {
	font-family: Manrope, Arial, sans-serif;
	font-weight: 700;
	font-style: normal;
	border-right-width: 0px;
	text-transform: uppercase;
	letter-spacing: 0.03em;
	line-height: 1.3;
	padding-top: 0px;
	padding-bottom: 8px;
	margin-bottom: 6px;
	border-bottom: 2px solid #e7f1e8;
	color: #2f5e3e;
	font-size: 1.35em;
	text-align: center;
	float: none;
}"""),
    (""".wstextarea_Intitule-categorie {
	font-weight: bold;
	padding: 0px;
	padding-left: 5px;
	color: #4E8DE8;
	text-align: center;
	font-size: 1.38em;
}""", """.wstextarea_Intitule-categorie {
	font-family: Inter, Arial, sans-serif;
	font-weight: 600;
	padding: 0px;
	padding-top: 6px;
	color: #4d6b56;
	text-transform: uppercase;
	letter-spacing: 0.05em;
	text-align: center;
	font-size: 1em;
}"""),
    (""".wstextarea_texte-avec-intitule {
	padding-top: 0px;
	color: #555555;""", """.wstextarea_texte-avec-intitule {
	padding-top: 0px;
	color: #1f2937;"""),
    ("""@media all {
	.nav_rubrique > .wstextarea_Lien_header {
		position: relative;
	}
}""", """@media all {
	.nav_rubrique > .wstextarea_Lien_header {
		position: relative;
	}
}
@media all {
	.nav_rubrique > .wstextarea_Lien_header a {
		flex-direction: row;
		gap: 8px;
		padding-left: 8px;
		padding-right: 8px;
	}
}
@media all {
	.nav_rubrique > .wstextarea_Lien_header a::after {
		content: "";
		flex: none;
		width: 7px;
		height: 7px;
		margin-top: -4px;
		border-right: 2px solid currentColor;
		border-bottom: 2px solid currentColor;
		transform: rotate(45deg);
		transition: transform 0.25s ease, margin 0.25s ease;
	}
}
@media all {
	.nav_rubrique:hover > .wstextarea_Lien_header a::after,
	.nav_rubrique:focus-within > .wstextarea_Lien_header a::after {
		margin-top: 4px;
		transform: rotate(225deg);
	}
}
@media (max-width: 900px) {
	.nav_rubrique > .wstextarea_Lien_header a {
		flex-direction: column;
		gap: 2px;
	}
}"""),
]
for old, new in REMPL:
    if new in css: continue
    assert old in css, old[:60]
    css = css.replace(old, new, 1)
open(CSS, 'w', encoding='utf-8').write(css)
print('ok')
