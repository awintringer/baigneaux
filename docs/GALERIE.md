# Galerie « Notre village en images »

Depuis le 29/10/2026, la galerie est découpée en albums :

- **Sommaire** : page `p325` (`galerie-evenements.html`). Une carte par album (photo de couverture 4:3,
  titre, date, nombre de photos), du plus récent au plus ancien. Les cartes sont des conteneurs-liens
  (`more_classes` `carte_album`) dans une grille (`albums_grille`).
- **Albums** : une page par événement (`galerie-<slug>.html`, `p334` et suivantes), rangée sous la galerie
  dans le plan du site. Le fil d'Ariane la montre, le menu non (il s'arrête au 2e niveau). Grille de
  vignettes carrées (`album_grille`) ; au clic, la visionneuse de WebSiCo ouvre la grande version et
  permet de passer d'une photo à l'autre dans l'album.

## Ajouter un album

1. Mettre les photos dans un dossier (ex. celles reçues par WhatsApp). Elles sont affichées dans
   l'ordre alphabétique des noms de fichiers, donc chronologique pour les photos WhatsApp.
2. Lancer :

   ```bash
   python3 tools/album.py ~/photos/fete-2027 --titre "Fête du village" --date "19 septembre 2027"
   # options : --couverture IMG_0042.jpg   (défaut : la première photo)
   #           --position 2                (place dans le sommaire ; défaut 0 = en tête)
   #           --nom "Nom court"           (si le titre dépasse 45 caractères, limite de WebSiCo)
   ```

3. Vérifier en local, construire l'archive et l'importer sur le dev (voir CLAUDE.md).

Le script produit, pour chaque photo, une grande version (1600 px max, orientation corrigée) et une
vignette carrée de 400 px, plus une couverture 600×450. L'adresse de la page est tirée du titre et du
mois de la date (`galerie-fete-du-village-septembre-2027.html`). Un album déjà présent est refusé.

## Retoucher un album existant

Dans l'éditeur WebSiCo : changer une photo, un texte alternatif, le titre ou le texte de la carte se fait
normalement. Pour **ajouter** des photos à un album, le plus simple est d'en dupliquer une dans la grille
de l'album puis de changer l'image (l'option « En galerie » reste cochée).
