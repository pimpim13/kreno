# Kreno — application de réservation de créneaux collectifs

**Kreno** est la version générique et adaptable de l'application développée pour la salle de sport **le Garage** (coaching : Loïc Fitness Coaching). Le code est issu d'un clone du dépôt `pimpim13/garage` ; il ne faut **jamais pousser vers ce dépôt** (le remote `garage` est volontairement bloqué).

## Cible et modèle de diffusion

- **Cible** : toute activité à réservation de créneaux collectifs (salle de sport, studio de yoga/pilates, cours de danse, escalade, arts martiaux, ateliers, etc.), et pas seulement les salles de sport.
- **Hébergement** : **une instance par client, hébergée chez lui**. Nous n'hébergeons qu'en **test** et en **pré-production**. Pas de multi-tenant : chaque instance a sa propre base, son propre `.env`, son propre thème. La livraison doit donc être simple à installer et à mettre à jour par le client (voir chantier 5).
- **Client n°1 : le Garage.** Ses réglages par défaut doivent **reproduire exactement le comportement actuel**. Les **369 tests existants doivent rester verts** à chaque étape : c'est le filet de sécurité de toute la généralisation. Toute nouvelle option se code avec une valeur par défaut égale au comportement historique du Garage, et un nouveau client ne fait que surcharger ces valeurs.

## Principe directeur de la généralisation

Ne rien casser, ne rien dupliquer : on remplace les valeurs codées en dur (nom, couleurs, mots, seuils, fonctionnalités) par des **réglages**, dont les défauts sont ceux du Garage. Une instance se configure par `.env` et/ou par un modèle de réglages en base éditable par le gestionnaire, jamais en modifiant le code.

## Ordre des chantiers

1. **Identité et thème** — nom de l'organisation, logo, icône, couleurs, textes de la page d'accueil, nom d'expéditeur des emails, etc., configurables par instance. Défaut = identité du Garage.
2. **Vocabulaire configurable** — les termes métier (séance, coach, membre, carnet, joker, salle…) deviennent des libellés réglables (singulier/pluriel, genre si nécessaire). Défaut = vocabulaire actuel.
3. **Règles métier réglables** — les seuils et comportements aujourd'hui fixes deviennent des paramètres (voir « Règles métier »).
4. **Modules activables** — chaque fonctionnalité optionnelle peut être activée ou désactivée par instance (voir « Modules »).
5. **Livraison Docker** — image et `docker-compose` pour installer une instance chez le client, avec volumes pour la base et les médias, sauvegardes (`scripts/backup_db.sh`, `docs/sauvegardes.md`), mise à jour documentée.
6. **Démo** — instance de démonstration avec données fictives et réinitialisables, pour présenter l'application à des prospects.
7. **Paiement en ligne** — intégration d'un prestataire (ex. Stripe Checkout) une fois le reste stabilisé (voir « Paiement »).

Chaque chantier se livre en étapes courtes et testées ; on ne démarre le suivant que lorsque les tests passent.

## Stack technique

- Langage : **Python**, framework **Django 5.2**, **Bootstrap 5** (via django-crispy-forms)
- Application **responsive**, utilisable sur smartphone
- Dépôt GitHub : `pimpim13/kreno` (remote `origin`)
- Applications Django : `accounts`, `actualites`, `bookings`, `notifications`, `offers`, `payments`, `purchases`, `scheduling` (dans `apps/`), configuration dans `config/`
- Configuration sensible et spécifique à l'instance (clé secrète Django, hosts autorisés, identifiants ntfy.sh, SMTP, coordonnées de paiement) isolée dans un fichier `.env` local non versionné ; la liste des variables attendues est dans `.env.example`
- Documentation d'architecture : `docs/architecture/`

## Règles métier de référence (comportement du Garage = valeurs par défaut)

Les sections suivantes décrivent le comportement actuel, qui sert de **spécification de non-régression**. Les valeurs entre « défaut » sont celles que le chantier 3 rendra réglables.

