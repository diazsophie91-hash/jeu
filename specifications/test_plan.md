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
- Le mode de jeu.
- La variante active.
- Le contenu et la compatibilité des cartes secrètes avec le mode sélectionné.
- La réserve de cartes et sa disponibilité, si la distribution des cartes est gérée par le moteur.
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
- Le joueur peut consulter sa propre carte en privé et le moteur évalue les conditions en interne. Aucun autre joueur n'est informé de cette évaluation ; aucune carte ni condition n'est révélée publiquement.
- La collection invalide ne provoque pas d'élimination et ne modifie pas le statut du joueur.
- Aucun point n'est attribué.
- La préparation ne déclare aucune victoire.

### T04 — Absence de victoire et d'élimination pendant la préparation

Faire en sorte qu'une collection initiale déclenche normalement une condition de défaite ou de victoire.

Vérifier que le joueur peut consulter sa propre carte en privé et que le moteur évalue la condition uniquement pour recommencer le tirage initial. Aucun autre joueur ne doit être informé de l'évaluation ; aucune carte ni condition ne doit être révélée publiquement ; le statut du joueur et le résultat de la partie restent inchangés. Répéter pour une condition de défaite en modes A et C, puis pour une condition de défaite et une condition de victoire en mode B.

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
- Le jeton quitte son emplacement temporaire dans la main du donneur et rejoint le sac personnel du destinataire.
- Le nombre total de jetons reste constant et le jeton ne figure qu'à un seul emplacement.
- En mode Objectif secret, la victoire est vérifiée en premier après réception ; si elle est satisfaite, la carte complète est révélée, la partie s'arrête et aucune vérification ni attribution ultérieure liée à cette action n'a lieu.
- Si aucune victoire immédiate n'a été déclarée, les conditions de défaite du destinataire sont vérifiées.

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
- Le jeton est transféré au destinataire sans retour préalable dans le sac du donneur.
- Aucun tirage de remplacement n'est effectué.
- Le jeton n'est jamais compté simultanément dans deux emplacements.
- La procédure de contrôle du destinataire est exactement celle d'une acceptation normale : en mode Objectif secret, contrôler la victoire en premier, puis la défaite seulement si aucune victoire immédiate n'est déclarée.
- Si le destinataire gagne immédiatement, la résolution s'arrête sans contrôle, attribution ou succession ultérieure.
- Sinon, les éliminations, la règle terminale d'égalité, les points et le compteur de manche sont traités comme pour une acceptation, y compris l'exception où l'action initiale élimine directement tous les joueurs encore en jeu.
- La succession ne démarre qu'après la résolution complète et après vérification des fins immédiates.

### T10 — Annonce facultative du donneur

Tester un cadeau sans message, une annonce spontanée, une question du destinataire et une réponse du donneur. Les messages écrits sont rattachés à l'identifiant de la proposition et ne sont visibles que des participants ; ils ne sont pas des événements publics du moteur.

Vérifier que les stratégies de communication et de décision sont configurées séparément et qu'elles peuvent choisir silence, annonce, question, réponse ou absence de réponse. Une annonce peut être vraie ou mensongère, y compris en réponse à une question ; le moteur ne contrôle pas la véracité du texte.

Vérifier que l'identité réelle du jeton reste cachée à tout agent non autorisé jusqu'à sa révélation prévue par les règles. Aucun message ne modifie l'état, ne devient une commande, ne contourne l'interdiction de refuser lorsque le sac commun est vide, et ne change pas la succession.

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
- Chaque condition de la carte est évaluée lors du déclencheur applicable.
- Le joueur est éliminé une seule fois.
- La carte est révélée une seule fois et tous ses jetons personnels sont rendus une seule fois.
- Le score et le compteur d'éliminations ne reçoivent pas plusieurs crédits pour la même élimination.
- La succession est déterminée une seule fois pour la résolution.
- Les invariants et la conservation des jetons sont respectés.

