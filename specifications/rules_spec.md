# Spécification des règles — C'est cadeau !

## 1. Objectif

Ce document définit les règles que le programme doit pouvoir vérifier et appliquer automatiquement.

Il complète :
- `game_flow.md`, qui décrit le déroulement de la partie ;
- `game_state.md`, qui définit les données à mémoriser.

Les règles établies doivent être appliquées sans interprétation personnelle du programme. Les paramètres expérimentaux restent configurables. Une valeur non encore définie ne doit pas être inventée par le moteur.

## 2. Principes de vérification

### 2.1. Conditions de défaite

Une condition de défaite est une règle associée à la carte secrète d'un joueur. Elle indique à partir de quelle collection de jetons le joueur est éliminé.

Le moteur doit pouvoir :
1. Connaître la collection actuelle du joueur.
2. Évaluer chaque condition de défaite applicable à sa carte.
3. Déterminer si une ou plusieurs conditions sont satisfaites.
4. Résoudre une seule élimination pour ce joueur pendant la résolution concernée.

Si plusieurs conditions de défaite sont satisfaites simultanément, elles ne doivent pas éliminer plusieurs fois le même joueur.

### 2.2. Conditions de victoire

Une condition de victoire est un objectif personnel associé à la carte secrète d'un joueur en mode Objectif secret.

Le moteur doit pouvoir évaluer ces objectifs à partir de la collection actuelle et du contexte de l'action.

Une condition de victoire ne peut être vérifiée que lorsqu'un événement autorisé la déclenche. Le simple retrait d'un jeton par le donneur ne peut jamais déclencher sa victoire personnelle.

### 2.3. Compatibilité entre victoire et défaite

La conception du jeu doit empêcher qu'une même collection de jetons satisfasse simultanément la condition de victoire et la condition de défaite d'une même carte secrète.

Les cartes générées ou configurées doivent être contrôlables à cet égard. Si une combinaison de paramètres rend une carte contradictoire, elle doit être signalée comme invalide avant son utilisation.

## 3. Conditions de défaite prévues

Les familles de conditions suivantes sont prévues. Leurs seuils et certaines interprétations restent des paramètres de test.

### 3.1. Accumulation d'une couleur dangereuse

Le joueur est éliminé lorsqu'il possède un nombre déterminé de jetons d'une couleur précise, indiquée par sa carte secrète.

Paramètres :
- Couleur dangereuse.
- Nombre de jetons requis.
- Éventuelle règle d'exactitude du seuil, si elle est retenue.

Le seuil de trois jetons d'une même couleur est une hypothèse de départ, pas une valeur définitivement validée.

Le programme doit compter les jetons de la couleur concernée dans le sac personnel du joueur et comparer le résultat au paramètre défini.

### 3.2. Deux paires de couleurs

Le joueur est éliminé lorsqu'il possède deux jetons d'une couleur et deux jetons d'une autre couleur.

Cette condition possède deux dimensions configurables :

**Couleurs concernées**
- Toute combinaison de deux couleurs peut être autorisée.
- Ou la carte peut imposer les deux couleurs à rechercher.

**Quantités exigées**
- Exactement deux jetons de chacune des deux couleurs.
- Ou au moins deux jetons de chacune des deux couleurs.

Le moteur doit appliquer la variante sélectionnée, sans mélanger les différentes interprétations.

### 3.3. Accumulation du nombre total de jetons

Le joueur est éliminé lorsqu'il atteint le seuil total de jetons défini sur sa carte ou dans la configuration.

Le moteur compte tous les jetons présents dans son sac personnel, quelle que soit leur couleur.

Le seuil de six jetons est une hypothèse de départ pour les tests avec quatre couleurs. Il ne doit pas être considéré comme définitif.

### 3.4. Ajout de nouvelles conditions

L'architecture doit permettre d'ajouter d'autres familles de conditions sans réécrire le moteur de résolution des tours.

Une condition doit pouvoir être représentée sous une forme structurée contenant son type, ses paramètres et sa règle d'évaluation.

