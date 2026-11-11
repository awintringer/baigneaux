# Couleurs et accessibilité (revue du 01/11/2026)

Contexte : le gestionnaire du site est daltonien ; une partie des visiteurs aussi (≈ 8 % des hommes).
Mesures faites sur l'instance locale (contraste WCAG 2.1 calculé sur le texte réellement affiché,
6 pages : accueil, actualités, galerie, conseil municipal, mairie, boîte à idées) et simulation
protanopie / deutéranopie (matrices de Machado 2009). Seuils WCAG AA : 4,5 pour le texte courant,
3 pour le grand texte.

## Ce qui va bien

- Couleur principale `#2f5e3e` (vert sapin) : 7,5 sur blanc, 7,0 sur `#f7f7f4`. Texte courant
  `#1f2937` / `#000` : 13 à 19. Boutons blancs sur vert : 7,5.
- Les liens « Lire la suite », téléphone, mail sont soulignés : l'information ne repose pas sur la
  couleur seule.
- Les dates des cartes d'événements (blanc sur vert) et les intitulés sont lisibles en toute vision.

## À corriger

### 1. Étiquettes de catégorie des cartes d'actu (accueil, actualités) — prioritaire

Petit texte gras en capitales (~11 px), couleur seule pour distinguer la catégorie :

| Catégorie | Actuel | Contraste | Proposé | Contraste |
|---|---|---|---|---|
| Mairie | `#007506` | 5,5 | `#2f5e3e` (couleur du site) | 7,0 |
| Vie communale | `#FF4DD5` | **2,7** | `#a1307f` | 6,0 |
| Santé | `#00A86B` | **2,9** | `#005fae` | 6,0 |
| Sécurité | `#A36D00` | **4,1** | `#a34700` | 5,7 |

- 3 couleurs sur 4 échouent au contraste.
- En protanopie, Mairie et Sécurité sont quasi identiques (écart ΔE ≈ 4) ; Santé et Mairie sont proches
  même en vision normale (ΔE ≈ 30). Avec la palette proposée, l'écart minimal passe à 18 (protan) /
  27 (deutan) / 55 (normal), tout en restant ≥ 4,5 de contraste. Le libellé reste écrit en toutes
  lettres : la couleur n'est qu'un repère d'appoint, c'est suffisant.
- Règles CSS : `.wstextarea_bulle_actu_categorie_*` dans `site/css/default.css` (l. ~730-880).

### 2. Fil d'Ariane

Trois couleurs sans rapport avec la charte : « Vous êtes ici » bleu marine `#000091`, liens rouge
foncé `#950000`, flèches orange. Contrastes corrects, mais en deutéranopie le rouge foncé devient un
kaki proche du vert du site et du texte. Proposition : liens en `#2f5e3e` soulignés, flèches grises.

### 3. Fond de page vert menthe `#d1ffe3`

Très saturé, il « vibre » à côté des cartes `#f7f7f4` et `#e7f1e8` ; en deutéranopie il devient un
beige-gris proche des cartes, les blocs se distinguent alors surtout par les ombres. Proposition : un
fond plus calme et plus contrasté avec les cartes, par exemple `#e3ece5`.

## Remarques générales (hors couleurs)

- Accueil : la colonne de menu de gauche (12 entrées en capitales) double la barre horizontale ;
  la retirer donnerait de la place aux horaires et contacts, comme sur les autres pages.
- Bannière « Services publics 33 » : texte blanc sur image, lisible ici, mais à surveiller si l'image
  change (pas de fond de secours).
- Les affiches d'événements sont des images de texte : le champ texte alternatif (`tooltip`) devrait
  reprendre l'essentiel (date, lieu, heure) pour les lecteurs d'écran.

**Appliqué le 01/11/2026** (choix d'Adrien : étiquettes, fil d'Ariane et fond) par `tools/oneoff/2026-11-01_couleurs.py` ; fond retenu `#DCE7DF`, séparateurs du fil d'Ariane `#5f6f64`. Restent à faire : colonne de menu de l'accueil, textes alternatifs des affiches.
