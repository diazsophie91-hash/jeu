# Déroulement d'une partie — C'est cadeau !

## 1. Objectif du document

Ce document décrit le déroulement général d'une partie de C'est cadeau !, depuis la préparation jusqu'à la fin d'une partie ou d'une manche.

Les conditions de victoire, les conditions d'élimination, les variantes et le système de points doivent être configurables. Les valeurs encore expérimentales ne doivent pas être considérées comme définitives.

## 2. Les éléments du jeu

Le jeu utilise :
- Un sac commun opaque contenant les jetons disponibles.
- Un petit sac opaque par joueur.
- Des jetons répartis en plusieurs couleurs.
- Des cartes secrètes contenant les conditions propres à chaque joueur.

Le contenu d'une carte dépend du mode : en mode A — Dernier survivant — et en mode C — Points et manches — chaque joueur reçoit une carte portant une condition de défaite, sans condition individuelle de victoire. En mode B — Objectif secret — la carte secrète ordinaire associe une condition de défaite et une condition de victoire. Une carte spéciale d'élimination précoce reste un élément à concevoir et ne doit pas être activée tant que son fonctionnement n'est pas défini.

Le destinataire connaît uniquement les couleurs ou les types de jetons susceptibles de se trouver dans le grand sac commun ; il ne connaît pas la composition exacte restante. Le règlement ne permet pas de supposer que cette information est également connue de tous les autres joueurs.

Les collections personnelles restent cachées aux autres joueurs. Chaque joueur peut consulter sa propre collection en privé pour vérifier ses conditions et choisir consciemment un jeton.

## 3. Préparation de la partie

Avant la mise en place, choisir le mode de jeu, la variante de succession et les autres variantes à tester. Les paramètres expérimentaux doivent être enregistrés avec la configuration de la partie.

### 3.1. Préparer les sacs

1. Placer tous les jetons de la configuration choisie dans le sac commun.
2. Distribuer une carte secrète à chaque joueur.
3. Chaque joueur tire trois jetons au hasard du sac commun et les place dans son sac personnel.
4. Chaque joueur vérifie en privé si sa collection initiale satisfait une condition de défaite ou, en mode Objectif secret, une condition de victoire. La carte secrète et les conditions qu'elle contient ne sont pas révélées.
5. Si une condition de défaite ou de victoire est satisfaite, la collection initiale est invalide : le joueur remet ses trois jetons dans le sac commun et en tire trois nouveaux.
6. Répéter cette vérification en privé jusqu'à obtenir une collection initiale valide.

Pendant la mise en place, chaque joueur peut consulter sa propre carte en privé et le moteur peut évaluer les conditions en interne. Si une condition est satisfaite, elle sert uniquement à rejeter la collection initiale : aucun autre joueur n'en est informé, et aucune carte ni condition n'est révélée publiquement. Le statut du joueur ne change pas ; aucune victoire, élimination ou attribution de points n'est déclenchée. La carte complète n'est révélée aux joueurs qu'en cours de jeu, lorsqu'une élimination ou une victoire secrète est effectivement déclenchée selon les règles.

La possibilité d'obtenir une mise en place complète ne doit pas être supposée sans validation. Avant de commencer, vérifier que le nombre de jetons est au moins égal à trois fois le nombre de joueurs, que la configuration et les cartes sont valides, et qu'il existe au moins une attribution complète de collections initiales de trois jetons respectant les cartes et le stock configuré. Si aucune attribution complète n'est possible, rejeter la configuration avec une erreur explicite. Si les tirages déjà acceptés rendent impossible tout tirage valide pour un joueur restant, arrêter proprement cette tentative de mise en place et signaler l'échec ; ne pas boucler indéfiniment, ne révéler aucune carte et ne déclarer ni victoire ni élimination.

**Configuration d'essai non définitive :** quatre couleurs, huit joueurs au maximum et quarante jetons au total constituent une hypothèse de départ pour les simulations. À huit joueurs, vingt-quatre jetons sont distribués lors de la mise en place initiale. Ces valeurs servent à un scénario de référence et ne doivent pas être codées comme des paramètres obligatoires ni présentées comme définitives.

### 3.2. Choisir le premier joueur