Les conditions ne doivent pas être implémentées uniquement sous forme de textes difficiles à interpréter automatiquement.

## 4. Moments auxquels les conditions de défaite sont vérifiées

Les conditions de défaite ne sont pas vérifiées à chaque modification interne de l'état. Elles le sont aux moments prévus par les règles.

### 4.1. Après réception d'un cadeau accepté

Après révélation et transfert du jeton, le destinataire vérifie sa condition de défaite à partir de sa nouvelle collection.

### 4.2. Après un tirage consécutif à un refus

Lorsque le sac commun contient encore des jetons, le destinataire tire un jeton après le refus et vérifie sa condition de défaite à partir de sa nouvelle collection.

### 4.3. Après le retrait d'un jeton par le donneur

Une variante de test détermine si la condition de défaite du donneur est vérifiée immédiatement après le retrait du jeton de son sac, avant la décision du destinataire.

Si cette option est activée :
1. Le donneur retire le jeton et le place dans sa main.
2. Sa condition de défaite est vérifiée à partir de sa collection après retrait.
3. S'il est éliminé, il révèle sa carte secrète complète.
4. La proposition de cadeau reste en cours.
5. Le destinataire décide ensuite d'accepter ou de refuser.
6. Le cadeau est résolu normalement, puis les conséquences restantes et la succession sont déterminées.

Si cette option est désactivée, la condition de défaite du donneur n'est pas vérifiée à ce moment-là.

Un refus ultérieur ne peut jamais annuler rétroactivement une élimination déjà prononcée. Le retrait du jeton ne déclenche jamais la condition de victoire personnelle du donneur.

### 4.4. Après un tirage nécessaire à un rejeu en variante A

Lorsqu'un joueur doit rejouer mais ne possède aucun jeton dans son sac personnel, il tire un jeton du sac commun si celui-ci n'est pas vide.

Il vérifie ensuite sa condition de défaite à partir de sa nouvelle collection.

Si le sac commun est vide, aucun jeton n'est tiré : le joueur est éliminé selon les règles de succession de la variante A.

### 4.5. Pendant la préparation

La collection initiale de trois jetons est vérifiée afin d'écarter une collection qui satisfait une condition de défaite ou, en mode Objectif secret, une condition de victoire.

Cette vérification ne provoque jamais une élimination ou une victoire. Si la collection n'est pas valide, les trois jetons sont remis dans le sac commun et une nouvelle collection de trois jetons est tirée.

## 5. Conditions de victoire du mode Objectif secret

Chaque carte du mode Objectif secret doit comporter une condition de défaite et une condition de victoire compatibles entre elles.

Les familles suivantes sont des propositions à tester et non un catalogue définitif de cartes.

### 5.1. Majorité d'une couleur

Objectif possible : posséder davantage de jetons d'une couleur que de chacune des autres couleurs, sans atteindre un seuil maximal de concentration.

Le sens exact de « majorité », le minimum de jetons requis et le seuil maximal restent à définir par configuration avant utilisation.

### 5.2. Composition précise de trois couleurs

Objectif possible : atteindre une composition donnée, par exemple :
- deux jetons bleus ;
- deux jetons jaunes ;
- un jeton vert.

Les quantités et les couleurs sont des paramètres. Il reste à décider, pour chaque carte, si les quantités doivent être exactes ou simplement atteintes.

### 5.3. Quantités égales de deux couleurs

Objectif possible : posséder une quantité identique de deux couleurs, avec un minimum requis.

Le minimum et la règle de comptage doivent être définis dans la configuration de l'objectif.

### 5.4. Diversification des couleurs

Objectif possible : posséder au moins un jeton de chacune des quatre couleurs, éventuellement avec une limite sur le nombre de jetons d'une seule couleur.

Le nombre de couleurs requis et une éventuelle limite de concentration doivent être configurables.

### 5.5. Accumulation de jetons d'une même couleur

Objectif possible : posséder quatre jetons d'une même couleur.

Deux interprétations doivent pouvoir être testées :
- exactement quatre jetons ;
- au moins quatre jetons.

