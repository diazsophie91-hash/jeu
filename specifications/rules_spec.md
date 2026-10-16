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

Une condition de victoire peut être évaluée par le moteur en privé pendant la mise en place uniquement pour vérifier la validité de la collection initiale. Ce contrôle de préparation n'est pas un déclencheur de victoire : si la condition est satisfaite, la collection est rejetée et le joueur tire trois nouveaux jetons ; aucune carte n'est révélée et aucune victoire ni élimination n'est déclarée.

En cours de partie, une condition de victoire ne peut être vérifiée comme déclencheur de victoire que lorsqu'un événement autorisé survient. En mode Objectif secret, les événements autorisés sont la réception d'un cadeau accepté, le tirage du sac commun après un refus, le tirage effectué pour permettre au responsable de rejouer en variante A et le tirage requis pour activer en variante A un successeur désigné dont le sac personnel est vide. Lorsqu'un objectif autorisé est satisfait en cours de jeu, la carte complète est révélée, la victoire est déclarée et la partie s'arrête. Le simple retrait d'un jeton par le donneur ne peut jamais déclencher sa victoire personnelle.

### 2.3. Compatibilité entre victoire et défaite

Le contenu d'une carte doit également correspondre au mode sélectionné : Dernier survivant et Points et manches exigent une condition de défaite sans condition individuelle de victoire ; Objectif secret exige une condition de défaite et une condition de victoire.

La conception doit empêcher qu'une même collection satisfasse simultanément les deux conditions d'une carte d'Objectif secret. Les cartes générées ou configurées doivent être contrôlées avant utilisation : carte incomplète, incompatible avec le mode, contradictoire, ou utilisant un type ou paramètre inconnu doit être signalée comme invalide. Si le moteur gère le paquet, il doit aussi vérifier qu'il contient suffisamment de cartes pour les joueurs concernés et que sa composition respecte la configuration déclarée. La conception prévoit deux exemplaires de chaque type de condition de défaite ; cette contrainte porte sur la configuration de paquet retenue et ne fixe pas les seuils expérimentaux des conditions.

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

Les conditions de défaite ne sont pas vérifiées à chaque modification interne de l'état. Elles le sont aux moments prévus par les règles. La variante de contrôle du donneur après retrait est distincte des contrôles du destinataire : lorsqu'elle est activée, elle est évaluée avant la décision du destinataire ; la décision et la résolution du cadeau continuent même si le donneur est alors éliminé.

### 4.1. Après réception d'un cadeau accepté

Après révélation et transfert du jeton, le destinataire vérifie les conditions applicables à partir de sa nouvelle collection. En mode Objectif secret, il vérifie d'abord sa condition de victoire : si elle est satisfaite, il révèle toute sa carte secrète, gagne immédiatement et la résolution s'arrête sans vérification ni attribution ultérieure liée à cette action. Si aucune victoire immédiate n'est déclarée, il vérifie sa condition de défaite. S'il est éliminé, il révèle toute sa carte et tous les jetons encore présents dans son sac personnel rejoignent le sac commun.

### 4.2. Après un tirage consécutif à un refus

Lorsque le refus est permis, le destinataire tire un jeton du sac commun et l'ajoute à sa collection. En mode Objectif secret, il vérifie d'abord sa condition de victoire : si elle est satisfaite, il révèle toute sa carte secrète, gagne immédiatement et la résolution s'arrête sans vérification ni attribution ultérieure liée à cette action. Sinon, il vérifie sa condition de défaite. S'il est éliminé, il révèle toute sa carte et les jetons encore présents dans son sac personnel rejoignent le sac commun.

### 4.3. Après le retrait d'un jeton par le donneur

La vérification de la condition de défaite du donneur après retrait est une variante transversale à tester dans les trois modes A, B et C, puisque chacun attribue une condition de défaite à chaque joueur. Si elle est activée, la condition est vérifiée immédiatement après que le donneur a retiré le jeton de son sac et l'a placé dans sa main, avant que le destinataire décide d'accepter ou de refuser. Si le donneur est éliminé, il révèle sa carte secrète complète et les jetons restant dans son sac personnel sont remis au sac commun ; le jeton proposé reste dans l'emplacement temporaire de la proposition. La proposition reste en cours et le destinataire doit encore pouvoir décider d'accepter ou de refuser.

