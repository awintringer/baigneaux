"""Floute les visages d'enfants des photos de l'album « Cérémonie du 11 novembre 2026 » (p342)
et de la vignette de la carte d'accueil.

Les zones (x0, y0, x1, y1, en pixels des grandes images 1600 px) ont été repérées à la main, photo par
photo (les détecteurs automatiques ratent les visages de dos ou très petits). Les adultes restent nets.
Usage : python3 flou_visages_enfants.py DOSSIER_ORIGINAUX_FLOUTES
  où le dossier contient outNN.jpg (grandes images déjà floutées par le script de repérage, voir
  l'historique git) ; ici on ne fait que les installer, régénérer les vignettes -m et la vignette d'accueil.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import album
from PIL import Image
SRC = sys.argv[1]
IMG = album.IMG
base = 'ceremonie-du-11-novembre-novembre-2026'
for n in range(1, 25):
    im = Image.open(os.path.join(SRC, f'out{n:02d}.jpg')).convert('RGB')
    album._save(im, f'{base}-{n:02d}.jpg', 82)
    album.make_thumb(os.path.join(IMG, f'{base}-{n:02d}.jpg'), f'{base}-{n:02d}')
im = Image.open(os.path.join(SRC, 'out14.jpg')).convert('RGB'); w, h = im.size
nh = int(round(w / (400 / 180))); y0 = int(h * .18)
im.crop((0, y0, w, y0 + nh)).resize((400, 180), Image.LANCZOS).save(
    os.path.join(IMG, 'vignette-ceremonie-11-novembre-2026.jpg'), 'JPEG', quality=80, optimize=True, progressive=True)
# couverture de l'album : même cadrage que album.make_cover, depuis la photo 14 floutée
album.make_cover(os.path.join(IMG, f'{base}-14.jpg'), base)