### Profils utilisateurs

- **Administrateur** (super utilisateur)
- **Gestionnaire** (« Coach gestionnaire » chez le Garage) — a tous les droits de gestion
- **Animateur** (« Coach » chez le Garage) — mêmes droits qu'un Membre, sauf la possibilité de marquer un membre inscrit comme non présent à une séance
- **Membre**

L'animateur d'une séance (champ `coach`) peut être un Gestionnaire ou un Animateur simple. L'Admin n'anime pas de séance et n'apparaît pas dans la liste des animateurs proposés.

### Calendrier et ouverture des inscriptions

- Calendrier hebdomadaire avec navigation avant/arrière, vue journalière, vue par séance ; depuis cette vue le membre s'inscrit ou se désinscrit ; affichage des participants inscrits et de l'animateur
- Nombre maximum de participants fixé par le créateur de la séance ; **modèles de séance type** disponibles
- Les inscriptions n'ouvrent qu'à partir du **mercredi de la semaine précédant** celle de la séance (défaut) ; avant, la séance est visible mais ni inscription ni liste d'attente. Les membres sont notifiés à l'**ouverture des inscriptions**, pas à la création de la séance
- **Annulation** par le gestionnaire/admin : usage recommandé sous **4 participants** (défaut, règle d'usage non vérifiée techniquement) ; inscrits notifiés (push + email), crédit restauré sans impact sur les jokers

### Crédit de séances, offres et achats

- Le catalogue d'**offres** est évolutif : le gestionnaire/admin crée, modifie, supprime depuis `/offres/` (suppression refusée si des achats y sont rattachés ; désactivation recommandée)
- Catalogue du Garage (4 offres de type carnet) : **1 séance** 10 € (sans prolongation de péremption) ; **10 + 1 offerte** 100 € (+3 mois) ; **20 + 3 offertes** 200 € (+6 mois) ; **25 + 5 offertes** 250 € (+6 mois)
- Restent à créer comme offres à part entière : une offre **famille** et des offres **personnalisées** (2 au début)
- Chaque achat (modèle `Achat`, lié à l'offre) **prolonge** la péremption globale du solde de la durée de l'offre, à partir de la péremption existante si future, sinon d'aujourd'hui ; prolongeable manuellement (ex. blessure)
- Sur la fiche membre : enregistrement d'un achat depuis le catalogue (prix modifiable pour une remise), boutons **+1 / −1** pour corrections
- Indicateur de solde (fiche séance et liste des membres) : **vert** solde positif ; **orange** solde nul, ou négatif sous la tolérance ; **rouge** tolérance négative atteinte
- **Tolérance de solde négatif** (défaut **0**) fixée par membre, ou par famille si rattaché

### Familles

Un membre peut appartenir à une **famille** : le crédit est **partagé** (un seul pool) et la tolérance négative est définie au niveau de la famille, identique pour tous ses membres.

### Jokers

Un membre peut recevoir un ou plusieurs jokers du gestionnaire/admin, à sa discrétion.

### Inscription, désinscription, liste d'attente

- Inscription/désinscription horodatées ; le crédit est décompté à l'inscription
- **Désinscription tardive** (échéance définie par le créateur de la séance) : un joker est consommé et le crédit recrédité ; sans joker, la séance reste décomptée
- **Liste d'attente** quand la séance est complète ; en cas de désistement, le premier de la file est inscrit automatiquement **uniquement si la séance a lieu dans plus de 24 h** (défaut) ; il est alerté par push ; une fois promu, il est un inscrit à part entière (règle de désinscription tardive incluse)
- **Permutation** vers une autre séance du jour sans consommer de joker

### Gestion des membres

- Création par le gestionnaire/admin (nom, prénom, email obligatoire, téléphone, tolérance), **sans mot de passe initial** : email avec lien sécurisé de définition du mot de passe
- **Désactivation** réversible (connexion bloquée, historique conservé)
- **Suppression définitive** possible ; avertissement si activité réelle (achats, inscriptions, séances animées), avec bouton « Forcer la suppression » (cascade)
- Un membre ne peut s'inscrire/désinscrire que lui-même ; admin et gestionnaire ont tous les droits

### Notifications

Deux canaux, réglables par chaque utilisateur dans l'onglet « Notifications » :

- **Email** (activable par type) : ouverture des inscriptions, annulation de séance ; autres types à ajouter au fil de l'eau. Mot de passe oublié et définition du mot de passe sont **toujours envoyés**
- **Push ntfy.sh** : canal partagé membres (ouverture, annulation) ; canal **individuel** aléatoire pour chaque animateur/gestionnaire/admin (inscription, désinscription, promotion depuis la liste d'attente, séance complète). Un animateur simple n'est notifié que pour ses séances ; gestionnaire/admin peuvent suivre d'autres animateurs

### Actualités

Bandeau carrousel géré depuis `/actualites/` par le gestionnaire/admin : texte (200 caractères max), dates de début/fin, **3 actualités actives maximum** (défaut), bouton optionnel vers une page de l'app (Calendrier, Offres, Notifications, Solde). Affiché en bas de la page d'accueil (visiteurs, sans croix) et au-dessus du calendrier (connectés, avec croix mémorisée dans le navigateur).

## Règles métier réglables (chantier 3)

À rendre paramétrables par instance, défaut = valeur du Garage : jour et semaine d'ouverture des inscriptions, délai de désinscription tardive (par séance et défaut global), seuil des 24 h pour la promotion automatique, seuil minimum de participants à l'annulation, tolérance négative par défaut, nombre maximum d'actualités actives, durées de validité des offres.

## Modules activables (chantier 4)

Chaque module doit pouvoir être désactivé sans casser le reste (menus, URLs, notifications et tests inclus) ; tous sont **activés par défaut** pour conserver le comportement du Garage. Candidats : jokers, familles, liste d'attente, permutation de séances, actualités, notifications push ntfy, notifications email, offres/carnets, paiement manuel, paiement en ligne (à venir).

## Paiement

- **Étape manuelle (implémentée)** : quand le crédit d'un membre est insuffisant pour réserver (ou rejoindre la liste d'attente), une carte remplace le bouton habituel et l'invite à régler son prochain carnet par **Wero** auprès du gestionnaire qui réceptionne les paiements (nom et téléphone via `.env`, boutons « Copier »). Le gestionnaire crédite ensuite manuellement le compte (+10/+1 sur la fiche membre). Aucune intégration API Wero (indisponible pour les marchands français)
- **À faire (chantier 7)** : paiement en ligne (ex. Stripe Checkout), derrière un module activable, sans remplacer le mode manuel pour les clients qui le préfèrent. Le moyen de paiement manuel et ses coordonnées doivent aussi devenir configurables (chantier 3/4), Wero n'étant qu'un défaut

## Design

- Structure et parcours UX (calendrier hebdomadaire, pastilles de jour, cards) inspirés de **peppy.cool**
- **Thème du Garage (défaut)** de style street-workout/graffiti : noir `#201e1f`, vert accent `#80b048`, fond sombre sur toutes les pages avec texte clair, cartes (contenu, formulaires) sur fond clair à texte sombre, icône = monogramme « G » vert sur fond noir
- Le chantier 1 remplace ces constantes par des réglages de thème (couleurs, logo, icône, nom) pour que chaque client ait sa propre identité sans toucher au code

## Conventions de travail

- Répondre et commenter en **français**, accents corrects
- Lancer la suite de tests avant et après chaque modification : **369 tests verts** = non-régression du Garage
- Pas de valeur « Garage » codée en dur dans de nouveaux développements : passer par un réglage
- Ne commiter que sur demande ; ne jamais pousser vers le remote `garage`
