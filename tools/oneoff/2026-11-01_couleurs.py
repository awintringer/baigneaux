#!/usr/bin/env python3
"""01/11/2026 — Couleurs : contraste et daltonisme (docs/COULEURS.md, choix d'Adrien : les 3 propositions).

- Étiquettes de catégorie des cartes d'actu : 3 sur 4 sous le seuil WCAG (4,5), Mairie et Sécurité
  indiscernables en protanopie. Nouvelle palette, toutes >= 5,6 de contraste sur #f7f7f4
  (Emploi #4A00B3 conservé : déjà conforme et distinct).
- Fil d'Ariane : bleu marine + rouge foncé + flèches orange -> liens vert du site soulignés,
  séparateurs gris, flèches retirées (le séparateur « > » suffit).
- Fond de page : vert menthe saturé #D1FFE3 -> #DCE7DF, plus calme.
"""
import os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from sitelib import SITE

f = os.path.join(SITE, 'css/default.css')
css = open(f, encoding='utf-8').read()

def regle(sel, old, new):
    """Remplace `old` par `new` dans la règle non-@media dont le sélecteur est exactement `sel`."""
    global css
    pat = re.compile(r'(^%s \{\n)([^}]*)(\})' % re.escape(sel), re.M)
    m = pat.search(css); assert m, sel
    body = m.group(2)
    if old is None: body = body + new
    else:
        assert old in body, (sel, old); body = body.replace(old, new)
    css = css[:m.start(2)] + body + css[m.end(2):]

for cat, old, new in [('securite', '#A36D00', '#a34700'), ('mairie', '#007506', '#2f5e3e'),
                      ('sante', '#00A86B', '#005fae'), ('vie_communale', '#FF4DD5', '#a1307f')]:
    regle(f'.wstextarea_bulle_actu_categorie_{cat}', f'color: {old};', f'color: {new};')

regle('.wsspage_Arriere_plan', 'background-color: #D1FFE3;', 'background-color: #DCE7DF;')
regle('.wscontainer_Path', 'color: #000091;\n\tborder-color: #000091;', 'color: #2f5e3e;\n\tborder-color: #2f5e3e;')
regle('.wsspagepath_Path', 'color: #950000;', 'color: #5f6f64;')
regle('.wsspagepath_Path a',
      'background-image: url(data/images/background/1875_arrow.png);\n\tbackground-repeat: no-repeat;\n\tbackground-position: 0% 50%;\n\tpadding-left: 15px;\n\ttext-decoration: none;',
      'padding-left: 4px;\n\ttext-decoration: underline;')
regle('.wsspagepath_Path a', 'color: #000091;', 'color: #2f5e3e;')
regle('.wsspagepath_Path a:hover, .wsspagepath_Path a.hover',
      'background-position: 0% 50%;\n\tbackground-repeat: no-repeat;\n\tbackground-image: url(data/images/background/1875_arrow.png);',
      'text-decoration: none;')
open(f, 'w', encoding='utf-8').write(css)
print('ok')
