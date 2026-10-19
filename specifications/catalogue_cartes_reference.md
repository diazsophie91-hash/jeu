# Catalogue de cartes de référence — « C’est cadeau ! »

## 1. Statut, portée et conventions

**Statut :** spécification de conception validée pour préparer l’implémentation et les tests. Elle formalise les décisions du catalogue retenues pour cette conception. Ce n’est ni une affirmation que les seuils sont équilibrés, ni une description de ce que le moteur sait déjà exécuter.

Le catalogue comprend **deux paquets physiques/configurations distincts de 24 cartes** : Paquet A/C, employé en mode A ou C, et Paquet B, employé en mode B. Ils ne sont jamais mélangés pour constituer un paquet de 48 cartes. Les mêmes identifiants de défaite peuvent apparaître dans les deux paquets : ils y désignent les mêmes variantes de défaite, mais l’association de victoire n’existe que dans le paquet B. Les identifiants sont uniques à l’intérieur de chaque paquet.

Conventions :

- `CD` = couleur dangereuse ; `DP` = deux paires ; `ACC` = accumulation ; `4C` = quatre couleurs.
- Les seuils formulés « au moins » sont inclusifs. Les couleurs non citées restent autorisées, sauf indication contraire.
- Chaque variante de défaite existe en deux exemplaires physiques, suffixés `-01` et `-02`. Les deux exemplaires d’une variante B portent la même association de victoire et de défaite.
- Les conditions sont vérifiées aux moments autorisés par les règles, et non à chaque mutation interne de collection. Une collection invalide pendant la mise en place est repiochée ; cette vérification ne produit pas une élimination réelle.
- En B, la victoire ordinaire de carte est vérifiée aux événements autorisés par le règlement (réception d’un cadeau, pioche après refus et pioches de succession A précisées en §6.2). Le retrait seul d’un jeton par le donneur n’est pas un déclencheur de victoire. Les autres contrôles de défaite suivent les moments de contrôle prescrits par la règle et la variante sélectionnée.

## 2. Configuration générale de référence

| Paramètre | Décision retenue | Note de conformité |
|---|---|---|
| Joueurs | 4 à 8 ; cible d’équilibrage : 6 | Le moteur valide actuellement au moins 2 joueurs ; la CLI du benchmark intégré est bornée à 2–4. La plage 4–8 n’est donc pas actuellement couverte par le benchmark intégré. |
| Sac commun | 52 jetons : 13 rouges, 13 bleus, 13 jaunes, 13 verts | Remplace l’hypothèse v67 de quatre couleurs / 40 jetons. |
| Collection initiale | 3 jetons par joueur | Conforme à la mise en place v67 et au défaut `initial_hand_size=3`. Huit joueurs prennent 24 jetons initiaux ; il en reste 28 dans le sac avant les contrôles/repioche. |
| Attribution des cartes | Une carte compatible avec le mode par joueur ; nouveau tirage de cartes à chaque nouvelle manche | Le moteur redonne des cartes à chaque manche si la réserve est fournie, mais le catalogue de 24 doit d’abord être représentable par le mécanisme de réserve actuel (voir §8). |
| Contrôles de collection | Aux événements de règles seulement ; aucune victoire ni élimination réelle pendant la mise en place | La mise en place v67 invalide et repioche une collection initiale qui remplit une condition pertinente. |

La cible à six joueurs est une cible de conception pour l’équilibrage, pas une valeur déduite du défaut du moteur ni du benchmark. Les seuils de cartes ci-dessous sont retenus pour établir la base de référence ; ils restent à mesurer et ne sont pas déclarés équilibrés.

## 3. Catalogue physique Paquet A/C — défaite uniquement

Paquet destiné aux modes A « Dernier survivant » et C « Points et manches ». Chaque ligne représente une carte physique.

