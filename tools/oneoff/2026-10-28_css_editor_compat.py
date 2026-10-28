#!/usr/bin/env python3
"""28/10/2026 — rend default.css compatible avec l'éditeur de styles WebSiCo (cf. tools/check_css.py) :
les ajouts (rangées défilantes, responsive, en-tête mobile) sont réécrits en un bloc @media par
règle, sans commentaires ; les styles nommés restent au format géré par l'éditeur."""
import re, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'site', 'css', 'default.css')
css = open(p, encoding='utf-8').read()
cut = css.index('/* ===== Rangées défilantes')
managed, custom = css[:cut], css[cut:]
custom = re.sub(r'/\*.*?\*/', '', custom, flags=re.S)

def parse(s):
    """-> list of (media_query or None, selector, declarations[])"""
    out, i = [], 0
    while True:
        m = re.compile(r'\s*([^{}]+?)\s*\{').match(s, i)
        if not m: break
        head = m.group(1); i = m.end()
        if head.startswith('@media'):
            depth, j = 1, i
            while depth:
                depth += {'{': 1, '}': -1}.get(s[j], 0); j += 1
            for _, sel, decls in parse(s[i:j - 1]):
                out.append((head, sel, decls))
            i = j
        else:
            j = s.index('}', i)
            decls = [d.strip() for d in s[i:j].split(';') if d.strip()]
            out.append((None, ' '.join(head.split()), decls)); i = j + 1
    assert not s[i:].strip(), s[i:i + 80]
    return out

rules = parse(custom)
blocks = []
for media, sel, decls in rules:
    sel = ',\n'.join(x.strip() for x in sel.split(','))
    body = ''.join(f'\t\t{d};\n' for d in decls)
    blocks.append(f'{media or "@media all"} {{\n\t{sel.replace(chr(10), chr(10) + chr(9))} {{\n{body}\t}}\n}}\n')
out = managed.rstrip('\n') + '\n' + ''.join(blocks)
open(p, 'w', encoding='utf-8').write(out)
print(f'{len(rules)} règles personnalisées réécrites en blocs @media')
