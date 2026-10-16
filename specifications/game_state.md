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
| Joueurs | Liste ordonnée des joueurs participant à la partie |
| Sac commun | Ensemble des jetons qui n'appartiennent actuellement à aucun joueur |
| Joueur actif | Joueur qui doit agir, ou aucune valeur lorsqu'aucune action n'est attendue |
| Phase | Étape en cours : préparation, choix du destinataire, décision sur le cadeau, résolution, fin de manche ou fin de partie |
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
| Carte secrète | Conditions secrètes attribuées à ce joueur pour la manche |
| Score total | Total des points conservés dans le mode Points et manches |
| Éliminations créditées pendant la manche | Nombre d'éliminations attribuées au joueur selon les règles de score, utilisé notamment pour déterminer s'il atteint le seuil de victoire de manche |
| État d'élimination | Informations nécessaires pour ne pas éliminer deux fois le même joueur pendant une résolution |

L'ordre des joueurs autour de la table doit être conservé même après des éliminations. Il sert à déterminer le prochain joueur actif dans les variantes de succession.

Un joueur éliminé reste présent dans l'état de la partie pour préserver son identité, sa position, son score et l'historique de ses actions. Il ne peut plus commencer d'action normale.

Toutefois, si un joueur est éliminé après avoir retiré un jeton pour proposer un cadeau, cette proposition reste en cours. Le destinataire doit encore décider d'accepter ou de refuser, et le cadeau doit être résolu normalement. L'élimination du donneur ne doit donc pas interrompre automatiquement l'action déjà engagée.

## 5. Représentation des jetons

Chaque jeton doit être représenté comme un élément identifiable par le moteur.

Un jeton doit au minimum avoir :

- Un identifiant interne unique dans la partie.
- Une couleur ou un type défini dans la configuration.

L'identifiant permet au moteur de suivre les déplacements d'un jeton sans en créer accidentellement un deuxième ni en perdre un.

Le programme doit connaître l'emplacement de chaque jeton : sac commun, sac personnel d'un joueur ou jeton temporairement conservé dans la main du donneur pendant une proposition de cadeau.

Un jeton en main pendant une proposition n'est pas encore transféré au destinataire. Il doit rester associé au donneur jusqu'à la résolution de l'acceptation ou du refus.

À tout moment, chaque jeton existant doit avoir un seul emplacement valide.

Le nombre total de jetons doit rester constant pendant une manche, sauf si une règle future prévoit explicitement une création ou une suppression de jetons.

## 6. Représentation des cartes secrètes

Chaque carte secrète doit contenir les informations nécessaires à la vérification des conditions du joueur.

Selon le mode de jeu, elle peut comprendre :

- Une condition de défaite.
- Une condition de victoire.
- Les paramètres nécessaires à l'évaluation de ces conditions.

Les conditions doivent être représentées de façon structurée afin que le moteur puisse les évaluer automatiquement.

Les seuils, couleurs concernées, quantités et autres paramètres des conditions ne doivent pas être dispersés dans le code. Ils doivent pouvoir être définis dans la configuration des cartes.

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

Ces informations ne doivent pas être révélées automatiquement aux joueurs.

### 7.2. Données visibles selon les règles

Les informations affichables comprennent notamment :

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
- Origine du jeton : cadeau accepté, tirage après refus ou tirage nécessaire à un rejeu.
- Étape actuelle de résolution.
- Statut du donneur : en jeu ou éliminé pendant la résolution de l'action.
- État de la proposition : en attente de la décision du destinataire, acceptée ou refusée.
- Joueurs dont les conditions doivent encore être vérifiées.
- Joueurs éliminés par l'action.
- Attribution éventuelle de points.
- Position de départ pour la succession des joueurs actifs.

Ces données temporaires permettent de résoudre correctement les situations où plusieurs éliminations se produisent à la suite d'une même action.

Si le donneur est éliminé après le retrait du jeton mais avant la décision du destinataire, le moteur doit conserver l'action en cours et le jeton proposé en main. Le destinataire doit pouvoir accepter ou refuser selon les règles normales. L'action ne se termine qu'après la résolution du cadeau, des conditions applicables, des éventuelles éliminations et des règles de succession.

