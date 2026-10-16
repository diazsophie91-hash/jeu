# Plan de tests — C'est cadeau !

## 1. Objectif

Ce document définit les tests nécessaires pour vérifier le fonctionnement de C'est cadeau ! avant de réaliser des simulations massives.

Les tests doivent vérifier que le moteur applique correctement les règles définies dans :
- `game_flow.md`
- `game_state.md`
- `rules_spec.md`

Les tests doivent détecter les erreurs de logique, les états impossibles, les erreurs de succession des joueurs et les erreurs de score.

Ce document décrit les tests à réaliser. Il ne signifie pas que ces tests ont déjà été exécutés ni que le jeu a été équilibré par simulation.

## 2. Principes de test

### 2.1. Tests indépendants

Chaque test doit vérifier un comportement précis autant que possible.

Lorsqu'un test échoue, le message d'erreur doit indiquer :
- Le comportement attendu.
- Le comportement obtenu.
- Les paramètres et l'état initial pertinents.

### 2.2. Configurations contrôlées

Les tests ne doivent pas dépendre uniquement de tirages aléatoires.

Pour vérifier une règle, le test doit pouvoir définir directement :
- Les joueurs en jeu.
- Le contenu de leurs sacs.
- Le contenu du sac commun.
- Les cartes secrètes.
- La variante active.
- Le mode de jeu.
- Les scores et compteurs initiaux.
- Le résultat attendu.

Le moteur peut utiliser des tirages aléatoires en production. Dans les tests, les tirages doivent pouvoir être contrôlés ou reproduits.

Les seuils expérimentaux doivent être configurés explicitement pour chaque scénario.

### 2.3. Tests des variantes

Une fonctionnalité configurable doit être testée dans chacune de ses configurations pertinentes.

Les tests ne doivent pas supposer que la variante choisie par défaut est la seule configuration valide.

## 3. Tests de préparation

### T01 — Distribution initiale

Préparer une partie avec plusieurs joueurs et une configuration connue du sac commun.

Vérifier que :
- Chaque joueur reçoit trois jetons.
- Les jetons sont retirés du sac commun.
- Aucun jeton n'est créé ou perdu.
- Chaque jeton appartient à un seul emplacement.

### T02 — Vérification des collections initiales

Préparer une collection initiale qui ne satisfait aucune condition de défaite ni de victoire.

Vérifier que le joueur conserve sa collection et que la préparation continue normalement.

### T03 — Nouvelle tentative après une collection invalide

Préparer un scénario dans lequel la première collection tirée satisfait une condition de défaite ou, en mode Objectif secret, une condition de victoire.

Vérifier que :
- Les trois jetons sont remis dans le sac commun.
- Une nouvelle collection de trois jetons est tirée.
- La collection invalide ne provoque pas d'élimination.
- Aucun point n'est attribué.
- La préparation ne déclare aucune victoire.

### T04 — Absence de victoire et d'élimination pendant la préparation

Faire en sorte qu'une collection initiale déclenche normalement une condition de défaite ou de victoire.

Vérifier que cette condition sert uniquement à recommencer le tirage initial et ne modifie pas le statut du joueur.

### T05 — Conservation du nombre total de jetons

Vérifier, après plusieurs tirages initiaux et nouvelles tentatives, que chaque jeton existe toujours et possède un seul emplacement valide.

### T06 — Reproductibilité d'un tirage

Lancer deux fois le même scénario avec la même configuration et la même graine aléatoire.

Vérifier que les résultats sont identiques lorsque le moteur utilise un générateur aléatoire reproductible.

## 4. Tests des cadeaux

### T07 — Acceptation d'un cadeau

Le destinataire accepte un cadeau.

Vérifier que :
- Le jeton est révélé conformément aux règles.
- Le jeton quitte le donneur.
- Le jeton rejoint le destinataire.
- Le nombre total de jetons reste constant.
- Les conditions applicables au destinataire sont vérifiées.

### T08 — Refus d'un cadeau lorsque le sac commun n'est pas vide

Le destinataire refuse un cadeau alors que le sac commun contient au moins un jeton.

