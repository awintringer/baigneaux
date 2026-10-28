#!/usr/bin/env python3
"""Rebuild an importable WebSiCo archive (.ws_data) from `site/`.

usage: python3 tools/build.py [OUT.ws_data] [--site site] [--light] [--with-prefs] [--verify ORIGINAL.ws_data]

Default: full archive WITHOUT data/ws_preferences.php. WebSiCo's import is a plain
`unzip -o` + SQL replay, so leaving the preferences out keeps the target site's own
preferences and admin password untouched (and the build needs no secret at all).

--light       only _mysql_dump + files that are new/changed vs the base export
              (existing files stay on the server: unzip never deletes, and the purge only
              removes files that are no longer referenced). Much smaller upload.
--with-prefs  include data/ws_preferences.php, re-injecting the password hash from
              secrets/ws_pwd (or env WS_PWD). Needed only for a byte-identical rebuild.
--verify F    fail unless the output is byte-identical to F (use with --with-prefs).

Unchanged files keep their original zip metadata (order, dates, owner).
"""
import sys, os, json, hashlib, subprocess, shutil, tempfile, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wsdata import Dump
from codec import dec_cell

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def build_dump(site):
    layout = json.load(open(os.path.join(site, 'layout.json'), encoding='utf-8'))
    lines = []
    for e in layout:
        if 'raw' in e: lines.append(['RAW', e['raw'].encode('utf-8')]); continue
        j = json.load(open(os.path.join(site, e['file']), encoding='utf-8'))
        cells = []
        for c in j['row']:
            if isinstance(c, dict) and '$file' in c:
                cells.append(open(os.path.join(site, c['$file']), 'rb').read())
            else:
                cells.append(dec_cell(c))
        lines.append(['INSERT', j['table'], cells])
    d = Dump(b''); d.lines = lines
    return d.to_bytes()

def password():
    pw = os.environ.get('WS_PWD')
    p = os.path.join(ROOT, 'secrets', 'ws_pwd')
    if not pw and os.path.exists(p): pw = open(p).read().strip()
    if not pw: sys.exit('missing password hash: put it in secrets/ws_pwd or WS_PWD (see README)')
    return pw.encode()

def main():
    args = [a for a in sys.argv[1:]]
    site = os.path.join(ROOT, args[args.index('--site')+1] if '--site' in args else 'site')
    verify = args[args.index('--verify')+1] if '--verify' in args else None
    pos = [a for i, a in enumerate(args) if not a.startswith('--') and (i == 0 or not args[i-1].startswith('--'))]
    out = os.path.abspath(pos[0] if pos else os.path.join(ROOT, 'dist', time.strftime('baigneaux-%Y%m%d-%H%M.ws_data')))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    zm = json.load(open(os.path.join(site, 'zipmeta.json')))
    meta = {m['name']: m for m in zm['entries']}
    tmp = tempfile.mkdtemp(); stage = os.path.join(tmp, 'site'); os.makedirs(stage)
    shutil.copytree(os.path.join(site, 'data'), os.path.join(stage, 'data'))
    prefs = os.path.join(stage, 'data', 'ws_preferences.php')
    if os.path.exists(prefs):
        if '--with-prefs' in args:
            t = open(prefs, 'rb').read().replace(b'__WS_PWD__', password())
            open(prefs, 'wb').write(t)
        else:
            os.remove(prefs)
    dump = build_dump(site)
    open(os.path.join(stage, '_mysql_dump'), 'wb').write(dump)
    # order: original entries first, then new ones
    order = [n for n in meta if os.path.exists(os.path.join(stage, n.rstrip('/')))]
    known = set(order)
    for r, dirs, files in os.walk(stage):
        dirs.sort(); files.sort(); rel = os.path.relpath(r, stage)
        for nm in [x + '/' for x in dirs] + files:
            n = os.path.normpath(os.path.join(rel, nm)) + ('/' if nm.endswith('/') else '')
            if n in known or (n.endswith('/') and n.count('/') == 1): continue
            order.append(n)
    now = int(time.time()); changed = []
    for n in sorted(order, key=lambda x: -x.count('/')):
        p = os.path.join(stage, n.rstrip('/')); m = meta.get(n)
        same = False
        if m and not n.endswith('/'):
            h = hashlib.sha256(open(p, 'rb').read()).hexdigest()
            same = (h == m.get('sha256'))
        elif m:
            same = True
        if not same and not n.endswith('/'): changed.append(n)
        mode = (m or {}).get('mode', 0o100644) & 0o7777
        os.chmod(p, mode)
        try: os.chown(p, (m or {}).get('uid', 100), (m or {}).get('gid', 101))
        except PermissionError: pass
        if n == '_mysql_dump' and not same and m:
            same = hashlib.sha256(open(p, 'rb').read()).hexdigest() == zm.get('dump_sha256')
        if same: os.utime(p, (m.get('atime', m['mtime']), m['mtime']))
        else: os.utime(p, (now, now))
    if '--light' in args:
        order = [n for n in order if n in changed or n == '_mysql_dump']
    if os.path.exists(out): os.remove(out)
    subprocess.run(['zip', '-q', '-@', out], cwd=stage, input='\n'.join(order).encode(), check=True)
    shutil.rmtree(tmp)
    print(f'built {out} ({os.path.getsize(out)} bytes, {len(order)} entries)')
    print('changed vs export:', ', '.join(changed) if changed else 'nothing')
    if verify:
        same = open(verify, 'rb').read() == open(out, 'rb').read()
        print('VERIFY:', 'byte-identical to' if same else 'DIFFERENT from', verify)
        if not same: sys.exit(1)

if __name__ == '__main__':
    main()
