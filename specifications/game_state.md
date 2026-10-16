# État du jeu — C'est cadeau !

## 1. Objectif du document

Ce document définit les données que le programme doit mémoriser pour représenter une partie de C'est cadeau !.

Il sert de référence pour le développement du moteur de jeu, la simulation de parties et les tests automatisés.

Il décrit les informations nécessaires, et non leur implémentation en Python. Les noms de variables pourront être adaptés pendant le développement, à condition de conserver les comportements définis ici.

## 2. Principes généraux

L'état du jeu doit permettre de connaître à tout moment :

- Les joueurs participant à la partie et ceux qui ont été éliminés.
- Les jetons présents dans le sac commun et dans chaque sac personnel.
- Les cartes secrètes attribuées aux joueurs.
- Le mode de jeu et les variantes actives.
- Le joueur actif et l'étape précise du tour.
- Les scores et les compteurs d'élimination.
- L'historique nécessaire à la résolution des actions et à l'analyse des simulations.
- La situation de fin de manche ou de partie.

L'état doit être suffisamment complet pour qu'une partie puisse être poursuivie sans avoir à reconstituer des informations manquantes à partir des messages précédemment affichés.

Le programme ne doit pas utiliser les informations affichées aux joueurs comme seule source de vérité : les données internes du moteur font autorité.

## 3. État général de la partie

L'état général doit contenir les éléments suivants.

| Information | Description |
|---|---|
| Identifiant de partie | Identifiant interne facultatif permettant de distinguer les parties simulées |
| Mode de jeu | Dernier survivant, Objectif secret ou Points et manches |
| Configuration | Paramètres de la partie et variantes activées |
| Validation de configuration | État de validation et éventuels motifs d'invalidité, notamment nombre de jetons, structure des cartes et possibilité d'une mise en place complète |
| Joueurs | Liste ordonnée des joueurs participant à la partie |
| Sac commun | Ensemble des jetons qui n'appartiennent actuellement à aucun joueur |
| Paquet ou réserve de cartes, si géré par le moteur | Cartes secrètes disponibles, déjà distribuées et restantes ; composition et disponibilité permettant de vérifier que le nombre de cartes suffit aux participants |
| Joueur actif | Joueur qui doit agir, ou aucune valeur lorsqu'aucune action n'est attendue |
| Phase | Étape précise : choix du mode et des variantes, préparation, choix du destinataire, retrait du jeton, contrôle éventuel du donneur après retrait et avant décision, présentation, décision, acceptation/refus, contrôle du destinataire, éliminations, succession, fin de manche ou fin de partie |
| Type de résolution | Action initiale, rejeu distinct en variante A, chaîne d'éliminations forcées en variante B, préparation ou transition entre manches |
| Manche actuelle | Numéro de la manche en cours, si le mode utilise des manches |
| Résultat | État de fin éventuel : victoire, égalité sans vainqueur ou partie en cours |
| Historique | Liste ordonnée des événements importants de la partie |
| Générateur aléatoire | État permettant de reproduire une simulation, lorsque cette fonctionnalité est activée |

Une partie en cours ne doit jamais avoir plusieurs joueurs actifs simultanément.

Le joueur actif peut être temporairement absent pendant la résolution d'une action, une élimination en chaîne ou une transition entre deux manches.

## 4. État de chaque joueur

Chaque joueur doit posséder les informations suivantes.

| Information | Description |
|---|---|
| Identifiant | Identifiant interne unique pendant la partie |
| Position | Place du joueur autour de la table, utilisée notamment pour la succession horaire |
| Nom ou libellé | Nom facultatif pour l'affichage |
| En jeu | Indique si le joueur peut encore participer aux actions normales |
| Sac personnel | Liste des jetons actuellement détenus par le joueur |
| Carte secrète | Conditions secrètes attribuées à ce joueur pour la manche ; les conditions sont évaluables en interne sans être révélées pendant la mise en place |
| État de révélation de la carte | Carte cachée ou révélée, avec le motif de révélation ; un tirage initial invalide ne révèle jamais la carte |
| Score total | Total des points conservés dans le mode Points et manches |
| Éliminations créditées pendant la manche | Nombre d'éliminations attribuées au joueur selon les règles de score, utilisé notamment pour déterminer s'il atteint le seuil de victoire de manche |
| État d'élimination | Informations nécessaires pour ne pas éliminer deux fois le même joueur pendant une résolution |

L'ordre des joueurs autour de la table doit être conservé même après des éliminations. Il sert à déterminer le prochain joueur actif dans les variantes de succession.