Si cette option est désactivée, la condition de défaite du donneur n'est pas vérifiée à ce moment-là. L'élimination éventuellement prononcée à la suite du retrait ne peut jamais être annulée rétroactivement par un refus. Le retrait ne déclenche jamais la condition de victoire personnelle du donneur. Le contrôle du donneur n'est jamais répété plus tard dans la même résolution.

Si le donneur a déjà été éliminé après retrait et que le destinataire refuse alors que le sac commun contient au moins un jeton, le jeton proposé est ajouté au sac commun sans révélation, puis le destinataire tire au hasard un jeton dans le sac commun ainsi augmenté. Le jeton proposé peut lui-même être tiré. Le jeton tiré rejoint le sac personnel du destinataire et sa visibilité suit la variante de pioche après refus.

### 4.4. Après un tirage nécessaire à un rejeu en variante A

Lorsqu'un joueur doit rejouer mais ne possède aucun jeton dans son sac personnel, il tire un jeton du sac commun si celui-ci n'est pas vide et l'ajoute à sa collection. Par défaut, ce jeton reste secret ; la variante qui le révèle immédiatement à tous doit également pouvoir être testée. En mode Objectif secret, le joueur vérifie d'abord sa condition de victoire après la pioche. S'il gagne, il révèle toute sa carte secrète et la partie s'arrête immédiatement ; sinon, il vérifie sa condition de défaite. S'il est éliminé, il révèle toute sa carte et la succession reprend après sa position. Cette élimination causée par sa propre pioche ne rapporte aucun point à un autre joueur en mode Points et manches. S'il survit sans gagner, il joue immédiatement son tour.

Si le sac commun est vide, aucune pioche n'a lieu : le joueur est éliminé, révèle sa carte secrète complète et la succession reprend après sa position dans le sens horaire. Cette élimination n'est attribuée à aucun autre joueur et ne rapporte aucun point.

### 4.5. Pendant la préparation

La collection initiale de trois jetons est évaluée en privé afin d'écarter une collection qui satisfait une condition de défaite ou, en mode Objectif secret, une condition de victoire. Le joueur peut consulter sa propre carte en privé et le moteur peut évaluer les conditions en interne ; aucun autre joueur n'est informé de l'évaluation.

Cette vérification ne provoque jamais une élimination ou une victoire et aucune carte ni condition n'est révélée publiquement. Si la collection n'est pas valide, les trois jetons sont remis dans le sac commun et une nouvelle collection de trois jetons est tirée. La condition satisfaite sert uniquement à invalider la collection de départ ; elle ne constitue pas un résultat de jeu. En cours de partie, la carte complète n'est révélée aux joueurs que lorsqu'une condition déclenche effectivement une élimination ou une victoire secrète selon les règles.

### 4.6. Validation des configurations de départ

Avant la mise en place, le moteur doit rejeter une configuration si le stock contient moins de trois jetons par joueur, si les données des jetons ou des cartes sont invalides, ou si aucune attribution complète de collections initiales valides de trois jetons n'est possible pour l'ensemble des joueurs avec le stock configuré. Pour ce contrôle, une collection initiale valide ne satisfait aucune condition de défaite ni, en mode Objectif secret, aucune condition de victoire.

Si une séquence de tirages déjà acceptés rend impossible tout tirage valide pour un joueur restant, le moteur doit arrêter cette tentative de mise en place avec une erreur explicite au lieu de boucler indéfiniment. Cet échec de préparation ne révèle aucune carte et ne constitue ni une victoire ni une élimination. Les conditions de départ doivent être vérifiées en privé et ne doivent pas être publiées dans le message d'erreur.

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
- après un tirage du sac commun effectué pour permettre au responsable de rejouer en variante A ;
- après un tirage du sac commun requis pour activer en variante A un successeur désigné dont le sac personnel est vide.