| Identifiant | Variante | Condition de défaite |
|---|---|---|
| CD-R-01 | CD-R | Au moins 3 rouges |
| CD-R-02 | CD-R | Au moins 3 rouges |
| CD-B-01 | CD-B | Au moins 3 bleus |
| CD-B-02 | CD-B | Au moins 3 bleus |
| CD-J-01 | CD-J | Au moins 3 jaunes |
| CD-J-02 | CD-J | Au moins 3 jaunes |
| CD-V-01 | CD-V | Au moins 3 verts |
| CD-V-02 | CD-V | Au moins 3 verts |
| DP-RB-01 | DP-RB | Au moins 2 rouges **et** au moins 2 bleus |
| DP-RB-02 | DP-RB | Au moins 2 rouges **et** au moins 2 bleus |
| DP-RJ-01 | DP-RJ | Au moins 2 rouges **et** au moins 2 jaunes |
| DP-RJ-02 | DP-RJ | Au moins 2 rouges **et** au moins 2 jaunes |
| DP-RV-01 | DP-RV | Au moins 2 rouges **et** au moins 2 verts |
| DP-RV-02 | DP-RV | Au moins 2 rouges **et** au moins 2 verts |
| DP-BJ-01 | DP-BJ | Au moins 2 bleus **et** au moins 2 jaunes |
| DP-BJ-02 | DP-BJ | Au moins 2 bleus **et** au moins 2 jaunes |
| DP-BV-01 | DP-BV | Au moins 2 bleus **et** au moins 2 verts |
| DP-BV-02 | DP-BV | Au moins 2 bleus **et** au moins 2 verts |
| DP-JV-01 | DP-JV | Au moins 2 jaunes **et** au moins 2 verts |
| DP-JV-02 | DP-JV | Au moins 2 jaunes **et** au moins 2 verts |
| ACC-06-01 | ACC-06 | Au moins 6 jetons au total, toutes couleurs confondues |
| ACC-06-02 | ACC-06 | Au moins 6 jetons au total, toutes couleurs confondues |
| 4C-01 | 4C | Au moins un rouge, un bleu, un jaune et un vert |
| 4C-02 | 4C | Au moins un rouge, un bleu, un jaune et un vert |

## 4. Catalogue physique Paquet B — défaite et victoire

Paquet réservé au mode B « Objectif secret ». La condition de victoire « deux paires complémentaires » est soumise à l’exclusion explicite de la défaite propre à la carte. Une victoire ordinaire ne peut pas coïncider avec la défaite de la carte ; l’exception contextuelle 4C est définie en §5.4.