Un joueur éliminé reste présent dans l'état de la partie pour préserver son identité, sa position, son score et l'historique de ses actions. Il ne peut plus commencer d'action normale.

Toutefois, si le donneur est éliminé après avoir retiré un jeton pour proposer un cadeau, cette proposition reste en cours. Le destinataire doit encore décider d'accepter ou de refuser, et la résolution engagée doit se poursuivre. Les autres jetons encore présents dans le sac personnel du donneur éliminé retournent immédiatement au sac commun ; le jeton proposé reste temporairement associé à la proposition. Si le destinataire refuse alors que le sac commun contient au moins un jeton, le jeton proposé est ajouté au sac commun sans être révélé, puis le destinataire tire au hasard un jeton dans le sac commun ainsi augmenté. Le jeton proposé peut donc être celui qui est tiré. Le résultat du tirage rejoint le sac personnel du destinataire et suit la règle de visibilité activée.

## 5. Représentation des jetons

Chaque jeton doit être représenté comme un élément identifiable par le moteur.

Un jeton doit au minimum avoir :

- Un identifiant interne unique dans la partie.
- Une couleur ou un type défini dans la configuration.

L'identifiant permet au moteur de suivre les déplacements d'un jeton sans en créer accidentellement un deuxième ni en perdre un.

Le programme doit connaître l'emplacement de chaque jeton : sac commun, sac personnel d'un joueur ou emplacement temporaire de la proposition (jeton conservé dans la main fermée du donneur).

Un jeton en main pendant une proposition n'est pas encore transféré au destinataire et ne compte plus dans le sac personnel du donneur. Il reste associé à l'action en cours jusqu'à la résolution de l'acceptation ou du refus. Si le donneur est éliminé, cette conservation temporaire perdure même si ses autres jetons personnels rejoignent le sac commun.

À tout moment, chaque jeton existant doit avoir un seul emplacement valide. Le jeton temporaire ne doit jamais être compté en même temps dans un sac personnel ou dans le sac commun. Si le destinataire refuse après l'élimination du donneur, déplacer d'abord le jeton temporaire vers le sac commun sans révélation, puis effectuer le tirage aléatoire dans le sac ainsi augmenté. Le jeton tiré quitte le sac commun et rejoint le sac personnel du destinataire ; il peut s'agir du jeton proposé.

Le nombre total de jetons doit rester constant pendant une manche, sauf si une règle future prévoit explicitement une création ou une suppression de jetons.

## 6. Représentation des cartes secrètes

Chaque carte secrète doit contenir les informations nécessaires à la vérification des conditions du joueur.

Le contenu de la carte doit respecter le mode sélectionné :

- Mode A — Dernier survivant : une condition de défaite, sans condition individuelle de victoire.
- Mode B — Objectif secret : une condition de défaite et une condition de victoire compatibles entre elles.
- Mode C — Points et manches : une condition de défaite, sans condition individuelle de victoire.

La carte contient également les paramètres nécessaires à l'évaluation de sa condition ou de ses conditions. Les objectifs spéciaux d'élimination précoce ne doivent pas être distribués comme règles actives avant que leur fonctionnement soit entièrement défini.

Les conditions doivent être représentées de façon structurée afin que le moteur puisse les évaluer automatiquement.

Si le moteur distribue lui-même les cartes, il doit suivre le paquet ou la réserve, vérifier sa capacité par rapport au nombre de joueurs et empêcher une distribution impossible. Si les cartes sont fournies explicitement par un scénario de test externe, la gestion physique du paquet peut être hors périmètre, mais la validité et la compatibilité des cartes fournies restent à contrôler.

Les seuils, couleurs concernées, quantités et autres paramètres des conditions ne doivent pas être dispersés dans le code. Ils doivent pouvoir être définis dans la configuration des cartes. La validation doit aussi refuser une carte dont le contenu ne correspond pas au mode sélectionné, une carte contradictoire, ou une carte faisant référence à un type ou paramètre inconnu.

Le programme doit pouvoir vérifier les conditions d'une carte à partir de la collection actuelle du joueur et du contexte de l'action.

Lorsqu'une carte doit être révélée après une élimination ou une victoire secrète, le moteur doit conserver toutes ses informations afin de pouvoir l'afficher intégralement.

## 7. Informations secrètes et informations publiques

Le moteur doit distinguer les données internes de la partie des informations accessibles aux joueurs.

### 7.1. Données internes

Le moteur peut accéder à toutes les informations nécessaires au fonctionnement du jeu, notamment :