Vérifier que :
- Le jeton proposé n'est pas révélé.
- Le jeton proposé retourne dans le sac du donneur.
- Un jeton est tiré du sac commun.
- Le jeton tiré rejoint le sac du destinataire.
- Les conditions applicables au destinataire sont vérifiées après le tirage.

Tester séparément les variantes où le jeton tiré est révélé et où il reste secret.

### T09 — Refus impossible lorsque le sac commun est vide

Le destinataire tente de refuser un cadeau alors que le sac commun est vide.

Vérifier que :
- Le refus est impossible.
- Le jeton proposé est révélé.
- Le jeton est transféré au destinataire.
- Aucun tirage de remplacement n'est effectué.
- Le jeton n'est jamais compté simultanément dans deux emplacements.

### T10 — Annonce facultative du donneur

Tester un cadeau sans annonce, un cadeau avec une annonce spontanée et un cadeau accompagné d'une réponse à une question.

Vérifier qu'une annonce n'est jamais obligatoire et qu'elle ne modifie pas les règles de transfert ou de vérification des conditions.

Une annonce mensongère ne doit pas modifier l'identité réelle du jeton enregistrée par le moteur.

### T11 — Choix d'un destinataire valide

Vérifier qu'un joueur peut choisir un autre joueur encore en jeu, mais ne peut pas choisir :
- Lui-même.
- Un joueur déjà éliminé.

Le moteur doit refuser toute action normale invalide sans corrompre l'état de la partie.

## 5. Tests des conditions de défaite

### T12 — Condition liée à une couleur

Configurer une condition de défaite déclenchée par un seuil précis de jetons d'une couleur.

Vérifier le comportement :
- Juste en dessous du seuil.
- Au seuil.
- Au-dessus du seuil, selon la variante configurée.

### T13 — Condition des deux paires

Tester les variantes de la condition des deux paires :
- Toute combinaison de deux couleurs ou couleurs imposées.
- Quantités exactes ou quantités minimales.

Vérifier que chaque configuration produit le résultat attendu, sans mélanger les interprétations.

### T14 — Condition liée au nombre total de jetons

Configurer un seuil total.

Vérifier que le moteur compte les jetons de toutes les couleurs et applique le seuil sélectionné.

### T15 — Plusieurs conditions de défaite simultanées

Créer une collection qui satisfait deux conditions de défaite ou davantage.

Vérifier que :
- Le joueur est éliminé une seule fois.
- La révélation de la carte secrète n'est pas répétée inutilement.
- Le score ne reçoit pas plusieurs points pour la même élimination.
- La succession est déterminée une seule fois pour la résolution.

### T16 — Vérification de la condition du donneur après retrait

Exécuter le même scénario avec les deux configurations :
- Vérification de la condition de défaite après retrait : activée.
- Vérification de la condition de défaite après retrait : désactivée.

Vérifier que le moteur applique exactement la configuration sélectionnée.

Dans les deux cas, le retrait du jeton par le donneur ne peut pas déclencher sa condition de victoire personnelle.

### T66 — Élimination du donneur avant la décision du destinataire

Activer la variante de vérification de la condition de défaite du donneur après retrait.

Préparer une situation dans laquelle le retrait du jeton déclenche sa condition de défaite.

Vérifier que :
- La condition est vérifiée avant la décision du destinataire.
- Le donneur est éliminé et révèle sa carte secrète complète.
- La proposition de cadeau reste en cours.
- Le destinataire peut encore accepter ou refuser.
- L'élimination du donneur n'est pas annulée par un refus.

### T67 — Résolution du cadeau après l'élimination du donneur

Reprendre le scénario T66 et tester séparément l'acceptation et le refus.

Vérifier que le cadeau est résolu selon les règles normales, que les jetons ne sont ni perdus ni dupliqués et que le joueur actif suivant est déterminé uniquement après la résolution complète.

Vérifier également les règles de points applicables si le destinataire est éliminé pendant cette même résolution.

### T68 — Variante désactivée