| Identifiant | Variante | Condition de défaite | Condition de victoire |
|---|---|---|---|
| CD-R-01 | CD-R | Au moins 3 rouges | Au moins 3 bleus, bleus strictement plus nombreux que chacune des autres couleurs, et moins de 3 rouges |
| CD-R-02 | CD-R | Au moins 3 rouges | Au moins 3 bleus, bleus strictement plus nombreux que chacune des autres couleurs, et moins de 3 rouges |
| CD-B-01 | CD-B | Au moins 3 bleus | Au moins 3 jaunes, jaunes strictement plus nombreux que chacune des autres couleurs, et moins de 3 bleus |
| CD-B-02 | CD-B | Au moins 3 bleus | Au moins 3 jaunes, jaunes strictement plus nombreux que chacune des autres couleurs, et moins de 3 bleus |
| CD-J-01 | CD-J | Au moins 3 jaunes | Au moins 3 verts, verts strictement plus nombreux que chacune des autres couleurs, et moins de 3 jaunes |
| CD-J-02 | CD-J | Au moins 3 jaunes | Au moins 3 verts, verts strictement plus nombreux que chacune des autres couleurs, et moins de 3 jaunes |
| CD-V-01 | CD-V | Au moins 3 verts | Au moins 3 rouges, rouges strictement plus nombreux que chacune des autres couleurs, et moins de 3 verts |
| CD-V-02 | CD-V | Au moins 3 verts | Au moins 3 rouges, rouges strictement plus nombreux que chacune des autres couleurs, et moins de 3 verts |
| DP-RB-01 | DP-RB | Au moins 2 rouges et 2 bleus | Au moins 2 jaunes et 2 verts, **si et seulement si la défaite DP-RB de cette carte n’est pas satisfaite** |
| DP-RB-02 | DP-RB | Au moins 2 rouges et 2 bleus | Au moins 2 jaunes et 2 verts, **si et seulement si la défaite DP-RB de cette carte n’est pas satisfaite** |
| DP-RJ-01 | DP-RJ | Au moins 2 rouges et 2 jaunes | Au moins 2 bleus et 2 verts, **si et seulement si la défaite DP-RJ de cette carte n’est pas satisfaite** |
| DP-RJ-02 | DP-RJ | Au moins 2 rouges et 2 jaunes | Au moins 2 bleus et 2 verts, **si et seulement si la défaite DP-RJ de cette carte n’est pas satisfaite** |
| DP-RV-01 | DP-RV | Au moins 2 rouges et 2 verts | Au moins 2 bleus et 2 jaunes, **si et seulement si la défaite DP-RV de cette carte n’est pas satisfaite** |
| DP-RV-02 | DP-RV | Au moins 2 rouges et 2 verts | Au moins 2 bleus et 2 jaunes, **si et seulement si la défaite DP-RV de cette carte n’est pas satisfaite** |
| DP-BJ-01 | DP-BJ | Au moins 2 bleus et 2 jaunes | Au moins 2 rouges et 2 verts, **si et seulement si la défaite DP-BJ de cette carte n’est pas satisfaite** |
| DP-BJ-02 | DP-BJ | Au moins 2 bleus et 2 jaunes | Au moins 2 rouges et 2 verts, **si et seulement si la défaite DP-BJ de cette carte n’est pas satisfaite** |
| DP-BV-01 | DP-BV | Au moins 2 bleus et 2 verts | Au moins 2 rouges et 2 jaunes, **si et seulement si la défaite DP-BV de cette carte n’est pas satisfaite** |
| DP-BV-02 | DP-BV | Au moins 2 bleus et 2 verts | Au moins 2 rouges et 2 jaunes, **si et seulement si la défaite DP-BV de cette carte n’est pas satisfaite** |
| DP-JV-01 | DP-JV | Au moins 2 jaunes et 2 verts | Au moins 2 rouges et 2 bleus, **si et seulement si la défaite DP-JV de cette carte n’est pas satisfaite** |
| DP-JV-02 | DP-JV | Au moins 2 jaunes et 2 verts | Au moins 2 rouges et 2 bleus, **si et seulement si la défaite DP-JV de cette carte n’est pas satisfaite** |
| ACC-06-01 | ACC-06 | Au moins 6 jetons au total | Au moins 4 jetons d’une même couleur et moins de 6 jetons au total |
| ACC-06-02 | ACC-06 | Au moins 6 jetons au total | Au moins 4 jetons d’une même couleur et moins de 6 jetons au total |
| 4C-01 | 4C | Au moins un jeton de chacune des quatre couleurs | **Objectif contextuel :** être éliminé en raison de la défaite 4C et être classé dans les premiers éliminés selon le barème de §5.4 |
| 4C-02 | 4C | Au moins un jeton de chacune des quatre couleurs | **Objectif contextuel :** être éliminé en raison de la défaite 4C et être classé dans les premiers éliminés selon le barème de §5.4 |

## 5. Détail des variantes et compatibilité B

### 5.1 Récapitulatif des 12 variantes

| Famille | Variantes distinctes | Exemplaires par variante | Cartes par paquet |
|---|---:|---:|---:|
| Couleur dangereuse | 4 : CD-R, CD-B, CD-J, CD-V | 2 | 8 |
| Deux paires | 6 : DP-RB, DP-RJ, DP-RV, DP-BJ, DP-BV, DP-JV | 2 | 12 |
| Accumulation | 1 : ACC-06 | 2 | 2 |
| Quatre couleurs | 1 : 4C | 2 | 2 |
| **Total** | **12** |  | **24** |

Le tableau s’applique séparément à Paquet A/C et Paquet B. Chaque paquet comporte 24 cartes physiques et les 24 identifiants listés dans son catalogue, sans doublon interne.

### 5.2 Rotation couleur dangereuse