- La composition exacte du sac commun.
- Le contenu exact de chaque sac personnel.
- La carte secrète de chaque joueur.
- La véritable identité d'un jeton proposé comme cadeau.
- Les informations nécessaires à la reproductibilité des tirages aléatoires.

Ces informations ne doivent pas être révélées automatiquement aux joueurs. Pendant la mise en place, le moteur peut évaluer en privé les conditions de chaque carte, mais ne révèle aucune carte parce qu'une collection initiale est invalide. Une carte n'est révélée qu'en cours de jeu lorsqu'une condition produit effectivement l'élimination du joueur ou qu'un objectif secret produit une victoire conformément aux règles.

### 7.2. Données visibles selon les règles

Les informations affichables comprennent notamment :

- Le destinataire connaît les couleurs ou types susceptibles de se trouver dans le sac commun, mais pas sa composition exacte restante. Cette connaissance ne doit pas être exposée aux autres joueurs sans règle explicite.
- Les annonces prononcées par les joueurs.
- L'identité du donneur et du destinataire d'un cadeau.
- La couleur du jeton lorsqu'il est révélé.
- Les éliminations annoncées publiquement.
- Les cartes secrètes révélées à la suite d'une élimination ou d'une victoire.
- Les scores affichés en mode Points et manches.
- Les jetons tirés lorsque la variante activée prévoit leur révélation.

Les informations visibles dépendent de la phase de jeu et des variantes sélectionnées.

L'interface utilisateur et les agents simulés ne doivent pas pouvoir consulter les informations secrètes uniquement accessibles au moteur.

## 8. État temporaire d'une action

Pendant la résolution d'un cadeau ou d'un tirage, le moteur doit pouvoir mémoriser les informations temporaires suivantes :

- Identité du donneur, s'il y en a un.
- Identité du destinataire concerné.
- Jeton actuellement proposé ou tiré.
- Décision du destinataire : accepter ou refuser, lorsqu'elle s'applique.
- Origine du jeton : cadeau accepté, proposition refusée, tirage après refus, tirage nécessaire au rejeu du responsable en variante A, tirage requis pour activer un successeur sans jeton en variante A, ou jeton en attente de résolution.
- Type de résolution : action initiale, rejeu distinct en variante A ou chaîne d'éliminations forcées en variante B.
- Étape actuelle de résolution.
- Statut du donneur : en jeu ou éliminé pendant la résolution de l'action.
- État de la proposition : en attente de la décision du destinataire, acceptée ou refusée.
- Emplacement courant exact du jeton proposé, y compris l'emplacement temporaire de la main du donneur.
- Joueurs dont les conditions doivent encore être vérifiées.
- Joueurs éliminés par l'action ou la chaîne en cours.
- Joueur responsable de l'action initiale, conservé jusqu'à la fin de toute chaîne B dont les éliminations forcées lui sont attribuées.
- Points et incréments du compteur de manche en attente de validation.
- Position de départ pour la succession des joueurs actifs.
- Sous-étape de refus après élimination du donneur : jeton proposé ajouté au sac commun sans révélation, puis pioche aléatoire dans le sac ainsi augmenté ; le jeton pioché peut être le jeton proposé.

Ces données temporaires permettent de résoudre correctement les situations où plusieurs éliminations se produisent à la suite d'une même action.

Si le donneur est éliminé après le retrait du jeton mais avant la décision du destinataire, le moteur doit conserver l'action en cours et le jeton proposé dans son emplacement temporaire. Le destinataire doit pouvoir accepter ou refuser. En cas d'acceptation, le jeton est transféré au destinataire ; en cas de refus autorisé, le jeton proposé rejoint d'abord le sac commun sans révélation, puis un jeton est tiré au hasard du sac ainsi augmenté et rejoint le sac personnel du destinataire. L'action ne se termine qu'après la résolution du cadeau, des conditions applicables, des éventuelles éliminations et des règles de succession.

Le moteur doit terminer la résolution de l'action avant de passer à une nouvelle action normale. Lorsqu'une condition de victoire secrète est déclenchée après un cadeau accepté ou une pioche autorisée, la carte complète est révélée et la partie s'arrête immédiatement, sans vérification ni attribution ultérieure liée à cette action. Pour un tirage de rejeu en variante A, les conditions de victoire applicables sont contrôlées avant la condition de défaite ; si le joueur survit sans gagner, il joue immédiatement son tour.

