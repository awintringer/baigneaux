# Pages de rubrique

Les 8 pages d'entrée de rubrique (Mairie, Vie communale, Enfance et jeunesse, Santé,
Assos commerces et services, Tourisme, Urbanisme, Intercommunalité) ne sont plus un simple menu :
depuis le 06/11/2026 elles affichent un titre, une phrase d'introduction et une **tuile cliquable
par page de la rubrique** (titre + une phrase de description). La page Mairie montre en plus
le maire et les adjoints (copie des cartes de la page Conseil municipal) et un bouton vers le
conseil complet.

Structure (dans le bloc `contenu_page`) : conteneur `rubrique` > titre (`Title`), texte
`rubrique_intro`, conteneur `tuiles_rubrique` > conteneurs-liens `tuile_rubrique` (un texte :
`<p><strong>Titre</strong></p><p>Description</p>`). Mairie : `rubrique_soustitre`, `apercu_elus`,
`rubrique_bouton`.

## Ajouter une page dans une rubrique

Le menu du haut (modèle `Header2`) et le menu de l'accueil listent la nouvelle page tout seuls.
**La tuile, elle, est à ajouter** : dans l'éditeur WebSiCo, dupliquer une tuile de la page de
rubrique, changer son texte et son lien ; ou par script avec `tools/sitelib.py` (`clone()`).

## Changement d'élus

L'aperçu de la page Mairie est une copie : après une modification des cartes du maire ou des
adjoints sur la page Conseil municipal, refaire la même modification sur la page Mairie.

Script d'origine : `tools/oneoff/2026-11-06_retouches_refonte.py` (descriptions des tuiles).
