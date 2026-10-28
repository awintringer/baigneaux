# Audit du site — export du 28/10/2026

Base : export `.ws_data` du 28/10/2026 10:31 (WebSiCo 6.1), comparé aux sites en ligne le même
jour. Chiffres produits par `tools/audit.py` et des scripts ponctuels.

## 1. État des lieux

- **Dev et prod identiques à l'export** : mêmes 4 actus à la une (dernière : rénovation du
  cimetière, 17/10), mêmes événements (marché 8/11, marché de Noël 5/12, spectacle 6/12),
  conseil municipal du 2/11. Dernière modification : page d'accueil le 23/10.
- **49 pages, 17 modèles, 8 brouillons, 4 153 éléments**, 398 images (101 Mo), 15 documents.
- Plan du site cohérent : aucune page orpheline, aucune entrée de menu sans page. Une entrée
  résiduelle `en` → `p102` (page anglaise inexistante) traîne dans `ws_map`.

### Historique des versions (page `historique-modifications`)

| Date | Contenu |
|---|---|
| 20/04/2026 | mise en ligne version dev |
| 22/04 | déchets verts, bulles info (commissions, RPI, CDC, carte communale), suppression PLU, page historique |
| 27/04 | actus, PV 30 mars, nettoyage modèles/styles, modèle bulle_info, infos services |
| 29/04 | refonte accueil, TL Plomberie, APE Frontenac, médecins de garde |
| 01/05 | refonte Santé |
| 10/05, 14/05 | événements, actus, photos journée citoyenne, menus écoles |
| 29/05 | **refonte graphique complète**, catégorie Sécurité |
| 22/09 | petit polish, marché des producteurs, changement du mail de contact |

**Retard** : rien n'est noté depuis le 22/09, alors que la base montre des modifications le
22/09 (annuaire, commerces), 28–29/09 (galerie, arrêtés préfectoraux, médecins de garde),
16/10 (salle des fêtes, demandes d'autorisations), 17/10 (actualités) et 23/10 (accueil).
Avec git, cette page pourra être générée à partir des messages de commit.

### Brouillons non publiés (`site/drafts/`)

| Brouillon | Situation |
|---|---|
| `p300` Associations (21/07) | titre de bandeau changé en « Evènements » : **probablement une erreur**, à jeter |
| `p330`, `p331` (02/06) | logo remplacé par les armoiries : publier ou jeter |
| `Fiche_actu_complete` (17/10) | modèle de fiche d'actu retouché, non publié |
| `vignette_info` (02/06) | contenu de vignette différent (OTV → branches) |
| `vignette_evenement` (02/06) | identique au publié : à jeter |
| `Bloc_evenement`, `bulle_version` | modèles jamais publiés |

## 2. Structure des données

Saine dans l'ensemble : un arbre d'objets clair, lisible, sans corruption (vérifié par
`unserialize()` de PHP sur les 70 enregistrements). Les limites sont celles de l'outil :

- **Mise en page par imbrication** : profondeur jusqu'à 14 niveaux. Une carte d'actu sur
  l'accueil = 10 éléments (conteneur > rangée > 2 colonnes > catégorie / date, titre, texte,
  image). D'où la pénibilité des mises à jour manuelles.
- **Modèles bien utilisés** pour en-tête, menu, menu burger, fil d'Ariane et pied de page
  (appliqués à 45–49 pages). Les copies stockées dans chaque page sont des caches régénérés au
  chargement : modifier le modèle suffit.
- **Les cartes d'actu et d'événement ne sont pas des modèles liés** : ce sont des copies
  indépendantes (`name_in_model` montre qu'elles viennent d'un modèle, mais elles vivent leur
  vie). Changer le style d'une carte = la modifier N fois.
- **Contenu en double** : chaque actu existe deux fois (carte courte sur l'accueil, fiche
  complète sur la page Actualités), saisies à la main séparément.
- **Dates en dur sans année** pour les événements (« 8 / nov ») : rien n'expire tout seul.
- `test_ikul` : un modèle de test utilisé sur 2 pages.

## 3. HTML (contenu des blocs texte)

- **186 attributs `style="..."`** dans le HTML (ex. bulle agenda :
  `<span style="font-size: 35px;">8</span>`) : la présentation est noyée dans le contenu.
- **772 `&nbsp;` et 214 paragraphes vides** utilisés comme espacement.
- **358 liens absolus vers `https://www.baigneaux.fr/...`** (+ 7 en `http://`) : sur le site de
  dev, cliquer dans le menu ou l'en-tête **renvoie vers la prod**. À remplacer par des liens
  relatifs (`mairie.html`), qui marchent sur les deux.
- **En-tête construit à la main** : 6 blocs texte contenant chacun un lien, au lieu d'un
  composant menu ; à maintenir à la main si une page change d'adresse.
