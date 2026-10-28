#!/usr/bin/env python3
"""Readable outline of a page/model from site/. usage: python3 tools/outline.py site/pages/home.json [--full] [--css]"""
import sys, json, re, html
def text(v): return '\n'.join(v['$text']) if isinstance(v, dict) and '$text' in v else (v if isinstance(v, str) else '')
def plain(v): return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', text(v)))).strip()
full, showcss = '--full' in sys.argv, '--css' in sys.argv
j = json.load(open(sys.argv[1], encoding='utf-8')); root = j['row'][-1]['$php']
def walk(n, d=0):
    c = n['$class']; st = n.get('user_style') or ''; mc = (n.get('more_classes') or '').strip(); extra = ''
    if c in ('WsTextarea', 'WssTitle', 'WssDownload', 'WsRawText'): extra = plain(n.get('value'))
    elif c == 'WsImage': extra = 'img=' + (n.get('value') or '')
    if not full and len(extra) > 110: extra = extra[:110] + '…'
    m = n.get('model_id') or ''
    line = '  ' * d + c + (f' .{st}' if st else '') + (f' [{mc}]' if mc else '') + (f' model={m}' if m else '') + (f'  «{extra}»' if extra else '')
    if showcss and text(n.get('embedded_css_rules')): line += '  {' + re.sub(r'\s+', ' ', text(n['embedded_css_rules'])) + '}'
    print(line)
    for ch in n.get('contents') or []: walk(ch, d + 1)
walk(root)
