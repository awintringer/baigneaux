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

# 2. Modifier les fichiers de site/ (JSON, CSS), vérifier en local (docs/LOCAL.md)
python3 tools/preview_local.py

# 3. Construire l'archive (liens vers le dev par défaut) et la valider
python3 tools/build.py --light                 # -> dist/baigneaux-dev-AAAAMMJJ-HHMM-light.ws_data
php tools/check_dump.php dist/xxx.ws_data      # validation par PHP lui-même

# 4. Importer dans WebSiCo (Administration > Charger des données) sur le dev, vérifier,
#    puis reconstruire pour la prod :
python3 tools/build.py --light --target prod
```

### URL du site

WebSiCo stocke les liens internes en absolu. Les sources gardent l'URL de prod
(`https://www.baigneaux.fr`) ; le build les réécrit selon `--target` :
`dev` (défaut, `https://dev.baigneaux.fr`), `prod`, `local` (`http://127.0.0.1:8080`), `asis`
(inchangé) ou une URL explicite. `unpack.py` ramène automatiquement un export du dev aux URL de
prod. Les adresses mail (`mairie@baigneaux.fr`) ne sont jamais touchées.

**Règle d'or** : une archive WebSiCo est un instantané **complet** de la base (toutes les tables
sont supprimées et recréées à l'import). Toujours repartir d'un export frais du site cible avant de
modifier, sinon les changements faits entre-temps dans l'interface sont perdus.

### Options de build

| Option | Effet |
|---|---|
| *(aucune)* | archive complète, **sans** `ws_preferences.php` : le site cible garde ses préférences et son mot de passe ; liens vers le dev |
| `--target prod` | liens vers `https://www.baigneaux.fr` (voir « URL du site ») |
| `--light` | seulement le dump SQL + fichiers nouveaux/modifiés (quelques Ko au lieu de ~100 Mo ; validé avec l'import officiel en local) |
| `--with-prefs` | inclut `ws_preferences.php` avec le hash de `secrets/ws_pwd` (rebuild identique) |
| `--verify F` | échoue si la sortie n'est pas identique octet pour octet à `F` |

Vérification de fidélité : `python3 tools/build.py /tmp/x.ws_data --target asis --with-prefs --verify export.ws_data`
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
| `tools/preview_local.py` | charge `site/` (ou une archive) dans l'instance WebSiCo locale |
| `tools/local/` | installation de l'instance locale, captures, import via l'admin (docs/LOCAL.md) |
| `tools/urls.py` | réécriture des URL du site selon la cible |
| `tools/check_css.py` | vérifie que `default.css` respecte la syntaxe de l'éditeur de styles WebSiCo |
| `tools/icons/make_icons.py` | génère les icônes SVG des tuiles de l'accueil (libellé masqué en petit) |
| `tools/local/edit_mode.js` | ouvre une page en mode édition et remonte les erreurs JavaScript |
| `tools/sitelib.py` | édition des pages en Python : recherche, clonage avec ids neufs, index, sauvegarde |
| `tools/oneoff/` | scripts de modifications datés (traçabilité de ce qui a été fait hors interface) |
| `tools/local/responsive_check.js` | audit débordements / images cassées sur toutes les pages, 4 largeurs |
| `tools/outline.py` | plan lisible d'une page (`--css` pour le CSS embarqué) |
| `tools/audit.py` | audit statique (styles, CSS, liens, images) |
| `tools/check_dump.php` | vérifie un dump avec `unserialize()` de PHP |
| `tools/wsdata.py`, `tools/codec.py` | bibliothèque : dump SQL, sérialisation PHP, codec JSON |

## Rangées défilantes de l'accueil

Les rangées « À la une » et « À venir » défilent horizontalement (flèches sur ordinateur, glisser
sur mobile). Une rangée devient défilante dès que ses cartes portent la classe `carte_actu` ou
`carte_evenement` (champ « classes supplémentaires » du conteneur dans WebSiCo) : dupliquer une
carte existante dans l'éditeur conserve la classe. CSS en fin de `site/css/default.css`, flèches
dans l'en-tête HTML de la page d'accueil. Convention : 10 dernières actus (plus récente à gauche),
tous les événements à venir (ordre chronologique).

## Polices

Inter, Manrope et Playfair Display sont hébergées dans `data/fonts/` (licence SIL OFL,
`data/fonts/OFL.txt`) et déclarées dans l'en-tête HTML de chaque page. Une nouvelle page créée
dans WebSiCo doit reprendre cet en-tête (copier celui d'une page existante).

## Feuille de style : contraintes de l'éditeur WebSiCo

L'éditeur de styles de WebSiCo (`ws_style.js`) découpe la feuille avec des expressions
régulières ; une syntaxe qu'il ne comprend pas **casse tout l'éditeur WYSIWYG** (incident du
28/10/2026, causé par un commentaire CSS). Règles :

- aucun commentaire `/* … */` ;
- styles nommés (`.wstextarea_Xxx`…) : un sélecteur par règle, en début de ligne ;
- tout le reste (`:has()`, sélecteurs multiples, `::-webkit-scrollbar`, media queries…) : **un bloc
  `@media` par règle** (`@media all { … }` pour du CSS sans condition). L'éditeur conserve ces
  blocs tels quels, sans les analyser, et les replace en fin de feuille quand on enregistre un style.

`python3 tools/check_css.py` doit répondre « compatible » avant chaque build.
