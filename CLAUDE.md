# Consignes pour Claude — dépôt baigneaux

Site WebSiCo 6.1 de la commune de Baigneaux, versionné sous forme de sources JSON (voir README.md
et docs/FORMAT.md). Langue de travail : français.

- Toujours partir d'un export frais : `python3 tools/unpack.py imports/<export>.ws_data`, puis
  commit « Export du … » avant toute modification. Une archive remplace TOUTE la base à l'import.
- Ne jamais committer `secrets/` ni un `ws_preferences.php` contenant un hash (dépôt public).
  `site/data/ws_preferences.php` doit contenir `__WS_PWD__`.
- Après modification : vérifier en local (`tools/local/setup.sh` si l'instance n'existe pas,
  puis `python3 tools/preview_local.py`, voir docs/LOCAL.md), puis
  `python3 tools/build.py --light` (liens vers le dev par défaut ; `--target prod` uniquement
  quand l'utilisateur demande une version prod) et `php tools/check_dump.php <archive>`.
  Le build par défaut n'inclut pas les préférences : le site cible garde son mot de passe.
- Tout élément ajouté à la main doit avoir un id neuf : `Z`/`Y` + compteur + `uniqid()` (13 hex),
  et une clé `owner` `{"$owner": "R"}`. Les `index` des enfants doivent rester cohérents.
- Les en-têtes/pieds dans les pages sont des copies de modèles régénérées au chargement :
  modifier `site/models/<modèle>.json`, pas les copies.
- Tester sur https://dev.baigneaux.fr avant la prod (https://www.baigneaux.fr).
- Éditer les pages avec `tools/sitelib.py` (clone() génère des ids neufs) ; garder les scripts de
  modification datés dans `tools/oneoff/`. Après toute modif visuelle : `tools/local/responsive_check.js`
  doit renvoyer 0 cas (1366, 1024, 820, 390 px).
- Navigation : barre horizontale = modèle `Header2` (5 rubriques, panneaux déroulants faits de WssMenu
  limités à une rubrique du plan du site) ; seul l'accueil garde la colonne de menu (modèle `MENU`).
  Les autres pages : en-tête mobile (`menu_burger`), fil d'Ariane (`Path`), puis le contenu dans un bloc
  `contenu_page` (indispensable : la règle CSS associée garde le bon affichage mobile).
- Accueil : cartes `carte_actu` (10 dernières, plus récente en premier) et `carte_evenement`
  (toutes, ordre chronologique) ; chaque actu a aussi sa fiche sur la page Actualités (ancre unique).
- Galerie : un album = une page sous p325 ; en ajouter un avec `python3 tools/album.py DOSSIER --titre … --date …`
  (voir docs/GALERIE.md), jamais en recopiant des images à la main dans le sommaire.
- Textes alternatifs = champ `tooltip` des WsImage (sinon WebSiCo affiche le nom de fichier).
- CSS : `python3 tools/check_css.py` doit passer (pas de commentaires, styles nommés simples,
  le reste en un bloc `@media` par règle) ; sinon l'éditeur WYSIWYG de WebSiCo est cassé.
  Vérifier aussi `node tools/local/edit_mode.js` (0 erreur JS) avant de livrer.
