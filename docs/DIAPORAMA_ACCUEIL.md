# Diaporama dans le cadre « Bienvenue à Baigneaux » (étude du 04/11/2026)

Étude de faisabilité, rien n'est encore implémenté. Base : archive livrée le 04/11/2026
(`baigneaux-dev-20261104-1824-light`), le site n'a pas bougé depuis.

## Situation actuelle

- Le cadre est le conteneur `Z196a19b5cbc8871` (style `Banniere`) en tête de `site/pages/home.json` :
  barre de rubriques, titre « Bienvenue à Baigneaux », sous-titre, logo « village ambassadeur ».
- La photo est un **fond CSS** du style `Banniere` (`data/images/background/1442_banner.png`,
  `background-size: cover`). Ce cadre est masqué sur mobile (`dontDisplayOnXS dontDisplayOnS`).

## Ce que WebSiCo 6.1 permet

- **Aucun composant diaporama natif.** Les classes du noyau (`ws_core_classes.php`,
  `ws_standard_classes.php`) : conteneurs, textes, images, menus, formulaires, `WsRawText`…
  La visionneuse « En galerie » ne s'ouvre qu'au clic, elle ne fait pas défiler seule.
  Les « wippets » (`ws_addons/*.ws_code`, ex. `imgSimpleSlider`) sont prévus dans le code mais
  aucun n'est livré avec WebSiCo ni présent sur le serveur.
- **`WsRawText` (HTML brut) affiche son contenu tel quel**, `<style>` et `<script>` compris
  (déjà utilisé pour les cartes OpenStreetMap, p259 et p320).
- La feuille `default.css` ne peut pas contenir de `@keyframes` à plusieurs étapes (le parseur de
  l'éditeur de styles casse, voir `tools/check_css.py`) : l'animation doit donc vivre dans un
  `<style>` du `WsRawText`, pas dans `default.css`.
- Tout se passe dans le navigateur : **aucun PHP ajouté**, donc aucun lien avec la version de PHP
  du serveur.

## Montage proposé (commun aux options)

1. Dans le cadre, un conteneur `diaporama_accueil` placé derrière le titre, contenant 4 à 6
   `WsImage` (photos recadrées en 1200×400 env., < 200 Ko chacune, texte alternatif dans `tooltip`,
   « En galerie » décoché). Les photos restent **modifiables dans l'éditeur WebSiCo**.
2. Le fond CSS actuel reste en secours (si les photos ne chargent pas).
3. Un voile léger derrière le titre pour garder le texte lisible sur toutes les photos.
4. Un `WsRawText` avec le `<style>` (et le petit script pour B/C).
5. Désactivé en mode édition (sinon les photos bougent sous la souris) et figé si le visiteur a
   demandé « réduire les animations » (`prefers-reduced-motion`).

## Options

| | Comportement | Technique | Risque |
|---|---|---|---|
| A | Fondu enchaîné automatique (toutes les 6 à 8 s), toujours la même photo au départ | CSS seul | très faible |
| B | Une photo tirée au hasard à chaque chargement, fixe ensuite | ~10 lignes de JS | très faible |
| C | B + A : départ au hasard puis fondu enchaîné | CSS + ~15 lignes de JS ; sans JS, retombe sur A | faible |

Recommandation : **C**. Sans JS ça reste un diaporama (A), sans les photos ça reste le fond actuel.

## Points d'attention

- Poids : 5 photos ≈ 0,8 Mo de plus sur l'accueil (téléchargées même sur mobile où le cadre est
  masqué, sauf si on les charge par le script).
- Vérifs habituelles : `check_css.py`, `responsive_check.js` (0 cas), `edit_mode.js` (0 erreur JS),
  puis archive DEV avant la prod.
- Il faut les photos : 4 à 6 vues horizontales du village (on peut puiser dans les albums de la
  galerie).