La couleur cible de victoire est la suivante dans le cycle rouge → bleu → jaune → vert → rouge. « Strictement plus représentée que chacune des trois autres » signifie qu’il n’y a pas d’égalité avec la deuxième couleur la plus représentée ; la cible est l’unique couleur la plus représentée. En outre, la victoire exige au moins trois jetons de cette couleur et moins de trois de la couleur dangereuse de la carte.

### 5.3 Deux paires complémentaires

Les six paires de couleurs sont les six partitions possibles en deux paires parmi quatre couleurs. La victoire porte sur la paire complémentaire de la défaite, avec au moins deux jetons de chaque couleur de cette paire. La vérification de victoire doit aussi vérifier que la condition de défaite propre à la carte n’est pas satisfaite. Une collection avec au moins deux jetons de chacune des quatre couleurs satisfait les deux motifs bruts, mais, sur une carte DP donnée, la défaite propre prévaut et la victoire n’est pas déclarée.

### 5.4 Objectif contextuel « quatre couleurs »

La condition de collection 4C est une condition de défaite ordinaire. L’objectif associé en B n’est pas une condition de collection : il faut que le porteur soit **éliminé à cause de sa condition 4C**, et que son rang d’élimination de la manche soit dans la limite suivante :

| Joueurs au début de la manche | Rang gagnant |
|---:|---|
| 4 | Premier éliminé |
| 5 ou 6 | Parmi les deux premiers éliminés |
| 7 ou 8 | Parmi les trois premiers éliminés |

Le classement repart à zéro à chaque manche avec la nouvelle distribution des cartes. Une élimination pour une autre condition ne satisfait pas cet objectif. En cas d’éliminations réellement simultanées sans ordre de résolution défini, le groupe partage le rang atteint au début de ces éliminations ; chaque porteur 4C de ce rang satisfait le critère si ce rang partagé est dans la limite. La victoire spéciale est alors déclarée immédiatement selon les règles de fin du mode B. Cette exception dépend de la raison et du rang de l’élimination, pas uniquement de la collection.

## 6. Exemples de déclenchement et de non-déclenchement

Les exemples décrivent l’évaluation au moment autorisé par la règle, jamais une élimination pendant l’installation.

| Carte / condition | Déclenchement | Ne déclenche pas |
|---|---|---|
| CD-R | 3 rouges (ou 4 rouges) | 2 rouges et 4 bleus |
| DP-RB | 2 rouges, 2 bleus et 1 jaune ; des couleurs supplémentaires sont autorisées | 2 rouges et 1 bleu, quelle que soit la quantité de jaune/vert |
| ACC-06 | 2 rouges, 2 bleus, 1 jaune et 1 vert (6 au total) | 2 rouges, 2 bleus et 1 jaune (5 au total) |
| 4C | 1 rouge, 1 bleu, 1 jaune et 1 vert | 2 rouges, 1 bleu et 1 jaune (vert absent) |
| B / CD-R victoire | 3 bleus, 1 jaune, 1 vert, 0 rouge : bleu est strictement le plus représenté et rouge reste sous 3 | 3 bleus, 2 jaunes, 1 rouge, 0 vert : bleu n’est pas strictement majoritaire |
| B / DP-RB victoire | 2 jaunes et 2 verts, sans atteindre 2 rouges et 2 bleus | 2 jaunes, 2 verts, 2 rouges et 2 bleus : la défaite propre DP-RB est satisfaite, donc la victoire est exclue |
| B / ACC-06 victoire | 4 rouges et 1 bleu : 5 jetons au total | 4 rouges, 1 bleu et 1 jaune : total 6, donc la défaite ACC-06 est satisfaite |
| B / 4C victoire | À 6 joueurs, le porteur éliminé par 4C est deuxième dans le classement d’élimination de la manche | Le porteur 4C est éliminé pour une autre condition, ou son rang dépasse le deuxième à 6 joueurs |

Pour les cartes B DP-RB et ACC-06, les cas « victoire » appliquent en plus les contraintes explicites de §4 : la victoire ne coïncide pas avec la défaite de cette carte.

## 7. Compatibilité, mise en place et renouvellement

