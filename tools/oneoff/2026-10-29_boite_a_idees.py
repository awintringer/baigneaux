#!/usr/bin/env python3
"""29/10/2026 — Boîte à idées : formulaire WebSiCo natif (WssForm) qui envoie un mail.

Crée deux pages à partir de la page « Mentions légales » (en-tête, menu, fil d'Ariane, pied) :
  p332 boite-a-idees        formulaire (menu : Ma Mairie > Boîte à idées)
  p333 boite-a-idees-merci  confirmation après envoi (hors menu, non indexée)

Le formulaire n'enregistre rien : WebSiCo envoie le contenu par mail (PHPMailer, réglages SMTP
de ws_config.php côté serveur, voir docs/BOITE_A_IDEES.md). Anti-spam : captcha WebSiCo,
identifiant de message horodaté (24 h, usage unique), copie à l'expéditeur désactivée.
"""
import sys, os, json, copy, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from sitelib import Page, new_id, set_text, ent, SITE

DEST = 'mairie@baigneaux.fr, awintringer@gmail.com'
CATEGORIES = ['Site internet', 'Évènements et activités', 'Services', 'Plaintes', 'Remerciements', 'Autre']
FORM_ID, THANKS_ID = 'p332', 'p333'
NOW = int(time.time())

def comp(cls, value, style='', props=1024, **extra):
    n = {'$class': cls}
    n.update(extra)
    n.update({'value': value, 'id': new_id('Y'), 'properties': props, 'owner': {'$owner': 'R'},
              'index': 0, 'user_style': style, 'more_classes': '', 'embedded_css_rules': ''})
    return n

def title(text):
    box = {'$class': 'WsContainer', 'valign': None, 'model_id': 0, 'id': new_id('Z'), 'properties': 8192,
           'owner': {'$owner': 'R'}, 'index': 0, 'user_style': 'Bloc-titre', 'more_classes': '',
           'embedded_css_rules': '', 'href': '',
           'contents': [comp('WssTitle', text, 'Title', level='2', href='')]}
    return box

def textarea(paragraphs, style='Texte_normal_align_gauche', classes=''):
    n = comp('WsTextarea', None, style, 2048)
    set_text(n, 'value', '\r\n'.join(f'<p>{p}</p>' for p in paragraphs))
    n['more_classes'] = classes
    return n

def field(label, ftype, required=False, params=0):
    return comp('WssInputField', label, '', 1024, type=ftype, required=required, params=params, htmlName='')

# required est un booléen PHP
_field = field
def field(label, ftype, required=False, params=0):
    n = _field(label, ftype, required, params); n['required'] = {'$bool': bool(required)}; return n

def make_page(pid, url_id, page_title, contents, no_robots='0'):
    src = Page('p266-mentions-legales')
    page = copy.deepcopy(src.data)
    root = page['row'][-1]['$php']
    # fresh ids everywhere except the page itself
    tmp = Page.clone(root); tmp['id'] = pid
    page['row'][-1]['$php'] = root = tmp
    # pages du menu : nom renseigné, titre vide (sinon WebSiCo répète le nom dans <title>)
    root.update({'title': '' if pid == FORM_ID else page_title, 'url_id': url_id, 'description': '', 'date': NOW,
                 'save_number': 1, 'no_robots': no_robots})
    page['row'][:-1] = [pid, 'fr', url_id, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(NOW)),
                        page_title if pid == FORM_ID else '', page['row'][5]]
    # main content block = the Subdivision holding the Bloc-titre
    def walk(n, ps=()):
        yield n, ps
        for c in n.get('contents') or []: yield from walk(c, ps + (n,))
    bloc = next(n for n, _ in walk(root) if n.get('user_style') == 'Bloc-titre')
    sub = next(ps[-1] for n, ps in walk(root) if n is bloc)
    sub['contents'] = contents
    Page.reindex(sub)
    path = os.path.join(SITE, 'pages', f'{pid}-{url_id}.json')
    with open(path, 'w', encoding='utf-8') as fh:
        json.dump(page, fh, ensure_ascii=False, indent=1); fh.write('\n')
    return path

# ---------- page formulaire ----------
fields = [
    field('Catégorie', 'select', True, '\r\n'.join(CATEGORIES)),
    field('Votre message', 'text', True, 8),
    field('Votre adresse mail (facultatif, pour que nous puissions vous répondre)', 'email'),
    field('Recopiez les caractères de l’image', 'captcha', True),
    field('Envoyer', 'submit'),
]
form = {'$class': 'WssForm',
        'destination': DEST,
        'return_url': f'https://www.baigneaux.fr/boite-a-idees-merci.html',
        'preamble': '', 'postamble': '', 'ccPrompt': '',
        'valign': None, 'model_id': 0, 'id': new_id('Z'), 'properties': 8194 | (1 << 20),
        'owner': {'$owner': 'R'}, 'index': 0, 'user_style': 0, 'more_classes': 'boite_idees',
        'embedded_css_rules': '', 'contents': fields}
Page.reindex(form)