Les deux derniers déclencheurs couvrent les tirages de succession en variante A : celui du responsable qui doit rejouer et celui d’un successeur vivant désigné après l’élimination du responsable mais dépourvu de jeton personnel.

La condition de victoire n'est jamais déclenchée par le seul retrait d'un jeton du sac personnel du donneur. Un tirage de succession en variante A ne peut la déclencher que si le tirage est effectivement requis par les règles pour que le responsable ou le successeur désigné puisse agir.

Lorsqu'un objectif est satisfait :
1. La carte secrète complète du joueur est révélée.
2. La victoire du joueur est déclarée.
3. La partie s'arrête immédiatement.
4. Aucune nouvelle action normale n'est autorisée.

Si une même résolution comporte plusieurs événements, le moteur doit appliquer les priorités de résolution définies dans `game_flow.md`. Il ne doit pas commencer un nouveau tour avant d'avoir terminé cette résolution.

## 7. Refus d'un cadeau et sac commun vide

Un joueur ne peut refuser un cadeau que si le sac commun contient au moins un jeton au moment où le refus doit être résolu.

Si le sac commun est vide, le refus est impossible : le donneur révèle le jeton qu'il tient et le transfère au destinataire. Aucun tirage de remplacement n'a lieu et le jeton n'est pas remis dans le sac personnel du donneur avant ce transfert. Les conditions applicables au destinataire sont ensuite vérifiées selon la procédure prévue pour une acceptation.

Lorsque le donneur est encore en jeu et que le refus est permis, le jeton proposé est remis dans son sac personnel sans être révélé, puis le destinataire tire un jeton au hasard dans le sac commun.

Si le donneur a déjà été éliminé avant la décision du destinataire, le jeton proposé reste temporaire jusqu'à la décision. En cas de refus autorisé, le jeton proposé rejoint d'abord le sac commun sans révélation, puis le destinataire tire au hasard dans le sac ainsi augmenté ; le jeton proposé peut être celui qui est tiré.

Le jeton proposé ne doit jamais être simultanément compté dans plusieurs emplacements.

## 8. Règles communes aux éliminations

### 8.1. Une seule élimination par joueur et par résolution

Un joueur dont la condition de défaite est satisfaite est éliminé au plus une fois pendant la résolution concernée.

Le moteur doit enregistrer les joueurs déjà éliminés par cette résolution pour empêcher les doublons.

### 8.2. Révélation des cartes secrètes et jetons restants

Après toute élimination, le joueur éliminé révèle sa carte secrète complète, y compris sa condition de victoire en mode Objectif secret.

Si plusieurs joueurs sont éliminés par la même résolution, chaque carte concernée doit être révélée.

Tous les jetons encore présents dans le sac personnel du joueur éliminé sont remis au sac commun. Un jeton déjà transféré à un destinataire suit son parcours normal ; si ce destinataire est également éliminé au cours de la même action, le jeton reçu rejoint le sac commun avec les autres jetons encore présents dans son sac. Un jeton temporairement tenu en main au titre d'une proposition en cours n'est pas un jeton encore présent dans le sac personnel et reste dans l'état temporaire jusqu'à résolution de la proposition.

Une victoire secrète provoque également la révélation complète de la carte du vainqueur et arrête immédiatement la partie.

### 8.3. Égalité terminale

Si tous les joueurs encore en jeu sont éliminés par la même résolution, la partie se termine sur une égalité sans vainqueur.

Il faut distinguer deux situations en mode Points et manches.

**Situation 1 — L'action initiale élimine directement tous les joueurs encore en jeu.**

Aucun point ni bonus de manche n'est attribué au titre de cette action.

**Situation 2 — L'action initiale déclenche une chaîne d'éliminations qui aboutit ensuite à une égalité terminale.**

Les points valablement acquis avant la dernière élimination restent conservés. La dernière élimination, celle qui élimine tous les joueurs encore en jeu, ne rapporte aucun point. Aucun bonus de manche n'est attribué pour cette résolution terminale.