Le premier joueur est choisi selon la méthode convenue par le groupe :
- choix collectif ;
- ou personne autour de la table ayant reçu le cadeau réel le plus récemment.

Si plusieurs personnes sont à égalité sur le critère du cadeau réel reçu le plus récemment, le groupe tranche par accord. La méthode utilisée peut être définie avant le début de la partie.

## 4. Déroulement normal d'un tour

Le tour commence avec un joueur actif.

1. Le joueur actif choisit un autre joueur encore en jeu.
2. Le donneur choisit consciemment un jeton dans son sac personnel.
3. Il retire ce jeton et le place dans sa main sans en révéler la couleur. La proposition de cadeau est engagée.
4. Si la variante transversale de vérification de la condition du donneur après retrait est activée, vérifier sa condition de défaite immédiatement après le retrait du jeton et avant la décision du destinataire. Cette vérification s'applique aux modes A, B et C, qui possèdent tous une condition de défaite.
5. Si cette condition est satisfaite, le donneur est éliminé et révèle sa carte secrète complète. Tous les jetons encore dans son sac personnel retournent au sac commun, mais le jeton proposé reste dans l'emplacement temporaire de la proposition. La proposition reste en cours : le destinataire doit toujours pouvoir décider d'accepter ou de refuser. Si la variante est désactivée, cette vérification n'a pas lieu à ce moment.
6. Le donneur présente le cadeau au destinataire sans révéler le jeton. Les annonces éventuelles restent facultatives et peuvent être mensongères.
7. Le destinataire décide d'accepter ou de refuser sans avoir vu le jeton. Si le sac commun est vide au moment de la décision, le refus est impossible.
8. Le cadeau est résolu conformément aux règles d'acceptation ou de refus et à l'état du sac commun.
9. Après le transfert ou le tirage correspondant, en mode Objectif secret, vérifier d'abord la condition de victoire lorsque l'événement l'autorise. Si elle est satisfaite, révéler la carte complète et terminer immédiatement la partie sans autre vérification ni attribution liée à l'action ; sinon, vérifier la condition de défaite du destinataire.
10. Le moteur résout les éventuelles éliminations supplémentaires, les points et les conditions de fin de partie, puis détermine le joueur actif suivant selon la variante de succession.
11. Le tour se termine, sauf si une victoire immédiate ou une égalité terminale met fin à la partie.

La vérification de la condition de défaite du donneur après retrait est désactivée lorsque la variante correspondante n'est pas sélectionnée.

Le retrait d'un jeton par le donneur ne déclenche jamais sa condition de victoire personnelle en mode Objectif secret.

Un joueur éliminé ne peut plus commencer d'action normale ni être choisi comme destinataire. Toutefois, si son élimination intervient alors que sa proposition de cadeau est en cours, celle-ci doit être résolue normalement avant de déterminer la succession.

## 5. Annonces et mensonges

Le donneur peut annoncer quelque chose au sujet du cadeau, mais il n'est jamais obligé de parler.

Il peut faire une annonce spontanément ou répondre à une question du destinataire.

Une annonce peut être vraie ou mensongère, y compris lorsqu'elle concerne la couleur ou la nature du jeton.

Avant la résolution du cadeau, le destinataire ne connaît pas la véritable identité du jeton.

## 6. Si le destinataire accepte le cadeau

1. Le donneur révèle le jeton à tous les joueurs.
2. Le jeton, jusque-là conservé temporairement dans la main du donneur, rejoint le sac personnel du destinataire.
3. En mode Objectif secret, le destinataire vérifie d'abord sa condition de victoire, puisque la réception d'un cadeau accepté est un déclencheur autorisé. Si elle est satisfaite, il révèle immédiatement sa carte secrète complète à tous les joueurs, la victoire est déclarée et la résolution s'arrête. Aucune vérification ni attribution ultérieure liée à cette action n'a lieu.
4. Si aucune victoire immédiate n'est déclarée, le destinataire vérifie sa condition de défaite. S'il est éliminé, il révèle sa carte secrète complète et tous les jetons encore présents dans son sac personnel sont remis dans le sac commun. Le jeton reçu fait partie de ces jetons.
5. Le moteur applique ensuite les règles de score, de fin immédiate et de succession pertinentes, sans répéter le contrôle de défaite du donneur : lorsque la variante est activée, ce contrôle a déjà eu lieu immédiatement après le retrait et avant la décision du destinataire.