- **Accessibilité** : 285 images sur 322 sans texte alternatif ; menus de cantine publiés
  uniquement en image PNG (illisibles par un lecteur d'écran et lourds).
- **Adresse mail incohérente** : le pied de page affiche `mairie@baigneaux.fr`, mais la version
  mobile du bloc « Nous contacter » de l'accueil affiche encore `communede.baigneaux@wanadoo.fr`.

## 4. CSS

### Feuille de style (`site/css/default.css`, 47 styles, 892 lignes)

Propriétés invalides (ignorées par les navigateurs) :

| Où | Problème |
|---|---|
| `.wsstitle_Title`, `.wsstitle_Titre_main_page_sub` | `undefined: #950000;` (déchet de l'éditeur), `border-color: aa8a8f;` (sans `#`), `text-shadow: #000000;` (pas de décalage) |
| `.wssdownload_Telechargement a`, `.wstextarea_Texte_important_centre a:hover` | `font-variant: bold;` (n'existe pas : c'est `font-weight`) |
| `.wscontainer_Path`, `.wsspagepath_Path a` | `color : #000091` (fonctionne, mais incohérent) |

Duplications et dette :

- `bulle_actu_categorie_{mairie,vie_communale,sante,securite,emploi}` : 5 × 3 blocs identiques
  qui ne diffèrent que par la couleur. Les trois derniers ne sont **jamais utilisés**, pas plus
  que `wscontainer_Main`.
- `Lien_header`, `liens_page_principale`, `retour_accueil` : mêmes boutons recopiés trois fois.
- Menus `Main` et `Sous-menus` : mêmes règles recopiées, et deux soulignements en dégradé
  différents (l'un avec un bleu `#1E4D8C` hérité de l'ancien thème).
- Restes de l'ancienne charte : `#000091` (bleu État), `#950000`, `#C95559`, `#4E8DE8`,
  `#AA8A8F`, `#d9b26f` dans un thème désormais vert (`#2f5e3e`, `#6baa7a`, `#e7f1e8`).
- Noms peu parlants ou trompeurs : `fred1` (pied de page), `Essai`, `Nom-endroti`, `Cadre-rose`
  (qui est vert), `FORMALITES` (utilisé pour les titres de l'historique), `Title3`.
- Pas de variables CSS : chaque couleur est recopiée en dur.

### CSS embarqué par élément

**1 332 éléments** portent leur propre règle CSS (81 Ko au total), surtout des largeurs de
colonnes (`width: 16%` ×230, `25%` ×141) et des centrages (`margin: auto` ×127), mais aussi des
polices et tailles répétées carte par carte (dates des actus en `Inter 2em` recopié à chaque
fiche). **62 rangées ont des colonnes dont la somme dépasse 100 %**, dont 15 sur Actualités
(deux colonnes à 60 % pour catégorie / date).

### Polices

- Inter, Manrope et Playfair Display sont déclarées dans le `<head>` de **chacune des 49 pages**
  (6,3 Ko recopiés, à modifier 49 fois). Une seule graisse (400) est chargée alors que le CSS
  utilise partout du gras : le navigateur fabrique un faux gras, moins net.
- Chargement depuis `fonts.gstatic.com` (Google) : l'adresse IP des visiteurs est transmise à
  Google, ce qui est contestable au regard du RGPD pour un site public. Héberger les polices sur
  le site règle les deux problèmes.
- `Calibri` (police Windows) est utilisée dans 4 styles : absente sur Mac, Android et iPhone.

## 5. Images et galerie

- 204 originaux uploadés (79 Mo) + 206 versions affichées (23 Mo). Les originaux sont surtout
  des photos WhatsApp et des flyers PNG.
- Images affichées trop lourdes : `cdc.png` 2 Mo (1920 px), `tl-plomberie-flyer.png` 1,6 Mo,
  menus de cantine en PNG 0,8–1,2 Mo. En JPEG/WebP, environ 10 fois plus léger.
- Galerie : 68 images sur une seule page de 215 éléments, sans chargement différé. Gros chantier
  identifié : compression systématique, vignettes, et regroupement par événement.

## 6. Priorités proposées

1. **Liens relatifs** partout (dev utilisable sans fuite vers la prod), correction du mail mobile.
2. **Nettoyage CSS** : propriétés invalides, styles morts, variables de couleur, factorisation
   des catégories et boutons (sans changement visuel).
3. **Actualités** : rangée défilante horizontalement sur l'accueil (faisable en CSS via
   `more_classes` sur la rangée, sans tricher), et un outil `tools/` d'ajout de carte qui crée
   en une commande la carte d'accueil + la fiche complète, avec des ids neufs.
4. **Polices auto-hébergées** avec les bonnes graisses, déclarées une seule fois.
5. **Images** : compression, et menus de cantine plus légers et lisibles.
6. Ménage : brouillons, `test_ikul`, entrée `en` du plan, page historique tenue à jour.