Répéter pendant la préparation : une collection qui satisfait l'une quelconque de plusieurs conditions invalide le tirage et est redonnée sans élimination, révélation ni attribution de points.

### T16 — Vérification de la condition du donneur après retrait

Comparer les deux configurations — contrôle après retrait activé et désactivé — dans chacun des trois modes A — Dernier survivant, B — Objectif secret et C — Points et manches, avec des états initiaux aussi similaires que possible.

Lorsque l'option est activée, vérifier que la condition est évaluée immédiatement après le retrait et avant la décision du destinataire. Si le donneur est éliminé, sa carte complète est révélée et ses autres jetons encore présents dans son sac rejoignent le sac commun, mais le jeton proposé reste temporaire, la proposition reste en cours et le destinataire peut encore décider.

Lorsque l'option est désactivée, vérifier que cette vérification n'a pas lieu à ce moment. Dans les deux cas, le retrait du jeton ne déclenche pas la condition de victoire personnelle du donneur. Vérifier également que le contrôle de défaite du donneur n'est pas répété plus tard pendant la même résolution.

## 6. Tests des objectifs secrets

### T17 — Déclencheur de victoire autorisé

Créer un objectif secret dont la condition est satisfaite après la réception d'un cadeau accepté.

Vérifier que :
- La carte secrète complète du vainqueur est révélée.
- La victoire est déclarée immédiatement.
- La résolution s'arrête : aucune vérification de défaite, attribution de point, succession ou autre conséquence ultérieure liée à cette action n'est appliquée.
- Aucune nouvelle action normale ne peut commencer.

### T18 — Victoire après un tirage consécutif à un refus

Créer un objectif qui devient satisfait après le tirage du sac commun effectué à la suite d'un refus.

Vérifier que l'objectif est contrôlé après le tirage et, si la condition est satisfaite, que la carte complète est révélée, la victoire est déclarée immédiatement et aucune vérification, attribution de point ou succession ultérieure liée à cette action n'a lieu.

### T19 — Victoire après un tirage nécessaire au rejeu du responsable en variante A

Configurer un objectif secret atteint par le tirage nécessaire au rejeu du responsable en variante A.

Vérifier qu'après ce tirage, en mode Objectif secret, la condition de victoire est contrôlée en premier. Si elle est satisfaite, la carte complète est révélée et la partie s'arrête immédiatement ; sinon, la condition de défaite est contrôlée. Si le joueur survit sans gagner, il joue immédiatement son tour.

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

Vérifier que la carte contradictoire est détectée et signalée comme invalide. Vérifier aussi la compatibilité du type de carte avec le mode : une carte de Dernier survivant ou de Points et manches ne porte pas de condition individuelle de victoire ; une carte ordinaire d'Objectif secret porte une condition de défaite et une condition de victoire. Tester les cartes incomplètes ou contenant des types/couleurs/paramètres inconnus.

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

Activer le contrôle de la condition de défaite du donneur après retrait et faire éliminer le donneur, tout en laissant le destinataire en jeu.

Vérifier que la proposition reste en cours et que le destinataire prend sa décision. Après la résolution complète du cadeau, si le destinataire survit sans gagner, il devient le joueur actif selon la règle établie. Le jeton proposé reste suivi comme emplacement temporaire jusqu'à la résolution.

### T27 — Variante A : rejeu sans jeton personnel

Le responsable qui doit rejouer possède un sac personnel vide et le sac commun contient un jeton.

Vérifier qu'il tire un jeton et l'ajoute à sa collection. En mode Objectif secret, la victoire est vérifiée en premier ; si elle n'est pas obtenue, vérifier la défaite. Si le joueur survit sans gagner, il joue immédiatement son tour. Si sa propre pioche le fait éliminer, sa carte est révélée et aucun autre joueur ne reçoit de point pour cette élimination.