Répéter le scénario avec la vérification de la condition du donneur après retrait désactivée.

Vérifier que cette vérification n'a pas lieu et que le cadeau suit son déroulement normal.

## 6. Tests des objectifs secrets

### T17 — Déclencheur de victoire autorisé

Créer un objectif secret dont la condition est satisfaite après la réception d'un cadeau accepté.

Vérifier que :
- La carte secrète complète du vainqueur est révélée.
- La victoire est déclarée.
- La partie s'arrête immédiatement.
- Aucune nouvelle action normale ne peut commencer.

### T18 — Victoire après un tirage consécutif à un refus

Créer un objectif qui devient satisfait après le tirage du sac commun effectué à la suite d'un refus.

Vérifier que l'objectif est contrôlé après le tirage et que la victoire est correctement déclarée si la condition est satisfaite.

### T19 — Victoire après un tirage nécessaire au rejeu en variante A

Configurer un objectif secret atteint par un tirage nécessaire au rejeu.

Vérifier que les conditions applicables sont contrôlées après ce tirage, conformément à la règle retenue pour la variante A.

### T20 — Absence de déclenchement au retrait d'un jeton

Créer une situation dans laquelle le donneur satisfait sa condition de victoire uniquement parce qu'un jeton vient de quitter son sac.

Vérifier que sa victoire n'est pas déclarée à ce moment-là.

### T21 — Dernier survivant en mode Objectif secret

Faire éliminer tous les joueurs sauf un, sans qu'aucun objectif personnel n'ait été satisfait.

Vérifier que le dernier joueur en jeu gagne conformément aux règles du mode.

### T22 — Contrôle de compatibilité des cartes

Tester des cartes dont les conditions de victoire et de défaite :
- Sont compatibles.
- Peuvent être satisfaites simultanément par une même collection.

Vérifier que la carte contradictoire est détectée et signalée comme invalide.

Le système doit aussi permettre de tester les familles d'objectifs dont les seuils restent expérimentaux, sans inventer leurs paramètres.

## 7. Tests des éliminations et de la succession

### T23 — Révélation après une élimination

Éliminer un joueur au cours d'une action.

Vérifier que sa carte secrète complète est révélée et que son statut passe à éliminé.

### T24 — Succession sans élimination

Réaliser une action sans élimination ni victoire immédiate.

Vérifier que le destinataire devient le joueur actif suivant.

### T25 — Variante A : rejeu du responsable

Déclencher une élimination dont le responsable est encore en jeu.

Vérifier que ce joueur doit rejouer immédiatement.

### T26 — Variante A : donneur éliminé, destinataire survivant

Déclencher l'élimination du donneur après le retrait d'un jeton, tout en laissant le destinataire en jeu.

Vérifier que le destinataire devient le joueur actif.

### T27 — Variante A : rejeu sans jeton personnel

Le joueur qui doit rejouer possède un sac personnel vide et le sac commun contient un jeton.

Vérifier qu'il tire un jeton, puis que les conditions applicables sont contrôlées.

Répéter le scénario avec un sac commun vide.

Vérifier que le joueur est alors éliminé, révèle sa carte secrète complète et que la succession continue.

### T28 — Variante A : visibilité du tirage de rejeu

Tester les deux options de visibilité du jeton tiré pour le rejeu.

Vérifier que seule la visibilité change et que l'identité du jeton et les règles de résolution restent correctes.

### T29 — Variante A : élimination après tirage de rejeu

Faire en sorte que le jeton tiré pour le rejeu entraîne une élimination.

Vérifier que :
- Le joueur est éliminé.
- Sa carte secrète est révélée.
- La succession reprend conformément aux règles.
- Aucun point n'est attribué pour cette élimination en mode Points et manches.

### T30 — Variante B : succession horaire

Déclencher une élimination.

Vérifier que le prochain joueur actif est déterminé dans le sens horaire depuis la position du joueur éliminé, en ignorant les joueurs éliminés.

### T31 — Variante B : sac personnel vide

La succession sélectionne un joueur encore en jeu dont le sac personnel est vide.

