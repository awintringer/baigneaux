"""JSON <-> WebSiCo value codec (lossless).

Encoding rules (JSON side):
  str / int / null           -> PHP string / int / NULL (strings are UTF-8)
  {"$text": [lines]}         -> multi-line string (joined with "\n"), for readable diffs
  {"$raw": "8202"}           -> unquoted SQL token
  {"$php": <tree>}           -> SQL cell holding a PHP-serialized value
  {"$class": "WsX", ...}     -> PHP object, properties in order
  [ ... ]                    -> PHP array with keys 0..n-1
  {"$arr": [[k, v], ...]}    -> PHP array with other keys (int or str)
  {"$owner": "R"|"r"}        -> back-reference to the enclosing object (WebSiCo 'owner')
  {"$d": "200.0"}            -> PHP double, exact text   {"$bool": true} -> PHP bool
"""
import re
from wsdata import PObj, PArr, Ref, unserialize, serialize

PHP_RE = re.compile(rb'^(O|a):\d+:')

def _str_out(b):
    t = b.decode('utf-8')
    if '\n' in t and len(t) > 60:
        return {'$text': t.split('\n')}
    return t

def enc(v, parent=None):
    if isinstance(v, Ref):
        if v.target is not parent:
            raise ValueError('reference that is not owner->parent: unsupported')
        return {'$owner': v.kind.decode()}
    if v is None or isinstance(v, int) and not isinstance(v, bool): return v
    if isinstance(v, bytes): return _str_out(v)
    if isinstance(v, tuple):
        if v[0] == 'b': return {'$bool': v[1]}
        if v[0] == 'd': return {'$d': v[1].decode()}
    if isinstance(v, PObj):
        o = {'$class': v.cls.decode()}
        for k, x in v.props:
            ks = k.decode()
            assert not ks.startswith('$')
            o[ks] = enc(x, parent) if isinstance(x, Ref) else enc(x, v)
        return o
    if isinstance(v, PArr):
        keys = [k for k, _ in v.items]
        if keys == list(range(len(keys))):
            return [enc(x, parent) for _, x in v.items]
        return {'$arr': [[k if isinstance(k, int) else k.decode(), enc(x, parent)] for k, x in v.items]}
    raise TypeError(type(v))

def dec(j, parent=None):
    if j is None or isinstance(j, int) and not isinstance(j, bool): return j
    if isinstance(j, str): return j.encode('utf-8')
    if isinstance(j, list):
        return PArr([[i, dec(x, parent)] for i, x in enumerate(j)])
    if isinstance(j, dict):
        if '$text' in j: return '\n'.join(j['$text']).encode('utf-8')
        if '$owner' in j: return Ref(j['$owner'].encode(), parent)
        if '$d' in j: return ('d', j['$d'].encode())
        if '$bool' in j: return ('b', j['$bool'])
        if '$arr' in j:
            return PArr([[k if isinstance(k, int) else k.encode(), dec(x, parent)] for k, x in j['$arr']])
        if '$class' in j:
            o = PObj(j['$class'].encode(), [])
            for k, x in j.items():
                if k == '$class': continue
                is_ref = isinstance(x, dict) and '$owner' in x
                o.props.append([k.encode(), dec(x, parent if is_ref else o)])
            return o
    raise TypeError(repr(j)[:80])

def enc_cell(c):
    if c is None: return None
    if isinstance(c, tuple): return {'$raw': c[1].decode()}
    if PHP_RE.match(c): return {'$php': enc(unserialize(c))}
    return _str_out(c)

def dec_cell(j):
    if j is None: return None
    if isinstance(j, dict) and '$raw' in j: return ('RAW', j['$raw'].encode())
    if isinstance(j, dict) and '$php' in j: return serialize(dec(j['$php']))
    return dec(j)