Répéter le scénario avec un sac commun vide. Vérifier que le joueur est éliminé sans pioche, révèle sa carte secrète complète, ne rapporte aucun point à un autre joueur et que la succession continue après sa position.

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

### T55 — Validation de la configuration et du paquet de cartes

Tester les configurations :
- Valides.
- Incomplètes.
- Contradictoires.
- Comportant des seuils ou des paramètres non pris en charge.
- Avec une carte secrète incompatible avec le mode sélectionné.
- Avec une carte dont les conditions victoire/défaite se contredisent.
- Avec une couleur, un type de condition ou un paramètre inconnu.
- Avec trop peu de cartes disponibles pour le nombre de joueurs, lorsque le moteur gère la distribution.
- Avec une réserve de cartes dont la composition ne respecte pas sa configuration, lorsque le moteur gère le paquet.
- Avec un nombre total de jetons inférieur à trois fois le nombre de joueurs.
- Avec une carte attribuée pour laquelle aucune collection valide de trois jetons n'est possible à partir du stock.
- Avec un stock et des cartes ne permettant aucune attribution complète de collections initiales valides à tous les joueurs.

La réserve configurable déclare les familles de conditions de défaite qu'elle contient ; tester exactement deux conditions de chaque famille déclarée, sans supposer un catalogue canonique ni fixer les seuils. Vérifier aussi la suffisance, les identifiants uniques, la compatibilité de mode, les conditions valides et non contradictoires, la distribution reproductible sans doublon et une nouvelle distribution à chaque manche lorsqu'une réserve est configurée. L'injection explicite de cartes de scénario reste prise en charge et contourne uniquement la sélection depuis la réserve.

Le moteur doit signaler clairement une configuration invalide plutôt que d'inventer un comportement. Vérifier aussi qu'une tentative de mise en place qui devient impossible pour un joueur restant s'arrête avec une erreur explicite au lieu de boucler indéfiniment, sans révéler les cartes et sans déclarer victoire ou élimination.

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

Les résultats doivent être enregistrés séparément, avec leur configuration, la stratégie de chaque agent, le numéro de simulation et la graine afin d'éviter de mélanger des règles différentes. Les agents automatisés agissent uniquement par les vues privées, les actions légales et l'API des contrôleurs. Ils peuvent utiliser des stratégies de communication distinctes de leurs stratégies de décision.

Les tests pytest ordinaires utilisent quelques graines fixes et restent rapides. Une campagne paramétrable peut exécuter davantage de graines séparément et rapporter les parties terminées, les vainqueurs/égalités, les tours moyens, les messages par type et les erreurs. Une comparaison de communication ne rapporte que les messages réellement envoyés ; un mode de véracité déclaratif décrit la stratégie configurée et ne constitue pas une validation automatique du texte.

### T64 — Arrêt de la succession B au dernier survivant

Créer une chaîne en variante B où une ou plusieurs éliminations forcées laissent exactement un joueur en jeu, sans que le seuil de manche ait été atteint.

Vérifier que la succession s'arrête immédiatement : le dernier survivant gagne selon le mode. En mode Points et manches, il remporte la manche et reçoit le bonus ; les points valablement crédités pour les éliminations non terminales sont conservés. Aucun autre joueur ne peut être éliminé après cette victoire. L'égalité terminale résultant d'une même résolution qui élimine directement tous les joueurs encore en jeu est couverte par T34 et T65.

### T65 — Action initiale éliminant directement tous les joueurs

Créer un scénario dans lequel l'action initiale élimine directement tous les joueurs encore en jeu.

Vérifier que :
- La partie se termine sur une égalité sans vainqueur.
- Aucun point n'est attribué au titre de cette action.
- Aucun bonus de manche n'est attribué.
- Aucun point n'est annulé ou ajouté rétroactivement.

### T66 — Élimination du donneur avant la décision du destinataire

Activer la variante transversale de vérification de la condition de défaite du donneur après retrait. Exécuter les variantes de mode A, B et C.

