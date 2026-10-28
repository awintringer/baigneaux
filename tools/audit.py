#!/usr/bin/env python3
"""Static audit of site/: styles, inline CSS, HTML smells, links, images. usage: python3 tools/audit.py"""
import os, sys, json, re, glob, collections, html
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); SITE = os.path.join(ROOT, 'site')

def text(v):
    if isinstance(v, dict) and '$text' in v: return '\n'.join(v['$text'])
    return v if isinstance(v, str) else ''

def nodes(n, parent=None, depth=0):
    if isinstance(n, dict) and '$class' in n:
        yield n, parent, depth
        for c in n.get('contents') or []:
            yield from nodes(c, n, depth + 1)

rows = {}
for f in sorted(glob.glob(f'{SITE}/*/*.json')):
    j = json.load(open(f, encoding='utf-8'))
    if 'row' in j and isinstance(j['row'][-1], dict) and '$php' in j['row'][-1] and j['table'].startswith('ws_tlc'):
        rows[os.path.relpath(f, SITE)] = j
css = open(f'{SITE}/css/default.css', encoding='utf-8').read()

R = collections.defaultdict(list)
cls_count = collections.Counter(); style_use = collections.Counter(); style_where = collections.defaultdict(set)
emb_count = 0; emb_bytes = 0; inline_style = 0; nbsp = 0; empty_p = 0; abs_links = collections.Counter()
img_refs = set(); doc_refs = set(); maxdepth = {}; hdr = {}; model_use = collections.Counter()
alltext = ''
for name, j in rows.items():
    root = j['row'][-1]['$php']; md = 0
    if text(root.get('hdr_html')): hdr[name] = len(text(root.get('hdr_html')))
    for n, p, d in nodes(root):
        md = max(md, d); c = n['$class']; cls_count[c] += 1
        st = n.get('user_style') or ''
        if st: style_use[f"{c.lower()}_{st}"] += 1; style_where[f"{c.lower()}_{st}"].add(name)
        if n.get('model_id'): model_use[n['model_id']] += 1
        e = text(n.get('embedded_css_rules'))
        if e: emb_count += 1; emb_bytes += len(e)
        for k in ('value', 'uploaded_image', 'hdr_html', 'href'):
            v = text(n.get(k))
            alltext += v + '\n'
        v = text(n.get('value'))
        inline_style += len(re.findall(r'style="', v)); nbsp += v.count('&nbsp;'); empty_p += len(re.findall(r'<p>(&nbsp;)?</p>', v))
        for u in re.findall(r'href="(https?://[^"]+)"', v): abs_links[re.sub(r'(https?://[^/]+).*', r'\1', u)] += 1
        if c == 'WsImage':
            for k in ('value', 'uploaded_image'):
                if n.get(k): img_refs.add(n[k])
    maxdepth[name] = md
alltext += css
for fn in os.listdir(f'{SITE}/data/rawdata'):
    pass

# CSS analysis
css_classes = collections.OrderedDict()
for m in re.finditer(r'^\.([a-z]+)_([A-Za-z0-9_-]+)[^{]*\{', css, re.M):
    css_classes.setdefault(f'{m.group(1)}_{m.group(2)}', 0)
defined = set(css_classes)
used = set(style_use)
bad_props = re.findall(r'^\s*(undefined:.*|border-color:\s*[0-9a-f]{6};|font-variant:\s*bold;|text-shadow:\s*#[0-9a-fA-F]+;|color\s+:.*)$', css, re.M)
print('== Pages/modèles:', len(rows))
print('== Classes d\'éléments:', dict(cls_count.most_common()))
print('== Nœuds total:', sum(cls_count.values()), ' profondeur max:', max(maxdepth.values()))
print('== Règles CSS embarquées par élément:', emb_count, f'({emb_bytes} octets)')
print('== style="" inline dans le HTML:', inline_style, ' &nbsp;:', nbsp, ' paragraphes vides:', empty_p)
print('== Liens absolus par domaine:', dict(abs_links))
print('== hdr_html (head custom) par page:', hdr)
print('== Styles CSS définis:', len(defined), ' utilisés:', len(used))
print('   définis mais jamais utilisés:', sorted(defined - used))
print('   utilisés mais non définis:', sorted(used - defined))
print('== Propriétés CSS invalides:', bad_props)
print('== Modèles utilisés:', dict(model_use))
imgs = os.listdir(f'{SITE}/data/images'); imgs = [i for i in imgs if os.path.isfile(f'{SITE}/data/images/{i}')]
unused = [i for i in imgs if i not in alltext]
size = lambda fs, d: sum(os.path.getsize(f'{SITE}/data/{d}/{x}') for x in fs)
print(f'== Images: {len(imgs)} ({size(imgs,"images")/1e6:.1f} Mo), non référencées: {len(unused)} ({size(unused,"images")/1e6:.1f} Mo)')
big = sorted(imgs, key=lambda x: -os.path.getsize(f'{SITE}/data/images/{x}'))[:10]
print('   plus grosses:', [(b, round(os.path.getsize(f"{SITE}/data/images/{b}")/1e6, 1)) for b in big])
docs = os.listdir(f'{SITE}/data/rawdata')
print('== Documents non référencés:', [d for d in docs if d not in alltext])
json.dump({'unused_images': unused}, open('/tmp/audit_unused.json', 'w'))
