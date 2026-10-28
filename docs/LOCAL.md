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

## Validé le 28/10/2026

Import via le formulaire officiel (`ws_tools.html`) d'une archive **allégée** (dump seul,
199 Ko) contenant une modification du sous-titre de l'accueil : modification visible, 398 images
intactes, préférences conservées, aucune ressource en erreur sur accueil, actualités, galerie, RPI,
PV des conseils.