Préparer une situation dans laquelle le retrait du jeton déclenche la condition de défaite du donneur.

Vérifier que :
- La condition est contrôlée immédiatement après le retrait et avant la décision du destinataire.
- Le donneur est éliminé une seule fois et révèle sa carte secrète complète.
- Les autres jetons de son sac personnel rejoignent le sac commun.
- Le jeton proposé reste dans l'emplacement temporaire unique et n'est pas remis au sac commun avec les autres jetons.
- La proposition reste en cours et le destinataire peut encore accepter ou refuser.
- L'élimination du donneur n'est pas annulée par un refus.
- Le contrôle n'est pas répété plus tard pendant la même résolution.

### T67 — Acceptation du cadeau après l'élimination du donneur

Reprendre le scénario T66 et faire accepter le cadeau. Vérifier que le jeton temporaire est révélé puis transféré au destinataire, que les conditions applicables sont vérifiées selon leur ordre, que les cartes des joueurs éliminés sont révélées et que la succession n'est déterminée qu'après la résolution complète. Tester les variantes où le destinataire survit, est éliminé, ou gagne immédiatement en mode Objectif secret.

Tester également les points applicables si le destinataire est éliminé pendant cette action, en distinguant l'action initiale qui élimine directement tout le monde d'une chaîne ultérieure en variante B.

### T68 — Variante désactivée

Répéter le scénario avec la vérification de la condition du donneur après retrait désactivée.

Vérifier que cette vérification n'a pas lieu et que le cadeau suit son déroulement normal.

### T69 — Retour des jetons restants au sac commun après élimination

Éliminer un joueur dont le sac personnel contient encore plusieurs jetons.

Vérifier que :
- Sa carte secrète complète est révélée.
- Tous les jetons encore présents dans son sac personnel sont remis dans le sac commun.
- Aucun jeton n'est perdu ni dupliqué.
- Un jeton déjà transféré à un autre joueur ne retourne au sac commun que si ce destinataire est lui aussi éliminé et que le jeton est alors dans son sac personnel.
- Un jeton temporairement conservé dans la main du donneur pour une proposition en cours reste dans l'état temporaire ; il n'est pas traité comme un jeton restant dans son sac personnel.

### T70 — Successeur sans jeton en variante A, sac commun non vide

Après l'élimination du responsable, désigner un successeur vivant dont le sac personnel est vide alors que le sac commun contient au moins un jeton.

Vérifier que le successeur pioche un jeton et l'ajoute à sa collection. Tester les deux options de visibilité prévues. En mode Objectif secret, vérifier d'abord la victoire, puis la défaite si aucune victoire n'est déclarée. S'il survit sans gagner, il joue immédiatement son tour ; s'il est éliminé par sa propre pioche, aucun autre joueur ne reçoit de point et la succession continue après sa position.

### T71 — Successeur sans jeton en variante A, sac commun vide

Après l'élimination du responsable, désigner un successeur vivant dont le sac personnel est vide et le sac commun également vide.

Vérifier que le successeur est éliminé sans pioche, révèle sa carte secrète complète, ne rapporte aucun point à un autre joueur et que la succession continue après sa position, sauf si une fin immédiate s'applique.

### T72 — Succession en variante B après l'auto-élimination du donneur

Activer le contrôle de la condition de défaite du donneur après retrait, faire éliminer le donneur puis laisser le destinataire en jeu.

Vérifier qu'après la résolution du cadeau et en l'absence de fin immédiate, le destinataire devient le joueur actif. Tester séparément le cas où le donneur et le destinataire sont éliminés lors de la même action initiale : si d'autres joueurs restent, la succession repart après la position du destinataire.

### T73 — Priorités après chaque élimination forcée en variante B

Créer une chaîne où les successeurs sans jeton sont éliminés successivement. Tester les branches atteignables :
- Une élimination forcée non terminale fait atteindre le seuil de manche : la manche s'arrête avant une nouvelle étape de succession.
- Le seuil n'est pas atteint et un seul joueur reste : le dernier survivant gagne selon le mode, avec bonus de manche en mode Points et manches.
- La chaîne continue lorsqu'aucune de ces conditions de fin n'est satisfaite.