1. Chaque joueur reçoit une seule carte correspondant au mode ; les deux paquets restent séparés.
2. Une collection initiale de trois jetons qui satisfait la condition de défaite de la carte est rejetée et repiochée par groupes de trois. En mode B, la mise en place invalide également une condition de victoire ordinaire de collection conformément à §3/§6.2 ; aucune vérification de mise en place ne produit une victoire ou une élimination effective.
3. Pour une carte B ordinaire, la victoire est vérifiée avant la défaite aux événements autorisés par le règlement, mais les conditions du catalogue sont définies pour éviter le chevauchement. La défaite propre exclut explicitement les victoires DP ; les formules CD et ACC comportent leurs exclusions respectives. L’objectif 4C, contextuel, ne se transforme pas en condition ordinaire de victoire de collection.
4. À chaque nouvelle manche, les cartes sont redistribuées depuis le paquet approprié et le classement d’élimination 4C est réinitialisé. Le score C est conservé selon les règles du mode ; le changement de carte n’efface pas les points.
5. Les seuils du présent catalogue sont la base de référence approuvée pour la conception ; leur équilibrage demeure une question expérimentale. Ils ne doivent pas être remplacés par les cartes ou paramètres artificiels de `simulation/experiments.py`.

## 8. Écarts identifiés avec le règlement et le code actuels

### Règlement version 67

- **Sac et joueurs :** §§3 et 12 donnent quatre couleurs, 40 jetons et huit joueurs au plus comme hypothèse d’essai ; cette spécification les remplace par 52 jetons (13 par couleur), plage 4–8 et cible 6. Ce sont des décisions explicites du catalogue, pas une interprétation de l’hypothèse v67.
- **Cartes :** §§8 et 12 laissent seuils, formulations, paquet final et objectifs B à concevoir. Les 12 variantes et associations de §3–§5 sont les décisions désormais retenues pour le catalogue.
- **Deux paires :** le catalogue tranche pour deux couleurs désignées et au moins deux de chacune, couleurs supplémentaires permises ; la v67 laissait ces deux aspects à tester.
- **Victoire spéciale 4C :** la v67 décrit un objectif d’élimination précoce encore indéfini (§8/§12), sans cette règle de rang. La spécification le spécialise par son barème et sa causalité ; son fonctionnement demande un mécanisme moteur nouveau.
- Les règles de timing de contrôle, l’absence de victoire/élimination réelle pendant la mise en place, la redistribution à nouvelle manche, les conditions de victoire autorisées et la priorité des fins de succession B restent applicables. Aucune priorité terminale de succession B n’est rouverte ici.

### Code actuel