Une égalité terminale obtenue lors d'une résolution distincte de rejeu en variante A ne doit pas annuler les points déjà validés lors de l'action initiale précédente. En variante B, l'identité du responsable initial doit être conservée jusqu'à la fin de la chaîne afin d'appliquer les points et le compteur de manche selon l'ordre de priorité établi.

## 9. Suivi des éliminations

Le programme doit distinguer :

- Le fait qu'un joueur soit éliminé de la partie.
- Le nombre d'éliminations créditées au joueur pendant la manche, lorsque ce compteur est utilisé pour déterminer le vainqueur de la manche.
- Le joueur responsable d'une élimination, lorsque cette information intervient dans l'attribution des points ou la succession.
- L'ensemble des éliminations issues d'une même résolution.

Une même condition de défaite ou plusieurs conditions satisfaites simultanément ne peuvent provoquer plusieurs éliminations du même joueur au cours d'une seule résolution.

Le moteur doit conserver l'information permettant de savoir si un joueur a déjà été éliminé pendant cette résolution.

Après une élimination, le joueur ne participe plus aux actions normales pendant la manche ou la partie en cours selon le mode. Sa carte secrète complète est révélée conformément aux règles et tous les jetons encore présents dans son sac personnel sont remis au sac commun. En modes Dernier survivant et Objectif secret, l'élimination est définitive pour la partie. En mode Points et manches, le joueur reste éliminé jusqu'à la nouvelle mise en place de la manche suivante, où il revient en jeu avec une nouvelle carte et une nouvelle collection.

Les détails de succession sont définis dans `game_flow.md` et devront être traduits en règles exécutables dans le moteur.

## 10. Scores et manches

En mode Points et manches, l'état doit notamment conserver :

- Le score total de chaque joueur.
- Le nombre d'éliminations d'adversaires créditées au joueur pendant la manche, distinct du score total et du nombre de fois où le joueur est lui-même éliminé.
- Le joueur responsable de chaque élimination, lorsqu'il peut être déterminé, et l'identité du joueur dont l'action initiale a déclenché une chaîne B.
- Les points déjà validés et les attributions en attente de résolution terminale.
- Le joueur ayant remporté la manche, le cas échéant.
- Le bonus de manche déjà attribué ou restant à déterminer.
- Le format de partie sélectionné : C1 ou C2.
- Le seuil de points choisi en C2, le cas échéant.
- Le nombre de manches déjà jouées.

Les compteurs d'éliminations sont réinitialisés au début de chaque nouvelle manche.

Les scores totaux sont conservés entre les manches.

La vérification du seuil de points en C2 ne doit pas arrêter une manche en cours. Le classement final est calculé à la fin de cette manche, conformément aux règles du jeu.

Une égalité terminale sans vainqueur doit être distinguée d'une égalité de scores à la fin d'une partie C1.

Le compteur d'éliminations créditées sert à vérifier le seuil de victoire de manche. Il augmente lorsqu'une élimination d'adversaire est attribuée au joueur et rapporte un point ; il n'augmente pas pour l'auto-élimination, pour une élimination causée par la propre pioche de rejeu du joueur, ni pour l'élimination terminale qui met fin à la partie sans vainqueur. Il ne doit pas être confondu avec le nombre d'éliminations subies ni être déduit du score total. Une attribution d'élimination d'adversaire reste créditée même si le responsable est également éliminé lors de la même action, sauf lorsque l'action initiale élimine directement tous les joueurs encore en jeu. Pour une chaîne B, chaque élimination forcée non terminale attribuable progresse le compteur ; la dernière élimination terminale ne le fait pas.

## 11. Fin de manche et nouvelle manche

À la fin d'une manche, l'état doit permettre de déterminer :

- Si la partie complète est terminée.
- Si une nouvelle manche doit commencer.
- Si une manche supplémentaire est nécessaire en C1.
- Si les scores doivent être conservés.
- Quels compteurs doivent être réinitialisés.

Lorsqu'une nouvelle manche commence :

1. Tous les jetons sont remis dans le sac commun.
2. Les cartes secrètes sont redistribuées.
3. Chaque joueur encore prévu dans la partie reçoit une nouvelle collection initiale de trois jetons, selon les règles de préparation.
4. Les conditions initiales sont vérifiées conformément aux règles.
5. Les compteurs propres à la manche sont réinitialisés.
6. Les scores cumulés sont conservés.
7. Un nouveau premier joueur est déterminé selon la méthode retenue pour cette manche.

Le traitement des manches ne doit pas effacer l'historique des manches précédentes.

## 12. Historique des événements

Le moteur doit pouvoir enregistrer les événements importants dans leur ordre chronologique.

Exemples d'événements :