Le moteur doit terminer la résolution de l'action avant de passer à une nouvelle action normale.

## 9. Suivi des éliminations

Le programme doit distinguer :

- Le fait qu'un joueur soit éliminé de la partie.
- Le nombre d'éliminations créditées au joueur pendant la manche, lorsque ce compteur est utilisé pour déterminer le vainqueur de la manche.
- Le joueur responsable d'une élimination, lorsque cette information intervient dans l'attribution des points ou la succession.
- L'ensemble des éliminations issues d'une même résolution.

Une même condition de défaite ou plusieurs conditions satisfaites simultanément ne peuvent provoquer plusieurs éliminations du même joueur au cours d'une seule résolution.

Le moteur doit conserver l'information permettant de savoir si un joueur a déjà été éliminé pendant cette résolution.

Après une élimination, le joueur ne participe plus aux actions normales. Sa carte secrète complète doit être révélée conformément aux règles.

Les détails de succession sont définis dans `game_flow.md` et devront être traduits en règles exécutables dans le moteur.

## 10. Scores et manches

En mode Points et manches, l'état doit notamment conserver :

- Le score total de chaque joueur.
- Le nombre d'éliminations créditées au joueur pendant la manche, distinct du score total.
- Le joueur responsable de chaque élimination, lorsqu'il peut être déterminé.
- Les points déjà attribués pendant la manche.
- Le joueur ayant remporté la manche, le cas échéant.
- Le bonus de manche déjà attribué ou restant à déterminer.
- Le format de partie sélectionné : C1 ou C2.
- Le seuil de points choisi en C2, le cas échéant.
- Le nombre de manches déjà jouées.

Les compteurs d'éliminations sont réinitialisés au début de chaque nouvelle manche.

Les scores totaux sont conservés entre les manches.

La vérification du seuil de points en C2 ne doit pas arrêter une manche en cours. Le classement final est calculé à la fin de cette manche, conformément aux règles du jeu.

Une égalité terminale sans vainqueur doit être distinguée d'une égalité de scores à la fin d'une partie C1.

Le compteur d'éliminations créditées sert à vérifier le seuil de victoire de manche. Il ne doit pas être confondu avec le nombre d'éliminations subies par le joueur ni être déduit automatiquement de son score total. Les règles d'attribution doivent déterminer explicitement quand ce compteur augmente.

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

## 13. Invariants à respecter

Les invariants sont des propriétés qui doivent rester vraies tout au long de la partie.

1. Chaque jeton existant possède un seul emplacement valide.
2. Aucun jeton n'est dupliqué ni perdu lors d'un transfert.
3. Le nombre total de jetons reste constant pendant la manche, sauf règle explicite contraire.
4. Un joueur éliminé ne peut plus réaliser d'action normale.
5. Un joueur ne peut pas être éliminé plusieurs fois pendant la même résolution.
6. Un joueur ne peut pas être simultanément en jeu et déclaré éliminé.
7. Une condition de victoire secrète ne peut être déclenchée que par les événements autorisés pour le mode Objectif secret.
8. La préparation initiale ne peut déclencher ni victoire ni élimination.
9. Les scores totaux sont conservés lors du passage d'une manche à la suivante.
10. Les compteurs d'élimination propres à la manche sont réinitialisés à chaque nouvelle manche.
11. Une partie terminée ne peut pas accepter de nouvelles actions normales.
12. Une égalité terminale sans vainqueur est un résultat explicite et ne doit pas être assimilée à une victoire ordinaire.

Ces invariants devront être vérifiés par des tests automatisés.

## 14. Paramètres à garder configurables

Les éléments suivants ne doivent pas être codés en dur dans la structure de l'état :

- Le nombre de joueurs.
- Le nombre de couleurs et la composition du sac commun.
- Les seuils des conditions de défaite et de victoire.
- Le mode de jeu et ses variantes.
- Les règles de visibilité des jetons.
- La variante de succession.
- Les paramètres de score et le seuil de victoire en points.
- Le nombre de manches prévues.
- Les paramètres nécessaires aux agents de simulation.

Les valeurs expérimentales, notamment la quantité totale de jetons et les seuils des conditions, doivent pouvoir évoluer sans imposer une refonte de la structure fondamentale de l'état.
