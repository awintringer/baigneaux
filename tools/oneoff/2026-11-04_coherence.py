#!/usr/bin/env python3
"""04/11/2026 — Passe de cohérence (voir docs/COHERENCE.md) : corrections sans impact sur le contenu.

  - Menus déroulants (modèle Header2) : les colonnes des grands panneaux (« Ma commune »,
    « Services ») ne débordent plus (« Espace France Services » dépassait de « Intercommunalité ») ;
    ces panneaux sont centrés sous la barre au lieu d'être collés à leur bouton, ce qui les gardait
    hors de l'écran en 1024 px ; zone de survol prolongée sous les boutons pour atteindre le panneau.
  - Titres d'onglet : restes d'anciennes pages copiées (« Chemins de randonnées Aire de Jeux »,
    « Tourisme Tourisme »…) effacés ; la page affiche alors seulement son nom.
  - Fil d'Ariane : « Vous êtes ici : » rétabli sur la page Patrimoine (copie du modèle Path périmée).
  - Petite enfance : les 5 liens mail des assistantes maternelles étaient cassés (guillemet en trop).
Idempotent.
"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from sitelib import Page, SITE

# ------------------------------------------------------------------ CSS menus
CSS = os.path.join(SITE, 'css', 'default.css')
REMPL = [
    ("""		z-index: 50;
		min-width: 260px;""", """		z-index: 50;
		width: max-content;
		min-width: 260px;"""),
    ("""		flex: 1 1 0;
		min-width: 210px;""", """		flex: 1 1 auto;
		min-width: min-content;
		max-width: 280px;"""),
    ("""	.nav_panneau.nav_large {
		width: max-content;
		max-width: min(900px, 92vw);
	}
}""", """	.nav_panneau.nav_large {
		top: calc(100% - 6px);
		left: 50%;
		right: auto;
		transform: translateX(-50%);
		width: max-content;
		max-width: min(1000px, calc(100% - 24px));
	}
}
@media all {
	.wscontainer.nav_rubrique:has(> .nav_large) {
		position: static;
	}
}
@media all {
	.nav_rubrique > .wstextarea_Lien_header {
		position: relative;
	}
}
@media all {
	.nav_rubrique:hover > .wstextarea_Lien_header::after {
		content: "";
		position: absolute;
		left: 0;
		right: 0;
		top: 100%;
		height: 48px;
	}
}"""),
]
css = open(CSS, encoding='utf-8').read()
for old, new in REMPL:
    if new in css: continue
    assert old in css, old
    css = css.replace(old, new, 1)
open(CSS, 'w', encoding='utf-8').write(css)

# ------------------------------------------------------------------ titres d'onglet
# WebSiCo affiche « Baigneaux - <nom> <titre> » : ces titres sont des restes de copies.
for page in ['p203-tourisme', 'p219-Domaines', 'p244-aire-jeux', 'p247-chemins-randonnees',
             'p270-annuaires-services', 'p314', 'p320', 'p321-annuaire']:
    p = Page(page)
    if p.root.get('title'):
        p.root['title'] = ''; p.save()

# ------------------------------------------------------------------ Patrimoine : copie du modèle Path
ref = Page('p313-deliberations').find(lambda n: n.get('model_id') == 'Path')[0]
p = Page('p312-patrimoine')
cur = p.find(lambda n: n.get('model_id') == 'Path')[0]
if 'Vous' not in Page.text(cur):
    neuf = Page.clone(ref)
    parent = p.parents(cur)[-1]
    i = parent['contents'].index(cur)
    neuf['index'] = cur.get('index', i); neuf['owner'] = cur.get('owner', {'$owner': 'R'})
    parent['contents'][i] = neuf
    p.reindex(parent); p.save()

# ------------------------------------------------------------------ liens mail cassés
p = Page('p229-asmat')
s = json.dumps(p.data, ensure_ascii=False)
if '&quot;mailto:' in s:
    p.data = json.loads(s.replace('\\"&quot;mailto:', '\\"mailto:'))
    p.save()
print('ok')
