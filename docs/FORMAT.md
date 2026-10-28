# Format des données WebSiCo (v6.1)

Notes établies par lecture du code source WebSiCo (AGPL, https://github.com/websico/websico)
et analyse de l'export du 28/10/2026.

## L'archive `.ws_data`

Un zip Info-ZIP 3.0 (`zip -rq site.ws_data data/* _mysql_dump`) contenant :

- `data/images/`, `data/images/background/` (images de fond du CSS), `data/rawdata/` (documents),
  `data/icon.ico`, `data/ws_preferences.php` ;
- `_mysql_dump` : dump SQL maison, **une instruction par ligne** pour les `INSERT`.

### Import (`WsMetaSite::RestoreData`)

1. vidage du cache ;
2. `unzip -oq archive` dans la racine du site : écrase les fichiers présents dans l'archive,
   **ne supprime rien** ;
3. rejeu du dump ligne à ligne (`DROP TABLE` / `CREATE TABLE` / `INSERT`) : **la base est
   intégralement remplacée** ;
4. purge (`purgeDataFiles(2)`) : suppression dans `images/`, `background/`, `rawdata/` de tout
   fichier non référencé par le CSS ou un élément (publié ou brouillon).

Conséquences : `ws_preferences.php` absent de l'archive ⇒ préférences et mot de passe du site
cible conservés ; une archive « légère » (dump + nouveaux fichiers) suffit en théorie (à valider).

## Tables

| Table | Contenu |
|---|---|
| `ws_tlc` | « top level containers » publiés : pages (`lang`=`fr`) et modèles (`lang`=`''`) |
| `ws_tlc_draft` | brouillons (pages/modèles modifiés non publiés, presse-papiers) |
| `ws_user_css` / `_draft` | feuille de style utilisateur (`id`=`default`) |
| `ws_map` / `_draft` | plan du site : tableau PHP sérialisé `[{id, category}]` par langue |
| `ws_system` | `data_version`, `last_id` (compteur des ids de pages `pNNN`), `purge_counter` |

Colonnes `ws_tlc` : `id, lang, url_id, date, name, properties, serialized_object`.

## Objets

`serialized_object` est un objet PHP sérialisé (`WssPage` ou `WsTopLevelContainer`) dont
`contents` contient récursivement des `WsContainer` et des composants :
`WsTextarea` (HTML TinyMCE dans `value`), `WssTitle`, `WsImage`, `WssMenu`, `WssDownload`,
`WssPagePath`, `WssBadge`, `WsRawText` (HTML brut).

Propriétés utiles : `id`, `user_style` (→ classe CSS `<classe>_<style>`, ex. `wstextarea_Titre`),
`more_classes` (classes CSS libres, ex. `dontDisplayOnXS`), `embedded_css_rules`
(CSS propre à l'élément, sélecteur `.id_<id>`), `model_id`, `index`, `properties` (drapeaux).

- **Ids** : `uniqid(préfixe . compteur)` — `Z…` conteneurs, `Y…` composants (13 hex de temps).
  Tout élément ajouté hors interface doit recevoir un id neuf et unique.
- **owner** : chaque élément référence son parent (`R:n` ou `r:n` selon les cas). Le codec de ce
  dépôt (`tools/codec.py`) le représente par `{"$owner": "R"}` et recalcule les numéros.
- **Modèles** : un conteneur avec `model_id` est **remplacé au chargement** par le contenu du
  modèle (`ApplyModel`). Les copies d'en-tête/pied dans chaque page sont donc des caches : pour
  changer l'en-tête partout, on modifie le modèle.
- **Rendu** : une rangée horizontale est un `div.wssystemcontainer.H.hDepthN` dont les enfants
  `div` sont les colonnes ; la classe utilisateur (`user_style`, `more_classes`) est portée par le
  `WsContainer` englobant. C'est l'accroche pour du CSS sur mesure (ex. défilement horizontal).

## Représentation JSON (dossier `site/`)

Voir l'en-tête de `tools/codec.py`. Le passage export → JSON → export est sans perte
(vérifié octet par octet).