- Début de partie ou de manche.
- Tirage d'un jeton pendant la préparation.
- Début d'un tour.
- Choix d'un destinataire.
- Proposition d'un cadeau.
- Acceptation ou refus.
- Révélation et transfert d'un jeton.
- Tirage dans le sac commun.
- Vérification d'une condition.
- Élimination d'un joueur.
- Révélation d'une carte secrète.
- Attribution de points.
- Fin de manche.
- Victoire ou égalité terminale.

Chaque événement doit contenir les informations utiles à son interprétation : type d'événement, joueur ou joueurs concernés, manche, ordre chronologique et données spécifiques à l'événement.

L'historique ne doit pas révéler publiquement des informations encore secrètes. Il s'agit d'abord d'un outil interne pour le moteur, les tests et les simulations. L'affichage public doit respecter les règles de visibilité.

## 13. Validation de la configuration et de la préparation

Avant de distribuer les jetons, le moteur doit vérifier que le nombre de jetons disponibles est au moins égal à trois fois le nombre de joueurs, que les quantités/types/couleurs et les paramètres sont valides, que les cartes sont compatibles avec le mode, et qu'une attribution complète d'une collection initiale valide de trois jetons à chaque joueur est possible avec le stock configuré. Une collection initiale valide ne satisfait aucune condition de défaite ni, en mode Objectif secret, aucune condition de victoire.

Si aucune attribution complète n'est possible, la configuration est rejetée avant le début de la partie avec une erreur explicite. Si une tentative de mise en place devient impossible à cause des collections déjà retenues et qu'aucun tirage valide ne reste possible pour un joueur, le moteur arrête cette tentative et signale un échec de préparation au lieu de boucler indéfiniment. Cet échec ne révèle aucune carte et ne déclare aucune victoire ou élimination. Il ne doit pas être présenté comme un événement de jeu.

## 14. Invariants à respecter

Les invariants sont des propriétés qui doivent rester vraies tout au long de la partie.

1. Chaque jeton existant possède un seul emplacement valide.
2. Aucun jeton n'est dupliqué ni perdu lors d'un transfert.
3. Le nombre total de jetons reste constant pendant la manche, sauf règle explicite contraire.
4. À l'élimination, les jetons restant dans le sac personnel rejoignent le sac commun ; un jeton temporairement tenu pour une proposition en cours reste temporaire jusqu'à résolution. Si le destinataire refuse après l'élimination du donneur, le jeton proposé rejoint le sac commun avant la pioche aléatoire du destinataire.
5. Un joueur éliminé ne peut plus réaliser d'action normale, sauf que la proposition de cadeau déjà engagée doit être résolue si le donneur est éliminé après retrait.
6. Un joueur éliminé en mode Points et manches revient uniquement lors de la nouvelle mise en place de la manche suivante.
7. Un joueur ne peut pas être éliminé plusieurs fois pendant la même résolution.
8. Un joueur ne peut pas être simultanément en jeu et déclaré éliminé.
9. Une condition de victoire secrète ne peut être déclenchée que par les événements autorisés pour le mode Objectif secret.
10. La préparation initiale ne peut déclencher ni victoire ni élimination et ne révèle aucune carte secrète ; une collection initiale qui satisfait une condition est simplement rejetée et remplacée par un nouveau tirage de trois jetons.
11. Les scores totaux sont conservés lors du passage d'une manche à la suivante.
12. Les compteurs d'élimination propres à la manche sont réinitialisés à chaque nouvelle manche.
13. Une partie terminée ne peut pas accepter de nouvelles actions normales.
14. Une égalité terminale sans vainqueur est un résultat explicite et ne doit pas être assimilée à une victoire ordinaire.

Ces invariants devront être vérifiés par des tests automatisés.

## 15. Paramètres à garder configurables

Les éléments suivants ne doivent pas être codés en dur dans la structure de l'état :

- Le nombre de joueurs.
- Le nombre de couleurs et la composition du sac commun.
- La composition et la capacité du paquet de cartes, lorsque sa distribution est gérée par le moteur.
- Les seuils des conditions de défaite et de victoire.
- Le mode de jeu et ses variantes.
- Les règles de visibilité des jetons.
- La variante de succession.
- Les paramètres de score et le seuil de victoire en points.
- Le nombre de manches prévues.
- Les paramètres nécessaires aux agents de simulation.

Les valeurs expérimentales, notamment la quantité totale de jetons et les seuils des conditions, doivent pouvoir évoluer sans imposer une refonte de la structure fondamentale de l'état.
