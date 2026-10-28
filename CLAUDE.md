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