La succession traite une élimination forcée à la fois et s'arrête dès qu'un seul joueur reste. Une élimination forcée ultérieure laissant zéro survivant est donc inaccessible ; ne pas la simuler en construisant un état privé artificiel. L'égalité terminale initiale, ses points antérieurs conservés et l'absence de crédit pour l'action terminale sont vérifiés séparément par T34/T65 et leurs tests de score.

### T74 — Égalité au score maximal à la fin normale de C2

Faire atteindre le seuil de points pendant une manche ou grâce à son bonus, puis terminer cette manche avec plusieurs joueurs à égalité au score total le plus élevé.

Vérifier que ces joueurs partagent la victoire. Ne pas confondre ce résultat avec une égalité terminale sans vainqueur causée par l'élimination de tous les joueurs.

### T75 — Compteur d'éliminations créditées en mode Points et manches

Vérifier que le compteur augmente exactement lorsqu'une élimination d'adversaire est attribuée et rapporte un point, y compris si le responsable est éliminé lors de la même action ou pendant une chaîne B non terminale.

Vérifier qu'il n'augmente pas pour l'auto-élimination, pour l'élimination causée par la propre pioche de rejeu du joueur, ni pour la dernière élimination qui produit une égalité terminale. Vérifier que l'action initiale qui élimine directement tous les joueurs ne rapporte ni point ni incrément de compteur.

### T76 — Confidentialité des informations sur le sac commun

Préparer une situation où le destinataire connaît les couleurs ou types susceptibles de se trouver dans le sac commun, sans en connaître la composition exacte restante.

Vérifier que le moteur et l'interface n'exposent pas la composition exacte. Ne pas étendre aux autres joueurs la connaissance explicitement attribuée au destinataire, sauf règle supplémentaire validée.

### T77 — Priorité entre l'auto-élimination du donneur et la victoire secrète du destinataire

En mode Objectif secret, activer le contrôle de défaite du donneur après retrait. Configurer le don de façon que le retrait élimine le donneur et que l'acceptation du cadeau satisfasse ensuite la condition de victoire du destinataire.

Vérifier que :
- Le donneur est éliminé avant la décision, sa carte est révélée et ses jetons personnels restants rejoignent le sac commun.
- Le jeton proposé reste disponible dans la proposition et peut être accepté.
- Après transfert, la condition de victoire du destinataire est contrôlée en premier parmi les conditions du destinataire.
- La victoire du destinataire révèle toute sa carte et arrête immédiatement la résolution ; aucune vérification, attribution de point ni succession ultérieure n'est appliquée après ce déclencheur de victoire.
- L'élimination du donneur déjà résolue n'est pas annulée rétroactivement.

Répéter avec la variante de contrôle du donneur désactivée : le contrôle lié au retrait ne doit pas être effectué, mais la victoire autorisée du destinataire doit toujours fonctionner.

### T78 — Configuration d'essai de référence non définitive

Configurer quatre couleurs, au maximum huit joueurs et quarante jetons au total. Avec huit joueurs, vérifier que vingt-quatre jetons sont distribués lors de la mise en place initiale et que les jetons restants demeurent dans le sac commun.

Vérifier que ces valeurs proviennent de la configuration du scénario, ne sont pas codées en dur comme valeurs obligatoires et ne sont jamais présentées comme des paramètres définitifs. Répéter avec d'autres configurations valides.

### T79 — Départage du premier joueur

Tester les deux méthodes prévues : choix collectif fourni explicitement et personne ayant reçu un cadeau réel le plus récemment à partir des données de récence fournies.

