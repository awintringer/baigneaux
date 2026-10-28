#!/usr/bin/env python3
"""Explode a WebSiCo export (.ws_data) into the readable source tree `site/`.

usage: python3 tools/unpack.py EXPORT.ws_data [--site site]

Writes:
  site/layout.json          order of the SQL dump (raw lines + references to row files)
  site/pages/<id>-<url>.json    ws_tlc rows of pages (lang fr)
  site/models/<id>.json     ws_tlc rows of models (header, footer, cards...)
  site/drafts/<...>.json    ws_tlc_draft rows (unpublished edits)
  site/tables/<table>.<key>.json   other rows (ws_map, ws_system...)
  site/css/default.css      the user stylesheet (ws_user_css)
  site/data/...             images, documents, icon (ws_preferences.php is sanitised)
  site/zipmeta.json         zip order/timestamps/owners + sha256, for faithful rebuilds
The admin password hash is moved to secrets/ws_pwd (git-ignored).
"""
import sys, os, json, zipfile, hashlib, re, shutil, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wsdata import Dump
from codec import enc_cell

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PWD_RE = re.compile(rb'(\$ws_pwd = ")([0-9a-f]*)(";)')

def zip_entries_meta(path):
    z = zipfile.ZipFile(path); f = open(path, 'rb'); out = []
    for zi in z.infolist():
        f.seek(zi.header_offset); h = f.read(30)
        nl, el = struct.unpack('<HH', h[26:30]); f.read(nl); extra = f.read(el)
        m = {'name': zi.filename, 'mode': zi.external_attr >> 16}
        i = 0
        while i < len(extra):
            tag, ln = struct.unpack('<HH', extra[i:i+4]); d = extra[i+4:i+4+ln]
            if tag == 0x5455:
                vals = struct.unpack('<%dI' % ((ln-1)//4), d[1:1+4*((ln-1)//4)])
                m['mtime'] = vals[0]
                if len(vals) > 1: m['atime'] = vals[1]
            elif tag == 0x7875:
                us = d[1]; m['uid'] = int.from_bytes(d[2:2+us], 'little'); gs = d[2+us]
                m['gid'] = int.from_bytes(d[3+us:3+us+gs], 'little')
            i += 4 + ln
        if not zi.is_dir():
            m['sha256'] = hashlib.sha256(z.read(zi)).hexdigest()
        out.append(m)
    return z, out

def dumpj(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1); fh.write('\n')

def safe(s):
    return re.sub(r'[^A-Za-z0-9_.-]', '_', s)

def main():
    src = sys.argv[1]
    site = os.path.join(ROOT, sys.argv[sys.argv.index('--site')+1] if '--site' in sys.argv else 'site')
    z, meta = zip_entries_meta(src)
    for sub in ('pages', 'models', 'drafts', 'tables', 'css', 'data'):
        shutil.rmtree(os.path.join(site, sub), ignore_errors=True)
    # files
    for zi in z.infolist():
        if zi.filename == '_mysql_dump' or zi.is_dir(): continue
        data = z.read(zi)
        if zi.filename == 'data/ws_preferences.php':
            m = PWD_RE.search(data)
            if m and m.group(2):
                os.makedirs(os.path.join(ROOT, 'secrets'), exist_ok=True)
                with open(os.path.join(ROOT, 'secrets', 'ws_pwd'), 'wb') as fh: fh.write(m.group(2))
                data = PWD_RE.sub(rb'\1__WS_PWD__\3', data)
        p = os.path.join(site, zi.filename); os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, 'wb') as fh: fh.write(data)
    for zi in z.infolist():   # keep empty dirs
        if zi.is_dir(): os.makedirs(os.path.join(site, zi.filename), exist_ok=True)
    # dump
    d = Dump(z.read('_mysql_dump')); layout = []
    for line in d.lines:
        if line[0] == 'RAW':
            layout.append({'raw': line[1].decode('utf-8')}); continue
        table, row = line[1], line[2]
        cells = [enc_cell(c) for c in row]
        if table in ('ws_tlc', 'ws_tlc_draft'):
            rid, lang = row[0].decode(), row[1].decode()
            folder = 'drafts' if table == 'ws_tlc_draft' else ('pages' if lang else 'models')
            name = rid + (f'-{safe(row[2].decode())}' if row[2] and row[2].decode() != rid else '')
            if lang and lang != 'fr': name += f'.{lang}'
            rel = f'{folder}/{name}.json'
        elif table in ('ws_user_css', 'ws_user_css_draft'):
            cssname = f"{'draft-' if table.endswith('draft') else ''}{safe(row[0].decode())}.css"
            with open(os.path.join(site, 'css', cssname) if os.makedirs(os.path.join(site, 'css'), exist_ok=True) is None else '', 'wb') as fh:
                fh.write(row[2])
            cells[2] = {'$file': f'css/{cssname}'}
            rel = f'css/{cssname[:-4]}.row.json'
        else:
            key = row[0].decode() if isinstance(row[0], bytes) else 'row'
            rel = f'tables/{table}.{safe(key)}.json'
            n = 2
            while any(e.get('file') == rel for e in layout):
                rel = f'tables/{table}.{safe(key)}.{n}.json'; n += 1
        dumpj(os.path.join(site, rel), {'table': table, 'row': cells})
        layout.append({'file': rel})
    dumpj(os.path.join(site, 'layout.json'), layout)
    dumpj(os.path.join(site, 'zipmeta.json'), {'dump_sha256': hashlib.sha256(z.read('_mysql_dump')).hexdigest(), 'entries': meta})
    print(f'unpacked {src} -> {site}')

if __name__ == '__main__':
    main()