Les points déjà attribués ne doivent pas être annulés rétroactivement simplement parce que la chaîne se termine par une égalité.

**Situation 3 — Égalité terminale pendant une résolution distincte en variante A.**

Si une élimination ultérieure liée au rejeu ou à un successeur sans jeton en variante A met fin à la partie sur une égalité, cette résolution distincte ne rapporte aucun point à un autre joueur pour l'élimination causée par la propre pioche ou l'absence de jeton. Les points valablement acquis pendant l'action initiale précédente restent conservés et ne sont pas annulés rétroactivement.

Cette distinction doit être respectée par le moteur et couverte par des tests automatisés.

## 9. Succession après une élimination

La règle de succession est une option de configuration.

### 9.1. Variante A — Rejeu du joueur responsable

Après résolution complète de l'action initiale, validation des points autorisés et contrôle des fins immédiates, le joueur responsable de l'élimination rejoue immédiatement s'il est encore en jeu et qu'aucune fin de partie ou de manche ne s'applique. Si aucune élimination n'a eu lieu, le destinataire devient actif. Si le donneur est éliminé à la suite du retrait de son propre jeton et que le destinataire survit, le destinataire devient actif après la résolution du cadeau.

Si le responsable qui doit rejouer possède au moins un jeton, il joue normalement. S'il n'en possède aucun, il vérifie le sac commun :
- Si le sac commun contient un jeton, il en tire un et l'ajoute à sa collection. Le jeton est secret par défaut ; la variante de révélation immédiate à tous reste à tester. En mode Objectif secret, la condition de victoire est vérifiée d'abord. Si elle est satisfaite, la carte complète est révélée, la victoire est déclarée et la partie s'arrête. Sinon, la condition de défaite est vérifiée. Si le joueur est éliminé, il révèle sa carte complète et la succession reprend après sa position ; cette élimination causée par sa propre pioche ne rapporte aucun point et ne fait pas progresser son compteur en mode Points et manches. S'il survit sans gagner, il joue immédiatement son tour.
- Si le sac commun est vide, il est éliminé sans pioche et révèle sa carte complète. La succession reprend après sa position ; aucun point n'est attribué à un autre joueur pour cette élimination.

Si le responsable a été éliminé, la succession reprend au prochain joueur encore en jeu rencontré dans le sens horaire après sa position, en sautant les éliminés. Si ce successeur a des jetons, il devient actif. S'il possède un sac personnel vide, il vérifie le sac commun : s'il est vide, il est éliminé sans pioche ni attribution de point et la succession continue après sa position ; s'il contient un jeton, le successeur pioche, vérifie d'abord sa condition de victoire (en mode Objectif secret), puis sa condition de défaite. S'il survit sans gagner, il joue immédiatement son tour ; s'il est éliminé, la succession continue après sa position et cette élimination n'est attribuée à aucun autre joueur.

Si plusieurs joueurs sont éliminés par la même action initiale, la succession reprend depuis la position du destinataire, dans le sens horaire, en ignorant les éliminés. Si une résolution distincte de rejeu se termine par une égalité terminale, elle n'annule pas les points valablement acquis lors de l'action initiale précédente. Les actions de rejeu et les éliminations qui en résultent ne rapportent aucun point à un autre joueur si elles sont causées par la propre pioche ou l'absence de jeton du joueur concerné.

### 9.2. Variante B — Joueur suivant dans le sens horaire

Lorsqu'une élimination a lieu, la succession recherche le prochain joueur encore en jeu dans le sens horaire après la position du joueur éliminé. Si le donneur est éliminé par sa propre condition après retrait et que le destinataire survit, le destinataire devient actif après la résolution du cadeau. Si le donneur et le destinataire sont tous deux éliminés pendant la même action initiale et qu'il reste d'autres joueurs, la succession commence après la position du destinataire. Les joueurs déjà éliminés sont toujours ignorés.

