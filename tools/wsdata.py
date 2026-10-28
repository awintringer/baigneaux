"""WebSiCo .ws_data toolkit: parse/emit the _mysql_dump and PHP-serialized objects, byte-exact."""
import re

# ---------------- SQL dump layer ----------------
_UNESC = {b'0': b'\0', b'n': b'\n', b'r': b'\r', b't': b'\t', b'Z': b'\x1a', b'b': b'\x08'}
_ESC = {0: b'\\0', 10: b'\\n', 13: b'\\r', 92: b'\\\\', 39: b"\\'", 34: b'\\"', 26: b'\\Z'}

def _parse_values(s):
    rows, i, n = [], 0, len(s)
    while i < n:
        while i < n and s[i:i+1] != b'(':
            i += 1
        if i >= n: break
        i += 1; row = []
        while True:
            while s[i:i+1] == b' ': i += 1
            if s[i:i+1] == b"'":
                i += 1; buf = bytearray()
                while True:
                    c = s[i:i+1]
                    if c == b'\\':
                        d = s[i+1:i+2]; buf += _UNESC.get(d, d); i += 2
                    elif c == b"'":
                        i += 1; break
                    else:
                        j = i
                        while s[j:j+1] not in (b'\\', b"'"): j += 1
                        buf += s[i:j]; i = j
                row.append(bytes(buf))
            else:
                j = i
                while s[j:j+1] not in (b',', b')'): j += 1
                tok = s[i:j].strip(); row.append(None if tok == b'NULL' else ('RAW', tok)); i = j
            if s[i:i+1] == b',': i += 1; continue
            if s[i:i+1] == b')': i += 1; break
        rows.append(row)
    return rows

def esc(v):
    if v is None: return b'NULL'
    if isinstance(v, tuple): return v[1]
    return b"'" + b''.join(_ESC.get(c, bytes([c])) for c in v) + b"'"

class Dump:
    """Keeps every line; INSERT lines become (table, row) entries editable in place."""
    def __init__(self, data: bytes):
        self.lines = []
        for line in data.split(b'\n'):
            m = re.match(rb'^INSERT INTO `([^`]+)` VALUES (.*)$', line, re.S)
            if m:
                rows = _parse_values(m.group(2)); assert len(rows) == 1
                self.lines.append(['INSERT', m.group(1).decode(), rows[0]])
            else:
                self.lines.append(['RAW', line])
    def rows(self, table):
        return [l[2] for l in self.lines if l[0] == 'INSERT' and l[1] == table]
    def to_bytes(self):
        out = []
        for l in self.lines:
            if l[0] == 'RAW': out.append(l[1])
            else: out.append(b'INSERT INTO `' + l[1].encode() + b'` VALUES (' + b','.join(esc(v) for v in l[2]) + b');')
        return b'\n'.join(out)

# ---------------- PHP serialize layer ----------------
class PObj:
    __slots__ = ('cls', 'props')
    def __init__(self, cls, props): self.cls, self.props = cls, props  # props: list of [key(bytes), value]
    def get(self, k, default=None):
        k = k.encode() if isinstance(k, str) else k
        for kk, v in self.props:
            if kk == k: return v
        return default
    def set(self, k, v):
        k = k.encode() if isinstance(k, str) else k
        for p in self.props:
            if p[0] == k: p[1] = v; return
        self.props.append([k, v])
    def __repr__(self): return f'<{self.cls.decode()} {self.get("id")!r}>'

class PArr:
    __slots__ = ('items',)
    def __init__(self, items): self.items = items  # list of [key(int|bytes), value]

class Ref:
    __slots__ = ('kind', 'target')   # kind b'R' or b'r'; target = PObj/PArr node
    def __init__(self, kind, target): self.kind, self.target = kind, target