make_page(FORM_ID, 'boite-a-idees', 'Boîte à idées', [
    title('Boîte à idées'),
    textarea([ent('Une idée pour la commune, une remarque sur un service, un problème à signaler, '
                  'ou simplement un remerciement ? Écrivez-nous : votre message est transmis directement à la mairie.'),
              ent('Seuls la catégorie et le message sont obligatoires. Laissez votre adresse mail si vous souhaitez une réponse.')]),
    form,
    textarea([ent('Votre adresse mail sert uniquement à vous répondre ; elle n’est ni publiée ni transmise à des tiers, '
                  'et votre message est conservé le temps nécessaire à son traitement. '
                  'Pour exercer vos droits sur vos données : mairie@baigneaux.fr (voir les ')
              + '<a href="https://www.baigneaux.fr/mentions-legales.html">mentions l&eacute;gales</a>).'],
             classes='boite_idees_rgpd'),
])

# ---------- page de confirmation ----------
make_page(THANKS_ID, 'boite-a-idees-merci', 'Message envoyé', [
    title('Merci !'),
    textarea([ent('Votre message a bien été transmis à la mairie. Si vous avez laissé votre adresse mail, '
                  'nous vous répondrons dès que possible.'),
              '<a href="https://www.baigneaux.fr/home.html">' + ent('Retour à l’accueil') + '</a>'
              + ' &nbsp;&middot;&nbsp; '
              + '<a href="https://www.baigneaux.fr/boite-a-idees.html">' + ent('Envoyer un autre message') + '</a>']),
], no_robots='1')

# ---------- plan du site, compteur, ordre du dump ----------
mp = json.load(open(os.path.join(SITE, 'tables/ws_map.fr.json'), encoding='utf-8'))
entries = mp['row'][1]['$php']
ids = [dict(e['$arr'])['id'] for e in entries]
def entry(pid, cat): return {'$arr': [['id', pid], ['category', cat]]}
if FORM_ID not in ids:
    last_mairie = max(i for i, e in enumerate(entries) if dict(e['$arr'])['category'] == 'p207')
    entries.insert(last_mairie + 1, entry(FORM_ID, 'p207'))
if THANKS_ID not in ids:
    entries.append(entry(THANKS_ID, 0))
def save(obj, rel):
    with open(os.path.join(SITE, rel), 'w', encoding='utf-8') as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1); fh.write('\n')
save(mp, 'tables/ws_map.fr.json')

sysf = os.path.join(SITE, 'tables/ws_system.6.1.json')
st = json.load(open(sysf)); st['row'][1] = str(max(int(st['row'][1]), 333))
save(st, 'tables/ws_system.6.1.json')

lay = json.load(open(os.path.join(SITE, 'layout.json'), encoding='utf-8'))
files = [e.get('file') for e in lay]
pos = files.index('pages/p331-securite.json') + 1
for f in ('pages/p333-boite-a-idees-merci.json', 'pages/p332-boite-a-idees.json'):
    if f not in files: lay.insert(pos, {'file': f})
save(lay, 'layout.json')
print('ok')

# ---------- styles du formulaire (un bloc @media par règle, cf. check_css.py) ----------
RULES = [
    ('.boite_idees', 'background: #e7f1e8; border: 1px solid #b9d5c0; border-radius: 14px; padding: 18px 22px 22px; margin: 8px 0 16px; box-sizing: border-box;'),
    ('.boite_idees .wsslabel', 'margin-top: 6px;'),
    ('.boite_idees .wsslabel label', "font-family: 'Inter', sans-serif; font-weight: 600; font-size: 1rem; color: #2f5e3e;"),
    ('.boite_idees .wsslabel span', 'color: #9a3b3b; font-size: 0.85em;'),
    ('.boite_idees .wssinput', "display: block; width: 100%; box-sizing: border-box; font-family: 'Inter', sans-serif; font-size: 1rem; color: #1d2b21; background: #ffffff; border: 1px solid #9cbfa5; border-radius: 8px; padding: 10px 12px; margin: 6px 0 14px;"),
    ('.boite_idees textarea.wssinput', 'min-height: 11em; resize: vertical; line-height: 1.5;'),
    ('.boite_idees .wssinput:focus', 'outline: 2px solid #2f5e3e; outline-offset: 1px; border-color: #2f5e3e;'),
    ('.boite_idees button.wssinput', 'display: inline-block; width: auto; margin: 6px 0 0; padding: 12px 34px; background: #2f5e3e; color: #ffffff; border: none; border-radius: 999px; font-weight: 600; letter-spacing: 0.02em; cursor: pointer;'),
    ('.boite_idees button.wssinput:hover', 'background: #23472f;'),
    ('.boite_idees .captchaImg', 'border-radius: 6px; border: 1px solid #b9d5c0; vertical-align: middle; cursor: pointer;'),
    ('.boite_idees .captchaRefresh', 'background: #ffffff; border: 1px solid #b9d5c0; border-radius: 50%; width: 36px; height: 36px; margin-left: 8px; vertical-align: middle; cursor: pointer;'),
    ('.boite_idees input[data-type="captcha"]', 'max-width: 14em;'),
    ('.wstextarea.boite_idees_rgpd', 'font-size: 0.85em; color: #4a5a4f; line-height: 1.5;'),
]
cssf = os.path.join(SITE, 'css/default.css')
css = open(cssf, encoding='utf-8').read()
if '.boite_idees ' not in css and '.boite_idees{' not in css:
    css = css.rstrip('\n') + '\n' + ''.join(
        '@media all {\n\t%s {\n%s\t}\n}\n' % (sel, ''.join(f'\t\t{d.strip()};\n' for d in decl.split(';') if d.strip()))
        for sel, decl in RULES)
    open(cssf, 'w', encoding='utf-8').write(css)
print('css ok')