## 7. Si le destinataire refuse le cadeau

Le refus est traité différemment selon l'état du sac commun.

### 7.1. Le sac commun contient encore des jetons

Si le donneur est encore en jeu, il ne révèle pas le jeton proposé et le remet dans son sac personnel. Le destinataire tire ensuite un jeton au hasard dans le sac commun et l'ajoute à son sac personnel.

Si le donneur a déjà été éliminé pendant que la proposition était en cours, le jeton proposé est ajouté au sac commun sans être révélé, puis le destinataire tire au hasard un jeton dans le sac commun ainsi augmenté et l'ajoute à son sac personnel. Le jeton proposé peut donc lui-même être tiré. Le tirage est effectué après la remise du jeton proposé dans le sac commun.

La visibilité du jeton tiré dépend de la variante configurée : il peut être révélé à tous ou rester secret, auquel cas seul le destinataire le connaît et peut le consulter pour vérifier sa collection.

Après la pioche, en mode Objectif secret, le destinataire vérifie d'abord sa condition de victoire. Si elle est satisfaite, il révèle toute sa carte secrète, gagne immédiatement et la résolution s'arrête. Sinon, il vérifie sa condition de défaite. S'il est éliminé, il révèle toute sa carte secrète et remet au sac commun tous les jetons qui restent dans son sac personnel. Le moteur applique ensuite les règles de score et de succession correspondant au résultat.

### 7.2. Le sac commun est vide

Le destinataire ne peut pas refuser le cadeau. Il doit l'accepter.

Le donneur révèle le jeton conservé temporairement dans sa main et le transfère au destinataire. Le jeton n'est pas remis dans le sac personnel du donneur avant ce transfert et aucun tirage de remplacement n'a lieu. Les conditions applicables au destinataire sont ensuite vérifiées selon la procédure d'acceptation.

## 8. Déterminer le joueur actif suivant

Si aucune victoire immédiate ni égalité terminale ne met fin à la partie, le joueur actif suivant dépend du résultat de l'action et de la variante de succession choisie.

### 8.1. Aucun joueur n'est éliminé

Le destinataire devient le joueur actif suivant, que le cadeau ait été accepté ou qu'un jeton ait été tiré après un refus.

### 8.2. Variante A — Rejeu du joueur responsable

Après résolution complète de l'action initiale, attribution des points autorisés et contrôle des fins immédiates, le joueur responsable de l'élimination rejoue immédiatement s'il est encore en jeu et qu'aucune fin de partie ou de manche ne s'applique. Si aucune élimination n'a eu lieu et qu'aucune victoire immédiate n'a été déclarée, le destinataire devient actif. Si le donneur a été éliminé par le retrait de son propre jeton et que le destinataire survit, le destinataire devient actif.

Si le responsable qui doit rejouer possède au moins un jeton dans son sac personnel, il joue normalement. S'il n'en possède aucun, il vérifie le sac commun :
- S'il contient un jeton, le joueur en tire un et l'ajoute à son sac personnel. Le jeton est secret par défaut ; l'option de le révéler à tous reste une variante à tester. En mode Objectif secret, il vérifie d'abord sa condition de victoire : si elle est satisfaite, il révèle toute sa carte et la partie s'arrête. Sinon, il vérifie sa condition de défaite. S'il est éliminé, il révèle sa carte et la succession reprend après sa position dans le sens horaire ; aucun point n'est attribué à un autre joueur pour une élimination provoquée par cette propre pioche. S'il survit sans gagner, il joue immédiatement son tour.
- Si le sac commun est vide, il est éliminé sans pioche, révèle sa carte secrète complète et la succession reprend après sa position dans le sens horaire. Cette élimination ne rapporte aucun point à un autre joueur.

Si le responsable n'est plus en jeu, la succession reprend au prochain joueur encore en jeu rencontré dans le sens horaire après sa position, en sautant les joueurs éliminés. Si ce successeur possède au moins un jeton, il devient actif et joue normalement. S'il a un sac personnel vide, il applique les mêmes règles de pioche dans le sac commun : pioche secrète par défaut, contrôle de victoire puis de défaite, élimination sans attribution de point si aucune pioche n'est possible ou si sa propre pioche entraîne sa défaite. S'il survit sans gagner après la pioche, il joue immédiatement son tour ; si cette pioche l'élimine, la succession continue après sa position.