Lorsque plusieurs personnes sont à égalité sur le critère de récence, vérifier que la sélection exige une décision explicite ou un mécanisme de consensus configuré et ne choisit pas silencieusement un joueur. Vérifier la participation de l'identifiant choisi, la trace de la méthode et sa transmission à la mise en place du moteur. L'API actuelle acceptant directement `first_player_id` reste compatible.

### T80 — Victoire après le tirage d’un successeur sans jeton en variante A

Éliminer le responsable du rejeu de la variante A afin que la succession désigne un joueur encore en jeu dont le sac personnel est vide, tandis que le sac commun contient au moins un jeton. Configurer son objectif secret pour que le jeton tiré satisfasse sa condition de victoire.

Vérifier que le successeur tire un jeton, que le moteur contrôle d’abord sa condition de victoire, qu’en cas de victoire sa carte complète est révélée et que la partie s’arrête immédiatement sans contrôle de défaite ni action ultérieure. Vérifier également que cette victoire n’est pas contrôlée avant le tirage et que, si aucune victoire n’est satisfaite, la condition de défaite est contrôlée ensuite.

### T81 — Refus après élimination préalable du donneur

Reprendre le scénario T66 avec un donneur déjà éliminé avant la décision et un sac commun contenant au moins un jeton au moment où le destinataire refuse. Prévoir dans le sac commun au moins un jeton identifiable distinct du jeton proposé. Contrôler le générateur aléatoire pour exécuter séparément les deux résultats possibles :
- **Sous-cas A — le cadeau est repioché :** après l'ajout du jeton proposé au sac commun, forcer le tirage de ce même jeton ;
- **Sous-cas B — un autre jeton est pioché :** après l'ajout du jeton proposé au sac commun, forcer le tirage du jeton distinct déjà présent.

Vérifier dans les deux sous-cas que :
- Le jeton proposé reste temporaire jusqu'à la décision, puis est ajouté au sac commun sans être révélé avant le tirage.
- Le jeton proposé est ajouté au sac commun avant le tirage du destinataire ; le tirage est effectué dans ce sac augmenté.
- Le jeton sélectionné quitte le sac commun et rejoint le sac personnel du destinataire ; tous les autres jetons restent à leur emplacement attendu, sans perte ni duplication.
- Le moteur conserve l'identité interne du jeton et ne révèle sa couleur aux joueurs que si le résultat est tiré et que la variante de visibilité prévoit cette révélation. En mode secret, seul le destinataire peut connaître le jeton tiré.
- En mode Objectif secret, la condition de victoire du destinataire est vérifiée en premier après la pioche ; si elle n'est pas satisfaite, sa condition de défaite est contrôlée.
- En mode Points et manches, si la pioche élimine le destinataire, appliquer l'attribution du point au donneur initial selon la règle de score, même si celui-ci est déjà éliminé, sauf si l'action initiale élimine directement tous les joueurs encore en jeu.
- La succession n'est déterminée qu'après la résolution complète, sous réserve d'une fin immédiate.


### T82 — Validation de la mise en place et confidentialité des cartes

Tester les configurations de départ suivantes :
- Le sac contient moins de trois jetons par joueur.
- Une carte assignée n'admet aucune collection valide de trois jetons dans le stock configuré.
- Chaque carte admet individuellement une collection valide, mais aucune attribution complète de collections valides n'est possible pour tous les joueurs avec le stock disponible.
- La configuration est valide et permet une mise en place complète.

Vérifier que les configurations impossibles sont rejetées avec un diagnostic explicite avant le début du jeu. Pour une mise en place valide, faire tirer à un joueur une collection qui satisfait une condition de défaite ou, en mode Objectif secret, une condition de victoire.

Vérifier que les trois jetons sont remis dans le sac commun et que trois nouveaux jetons sont tirés, sans révéler la carte ni les conditions, sans éliminer le joueur, sans déclarer de victoire et sans attribuer de point. Vérifier qu'une tentative de mise en place devenue impossible s'arrête proprement au lieu de boucler indéfiniment, sans produire de révélation publique.


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
