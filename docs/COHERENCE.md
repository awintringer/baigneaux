# Passe de cohérence du site (04/11/2026)

Base : site/ au 04/11 (= archive livrée `baigneaux-dev-20261104-1824`), relu page par page sur
l'instance locale (55 pages publiées, 4 largeurs d'écran). Hors périmètre : le diaporama de
l'accueil (docs/DIAPORAMA_ACCUEIL.md, autre chantier).

## Corrigé dans cette livraison (`tools/oneoff/2026-11-04_coherence.py`)

- **Menus déroulants** : dans « Services », la colonne « Intercommunalité » débordait du panneau
  blanc (« Espace France Services » coupé). Cause : 4 colonnes de 246 px minimum dans un panneau de
  900 px. Les colonnes s'adaptent maintenant à leur contenu. En 1024 px, le panneau « Services »
  sortait de l'écran à gauche et « Ma commune » à droite : les deux grands panneaux sont désormais
  centrés sous la barre. Vérifié en 1366, 1024 et 820 px (aucun débordement, panneau atteignable
  à la souris).
- **Titres d'onglet** : 8 pages traînaient le titre d'une page copiée (« chemins de randonnées
  Aire de Jeux », « Hébergeurs Domaines viticoles », « Tourisme Tourisme »…). Effacés.
- **Fil d'Ariane de Patrimoine** : il manquait « Vous êtes ici : » (copie de modèle périmée).
- **Petite enfance** : les 5 liens mail des assistantes maternelles ne fonctionnaient pas.

## 1. Informations périmées (à fournir par Adrien)

| Page | Problème |
|---|---|
| Accueil | « Prochain conseil municipal : le 2 novembre » est passé, et le lien « Convocation » ouvre l'avis du **5 octobre** |
| Médecins de garde | titre « septembre 2026 », liste d'octobre, rien pour novembre |
| Procès-verbaux | « Réunion du 31 août (à venir) » : lien vide ; aucun PV depuis le 15 juin |
| Délibérations | rubrique « Année 2026 » vide |
| Arrêtés municipaux | l'arrêté chasse/incendie du 25 juillet est-il encore « en vigueur » ? |
| Arrêtés préfectoraux | arrêté Tour de France 2021 à retirer |
| Emplois | offre GDON pour l'été 2026, terminée |
| Formalités administratives | texte de 2017 (« à compter du 15 mars 2017 », « 36 mairies ») : à remplacer par un renvoi à service-public.fr / ANTS |
| Hébergeurs, Office de tourisme | pages vides (titre seul) : remplir ou retirer du menu |
| Demandes d'autorisations | « déposés sur e-permis » sans lien vers le guichet |

## 2. Contradictions entre pages

- **Traiteur du marché du 8/11** : la page Évènements annonce « notre traiteur Jérôme » (encornets,
  chipirons, aïoli), l'actu du 4/11 présente Antonio « pour la toute première fois ». À trancher,
  puis aligner les deux textes.
- **Maïade** : l'actu du 22 juin dit que l'arbre sera planté « lui aussi le 13 septembre » alors
  que la fête est reportée au 20 septembre ; l'album Maïade n'a pas de date.
- **Gentilé** : Baigneudais (11 novembre), Baignaudais (Patrimoine, page Facebook), Baigneaudais /
  Baigneaudaise (vide-grenier, baguette). Choisir une forme.
- **Évènements** : « Evènements » (menu), « Evenements de notre commune » (titre de page et menu de
  l'accueil), « évènements » ailleurs. Proposition : « Évènements » partout, page renommée
  « Évènements de la commune ».
- **Catégories d'actus** : Actualités utilise « Vie Communale », « Services municipaux », « Santé
  Publique » ; l'accueil « Vie communale », « Mairie », « Santé ». Harmoniser sur les 4 étiquettes
  colorées. L'actu du 1er juin est classée sous « MAI 2026 ».
- **RPI 2026/2027** : CM1 à la fois à Lugasson et à Baigneaux, à vérifier.
- **Patrimoine** : « Canton de Targon » n'existe plus depuis 2015 (canton de l'Entre-Deux-Mers).

## 3. Navigation et structure

- **Accueil sans menus déroulants** : sa bannière a ses propres boutons (pas le modèle Header2),
  qui mènent aux pages de rubrique sans panneau ; la colonne de menu de gauche (12 entrées en
  capitales) fait doublon. Proposition : mêmes panneaux que partout ailleurs, colonne retirée.
- **Mentions légales, Historique** : fil d'Ariane « Vous êtes ici : mentions-legales » et onglet
  « Baigneaux - » sans nom ; ces pages sont hors plan du site. Les ajouter au plan (rubrique
  masquée) ou y retirer le fil d'Ariane.
- **Libellés** : « chemins de randonnées » sans majuscule (→ « Chemins de randonnée »),
  « Plan et Accès », « Mentions Légales ». Pages Santé/Mairie/… : liste de liens nue suivie de
  l'encart « Services publics 33 », pendant que d'autres rubriques ont des cartes : à uniformiser.
- **Historique des versions** : rien depuis le 28/10 (menu horizontal, trombinoscope, galerie par
  albums, boîte à idées, couleurs, actu du marché). Entrée prête à ajouter si Adrien valide.

## 4. Couleurs (complète docs/COULEURS.md)

- **Annuaire des services** : noms en rouge `#C95559` (contraste 4,0) et intitulés en bleu
  `#4E8DE8` (3,1, sous le seuil) hors charte verte. Proposition : noms en vert `#2f5e3e` (7,0),
  intitulés en gris foncé `#4a5a4f`. Sans dépendance à la couleur, donc sans risque en daltonisme.
- Survol des menus de l'accueil en vert clair `#3FA66B` (2,8) : préférer `#2f5e3e` souligné.

## 5. Orthographe (relevé, non corrigé)

Tranquilité → Tranquillité (×3) · accesible · nationnal · janiver · ultèrieurement · « S'y
ajouterons » → ajouteront · « vous serons communiqués » → seront · « pensant cette période » →
pendant · « l'entreprise que nous avons choisi » → choisie · notemment · « plats chaud » ·
« Nos bénévoles se sont arrêté » → arrêtés · « ont évoluées » → ont évolué · « rendre
rendez-vous » → prendre · « 19èmet » · « Arreté » · « ou nos élus » → où · « les differentes
demandes » · « SdF » (titre d'actu) → salle des fêtes.

## Suite donnée le 05/11/2026 (choix d'Adrien, `tools/oneoff/2026-11-05_retours_adrien.py`)

- Fait : prochain conseil le 14 décembre (convocation d'octobre retirée de l'accueil : ajouter un
  élément « Téléchargement » avec la nouvelle) ; arrêtés échus gardés et marqués « terminé » ;
  traiteur « Jérôme, Antonio pour les intimes » ; Baigneaudais / Baigneaudaises ; « Évènements »
  partout ; orthographe (§5) ; Annuaire des services aux couleurs de la charte (noms vert
  `#2f5e3e` en Manrope, intitulés `#4d6b56`, texte `#1f2937`) ; chevron sur les boutons à menu
  déroulant (sous le libellé en dessous de 900 px).
- Laissé tel quel : colonne de gauche et boutons sans panneau sur l'accueil, pages Hébergeurs et
  Office de tourisme, médecins de garde (mis à jour à la main), Maïade (report canicule).
- Reste ouvert : PV et délibérations, offre d'emploi échue, formalités (texte 2017), lien e-permis,
  catégories d'actus, fil d'Ariane des mentions légales / historique, bannière bleue de l'annuaire
  (image hors charte).