Cette condition ne doit pas être confondue avec une condition de défaite, et la conception de la carte doit empêcher leur déclenchement simultané sur une même collection.

### 5.6. Objectifs spéciaux d'élimination précoce

Un objectif spécial pourrait récompenser un joueur éliminé parmi les premiers de la partie, selon le nombre de participants.

Cette idée n'est pas suffisamment définie pour être considérée comme une règle implémentable. Son déclencheur, la manière dont elle interagit avec l'élimination et ses conséquences sur la victoire restent à concevoir.

Elle ne doit pas être activée dans le moteur tant que ses règles n'ont pas été spécifiées.

## 6. Déclenchement des victoires secrètes

En mode Objectif secret, la condition de victoire est vérifiée uniquement :
- après la réception d'un cadeau accepté ;
- après un tirage du sac commun consécutif à un refus ;
- après un tirage du sac commun effectué pour permettre un rejeu en variante A.

Le troisième déclencheur permet de vérifier les conditions après le tirage effectué pour le rejeu, conformément à la règle de la variante A.

La condition de victoire n'est jamais déclenchée par le seul retrait d'un jeton du sac personnel du donneur.

Lorsqu'un objectif est satisfait :
1. La carte secrète complète du joueur est révélée.
2. La victoire du joueur est déclarée.
3. La partie s'arrête immédiatement.
4. Aucune nouvelle action normale n'est autorisée.

Si une même résolution comporte plusieurs événements, le moteur doit appliquer les priorités de résolution définies dans `game_flow.md`. Il ne doit pas commencer un nouveau tour avant d'avoir terminé cette résolution.

## 7. Refus d'un cadeau et sac commun vide

Un joueur ne peut refuser un cadeau que si le sac commun contient au moins un jeton au moment où le refus doit être résolu.

Si le sac commun est vide :
- le refus est impossible ;
- le donneur révèle le jeton qu'il tient ;
- il transfère ce jeton au destinataire ;
- aucun tirage de remplacement n'a lieu.

Cette règle doit être appliquée même si le destinataire aurait préféré refuser le cadeau.

Le jeton proposé reste placé dans l'état temporaire de l'action jusqu'à sa résolution. Il ne doit pas être simultanément présent dans le sac du donneur et dans celui du destinataire.

## 8. Règles communes aux éliminations

### 8.1. Une seule élimination par joueur et par résolution

Un joueur dont la condition de défaite est satisfaite est éliminé au plus une fois pendant la résolution concernée.

Le moteur doit enregistrer les joueurs déjà éliminés par cette résolution pour empêcher les doublons.

### 8.2. Révélation des cartes secrètes

Après toute élimination, le joueur éliminé révèle sa carte secrète complète.

Si plusieurs joueurs sont éliminés par la même résolution, chaque carte concernée doit être révélée.

Une victoire secrète provoque également la révélation complète de la carte du vainqueur.

### 8.3. Égalité terminale

Si tous les joueurs encore en jeu sont éliminés par la même résolution, la partie se termine sur une égalité sans vainqueur.

Il faut distinguer deux situations en mode Points et manches.

**Situation 1 — L'action initiale élimine directement tous les joueurs encore en jeu.**

Aucun point ni bonus de manche n'est attribué au titre de cette action.

**Situation 2 — L'action initiale déclenche une chaîne d'éliminations qui aboutit ensuite à une égalité terminale.**

Les points valablement acquis avant la dernière élimination restent conservés. La dernière élimination, celle qui élimine tous les joueurs encore en jeu, ne rapporte aucun point. Aucun bonus de manche n'est attribué pour cette résolution terminale.

Les points déjà attribués ne doivent pas être annulés rétroactivement simplement parce que la chaîne se termine par une égalité.

Cette distinction doit être respectée par le moteur et couverte par des tests automatisés.

## 9. Succession après une élimination

La règle de succession est une option de configuration.

### 9.1. Variante A — Rejeu du joueur responsable

Après une élimination, le joueur responsable de l'action rejoue immédiatement s'il est encore en jeu.

Si le donneur est éliminé par sa propre condition après retrait et que le destinataire survit, le destinataire devient actif.

