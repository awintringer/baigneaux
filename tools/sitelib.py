"""Helpers to edit site/ JSON pages safely (ids, owners, indexes, images).

    from sitelib import Page
    p = Page('home')                      # site/pages/home*.json (or 'models/Footer')
    card = p.find(lambda n: 'cimeti' in p.text(n))[0]
    new = p.clone(card)                   # deep copy with fresh WebSiCo ids
    p.insert(parent, new, 0); p.save()
"""
import os, re, json, glob, copy, time, html, itertools

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, 'site')

# ---------- ids -------------------------------------------------------------
_used = None
_counter = itertools.count(90)
_t = [time.time()]

def _all_ids():
    ids = set()
    for f in glob.glob(f'{SITE}/*/*.json'):
        ids.update(re.findall(r'"id": "([ZY][0-9a-f]+)"', open(f, encoding='utf-8').read()))
    return ids

def new_id(prefix):
    """WebSiCo id: prefix + counter + uniqid() (8 hex seconds + 5 hex microseconds)."""
    global _used
    if _used is None: _used = _all_ids()
    while True:
        _t[0] += 0.000137
        sec = int(_t[0]); usec = int((_t[0] - sec) * 1e6)
        i = f'{prefix}{next(_counter)}{sec:08x}{usec:05x}'
        if i not in _used:
            _used.add(i); return i

# ---------- text helpers ----------------------------------------------------
def T(v):
    if isinstance(v, dict) and '$text' in v: return '\n'.join(v['$text'])
    return v if isinstance(v, str) else ''

def plain(v):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', T(v)))).strip()

def ent(s):
    """UTF-8 text -> HTML with named entities, as TinyMCE stores it (emoji kept as is)."""
    out = []
    for ch in html.escape(s, quote=False):
        if ord(ch) < 128 or ord(ch) > 0xFFFF: out.append(ch); continue
        name = next((k for k, v in html.entities.name2codepoint.items() if v == ord(ch)), None)
        out.append(f'&{name};' if name else ch)
    return ''.join(out)

def set_text(node, key, value):
    """Store a string the way the codec does ($text for long multi-line values)."""
    node[key] = {'$text': value.split('\n')} if ('\n' in value and len(value) > 60) else value

# ---------- page ------------------------------------------------------------
class Page:
    def __init__(self, name):
        cands = glob.glob(f'{SITE}/{name}.json') + glob.glob(f'{SITE}/pages/{name}.json') + glob.glob(f'{SITE}/pages/{name}-*.json')
        if not cands: raise FileNotFoundError(name)
        self.path = cands[0]
        self.data = json.load(open(self.path, encoding='utf-8'))
        self.root = self.data['row'][-1]['$php']

    def save(self):
        with open(self.path, 'w', encoding='utf-8') as fh:
            json.dump(self.data, fh, ensure_ascii=False, indent=1); fh.write('\n')

    # navigation
    def walk(self, n=None, parents=()):
        n = n or self.root
        yield n, parents
        for c in n.get('contents') or []:
            yield from self.walk(c, parents + (n,))

    def find(self, pred):
        return [n for n, _ in self.walk() if pred(n)]

    def parents(self, target):
        for n, ps in self.walk():
            if n is target: return ps
        raise ValueError('node not in page')

    @staticmethod
    def text(n):
        return plain(n.get('value')) if n.get('$class') in ('WsTextarea', 'WssTitle') else \
            ' '.join(plain(c.get('value')) for c, _ in Page._walk_static(n) if c.get('$class') in ('WsTextarea', 'WssTitle'))

    @staticmethod
    def _walk_static(n):
        yield n, None
        for c in n.get('contents') or []:
            yield from Page._walk_static(c)

    # edition
    @staticmethod
    def clone(n):
        c = copy.deepcopy(n)
        for x, _ in Page._walk_static(c):
            old = x.get('id')
            if old and old[0] in 'ZY':
                new = new_id(old[0]); x['id'] = new
                css = T(x.get('embedded_css_rules'))
                if css: set_text(x, 'embedded_css_rules', css.replace(old, new))
        return c

    @staticmethod
    def reindex(parent):
        for i, c in enumerate(parent.get('contents') or []):
            if i or 'index' in c: c['index'] = i
            if 'owner' not in c: c['owner'] = {'$owner': 'R'}

    def insert(self, parent, node, pos=None):
        lst = parent.setdefault('contents', [])
        lst.insert(len(lst) if pos is None else pos, node)
        self.reindex(parent)

    def remove(self, node):
        parent = self.parents(node)[-1]
        parent['contents'].remove(node); self.reindex(parent)