Vérifier que :
- Ce joueur est éliminé.
- Sa carte secrète complète est révélée.
- La succession continue depuis sa position.
- Les joueurs déjà éliminés sont ignorés.

### T32 — Élimination simultanée du donneur et du destinataire

Créer une résolution qui élimine le donneur et le destinataire.

Vérifier que :
- Les deux éliminations sont enregistrées.
- Les deux cartes secrètes sont révélées.
- La succession commence depuis la position du destinataire, conformément aux règles communes.
- Aucun joueur éliminé n'est sélectionné ensuite.

Tester les variantes A et B lorsque leur règle spécifique s'applique.

### T33 — Éliminations multiples au cours d'une même résolution

Créer une résolution impliquant plusieurs joueurs éliminés.

Vérifier que toutes les éliminations sont traitées avant la désignation du prochain joueur actif et qu'un joueur éliminé n'est compté qu'une fois.

### T34 — Égalité terminale sans vainqueur

Créer un scénario dans lequel tous les joueurs encore en jeu sont éliminés par la même résolution.

Vérifier que :
- La partie se termine.
- Le résultat est enregistré comme égalité sans vainqueur.
- Aucun nouveau joueur actif n'est désigné.
- Aucun tour supplémentaire ne peut être joué.
- Aucun point ni bonus n'est attribué pour l'action terminale.

## 8. Tests de score en mode Points et manches

### T35 — Élimination du destinataire après acceptation

Éliminer le destinataire après un cadeau accepté.

Vérifier que le donneur reçoit un point lorsque les exceptions terminales ne s'appliquent pas.

### T36 — Élimination du destinataire après refus

Éliminer le destinataire après le tirage consécutif à un refus.

Vérifier que le donneur reçoit un point lorsque les exceptions terminales ne s'appliquent pas.

### T37 — Auto-élimination du donneur

Éliminer le donneur à cause de sa propre condition après le retrait du jeton.

Vérifier qu'aucun point ne lui est attribué pour sa propre élimination.

### T38 — Donneur et destinataire éliminés par la même action

Créer une résolution où le donneur et le destinataire sont éliminés, mais où d'autres joueurs survivent.

Vérifier que le point dû pour l'élimination du destinataire est attribué même si le donneur est également éliminé, conformément aux règles.

Répéter avec une résolution qui élimine tous les joueurs restants.

Vérifier que l'égalité terminale ne rapporte aucun point ni bonus pour l'action terminale.

### T39 — Chaîne d'éliminations forcées en variante B

Créer une chaîne dans laquelle plusieurs joueurs au sac vide sont éliminés successivement.

Vérifier que chaque élimination est attribuée au joueur responsable de l'action initiale et rapporte le point prévu si la chaîne ne se termine pas sur une égalité terminale.

### T40 — Bonus de manche après atteinte du seuil d'éliminations

Configurer un seuil d'éliminations pour remporter la manche.

Vérifier que le vainqueur reçoit le bonus d'un point même s'il est éliminé au cours de la même action qui lui permet d'atteindre le seuil.

Répéter avec une résolution qui élimine tous les joueurs restants. Dans ce cas, aucun bonus n'est attribué.

### T41 — Bonus au dernier survivant

Faire gagner un joueur en tant que dernier survivant avant qu'il n'atteigne le seuil d'éliminations.

Vérifier que le bonus de manche prévu est attribué.

## 9. Tests du mode Points et manches : C1 et C2

### T42 — Réinitialisation entre les manches

Terminer une manche puis commencer la suivante.

Vérifier que :
- Tous les jetons retournent dans le sac commun.
- Les cartes secrètes sont redistribuées.
- Chaque joueur reçoit trois jetons.
- Les collections initiales sont vérifiées.
- Les compteurs d'élimination sont réinitialisés.
- Les scores totaux sont conservés.

### T43 — Format C1 : trois manches

Simuler une partie C1 jusqu'à la fin de la troisième manche.

Vérifier que le classement final utilise les scores cumulés des trois manches.

### T44 — Format C1 : égalité en tête