Si le successeur désigné est encore en jeu mais possède un sac personnel vide, il est éliminé à son tour et révèle sa carte secrète complète. Les jetons encore présents dans son sac personnel sont remis au sac commun, puis la succession continue après sa position.

Après chaque élimination forcée, contrôler d'abord si aucun joueur ne reste : si oui, terminer par une égalité sans vainqueur ; la dernière élimination ne rapporte aucun point ni bonus de manche, et les points antérieurs sont conservés. Si des joueurs restent, en mode Points et manches, attribuer au responsable initial le point lié à cette élimination forcée d'un adversaire et incrémenter son compteur d'éliminations créditées, même si le responsable est déjà éliminé. Puis vérifier le seuil de manche ; s'il est atteint, la manche se termine et le bonus correspondant est attribué. Si le seuil n'est pas atteint et qu'un seul joueur reste, ce dernier gagne la partie en mode A/B ou la manche avec son bonus en mode C. Sinon, poursuivre la succession.

L'auto-élimination du responsable initial ne rapporte jamais de point supplémentaire. Si l'action initiale élimine directement tous les joueurs encore en jeu, aucun point ni bonus n'est attribué au titre de cette action initiale.

### 9.3. Aucun joueur restant

Si aucun joueur ne demeure en jeu, la partie se termine sur une égalité sans vainqueur.

Le moteur ne doit pas rechercher un prochain joueur actif lorsqu'il n'existe plus aucun joueur valide.

## 10. Attribution des points en mode Points et manches

Lorsqu'une élimination d'adversaire est effectivement attribuée à un joueur et rapporte un point, son compteur d'éliminations créditées pendant la manche augmente également d'une unité. Cette attribution reste valable même si le responsable est lui-même éliminé au cours de la même action, sauf si l'action initiale élimine directement tous les joueurs encore en jeu. L'auto-élimination ne donne aucun point ni incrément supplémentaire.

### 10.1. Élimination d'un destinataire après acceptation

Si le destinataire est éliminé après avoir accepté un cadeau, le donneur reçoit un point et son compteur d'éliminations créditées augmente d'une unité, sauf si l'action initiale élimine directement tous les joueurs encore en jeu.

### 10.2. Élimination d'un destinataire après refus

Si le destinataire est éliminé après le tirage consécutif à un refus, le donneur reçoit un point et son compteur d'éliminations créditées augmente d'une unité, sauf si l'action initiale élimine directement tous les joueurs encore en jeu.

### 10.3. Auto-élimination du donneur

Si le donneur est éliminé à cause de sa propre condition après avoir retiré le jeton de son sac, il ne reçoit aucun point pour sa propre élimination.

Si le destinataire est également éliminé par la même action initiale, le point dû pour cette élimination d'adversaire est attribué au donneur et son compteur de manche progresse, même s'il est lui-même éliminé, sauf si l'action initiale élimine directement tous les joueurs encore en jeu. Cette attribution ne constitue pas un point pour l'auto-élimination du donneur.

Si l'action initiale ne provoque pas à elle seule l'élimination de tous les joueurs, le point valablement attribué pour l'élimination du destinataire est conservé, même si une chaîne ultérieure en variante B aboutit à une égalité terminale ou si une élimination distincte en variante A aboutit ensuite à une égalité. Les points précédemment acquis ne sont jamais annulés rétroactivement.

### 10.4. Chaîne d'éliminations en variante B

Lorsqu'une action initiale déclenche une chaîne d'éliminations forcées de successeurs sans jeton, chaque élimination forcée non terminale d'un adversaire est attribuée au joueur responsable de l'action initiale et rapporte un point ; son compteur d'éliminations créditées progresse également, même si le responsable est éliminé pendant la chaîne.

Après chaque élimination forcée, la priorité est la suivante : si aucun joueur ne reste, égalité sans vainqueur, sans point ni bonus pour cette dernière élimination ; sinon, attribuer le point et incrémenter le compteur si l'élimination est attribuable ; ensuite vérifier le seuil de manche ; si le seuil n'est pas atteint et qu'un seul joueur reste, ce dernier gagne la manche et reçoit le bonus ; sinon, poursuivre la succession.