Si plusieurs joueurs sont éliminés pendant l'action initiale, la succession reprend depuis la position du destinataire, dans le sens horaire, en ignorant les joueurs éliminés. Si une résolution distincte liée au rejeu se termine par une égalité terminale, les points déjà acquis lors de l'action initiale ne sont pas annulés rétroactivement. En mode Points et manches, les éliminations provoquées par l'absence de jeton du responsable ou par sa propre pioche de rejeu ne rapportent aucun point et ne font pas progresser son compteur d'éliminations créditées.

### 8.3. Variante B — Joueur suivant dans le sens horaire

Lorsqu'une élimination se produit, le prochain joueur actif est déterminé dans le sens horaire après la position du joueur éliminé, en ignorant les joueurs déjà éliminés. Exception : si le donneur est éliminé par sa propre condition après retrait et que le destinataire survit, le destinataire devient actif après la résolution du cadeau. Si le donneur et le destinataire sont éliminés pendant la même action initiale et qu'il reste d'autres joueurs, la succession recherche le prochain joueur encore en jeu dans le sens horaire après la position du destinataire.

Si le successeur désigné est encore en jeu mais que son sac personnel est vide, il est éliminé et révèle sa carte secrète complète. Tous les jetons encore présents dans son sac personnel sont remis au sac commun. La succession continue après sa position, dans le sens horaire, en ignorant les joueurs éliminés.

Après chaque élimination forcée de cette chaîne, appliquer les contrôles dans cet ordre :
1. Si aucun joueur ne reste en jeu, la partie se termine sur une égalité sans vainqueur. La dernière élimination ne rapporte aucun point ni bonus de manche ; les points acquis avant elle sont conservés. Cette égalité terminale est prioritaire sur le seuil de manche.
2. Si des joueurs restent et que le mode est Points et manches, attribuer le point et faire progresser le compteur du joueur auquel cette élimination d'adversaire est attribuée, même si ce joueur a été éliminé plus tôt dans la même chaîne. Puis vérifier si son compteur atteint le seuil de manche ; si oui, la manche se termine et son bonus est attribué.
3. Si le seuil de manche n'est pas atteint et qu'un seul joueur reste, ce dernier gagne la partie en mode A/B, ou la manche et son bonus en mode C.
4. Sinon, poursuivre la succession.

Si l'action initiale élimine directement tous les joueurs encore en jeu, elle se termine par une égalité sans vainqueur et n'accorde aucun point ni bonus au titre de cette action. L'auto-élimination du joueur responsable ne rapporte jamais de point supplémentaire.

## 9. Règles communes aux éliminations

Une même action ne peut éliminer un même joueur qu'une seule fois, même si plusieurs conditions de défaite sont satisfaites simultanément.

Après toute élimination, le joueur éliminé révèle sa carte secrète complète aux autres joueurs et tous les jetons encore présents dans son sac personnel sont remis au sac commun. Un jeton transféré au destinataire fait partie de son sac personnel dès le transfert ; si le destinataire est éliminé au cours de la même action, ce jeton revient donc au sac commun avec les autres jetons qu'il détient encore. Le jeton temporairement tenu dans la main du donneur pour une proposition en cours n'est pas un jeton de son sac personnel.

Si plusieurs joueurs sont éliminés par une même action, toutes les éliminations concernées sont résolues avant de déterminer le joueur actif suivant.

Si tous les joueurs encore en jeu sont éliminés par la même résolution, la partie se termine sur une égalité sans vainqueur. Cette issue prévaut sur les conditions normales de victoire de manche et sur les bonus associés à cette résolution.

En mode Points et manches, lorsqu'une égalité terminale résulte d'une chaîne d'éliminations, les points valablement acquis avant la dernière élimination restent conservés. La dernière élimination ne rapporte aucun point et aucun bonus de manche n'est attribué.

Si l'action initiale élimine directement tous les joueurs encore en jeu, aucun point ni bonus n'est attribué pour cette action.

