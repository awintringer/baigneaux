#!/usr/bin/env python3
"""Check site/css/default.css against WebSiCo's style-editor parser (ws_style.js).

The editor explodes the sheet with regexps and breaks (blank WYSIWYG editor) when the CSS does
not follow its restricted syntax:
  - no comments at all
  - managed rules: one selector per rule, at line start, no comma lists (except ", .x.hover")
  - property names become a RegExp: only [a-z-] allowed
  - @-blocks are kept verbatim ("unmanaged") but the splitter only understands ONE inner rule
    per block: "@media … { selector { … } }"
Custom CSS (:has(), comma lists, several rules for one breakpoint…) must therefore be written as
one "@media all { … }" (or "@media (max-width…) { … }") block per rule.

usage: python3 tools/check_css.py [file.css]   -> exit 1 on problems
"""
import re, sys, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def check(css):
    errs = []
    if '/*' in css or '*/' in css:
        errs.append('commentaire(s) présent(s) : le parseur WebSiCo ne les supporte pas')
    # same splitter as ws_style.js
    rules = re.findall(r'[^\s][^}]*{[^}]*}\s*}?', css, flags=re.I)
    rebuilt = ''.join(rules)
    stripped = re.sub(r'\s+', '', css)
    if re.sub(r'\s+', '', rebuilt) != stripped:
        errs.append('le découpage WebSiCo ne retrouve pas toute la feuille (accolades imbriquées ?)')
    for r in rules:
        head = r[:r.index('{')].strip()
        if r.startswith('@'):
            inner = r[r.index('{') + 1:]
            if inner.count('{') != 1 or inner.rstrip().count('}') != 2:
                errs.append(f'bloc @ avec plusieurs règles : {head[:60]}')
            continue
        sels = [s.strip() for s in head.split(',')]
        if len(sels) > 1 and not (len(sels) == 2 and sels[1] == sels[0].replace(':hover', '.hover')):
            errs.append(f'sélecteurs multiples (non gérés) : {head[:70]}')
        for prop in re.findall(r'[{;]([^:]+):', r):
            name = re.sub(r'^[^a-z\-]*', '', prop.strip().lower())
            if not re.fullmatch(r'[a-z\-]+', name):
                errs.append(f'propriété illisible pour WebSiCo {name[:40]!r} dans {head[:50]}')
        if ':has(' in head or '::' in head and '-webkit' in head:
            errs.append(f'sélecteur avancé hors bloc @ : {head[:60]}')
    return errs

if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'site', 'css', 'default.css')
    errs = check(open(path, encoding='utf-8').read())
    for e in errs: print('ERREUR', e)
    print('CSS compatible avec l\'éditeur WebSiCo' if not errs else f'{len(errs)} problème(s)')
    sys.exit(1 if errs else 0)