L'élimination forcée qui met fin à la partie en éliminant le dernier joueur ne rapporte aucun point et aucun bonus de manche. Les points et incréments de compteur valablement acquis avant cette dernière élimination restent conservés.

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

À la fin de cette manche, si le seuil a été atteint pendant la manche ou grâce au bonus attribué à sa fin :
1. Attribuer le bonus de manche au vainqueur de la manche, si un vainqueur existe.
2. Comparer les scores totaux.
3. Le joueur ou les joueurs ayant le score total le plus élevé gagnent ; les joueurs à égalité en tête partagent la victoire.

Le joueur ayant franchi le seuil en premier ne gagne donc pas automatiquement. Un autre joueur peut le dépasser avant la fin de la manche.

Si le seuil n'est atteint ni pendant la manche ni par l'attribution du bonus de manche, une nouvelle manche complète commence.

Une égalité terminale sans vainqueur met fin à la partie indépendamment du classement des scores ; elle ne doit pas être confondue avec une égalité de scores en fin normale de C2.

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

Le moteur doit notamment signaler :
- une carte de victoire individuelle en mode A ou C ;
- une carte Objectif secret dépourvue de condition de victoire ou de défaite ;
- une carte dont les conditions de victoire et de défaite peuvent être satisfaites simultanément par une même collection ;
- une référence à une couleur, un type de condition ou un paramètre inconnu ;
- un paquet géré par le moteur qui ne contient pas suffisamment de cartes pour la distribution prévue ou qui ne respecte pas sa composition configurée.

Ces validations ne doivent pas inventer de valeurs définitives pour les paramètres encore expérimentaux.

Le moteur et les tests doivent notamment détecter les situations suivantes :

- Un jeton se trouve dans plusieurs emplacements.
- Un jeton disparaît pendant un transfert.
- Un joueur éliminé effectue une action normale.
- Une même élimination est comptée plusieurs fois dans une résolution.
- Une condition de victoire est vérifiée après un événement non autorisé.
- Une collection initiale invalide provoque une élimination ou une révélation de carte au lieu d'un nouveau tirage.
- Une configuration avec moins de trois jetons par joueur, une carte de départ invalide ou aucune attribution complète de collections initiales valides est acceptée.
- Une tentative de préparation impossible boucle indéfiniment au lieu de produire une erreur explicite.
- Un destinataire refuse alors que le sac commun est vide.
- Le donneur récupère ou transfère incorrectement le jeton proposé après un refus.
- Une proposition déjà engagée est interrompue parce que le donneur est éliminé avant la décision du destinataire.
- Le moteur traite incorrectement le refus après élimination préalable du donneur : le jeton proposé doit rejoindre sans révélation le sac commun avant le tirage du destinataire, et ce tirage doit porter sur le sac ainsi augmenté.
- Les jetons encore présents dans le sac personnel d'un joueur éliminé ne sont pas remis au sac commun.
- La succession A omet le tirage obligatoire d'un successeur sans jeton ou attribue à tort un point pour une élimination causée par sa propre pioche.
- La succession B poursuit la chaîne après une égalité terminale ou vérifie les priorités dans le mauvais ordre.
- Le compteur d'éliminations créditées progresse sans point attribué ou n'augmente pas lorsqu'un point valide est attribué.
- Une égalité des scores au terme normal de C2 ne partage pas la victoire entre les joueurs à égalité en tête.
- Un point est attribué pour une auto-élimination du donneur.
- Une élimination provoquée par un tirage de rejeu en variante A rapporte un point.
- Une égalité terminale déclenche à tort un bonus ou des points pour l'action terminale.
- La fin de partie C2 intervient avant la fin normale de la manche.
- Les scores totaux sont effacés au début d'une nouvelle manche.
- Une carte secrète présente des conditions de victoire et de défaite qui peuvent être satisfaites simultanément par une même collection.

Toutes ces situations doivent faire l'objet de tests automatisés.
