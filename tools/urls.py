"""Site URL parametrisation.

The sources in site/ keep absolute links on the production host (https://www.baigneaux.fr),
as WebSiCo stores them. At build time they are rewritten for the target site.
Matches http/https, with or without www/dev, but never e-mail addresses (mairie@baigneaux.fr).
"""
import re

TARGETS = {
    'dev': 'https://dev.baigneaux.fr',
    'prod': 'https://www.baigneaux.fr',
    'local': 'http://127.0.0.1:8080',
}
CANONICAL = TARGETS['prod']
SITE_URL_RE = re.compile(r'https?://(?:www\.|dev\.)?baigneaux\.fr(?![\w.-])')
DEV_URL_RE = re.compile(r'https?://dev\.baigneaux\.fr(?![\w.-])')

def resolve(target):
    """'dev' | 'prod' | 'local' | 'asis' | explicit base URL -> base URL or None (no rewrite)."""
    if target in (None, 'asis'): return None
    return TARGETS.get(target, target.rstrip('/'))

def rewrite_str(s, base, regex=SITE_URL_RE):
    return regex.sub(base, s)

def rewrite_json(j, base, regex=SITE_URL_RE):
    """Rewrite every string of a site/ JSON tree (including {"$text": [...]} lines)."""
    if isinstance(j, str): return rewrite_str(j, base, regex)
    if isinstance(j, list): return [rewrite_json(x, base, regex) for x in j]
    if isinstance(j, dict): return {k: rewrite_json(v, base, regex) for k, v in j.items()}
    return j

def count(j, regex=SITE_URL_RE):
    if isinstance(j, str): return len(regex.findall(j))
    if isinstance(j, list): return sum(count(x, regex) for x in j)
    if isinstance(j, dict): return sum(count(v, regex) for v in j.values())
    return 0