## 10. Les trois modes de jeu

### Mode A — Dernier survivant

Chaque joueur possède une condition secrète de défaite, mais pas d'objectif personnel de victoire.

La partie continue tant que plusieurs joueurs sont encore en jeu et qu'aucune égalité terminale ne se produit.

Le dernier joueur encore en jeu remporte la partie.

### Mode B — Objectif secret

Chaque joueur possède une condition secrète de défaite et une condition secrète de victoire.

La condition de victoire est vérifiée uniquement après :
- la réception d'un cadeau accepté ;
- le tirage d'un jeton du sac commun après un refus ;
- le tirage d'un jeton du sac commun nécessaire pour permettre au responsable de rejouer en variante A ;
- le tirage requis, en variante A, pour qu'un successeur désigné après l'élimination du responsable puisse agir alors que son sac personnel est vide.

Pour le second cas de succession, la condition n'est contrôlée qu'après le tirage effectivement requis, jamais au seul moment où le successeur est désigné. La condition de victoire n'est pas vérifiée lorsque le joueur retire simplement un jeton de son sac en tant que donneur.

Lorsqu'un joueur satisfait son objectif, il révèle sa carte secrète complète et la partie s'arrête immédiatement.

Si aucun objectif personnel n'est satisfait et qu'il ne reste qu'un joueur en jeu, celui-ci gagne en tant que dernier survivant.

### Mode C — Points et manches

Chaque joueur possède une condition secrète de défaite, mais pas d'objectif personnel de victoire.

En mode Points et manches, une élimination d'adversaire attribuée au joueur et donnant lieu à un point augmente aussi son compteur personnel d'éliminations créditées pendant la manche. Ce compteur est distinct du score total et des éliminations que le joueur subit. Il n'augmente pas pour l'auto-élimination, pour une élimination causée par la propre pioche de rejeu du joueur, ni pour l'élimination terminale qui met fin à la partie sans vainqueur.

Les éliminations rapportent des points selon les règles de score et les exceptions prévues. Une manche se termine lorsqu'un de ses critères de fin est atteint.

À la fin d'une manche, les jetons sont remis dans le sac commun, les cartes secrètes sont redistribuées et la mise en place complète est répétée. Les scores cumulés sont conservés et les compteurs d'éliminations de la manche sont réinitialisés.

Deux formats de partie sont prévus :

- **C1 — Nombre fixe de manches :** jouer trois manches. Le joueur ayant le plus de points à la fin gagne. En cas d'égalité en tête, une manche supplémentaire est jouée. Si l'égalité persiste après cette manche supplémentaire, les joueurs encore à égalité partagent la victoire.
- **C2 — Seuil de points :** le seuil est choisi avant la partie. Si un joueur atteint ou dépasse ce seuil pendant une manche, celle-ci continue jusqu'à sa fin normale. À la fin de cette manche, si le seuil a été atteint pendant la manche ou grâce au bonus attribué à sa fin, le classement est calculé à partir des scores totaux : le joueur ou les joueurs ayant le score le plus élevé gagnent, et partagent la victoire en cas d'égalité en tête. Un joueur peut donc être dépassé avant la fin de la manche. Si le seuil n'est pas atteint pendant la manche ni par son bonus, une nouvelle manche complète commence. Une égalité terminale sans vainqueur met fin à la partie indépendamment des scores.

Dans le format C2, une égalité terminale sans vainqueur prévaut sur le classement des scores. Les points acquis avant cette résolution sont conservés, mais l'action terminale ne rapporte aucun point ni bonus.

## 11. Paramètres configurables

Les éléments suivants doivent être pilotables dans la configuration du moteur :

- Le mode de jeu.
- La variante de succession A ou B.
- La vérification ou non de la condition de défaite du donneur après retrait du jeton.
- La visibilité du jeton tiré après un refus.
- La visibilité du jeton tiré pour un rejeu en variante A.
- Le nombre de couleurs et la quantité totale de jetons.
- Les seuils et paramètres des conditions de défaite et de victoire.
- Les paramètres de score et d'élimination du mode Points et manches.
- Le format C1 ou C2 et, pour C2, le seuil de points.

Les valeurs encore expérimentales doivent rester modifiables sans réécrire le moteur du jeu.

