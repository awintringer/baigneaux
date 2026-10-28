# baigneaux

Site web de la commune de Baigneaux, réalisé avec [WebSiCo](https://github.com/websico/websico) 6.1.

- Production : https://www.baigneaux.fr
- Développement : https://dev.baigneaux.fr

Ce dépôt contient le site **sous forme de sources lisibles**, reconstruites à partir des exports
WebSiCo (`.ws_data`), et des outils pour produire une archive importable après modification.
L'historique git sert d'historique des versions du site.

## Organisation

```
site/
  pages/<id>-<url>.json   une page publiée = un fichier (arbre d'éléments WebSiCo)
  models/<id>.json        modèles : en-tête, menus, pied de page, cartes d'actu...
  drafts/                 brouillons non publiés (table ws_tlc_draft)
  css/default.css         feuille de style utilisateur (éditeur de styles WebSiCo)
  tables/                 plan du site (ws_map), ws_system
  data/images, rawdata    images et documents téléchargeables
  data/ws_preferences.php préférences du site, mot de passe retiré (__WS_PWD__)
  layout.json             ordre des instructions du dump SQL
  zipmeta.json            métadonnées de l'archive d'origine (ordre, dates, empreintes)
tools/                    outils (Python 3, aucune dépendance ; PHP pour check_dump.php)
docs/                     audit, format des données
```

## Flux de travail

```bash
# 1. Importer un export frais (WebSiCo > Administration > Télécharger les données)
python3 tools/unpack.py imports/baigneaux.ws_data
git diff --stat          # ce qui a changé depuis le dernier export (modifs faites dans l'interface)
git commit -am "Export du JJ/MM/AAAA"

# 2. Modifier les fichiers de site/ (JSON, CSS), puis construire l'archive
python3 tools/build.py --light            # -> dist/baigneaux-AAAAMMJJ-HHMM.ws_data
php tools/check_dump.php dist/xxx.ws_data # validation par PHP lui-même

# 3. Importer l'archive dans WebSiCo (dev d'abord), vérifier, puis prod
```

**Règle d'or** : une archive WebSiCo est un instantané **complet** de la base (toutes les tables
sont supprimées et recréées à l'import). Toujours repartir d'un export frais du site cible avant de
modifier, sinon les changements faits entre-temps dans l'interface sont perdus.

### Options de build

| Option | Effet |
|---|---|
| *(aucune)* | archive complète, **sans** `ws_preferences.php` : le site cible garde ses préférences et son mot de passe |
| `--light` | seulement le dump SQL + fichiers nouveaux/modifiés (quelques Ko au lieu de ~100 Mo) |
| `--with-prefs` | inclut `ws_preferences.php` avec le hash de `secrets/ws_pwd` (rebuild identique) |
| `--verify F` | échoue si la sortie n'est pas identique octet pour octet à `F` |

Vérification de fidélité : `python3 tools/build.py /tmp/x.ws_data --with-prefs --verify export.ws_data`
reconstruit l'export d'origine **à l'octet près**.

## Mot de passe

`unpack.py` extrait le hash du mot de passe d'administration vers `secrets/ws_pwd` (ignoré par git)
et le remplace par `__WS_PWD__` dans le dépôt. Le dépôt étant public, ce fichier ne doit jamais
être commité. Le build par défaut n'en a pas besoin.

## Outils

| Outil | Rôle |
|---|---|
| `tools/unpack.py` | export `.ws_data` → `site/` |
| `tools/build.py` | `site/` → archive importable |
| `tools/outline.py` | plan lisible d'une page (`--css` pour le CSS embarqué) |
| `tools/audit.py` | audit statique (styles, CSS, liens, images) |
| `tools/check_dump.php` | vérifie un dump avec `unserialize()` de PHP |
| `tools/wsdata.py`, `tools/codec.py` | bibliothèque : dump SQL, sérialisation PHP, codec JSON |
