# Décisions de conception encore ouvertes — état après configuration de référence

## Portée

La configuration générale décidée est détaillée dans [configuration_reference.md](configuration_reference.md), et les cartes dans [catalogue_cartes_reference.md](catalogue_cartes_reference.md). Ce document ne répète pas leurs tableaux : il conserve seulement les questions qui ne sont pas encore résolues et les divergences qu’il faut traiter avant une implémentation ou une campagne d’équilibrage.

Une décision peut être validée en conception sans être implémentée. Les divergences de code ci-dessous ne réouvrent pas automatiquement ces décisions.

## Décisions désormais définies

- 4 à 8 joueurs, six comme cible d’équilibrage ; sac de 52 jetons (13 par couleur), quatre couleurs ; trois jetons initiaux.
- Paquet A/C et paquet B indépendants, 24 cartes chacun, avec les variantes et associations fixées dans le catalogue.
- Succession B comme référence ; A conservée comme comparaison expérimentale. La priorité terminale B de la v67 reste établie.
- Contrôle de défaite du donneur après retrait désactivé pour la référence ; pioche après refus publique ; pioche de rejeu en A secrète.
- Mode C : seuils 4→2, 5→2, 6→3, 7→3, 8→4 ; 1 point par élimination créditée et 1 point bonus de manche ; C1 et C2 exclusifs ; C2 4→6, 5→7, 6→8, 7→9, 8→10.
- Si le seuil C n’est pas atteint, le joueur au score maximal gagne la manche même s’il a été éliminé ; le dernier survivant ne gagne pas automatiquement. L’égalité au score maximal reste ouverte.
- Le nombre de manches C1 reste fixé à trois, avec la manche de départage v67 en cas d’égalité en tête.

Ces valeurs sont des décisions de référence de conception ; elles ne sont pas les paramètres du benchmark courant et ne sont pas toutes implémentées.

## Questions qui nécessitent encore une réponse

1. **Égalité au score maximal en fin d’une manche C sans seuil atteint :** choisir entre (a) partager la victoire de manche et (b) jouer une manche supplémentaire pour départager les joueurs concernés. La manche supplémentaire C1 s’applique à l’égalité du classement final après trois manches ; elle ne tranche pas une égalité en fin de manche. L’attribution du bonus dans ce cas reste à préciser selon la solution retenue.
2. **Si plusieurs cartes 4C sont éligibles dans un groupe d’éliminations au même rang, qui gagne la partie B ?** Le catalogue dit que chaque porteur du rang partagé satisfait le critère et que la victoire spéciale est déclarée immédiatement ; il ne formalise pas explicitement si ces joueurs deviennent co-vainqueurs du mode B ou comment plusieurs victoires immédiates sont enregistrées.
3. **L’objectif d’élimination précoce générique de la v67 est-il remplacé par la seule exception 4C du catalogue, ou reste-t-il souhaité comme mécanisme distinct ?** Le catalogue fixe le cas propre aux cartes 4C ; il ne définit pas un objectif générique pour les autres cartes.
4. **Les pouvoirs secrets restent-ils reportés à une phase future ?** La v67 §§9 et 12 les réserve à une conception ultérieure ; aucun effet n’est spécifié dans la configuration de référence. Aucune décision immédiate n’est nécessaire pour les premières campagnes sans pouvoirs.

Les règles v67 précisent déjà que, dans une chaîne B, les éliminations forcées sont examinées une par une ; l’initiateur reçoit le point de chaque élimination admissible d’un adversaire, puis le seuil de manche est contrôlé avant la fin du dernier survivant. Le premier compteur qui atteint le seuil termine la manche. L’action initiale qui élimine tout le monde reste une égalité terminale sans point/bonus pour cette action. Aucun arbitrage supplémentaire n’est requis pour ce cas séquentiel. Le code suit cette séquence dans `engine/transitions.py::_decide` et `_clockwise_chain`; aucun chemin normal actuel ne crédite simultanément plusieurs joueurs dans une même étape.