| Sujet | État constaté | Conséquence pour l’implémentation future |
|---|---|---|
| Configuration matérielle | `rules/config.py::GameConfig` reçoit un mapping de couleurs ; son défaut `initial_hand_size=3` correspond au catalogue. `simulation/experiments.py::benchmark_config` remplace toutefois le sac par 8 rouges + 8 bleus, la main initiale par 2 et utilise 4 joueurs. | Le benchmark actuel n’est pas la configuration de référence catalogue. Configurer 13 de chacune des quatre couleurs et trois jetons initiaux ; ne pas réutiliser silencieusement les chiffres benchmark. |
| Identifiants et réserve physique | `rules/card_pool.py::CardPool` compare les effectifs de cartes par `ConditionKind` et impose actuellement exactement deux exemplaires **par type de condition**. Le catalogue comporte 8 `COLOR_COUNT`, 12 `TWO_PAIRS`, 2 `TOTAL_COUNT` et 2 `DIVERSITY` dans le paquet A/C (comptes analogues par défaite dans B), parce que le contrat distingue les variantes et met deux exemplaires de chacune. `expected_defeat_counts` refuse des effectifs 8 ou 12. | Le modèle de réserve doit représenter les 12 variantes et leurs exemplaires, pas seulement un effectif fixe de deux par enum `ConditionKind`. En l’état, le catalogue de 24 cartes ne peut pas être validé comme `CardPool`. |
| Paquet de 24 / distribution | Sans réserve, `GameConfig.validate` exige une carte injectée par joueur et `create_game` joue ces cartes ; avec réserve, il faut `CardPool`. | L’injection directe peut servir à des tests déterministes avec N cartes, pas à distribuer aléatoirement le catalogue physique complet tel quel. Une future adaptation devra préserver la distinction paquet/partie et le tirage reproductible d’une carte par joueur. |
| Expressions de condition B | `rules/cards.py::Condition` porte un seul prédicat ; `Card.victory` est un seul `Condition`. Il n’exprime pas une conjonction arbitraire ni la négation de la défaite. | Les victoires CD (plancher + pluralité stricte + plafond dangereux), DP (paires complémentaires + exclusion de la défaite) et ACC (même couleur ≥4 + total <6) ne sont pas représentables fidèlement par la condition ordinaire actuelle. |
| Validation chevauchement B | `GameConfig.validate` rejette une carte dont victoire et défaite peuvent coïncider (`_conditions_overlap`). Une victoire DP complémentaire seule peut coïncider avec la défaite propre sur une collection ayant deux jetons de chaque couleur ; le catalogue exige alors que la défaite propre exclue la victoire. La condition ACC de quatre jetons d’une couleur peut aussi coïncider avec la défaite à total six si elle ne comporte pas l’exclusion total <6. | La compatibilité demandée ne peut pas être simulée en donnant simplement deux prédicats indépendants au code : le nouveau prédicat doit formaliser l’exclusion, et la validation doit reconnaître la sémantique conjointe, au lieu de rejeter les cartes valides ou d’accepter un chevauchement. |
| Victoire contextuelle 4C | La carte actuelle ne contient ni rang d’élimination, ni raison d’élimination dans la condition de victoire. `GameConfig` exige en outre une condition `victory` ordinaire non nulle en mode B. Le moteur `engine/transitions.py::_check_recipient` teste actuellement la victoire du destinataire vivant avant sa défaite ; il ne déclare pas une victoire après élimination conditionnée par cause et rang. | Il faudra conserver le nombre de joueurs au début de manche, l’ordre/groupe d’élimination et la raison `4C`, puis déclencher l’objectif au bon événement avant toute suite de résolution pertinente. Il faut aussi préciser/tester le cas de plusieurs bénéficiaires simultanés et sa relation à la fin immédiate du mode B ; le code actuel n’a ni rangs ni victoire partagée contextuelle. |
| Faisabilité initiale et manche suivante | `rules/config.py::_complete_setup_possible`, `CardPool.validate_setup`, `engine/setup.py::_deal_valid_hands` rejettent les mains initiales déjà gagnantes/perdantes et cherchent une attribution complète. `engine.transitions::_start_new_round` redistribue les cartes et les mains. | Conditions collection ordinaires du catalogue : les défaites DP (quatre jetons requis), ACC (six), et 4C (quatre couleurs) ne peuvent pas se déclencher dans trois jetons initiaux ; une carte CD invalide une main de trois jetons de la couleur dangereuse. L’objectif ordinaire CD en B exige aussi d’éviter sa collection gagnante en setup selon la règle de mise en place. L’objectif 4C contextuel ne doit pas invalider une main au seul titre d’un futur rang. La faisabilité combinatoire doit être conservée et testée pour 8 joueurs et au début de chaque manche. |

La faisabilité initiale à huit joueurs peut aussi être montrée pour toutes les sélections de huit cartes de ces catalogues : distribuer des mains de trois en motifs non monochromes (deux jetons d’une couleur et un d’une suivante, en faisant deux cycles des quatre couleurs) utilise six jetons de chaque couleur. Cela évite les conditions CD ; DP demande au moins quatre jetons, ACC au moins six et 4C quatre couleurs, donc aucune de ces défaites ne peut apparaître dans ces mains de trois. Les victoires CD exigent au moins trois jetons de la couleur cible, les victoires DP quatre jetons et les victoires ACC quatre jetons d’une couleur ; aucune victoire de collection du catalogue B ne se produit dans ces mains. L’objectif contextuel 4C ne s’applique qu’à une élimination en partie. Il reste 7 jetons de chaque couleur, donc 28 au sac commun. Cette construction établit la faisabilité mathématique des mains initiales pour ces catalogues ; elle ne lève pas les incompatibilités de représentation et de validation du code listées ci-dessus.