Terminer la troisième manche avec plusieurs joueurs à égalité en tête.

Vérifier qu'une manche supplémentaire est lancée.

Après cette manche :
- Si un joueur a le score le plus élevé, il gagne.
- Si plusieurs joueurs sont encore à égalité en tête, ils partagent la victoire.

Vérifier qu'un joueur qui n'était pas dans le groupe initial de tête peut dépasser les autres durant la manche supplémentaire.

### T45 — Format C2 : seuil atteint en cours de manche

Faire atteindre le seuil à un joueur avant la fin de la manche.

Vérifier que la manche continue normalement jusqu'à sa fin.

### T46 — Format C2 : seuil non atteint

Terminer une manche sans qu'aucun joueur n'atteigne le seuil, y compris après le bonus de manche.

Vérifier qu'une nouvelle manche commence.

### T47 — Format C2 : dépassement du joueur ayant atteint le seuil

Faire atteindre le seuil à un joueur, puis permettre à un autre joueur de le dépasser avant la fin de la manche.

Vérifier que le classement final est déterminé par les scores totaux à la fin de la manche et non par l'ordre dans lequel le seuil a été franchi.

### T48 — Format C2 : seuil franchi par le bonus de manche

Faire en sorte qu'aucun joueur n'atteigne le seuil pendant les actions de la manche, mais que l'attribution du bonus de manche fasse franchir le seuil.

Vérifier que la partie se termine à la fin de cette manche et que le classement final est établi après le bonus.

### T49 — Format C2 : égalité terminale

Déclencher une égalité terminale sans vainqueur.

Vérifier qu'elle met fin à la partie indépendamment du classement des scores.

Les scores acquis avant la résolution sont conservés, mais l'action terminale n'accorde aucun point ni bonus.

## 10. Tests des invariants de l'état

### T50 — Unicité de l'emplacement des jetons

Après chaque action testée, vérifier que chaque jeton est présent à un seul emplacement valide.

### T51 — Conservation du nombre de jetons

Comparer le nombre total de jetons avant et après chaque action.

Les transferts, refus, tirages et éliminations ne doivent pas créer ni supprimer de jetons.

### T52 — Joueurs éliminés

Vérifier qu'un joueur éliminé :
- Ne peut pas être choisi pour un cadeau.
- Ne peut pas effectuer d'action normale.
- Ne devient jamais joueur actif.
- Ne peut pas être éliminé une deuxième fois dans la même résolution.

### T53 — État final

Après une victoire ou une égalité terminale, tenter de réaliser une action supplémentaire.

Vérifier que le moteur refuse l'action et conserve le résultat final.

### T54 — Historique des événements

Vérifier que les événements sont enregistrés dans l'ordre de résolution et que les informations secrètes ne sont pas automatiquement exposées dans l'affichage public.

### T55 — Validation de la configuration

Tester les configurations :
- Valides.
- Incomplètes.
- Contradictoires.
- Comportant des seuils ou des paramètres non pris en charge.

Le moteur doit signaler clairement une configuration invalide plutôt que d'inventer un comportement.

## 11. Tests de robustesse

### T56 — Joueurs déjà éliminés dans la succession

Créer une situation où plusieurs positions successives autour de la table correspondent à des joueurs éliminés.

Vérifier que la succession les ignore sans boucle infinie.

### T57 — Sac commun et sacs personnels vides

Tester les combinaisons suivantes :
- Sac commun vide et sac personnel non vide.
- Sac commun non vide et sac personnel vide.
- Sac commun vide et sac personnel vide.
- Aucun joueur encore en jeu.

Vérifier que chaque situation est résolue selon les règles et sans état impossible.

### T58 — Actions invalides

Tenter des actions impossibles, par exemple choisir un destinataire éliminé ou résoudre deux fois la même action.

Vérifier que le moteur refuse l'action sans corrompre l'état de la partie.

### T59 — Absence de boucle infinie

Tester notamment :
- Les nouvelles tentatives de préparation.
- Les chaînes d'éliminations.
- La succession lorsqu'il reste très peu de joueurs.
- La fin de partie lorsque tous les joueurs sont éliminés.