## Divergences d’implémentation à traiter, sans les confondre avec des choix ouverts

| Décision de référence | État du code actuel | Conséquence |
|---|---|---|
| Succession B de référence ; A expérimentale | `GameConfig.succession` a pour défaut A ; benchmarks de base aussi. | Configurer explicitement B pour une campagne de référence. Garder les données A séparées. |
| Pioche après refus publique | `reveal_refusal_draw=False` par défaut. | La référence doit passer `True`. Le retour du jeton proposé au sac du donneur est déjà masqué publiquement ; les tests de visibilité couvrent les deux options. |
| Seuil d’éliminations fonction du nombre initial de joueurs | `elimination_threshold` est un entier scalaire obligatoire, sans table automatique. | Construire une configuration distincte pour chaque taille 4–8 ; la table de référence n’est pas appliquée par le moteur. |
| Gagnant de manche C sans seuil atteint = score le plus élevé, même si le joueur a été éliminé | Les transitions terminent actuellement C par le joueur qui atteint le seuil ou par le dernier survivant. | Décision validée mais non implémentée ; harmoniser ultérieurement le texte source, adapter le moteur et ajouter des tests. |
| Paquets physiques de 24 cartes et catalogue B | `CardPool` impose actuellement exactement deux cartes par enum `ConditionKind`; `Condition` et `Card.victory` ne représentent pas les conjonctions/exclusions du catalogue ; le rang/raison 4C n’existe pas dans `GameState`. | Le catalogue validé ne peut pas être chargé/exécuté fidèlement. Voir l’analyse précise et les contrôles futurs dans `catalogue_cartes_reference.md` §8. |
| C2 : seuil contrôlé après fin normale de manche | `_finish_round` attribue le bonus puis vérifie le seuil ; le seuil C2 ne coupe pas une chaîne au milieu. | Conforme à la règle de fin de manche ; les valeurs par nombre de joueurs restent à configurer explicitement. |
| Défaite du donneur après retrait désactivée ; pioche A secrète | Les défauts `False` sont alignés avec ces deux choix. | Conforme aux réglages de référence pour ces options ; cela ne rend pas le défaut de succession ou de visibilité après refus conforme. |

Les valeurs artificielles de `simulation/experiments.py` (4 joueurs, deux jetons initiaux, sac rouge/bleu, paquet réduit, seuil C de 1, deux manches C expérimentales) ne constituent pas une autre proposition de référence. `simulation/README.md` les qualifie d’expérimentales et non officielles.

## Éléments de preuve déjà présents

- Succession B et arrêt de chaîne au dernier survivant : `tests/test_regressions_point2.py::test_variant_b_stops_at_last_survivor_and_awards_expected_points_and_bonus`. Ce test ne couvre pas la nouvelle décision de désigner le gagnant C selon le score lorsqu’aucun seuil n’est atteint.
- Seuil et fin C2 après bonus : `tests/test_modes.py::test_t62_complete_c2_pilot_finishes_after_elimination_point_and_last_survivor_bonus`.
- C1 et partage après départage : `tests/test_modes.py::test_t43_c1_ends_after_three_rounds_using_cumulative_scores`, `test_t44_c1_tiebreak_round_shares_persistent_tie_or_accepts_new_leader`.
- Contrôle donneur désactivé : `tests/test_gifts.py::test_t16_disabled_donor_removal_check_does_not_eliminate_donor`.
- Visibilité après refus : `tests/test_gifts.py::test_t08_refusal_returns_offer_and_draws_replacement_with_configured_visibility`, `tests/test_privacy.py::test_t08_t28_hidden_refusal_draw_is_known_to_recipient_but_not_public`.
- Pioche secrète de rejeu A paramétrable : `tests/test_eliminations.py::test_t27_t28_responsible_replay_empty_hand_draw_visibility_and_empty_bag`.
- Aucun test ne prouve l’équilibre des nouvelles valeurs, du catalogue complet, des effectifs 4–8, du seuil dépendant de la table, du nouveau gagnant au score en fin de manche ni du rang 4C.
