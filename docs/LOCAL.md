# Instance WebSiCo locale (préprod)

Une copie de WebSiCo 6.1 (code AGPL, https://github.com/websico/websico) tourne en local avec
PHP intégré et MariaDB, pour vérifier une modification avant de produire l'archive à importer.

```bash
tools/local/setup.sh imports/export.ws_data   # installe et charge un export (ou site/ sans argument)
tools/local/serve.sh                          # http://127.0.0.1:8080/  (laisser tourner)
python3 tools/preview_local.py                # recharge site/ après modification (liens -> local)
node tools/local/shot.js http://127.0.0.1:8080/ /tmp/home.png 1366   # capture + ressources en erreur
node tools/local/ui_import.js archive.ws_data # import via le formulaire d'admin officiel
```

- Mode édition : `http://127.0.0.1:8080/?mode=1`, mot de passe super-utilisateur **`local`**
  (`WS_SU_PWD` de la config locale). Le vrai mot de passe du site n'est jamais nécessaire.
- `router.php` reproduit les règles du `.htaccess` d'Apache pour le serveur PHP intégré.
- Les polices Google ne se chargent pas depuis le conteneur : titres en police de secours,
  sans incidence sur le site réel.

## Incompatibilité WebSiCo 6.1 / PHP ≥ 8.2 (constatée le 28/10/2026)

Tout import de données (y compris un export non modifié) se termine par :

```
8192......Creation of dynamic property WsTextarea::$name_in_model is deprecated (242)
Operation aborted.
```

- Origine : `WsSite::purgeDataFiles()` (`ws_site.php` l. 242) relit chaque page avec
  `unserialize()`. Les objets WebSiCo portent des propriétés non déclarées (`name_in_model`,
  `href`, `hdr_html`…, par conception), ce qui lève un `E_DEPRECATED` depuis PHP 8.2. Le
  gestionnaire `WsSite::abortPurge()` interrompt alors l'opération pour toute erreur sauf
  `E_STRICT`.
- La purge s'exécute **après** le dézippage et la restauration de la base : les données sont
  bien importées, seuls le ménage des fichiers non référencés et la redirection finale manquent.
- La même purge est lancée environ une fois sur cinq après un enregistrement dans l'éditeur
  (`ws_inits.php` l. 306) : le message peut donc aussi apparaître en édition.
- Baisser `error_reporting` dans `php.ini` ne suffit pas (le gestionnaire ne teste que
  `error_reporting() != 0`).

Correctif (une ligne, `ws_lib/ws_core/ws_site.php`, fonction `abortPurge`), appliqué par
`setup.sh` en local (`WS_NO_PATCH=1` pour s'en passer) :

```php
// avant
if (error_reporting() && $errno != E_STRICT)
// après
if (error_reporting() && !in_array($errno, array(E_STRICT, E_DEPRECATED, E_USER_DEPRECATED)))
```

Validé en local (PHP 8.3) : sans le correctif, même erreur que sur le dev ; avec, import
complet via le formulaire officiel d'une archive allégée (dump seul, 199 Ko), purge exécutée,
398 images conservées, préférences intactes.