## 9. Tests à préparer avant ou avec l’implémentation

1. **Catalogue statique :** compter 12 variantes (4 CD, 6 DP, 1 ACC, 1 4C), deux exemplaires de chaque variante et 24 cartes par paquet ; unicité des identifiants à l’intérieur de chacun ; correspondance exacte des 24 associations B.
2. **Table de vérité des conditions :** cas au seuil, au-dessus et juste en dessous pour chaque famille ; autres couleurs présentes ; toutes les six combinaisons DP ; rotation CD rouge→bleu→jaune→vert→rouge ; cible CD strictement première ; plafond `danger < 3` ; ACC avec total 5/6 ; 4C avec une couleur absente/présente.
3. **Compatibilité B :** prouver par énumération des collections possibles au stock 13/couleur qu’aucune victoire ordinaire ne coïncide avec la défaite propre, en particulier DP sur les quatre couleurs et ACC au total 6 ; tester la priorité explicite défaite-exclut-victoire.
4. **Objectif 4C contextuel :** vérifier cause d’élimination, bornes de rang selon 4/5/6/7/8 joueurs, réinitialisation par manche, exclusions pour une autre cause, groupes de rang partagé, arrêt immédiat et évènements émis. Tester séparément le porteur qui est dernier éliminé et les résultats impliquant plusieurs porteurs qualifiants.
5. **Mise en place :** à 8 joueurs, distribuer 24 des 52 jetons ; générer des mains valides pour les cartes sélectionnées ; invalider/repiocher les collections perdantes ou gagnantes ordinaires sans événement public de victoire/élimination ; ne pas appliquer l’objectif 4C contextuel à la main de départ.
6. **Réserve et manches :** sélectionner 8 cartes distinctes sans mélange des paquets, deux copies physiques par variante, graine reproductible, combinaisons impossibles rejetées avant le deal ; à nouvelle manche, nouvelle sélection/redistribution selon le paquet du mode et réinitialisation du rang 4C.
7. **Invariants de modes :** Paquet A/C accepté seulement en modes A/C et dépourvu de victoire ; Paquet B accepté seulement en mode B et chaque carte ayant son association ; comportement conservé aux déclencheurs de règles, y compris succession B v67.

## 10. Décisions encore ouvertes

Ce catalogue ne prend pas de nouvelle décision sur les sujets laissés ouverts par les sources de conception :

- le choix de la variante de succession A ou B comme référence, même si la résolution terminale B est établie en v67 ;
- le contrôle de la défaite du donneur après retrait ;
- la visibilité de la pioche après refus et des pioches de rejeu en A ;
- les paramètres définitifs du mode C, notamment seuil d’éliminations par manche selon le nombre de joueurs et seuil C2 (C1 reste à trois manches avec son départage) ;
- l’objectif d’élimination précoce générique et les pouvoirs secrets, distincts de l’objectif spécial 4C ici défini ;
- l’équilibrage statistique des 12 variantes et de leurs associations B. Les quantités et formulations du catalogue sont validées comme base de conception, pas comme équilibrées.

## Références

- `C'est cadeau !.docx`, version 67 : §§3–8, 11–14 et registre des décisions ; en particulier setup (§3), mode B (§6.2), modes C (§6.3), variantes (§7), cartes candidates (§8), paramètres à fixer (§12) et cohérence croisée (§14).
- `specifications/audit_decisions_ouvertes.md` : configuration du sac, joueurs, paquet, conditions, mode C, variantes et distinction entre décisions et benchmarks.
- `rules/config.py`, `rules/cards.py`, `rules/card_pool.py`, `rules/rules.py`.
- `engine/setup.py`, `engine/transitions.py`, `engine/state.py`.
- `simulation/experiments.py` : valeurs de benchmark explicites expérimentales, non officielles.
- Tests de référence existants à consulter pour l’implémentation : `tests/test_config.py`, `tests/test_card_pool.py`, `tests/test_setup.py`, `tests/test_modes.py`, `tests/test_regressions_point2.py`, `tests/test_simulation_experiments.py`.