class _P:
    def __init__(self, s): self.s, self.i, self.slots = s, 0, [None]
    def read_until(self, ch):
        j = self.s.index(ch, self.i); v = self.s[self.i:j]; self.i = j + 1; return v
    def key(self):
        t = self.s[self.i:self.i+1]; self.i += 2
        if t == b'i': return int(self.read_until(b';'))
        n = int(self.read_until(b':')); v = self.s[self.i+1:self.i+1+n]; self.i += n + 3; return v
    def value(self):
        t = self.s[self.i:self.i+1]; self.i += 2
        if t in (b'R', b'r'):
            n = int(self.read_until(b';')); node = self.slots[n]
            if t == b'r': self.slots.append(node)   # r: occupies a slot, R: does not
            return Ref(t, node)
        if t == b'N': self.slots.append(None); return None  # 'N;' : i already past ';'
        if t == b'b': v = self.read_until(b';') == b'1'; self.slots.append(v); return ('b', v)
        if t == b'i': v = int(self.read_until(b';')); self.slots.append(v); return v
        if t == b'd': v = self.read_until(b';'); self.slots.append(v); return ('d', v)
        if t == b's':
            n = int(self.read_until(b':')); v = self.s[self.i+1:self.i+1+n]; self.i += n + 3
            self.slots.append(v); return v
        if t == b'a':
            n = int(self.read_until(b':')); self.i += 1; node = PArr([]); self.slots.append(node)
            for _ in range(n):
                k = self.key(); node.items.append([k, self.value()])
            self.i += 1; return node
        if t == b'O':
            ln = int(self.read_until(b':')); cls = self.s[self.i+1:self.i+1+ln]; self.i += ln + 3
            n = int(self.read_until(b':')); self.i += 1; node = PObj(cls, []); self.slots.append(node)
            for _ in range(n):
                k = self.key(); node.props.append([k, self.value()])
            self.i += 1; return node
        raise ValueError(f'bad type {t!r} at {self.i}')

def unserialize(s: bytes):
    p = _P(s); v = p.value(); assert p.i == len(s), (p.i, len(s)); return v

def serialize(v) -> bytes:
    out, idx, counter = [], {}, [0]
    def k(x):
        return b'i:%d;' % x if isinstance(x, int) else b's:%d:"%s";' % (len(x), x)
    def w(x):
        if isinstance(x, Ref):
            out.append(x.kind + b':%d;' % idx[id(x.target)])
            if x.kind == b'r': counter[0] += 1
            return
        counter[0] += 1
        if x is None: out.append(b'N;')
        elif isinstance(x, tuple) and x[0] == 'b': out.append(b'b:%d;' % x[1])
        elif isinstance(x, tuple) and x[0] == 'd': out.append(b'd:' + x[1] + b';')
        elif isinstance(x, bool): out.append(b'b:%d;' % x)
        elif isinstance(x, int): out.append(b'i:%d;' % x)
        elif isinstance(x, str): x = x.encode(); out.append(b's:%d:"%s";' % (len(x), x))
        elif isinstance(x, bytes): out.append(b's:%d:"%s";' % (len(x), x))
        elif isinstance(x, PArr):
            idx[id(x)] = counter[0]; out.append(b'a:%d:{' % len(x.items))
            for kk, vv in x.items: out.append(k(kk)); w(vv)
            out.append(b'}')
        elif isinstance(x, PObj):
            idx[id(x)] = counter[0]; out.append(b'O:%d:"%s":%d:{' % (len(x.cls), x.cls, len(x.props)))
            for kk, vv in x.props: out.append(k(kk)); w(vv)
            out.append(b'}')
        else: raise TypeError(type(x))
    w(v); return b''.join(out)

# ---------------- helpers ----------------
def children(o):
    c = o.get('contents') if isinstance(o, PObj) else None
    return [v for _, v in c.items] if isinstance(c, PArr) else []

def walk(o, depth=0, parent=None):
    yield o, depth, parent
    for ch in children(o):
        yield from walk(ch, depth + 1, o)

def s(v):
    """bytes -> str for display"""
    return v.decode('utf-8', 'replace') if isinstance(v, bytes) else v