Le moteur doit toujours pouvoir terminer la résolution ou signaler explicitement une configuration invalide.

## 12. Tests de simulation

Ces tests ne remplacent pas les tests unitaires. Ils servent à vérifier que des parties complètes peuvent se dérouler sans erreur.

### T60 — Partie complète en mode Dernier survivant

Simuler plusieurs parties avec plusieurs nombres de joueurs et différentes configurations valides.

Vérifier que chaque partie se termine par une victoire ou une égalité terminale, sans état impossible.

### T61 — Partie complète en mode Objectif secret

Simuler plusieurs parties avec les objectifs activés.

Vérifier que les objectifs ne sont évalués que lors des événements autorisés et que les victoires immédiates arrêtent bien la partie.

### T62 — Partie complète en mode Points et manches

Simuler des parties C1 et C2.

Vérifier que les manches, scores, bonus, réinitialisations et critères de fin sont cohérents.

### T63 — Comparaison des variantes

Comparer les résultats des variantes :
- Succession A et succession B.
- Vérification de la condition du donneur activée ou désactivée.
- Tirage après refus visible ou secret.
- Tirage de rejeu visible ou secret.
- Variantes de conditions de défaite.

Les résultats doivent être enregistrés séparément, avec leur configuration, afin d'éviter de mélanger des règles différentes.

## 13. Exigences de sortie des tests

Le système de tests doit permettre d'identifier :
- Le nombre de tests exécutés.
- Le nombre de tests réussis et échoués.
- Les raisons des échecs.
- La configuration utilisée.
- Les scénarios qui n'ont pas encore été testés.

Il ne faut pas annoncer que le moteur est validé si certains tests critiques échouent ou n'ont pas été exécutés.

Les résultats de tests unitaires doivent être distingués des résultats de simulation et des conclusions d'équilibrage.

## 14. Ordre de réalisation recommandé

Les tests doivent être développés progressivement :

1. Préparation et invariants des jetons.
2. Acceptation et refus des cadeaux.
3. Conditions de défaite.
4. Éliminations et succession.
5. Attribution des points.
6. Objectifs secrets.
7. Fin des manches et réinitialisations.
8. Options et variantes.
9. Simulations de parties complètes.
10. Analyse de l'équilibrage.

Les fonctionnalités expérimentales doivent être testables par configuration sans modifier les règles déjà stabilisées.

## 15. Critères avant les simulations massives

Avant de lancer des simulations massives, vérifier que :

- Les tests de préparation passent.
- Les transferts et tirages conservent tous les jetons.
- Les conditions de défaite sont évaluées correctement.
- Les objectifs secrets respectent leurs déclencheurs.
- Les deux variantes de succession sont couvertes.
- Les cas de sac commun vide sont couverts.
- Les éliminations simultanées et les chaînes sont résolues correctement.
- Les règles de score et de bonus sont testées.
- Les transitions entre manches sont correctes.
- Les parties complètes terminent sans état impossible.
- Les configurations et les graines aléatoires peuvent être enregistrées pour reproduire les résultats.

L'équilibrage du jeu devra ensuite être étudié séparément à partir de simulations suffisamment nombreuses et de statistiques explicites.

### T64 — Égalité terminale après une chaîne d'éliminations

Créer un scénario dans lequel une action initiale provoque plusieurs éliminations, puis une chaîne d'éliminations forcées qui se termine par une égalité terminale.

Vérifier que :
- Les points valablement attribués avant la dernière élimination sont conservés.
- La dernière élimination ne rapporte aucun point.
- Aucun bonus de manche n'est attribué.
- La partie se termine sans vainqueur.

### T65 — Action initiale éliminant directement tous les joueurs

Créer un scénario dans lequel l'action initiale élimine directement tous les joueurs encore en jeu.

Vérifier que :
- La partie se termine sur une égalité sans vainqueur.
- Aucun point n'est attribué au titre de cette action.
- Aucun bonus de manche n'est attribué.
- Aucun point n'est annulé ou ajouté rétroactivement.