## 12. Priorités de résolution

La résolution doit distinguer l'action initiale (acceptation, refus suivi d'une pioche, ou acceptation forcée parce que le sac commun est vide) des éliminations distinctes que la succession peut provoquer ensuite. Les étapes suivantes s'appliquent sous réserve de la règle d'arrêt immédiat après une victoire secrète. Cette séquence normative précise l'ordre retenu pour le contrôle du donneur après retrait, afin d'éviter de le confondre avec les vérifications du destinataire après transfert ou pioche.

1. **Après le retrait et avant la décision du destinataire :** si la variante transversale est activée, vérifier la condition de défaite du donneur dans les modes A, B et C. Si le donneur est éliminé, révéler sa carte complète et remettre au sac commun les jetons encore présents dans son sac personnel. Le jeton proposé reste dans son emplacement temporaire ; la proposition continue et le destinataire décide toujours d'accepter ou de refuser. Si la variante est désactivée, ne pas effectuer ce contrôle à cette étape.
2. **Résoudre le cadeau :** si le cadeau est accepté, révéler le jeton et le transférer au destinataire ; si le refus est permis et que le donneur est encore en jeu, remettre le jeton proposé dans son sac personnel puis faire piocher le destinataire dans le sac commun ; si le donneur a déjà été éliminé, ajouter d'abord le jeton proposé au sac commun sans le révéler, puis faire piocher le destinataire au hasard dans le sac commun ainsi augmenté. Le jeton proposé peut lui-même être tiré. Si le sac commun est vide au moment de la décision, le refus est impossible et le jeton est transféré comme lors d'une acceptation.
3. **Après la réception ou la pioche autorisée :** en mode Objectif secret, vérifier d'abord la condition de victoire du destinataire. Si elle est satisfaite, révéler sa carte complète, déclarer sa victoire et arrêter immédiatement la résolution. Sinon, vérifier sa condition de défaite.
4. **Résoudre l'élimination :** chaque joueur ne peut être éliminé qu'une seule fois au cours de la résolution concernée ; révéler immédiatement sa carte secrète complète et remettre au sac commun tous les jetons encore présents dans son sac personnel. Le jeton proposé qui reste en main pendant une proposition en cours est temporaire et n'est pas traité comme un jeton encore dans le sac personnel.
5. **Vérifier l'égalité terminale de l'action initiale :** si cette action élimine directement tous les joueurs encore en jeu, terminer par une égalité sans vainqueur et n'attribuer aucun point ni bonus pour cette action. Sinon, valider les attributions de points qui s'appliquent. Une élimination d'adversaire attribuée au donneur en mode Points et manches rapporte un point et fait progresser son compteur d'éliminations créditées même si le donneur est également éliminé ; son auto-élimination n'accorde aucun point supplémentaire.
6. **Vérifier les fins immédiates :** en mode Points et manches, si le compteur d'éliminations créditées d'un joueur atteint le seuil, la manche se termine et le bonus revient à ce joueur, même s'il a été éliminé pendant cette même résolution, à moins qu'une égalité terminale prioritaire ne soit survenue. Si le seuil n'est pas atteint et qu'il ne reste qu'un joueur, le dernier survivant gagne la partie en mode A/B ou la manche avec son bonus en mode C.
7. **Appliquer la succession :** en variante A, le responsable rejoue s'il est encore en jeu ; les tirages de rejeu sont secrets par défaut et déclenchent d'abord le contrôle de victoire secrète (si autorisé), puis celui de défaite. Une élimination distincte pendant le rejeu ne supprime pas des points déjà acquis lors de l'action initiale. Si le responsable est éliminé, la succession repart après sa position, avec les règles de tirage prévues pour un successeur sans jeton. En variante B, après chaque élimination forcée d'un successeur sans jeton, vérifier dans cet ordre : égalité terminale sans points/bonus pour la dernière élimination, sinon point et progression du compteur, puis seuil de manche, puis victoire du dernier survivant, sinon poursuite de la succession.
8. **Continuer ou terminer :** aucune action normale ne peut commencer après une victoire ou une égalité terminale. Une nouvelle manche ne commence qu'après application complète de la procédure de fin et de remise en place.