Si le joueur qui doit rejouer n'a plus de jeton :
- il en tire un du sac commun si celui-ci contient encore des jetons ;
- il vérifie les conditions applicables après ce tirage ;
- s'il ne peut tirer aucun jeton parce que le sac commun est vide, il est éliminé et révèle sa carte secrète complète.

La succession continue alors en ignorant les joueurs éliminés.

Si plusieurs joueurs sont éliminés par la même action, la succession reprend depuis la position du destinataire dans le sens horaire, en ignorant les joueurs éliminés.

Le tirage nécessaire au rejeu est secret par défaut. Sa révélation peut être activée comme variante de test.

En mode Points et manches, une élimination causée par le tirage nécessaire au rejeu ne rapporte aucun point.

### 9.2. Variante B — Joueur suivant dans le sens horaire

Après une élimination, la succession reprend dans le sens horaire depuis la position du joueur éliminé, en ignorant les joueurs éliminés.

Si le donneur et le destinataire sont éliminés par la même action, le parcours commence depuis la position du destinataire.

Si la succession sélectionne un joueur encore en jeu dont le sac personnel est vide, ce joueur est éliminé à son tour. Il révèle sa carte secrète complète. La succession continue depuis sa position.

En mode Points et manches, chaque élimination forcée de cette chaîne est attribuée au joueur dont l'action initiale a déclenché la chaîne, sauf lorsque la résolution aboutit à une égalité terminale sans vainqueur.

### 9.3. Aucun joueur restant

Si aucun joueur ne demeure en jeu, la partie se termine sur une égalité sans vainqueur.

Le moteur ne doit pas rechercher un prochain joueur actif lorsqu'il n'existe plus aucun joueur valide.

## 10. Attribution des points en mode Points et manches

### 10.1. Élimination d'un destinataire après acceptation

Si le destinataire est éliminé après avoir accepté un cadeau, le donneur reçoit un point, sous réserve des exceptions applicables aux égalités terminales.

### 10.2. Élimination d'un destinataire après refus

Si le destinataire est éliminé après le tirage consécutif à un refus, le donneur reçoit un point, sous réserve des exceptions applicables aux égalités terminales.

### 10.3. Auto-élimination du donneur

Si le donneur est éliminé à cause de sa propre condition après avoir retiré le jeton de son sac, il ne reçoit aucun point pour sa propre élimination.

Si le destinataire est également éliminé par la même action, le point dû pour son élimination est attribué au donneur, même si celui-ci est également éliminé, sauf si l'action initiale élimine directement tous les joueurs encore en jeu.

Si l'action initiale ne provoque pas à elle seule l'élimination de tous les joueurs, le point valablement attribué pour l'élimination du destinataire est conservé, même si une chaîne ultérieure aboutit à une égalité terminale.

### 10.4. Chaîne d'éliminations en variante B

Lorsqu'une action déclenche une chaîne d'éliminations forcées, chaque élimination forcée rapporte normalement un point au joueur responsable de l'action initiale.

Toutefois, l'élimination qui met fin à la partie en éliminant tous les joueurs encore en jeu ne rapporte aucun point.

Les points acquis avant cette dernière élimination restent conservés.

Si l'action initiale élimine directement tous les joueurs encore en jeu, aucun point ni bonus n'est attribué au titre de cette action initiale.

### 10.5. Élimination liée au rejeu en variante A

Lorsqu'un joueur est éliminé après avoir tiré un jeton pour effectuer un rejeu, cette élimination ne rapporte aucun point.

### 10.6. Bonus de manche

Le joueur qui remporte la manche reçoit un bonus d'un point, conformément aux règles du mode Points et manches.

Le bonus est attribué même si ce joueur est éliminé lors de la même action qui lui permet d'atteindre le seuil d'éliminations prévu pour remporter la manche, sauf si la résolution entraîne une égalité terminale sans vainqueur.

Si un joueur remporte normalement la manche en tant que dernier survivant avant d'atteindre ce seuil, il reçoit également le bonus.

