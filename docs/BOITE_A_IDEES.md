# Boîte à idées (formulaire WebSiCo natif)

Mise en place le 29/10/2026 (`tools/oneoff/2026-10-29_boite_a_idees.py`).

- **Page** `boite-a-idees.html` (p332), menu Ma Mairie > Boîte à idées. Formulaire `WssForm` :
  catégorie (liste), message, adresse mail facultative, captcha, bouton Envoyer.
- **Après envoi** : redirection vers `boite-a-idees-merci.html` (p333, hors menu, non indexée).
- **Destinataires** : `mairie@baigneaux.fr, awintringer@gmail.com` (champ « destination » du
  formulaire). WebSiCo ne gère pas la copie cachée : les deux adresses figurent en « À », visibles
  seulement des destinataires (l'habitant ne reçoit rien). « Répondre » répond à l'habitant
  (en-tête Reply-To) s'il a laissé son adresse.
- **Rien n'est stocké** sur le serveur : le message n'existe que dans les boîtes mail.

## Protections

| Risque | Protection |
|---|---|
| Injection SQL | aucune base de données touchée par le formulaire |
| Injection HTML / script dans le mail | contenu échappé (`htmlspecialchars`) par WebSiCo |
| Injection d'en-têtes (Bcc…) | retours à la ligne supprimés par PHPMailer (testé) |
| Robots | captcha image ; identifiant de message horodaté, valable 24 h, usage unique ; envoi refusé s'il suit l'affichage de moins d'une seconde |
| Relais de spam | copie à l'expéditeur désactivée (`ccPrompt` vide) : une copie demandée par un robot est refusée |
| Pièces jointes forgées | WebSiCo joindrait tout fichier posté ; sur PHP 8, PHPMailer 5.2 plante sur ce cas et rien n'est envoyé (testé) |

Limites connues : la catégorie n'est pas vérifiée côté serveur (un robot peut en inventer une) ;
si l'envoi SMTP échoue, l'habitant voit quand même la page « Merci » (erreur seulement dans le
journal PHP). D'où l'importance du test sur le dev.

## Prérequis serveur (prestataire)

Le serveur n'envoie pas de mail aujourd'hui. Deux interventions, sur le dev puis la prod :

### 1. Réglages d'envoi dans `ws_config.php` (racine du site)

```php
define ("WS_CONTACT_MAIL", 'mairie@baigneaux.fr');   // expéditeur (« From ») des mails du site
define ("WS_SMTP_HOST", 'smtp.xxx');                 // relais SMTP de l'hébergeur / de la messagerie
define ("WS_SMTP_PORT", 587);
define ("WS_SMTP_USER_NAME", '...');
define ("WS_SMTP_USER_PWD", '...');
```

L'adresse d'expéditeur doit être autorisée par le relais et par le SPF/DKIM de `baigneaux.fr`,
sinon les mails arrivent en spam (Gmail surtout).

### 2. Correctif WebSiCo 6.1 pour PHP 8 : `tools/serveur/websico-formulaires-php8.patch`

À appliquer à la racine du site : `patch -p1 < websico-formulaires-php8.patch`
(vérifié : s'applique proprement sur WebSiCo 6.1).

- `ws_lib/third_party_includes/PHPMailer/PHPMailerAutoload.php` : suppression de la fonction
  `__autoload()`, **erreur fatale sur PHP 8** : sans ce correctif, tout envoi de formulaire
  produit une erreur 500 et aucun mail ne part.
- `ws_lib/ws_core/ws_standard_classes.php` (contrôle du captcha) :
  - un reste de débogage (`var_dump($value); exit();`) affichait une page blanche avec le code
    tapé en cas d'erreur ; remplacé par un message en français avec un lien de retour au formulaire ;
  - comparaison insensible à la casse et aux espaces : le captcha mélange majuscules et minuscules
    (k/K, x/X, w/W…), source d'échecs pour les habitants.

Ces fichiers font partie du moteur WebSiCo, pas des données : nos archives `.ws_data` ne les
contiennent pas et ne les écrasent pas.

## Tester sur le dev

1. Importer l'archive légère (`python3 tools/build.py --light`).
2. Envoyer un message depuis https://dev.baigneaux.fr/boite-a-idees.html, puis un second avec un
   captcha volontairement faux (message d'erreur attendu).
3. Vérifier la réception sur les deux adresses (et le dossier spam), l'expéditeur, et que
   « Répondre » vise l'adresse saisie.

## En local

`tools/local/setup.sh` n'active pas l'envoi. Pour tester : appliquer le correctif ci-dessus dans
l'instance locale, définir `WS_SMTP_HOST` = `127.0.0.1` et `WS_SMTP_PORT` = `2525` dans son
`ws_config.php`, et lancer un faux serveur SMTP qui range les mails dans un dossier :
`python3 -m aiosmtpd -n -l 127.0.0.1:2525 -c aiosmtpd.handlers.Mailbox <dossier>`
(`pip install aiosmtpd` ; le dossier doit contenir `tmp/`, `new/`, `cur/`).

## Évolution prévue

Enregistrement des messages, modération et page publique « Idées » : demande un petit module PHP
déposé sur le serveur (accès FTP ou intervention du prestataire), hors WebSiCo.