Aucun bonus de manche n'est attribué si la résolution aboutit à une égalité terminale sans vainqueur.

## 11. Fin des manches en mode Points et manches

### 11.1. Format C1 — Nombre fixe de manches

Le format C1 prévoit trois manches.

À la fin de la troisième manche :
1. Comparer les scores totaux.
2. Si un joueur possède le score le plus élevé sans égalité en tête, il gagne la partie.
3. Si plusieurs joueurs sont à égalité en tête, organiser une manche supplémentaire.
4. À la fin de cette manche supplémentaire, comparer les scores totaux.
5. Si plusieurs joueurs sont encore à égalité en tête, ils partagent la victoire.

Le moteur doit conserver tous les scores acquis pendant les manches précédentes.

### 11.2. Format C2 — Seuil de points

Le seuil de points est choisi avant la partie.

Lorsqu'un joueur atteint ou dépasse ce seuil pendant une manche, la manche continue jusqu'à sa fin normale.

À la fin de cette manche :
1. Attribuer le bonus de manche au vainqueur, si un vainqueur de manche existe.
2. Comparer les scores totaux.
3. Terminer la partie et désigner le joueur ayant le score le plus élevé.

Le joueur ayant franchi le seuil en premier ne gagne donc pas automatiquement. Un autre joueur peut le dépasser avant la fin de la manche.

Si le seuil n'est pas atteint pendant une manche et n'est pas franchi par l'attribution du bonus de manche, une nouvelle manche commence.

Une égalité terminale sans vainqueur met fin à la partie indépendamment du classement des scores.

## 12. Nouvelle manche

Lorsqu'une nouvelle manche doit commencer :
- Tous les jetons sont remis dans le sac commun.
- Les cartes secrètes sont redistribuées.
- Chaque joueur participant à la nouvelle manche reçoit trois jetons.
- Les collections initiales sont vérifiées.
- Les compteurs d'élimination de la manche sont réinitialisés.
- Les scores totaux sont conservés.
- Le premier joueur est déterminé selon la méthode retenue.

Le résultat d'une manche précédente ne doit pas être effacé de l'historique.

## 13. Paramètres à garder configurables

Les éléments suivants doivent être pilotables sans réécrire le moteur :

- Mode de jeu.
- Variante de succession.
- Vérification ou non de la condition du donneur après retrait.
- Visibilité des tirages après refus.
- Visibilité des tirages pour le rejeu.
- Nombre de couleurs.
- Quantités de jetons par couleur.
- Familles de conditions de défaite et leurs paramètres.
- Familles de conditions de victoire et leurs paramètres.
- Règles exactes ou minimales de comptage.
- Nombre de manches en C1.
- Seuil de points en C2.
- Seuil d'éliminations utilisé pour gagner une manche.
- Règles d'attribution des points.

Les valeurs proposées dans ce document sont des hypothèses de départ quand elles ne sont pas explicitement validées. Elles doivent être identifiables comme telles dans la configuration.

## 14. Erreurs de règles à détecter

Le moteur et les tests doivent notamment détecter les situations suivantes :

- Un jeton se trouve dans plusieurs emplacements.
- Un jeton disparaît pendant un transfert.
- Un joueur éliminé effectue une action normale.
- Une même élimination est comptée plusieurs fois dans une résolution.
- Une condition de victoire est vérifiée après un événement non autorisé.
- Une collection initiale invalide provoque une élimination au lieu d'un nouveau tirage.
- Un destinataire refuse alors que le sac commun est vide.
- Le donneur récupère ou transfère incorrectement le jeton proposé après un refus.
- Un point est attribué pour une auto-élimination du donneur.
- Une élimination provoquée par un tirage de rejeu en variante A rapporte un point.
- Une égalité terminale déclenche à tort un bonus ou des points pour l'action terminale.
- La fin de partie C2 intervient avant la fin normale de la manche.
- Les scores totaux sont effacés au début d'une nouvelle manche.
- Une carte secrète présente des conditions de victoire et de défaite qui peuvent être satisfaites simultanément par une même collection.

Toutes ces situations doivent faire l'objet de tests automatisés.
