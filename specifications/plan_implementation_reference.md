# Plan d’implémentation de la configuration de référence

## 1. Portée et état de référence

Ce plan décrit les écarts constatés dans le dépôt au 19 octobre 2026 et propose un ordre de correction vérifiable. Il ne modifie ni les règles, ni le moteur, ni les tests, ni le catalogue. Les comportements actuels cités ci-dessous ont été vérifiés dans les fichiers présents ; les tests mentionnés sont ceux réellement repérés dans `tests/`.

La configuration de conception est spécifiée dans [`configuration_reference.md`](configuration_reference.md), les décisions non résolues sont suivies dans [`audit_decisions_ouvertes.md`](audit_decisions_ouvertes.md), et les cartes dans [`catalogue_cartes_reference.md`](catalogue_cartes_reference.md). La référence cible est 4–8 joueurs (six prioritaires pour l’équilibrage), quatre couleurs à 13 jetons, trois jetons initiaux, deux paquets distincts de 24 cartes, succession B, et modes C avec seuils liés à l’effectif initial. Si le seuil C n’est pas atteint, le meilleur score de manche désigne le gagnant, y compris s’il est éliminé.

La dernière règle de gagnant C est une décision de conception validée qui contredit encore la v67 et le code : elle est incluse dans le plan comme adaptation future, sans prétendre qu’elle est implémentée. Aucune campagne ni test n’a été exécuté pour préparer ce plan.

## 2. Synthèse des écarts majeurs

1. **La configuration de référence matérielle n’est pas fournie comme profil exécutable.** Le modèle accepte un stock configurable et trois jetons initiaux par défaut, mais ne contraint pas les parties à 4–8 joueurs ni à quatre couleurs de 13. La CLI intégrée ne permet que 2–4 joueurs. Les benchmarks utilisent quatre joueurs, 16 jetons rouges/bleus, deux jetons initiaux, quatre cartes artificielles et un seuil C de 1.
2. **Le catalogue de 24 cartes n’est pas chargeable comme paquet.** `CardPool` vérifie deux cartes par type d’enum de condition, tandis que le catalogue dépend de 12 variantes et de deux exemplaires de chacune. Sans réserve, `GameConfig` exige exactement N cartes ; cela sert aux scénarios déterministes mais ne prélève pas N cartes reproductibles parmi les 24.
3. **Les expressions de victoire du catalogue B dépassent le modèle actuel.** Une victoire est une unique `Condition`; les associations CD, DP et ACC ont des exigences composées et des exclusions de la défaite propre. Le modèle n’exprime pas non plus l’objectif 4C par cause et rang d’élimination.
4. **La mise en place possède déjà des contrôles de faisabilité utiles.** `GameConfig.validate`, `CardPool.validate_setup`, `_complete_setup_possible` et `_deal_valid_hands` rejettent les mains initiales invalides et évitent de choisir des sous-ensembles de réserve non distribuables. Ces contrôles doivent survivre à l’intégration des nouveaux paquets. Il faut vérifier leur coût avec les réserves réelles avant une campagne.
5. **Succession B est implémentée et testée, mais pas choisie par défaut.** `GameConfig` a A comme défaut. Le code B traite une élimination forcée à la fois ; il vérifie l’égalité terminale, crédite le point non terminal, teste le seuil C, puis teste le dernier survivant.
6. **La visibilité publique après refus exige un réglage explicite.** Le retour secret est masqué et le tirage peut être public, mais `reveal_refusal_draw=False` par défaut, comme dans le benchmark. La pioche de rejeu A est secrète par défaut et ce réglage n’est pas appliqué à B.
7. **Le mode C a le seuil scalaire, les points et C1/C2, mais pas la table de référence ni le gagnant de manche au score.** Lorsque le seuil n’est pas atteint, les chemins actuels transmettent le dernier survivant à `_finish_round`. Le score leader, qui peut être éliminé, n’est pas sélectionné.
8. **Les structures d’export peuvent porter une partie des nouveaux résultats, mais leur propagation doit être testée.** `RoundRun`, les lignes joueur-manche, les statistiques de victoires par carte et les exports existent. Il faut assurer qu’un gagnant C éliminé reste qualifié comme vainqueur de manche, que son bonus et ses scores sont capturés, et que les égalités terminales restent distinctes.

## 3. Matrice de conformité

| Décision de référence | Comportement actuel vérifié | Fichiers / fonctions concernés | Statut |
|---|---|---|---|
| 4–8 joueurs ; 6 est la priorité d’équilibrage | `GameConfig.validate` exige au moins deux joueurs, sans maximum ; la CLI de simulation accepte 2–4. Le profil intégré fixe 4. | `rules/config.py::GameConfig.validate`; `simulation/__main__.py::_parser`, `main`; `simulation/experiments.py::benchmark_config` | Divergence de plage et absence de profil 4–8. Six n’est qu’une priorité de futures campagnes. |
| 52 jetons, quatre couleurs ×13 ; trois jetons distribués | Le stock vient du mapping passé à `GameConfig`; `initial_hand_size=3` par défaut. Le deal conserve les identifiants et cherche une distribution complète faisable. | `rules/config.py::GameConfig`; `_complete_setup_possible`; `engine/setup.py::create_game`, `_deal_valid_hands`; `engine/transitions.py::_start_new_round` | Mécanisme de distribution déjà présent ; stock/référence générale à configurer et vérifier à 4–8. |
| Paquet A/C 24 défaites ; paquet B séparé 24 défaites/victoires | Réserve exigée par `GameConfig` si on n’injecte pas N cartes, mais `CardPool` exige deux exemplaires par `ConditionKind`. Les associations et identifiants du catalogue ne sont pas consommés par le code. | `rules/card_pool.py::CardPool`; `rules/config.py::GameConfig.validate`; `engine/setup.py::create_game`; `engine/transitions.py::_start_new_round`; `specifications/catalogue_cartes_reference.md` §§5, 7–8 | Divergence structurelle de modèle et de chargement. |
| Main initiale valide et distribution faisable | Les conditions ordinaires de défaite, et en B la victoire de collection, invalident une main de départ. Les tests de faisabilité examinent les affectations complètes ; le deal a un repli déterministe après ses tentatives aléatoires bornées. | `rules/config.py::_complete_setup_possible`; `rules/card_pool.py::validate_setup`, `draw_usable`; `engine/setup.py::_deal_valid_hands` | Fonctionnement existant. À préserver ; ajouter l’acceptation catalogue et effectifs 4–8. |
| Succession B de référence, A expérimentale | A est le défaut `GameConfig.succession`; les deux mécanismes sont implémentés et comparés dans tests. | `rules/config.py::Succession`, `GameConfig`; `engine/transitions.py::_succession_a`, `_clockwise_chain` | Règles des variantes présentes ; le profil de référence doit sélectionner B explicitement. |
| Ordre B : égalité terminale, seuil C, dernier survivant, puis poursuite | `_decide` vérifie d’abord zéro survivant, puis crédits/seuil, puis un seul vivant. `_clockwise_chain` vérifie zéro, attribue le point de l’élimination forcée non terminale, teste le seuil, puis le dernier survivant. | `engine/transitions.py::_decide`, `_clockwise_chain`, `_terminal_tie`, `_credit_elimination` | Ordre de résolution testé. Ne pas altérer l’égalité terminale ni le contrôle du seuil avant dernier survivant. |
| Gagnant C sans seuil : score maximal, même éliminé | `_decide`, `_succession_a` et `_clockwise_chain` finissent actuellement la manche en passant le dernier survivant à `_finish_round`; le leader du score n’est pas consulté. La v67 §6.3 et `specifications/game_flow.md` §8.3 disent encore dernier survivant. | `engine/transitions.py::_decide`, `_succession_a`, `_clockwise_chain`, `_finish_round`; `specifications/configuration_reference.md` §6 ; Word v67 §6.3 | Décision validée, divergence source/code. Harmoniser le texte source dans une autorisation séparée ; moteur et tests à adapter. L’égalité au score maximal de manche reste ouverte. |
| Point d’élimination et seuil de manche | Chaque élimination créditée augmente score et compteur ; une élimination terminale à zéro survivant ne donne pas de nouveau point. Chaque élimination forcée B non terminale est créditée à l’initiateur, même éliminé. | `engine/transitions.py::_credit_elimination`, `_round_threshold_was_hit`, `_threshold_player`; `rules/rules.py::awarded_point_allowed`, `round_threshold_reached` | Points de base présents et couverts ; table d’effectif et attribution du gagnant sans seuil manquantes. |
| Seuils C 4→2, 5→2, 6→3, 7→3, 8→4 | Un entier `elimination_threshold` obligatoire ; pas de table ni validation de relation avec l’effectif initial. | `rules/config.py::GameConfig.validate`; `rules/rules.py::round_threshold_reached`; `simulation/experiments.py::benchmark_config` | Divergence de configuration. Le paramètre doit être résolu depuis le nombre au début, sans se recalculer selon les survivants. |
| C1 : trois manches cumulées, départage final ; C2 alternatif : cible 6–10 et fin après manche | `PointsFormat` distingue C1/C2. `_finish_round` attribue le bonus avant le contrôle C2, ou déclenche le départage après trois manches C1. Seuils C2 et C ne sont que des paramètres. | `rules/config.py::PointsFormat`, `GameConfig`; `engine/transitions.py::_finish_round`, `_start_new_round`; `rules/rules.py::points_game_should_end` | Flux C1/C2 et exclusion des conditions cumulatives présents ; valeurs de référence multi-effectif à fournir et vérifier. |
| Refus : restitution secrète, pioche commune publique | `token_returned` publie destination sans identité/couleur ; `token_drawn` n’expose couleur/id que si `reveal_refusal_draw=True`. Défaut false. | `engine/transitions.py::_decide`, `_draw`; `engine/state.py::GameState.emit`, historique public; `rules/config.py::GameConfig` | Mécanisme configurable ; valeur par défaut divergente. Exports ne conservent que `event_counts_json`, pas la charge utile complète de pioche. |
| Repioche A secrète ; aucun transfert de cette règle à B | `reveal_replay_draw=False`; A l’utilise pour rejeu et successeur vide. B élimine le successeur vide sans pioche. | `engine/transitions.py::_succession_a`, `_clockwise_chain`, `_draw`; `rules/config.py::GameConfig` | Conforme au défaut de confidentialité A ; préserver l’isolation des variantes. |
| Contrôle de défaite du donneur immédiatement après retrait désactivé | Le contrôle est conditionnel au booléen `donor_defeat_after_removal`, défaut false ; les contrôles ultérieurs continuent. | `engine/transitions.py::_propose`; `rules/config.py::GameConfig` | Conforme au réglage par défaut ; conserver les deux scénarios de test (off/on). |
| Victoires B du catalogue et exclusion de la défaite propre | `Condition` évalue un prédicat par condition ; une carte peut avoir plusieurs défaites, mais une victoire `Condition | None`. Le validateur rejette les chevauchements bruts. | `rules/cards.py::Condition`, `Card`, `condition_matches`; `rules/rules.py::evaluate_victory`; `rules/config.py::_conditions_overlap`, `_validate_condition`, `GameConfig.validate` | Modèle insuffisant pour conjonctions et exclusions du catalogue ; aucun test du paquet complet. |
| Victoire 4C causale et par rang selon effectif initial | Ni cause/rang de manche ni victoire après élimination ne sont conservés comme données de jeu. `_check_recipient` exige un joueur vivant et vérifie une victoire de collection ordinaire avant sa défaite. | `engine/state.py::GameState`, `PlayerState`; `engine/transitions.py::_check_recipient`, `_eliminate`, `_finish_game`; `rules/cards.py::Card` | Fonctionnalité non représentée ; tests contextuels absents. Cas des rangs partagés et plusieurs gagnants demeure ouvert. |
| Résultats C disponibles et exacts dans les exports | `RoundRun` stocke gagnant, scores cumulés et compteurs ; `PlayerRun` stocke résultat et score par manche. JSON, CSV joueur/partie, agrégats statistiques et Markdown existent. Le runner classe toute ligne selon `RoundRun.winner_id`, même si éliminée. | `simulation/runner.py::RoundRun`, `_player_results`, `run_game`; `simulation/statistics.py::summarize`; `simulation/reporting.py::write_campaign` | Structures en principe compatibles ; aucun test sur un joueur éliminé vainqueur au score. Tests d’export actuels couvrent autres cas. |

## 4. Modifications futures, ordre recommandé

### Étape 1 — Formaliser le contrat de profil de référence

Ajouter une fabrique/configuration nommée pour le profil A/C et B, sans détourner les benchmarks. Elle doit sélectionner explicitement B comme référence, désactiver le contrôle du donneur, activer la révélation de la pioche après refus, conserver la pioche A secrète, fournir 52 jetons, trois jetons initiaux et résoudre les seuils C depuis l’effectif initial. Vérifier explicitement 4, 5, 6, 7 et 8 joueurs. Garder les configurations artificielles de `benchmark_config` étiquetées expérimentales.

Fichiers probables : `rules/config.py` (validation seulement si nécessaire), un module de configuration de référence à définir ou `simulation/experiments.py` pour l’orchestration sans faire passer le benchmark pour référence ; `simulation/__main__.py` pour la plage CLI. Garder les tests déterministes existants injectant exactement N cartes.

### Étape 2 — Adapter le modèle de paquets au catalogue

Remplacer le contrat qui compte deux cartes uniquement par enum de condition par un contrat représentant les variantes/identifiants et leurs exemplaires. Construire deux paquets disjoints : A/C sans victoire et B avec les associations cataloguées. Le moteur doit échantillonner N cartes distinctes de 24 avec le RNG de partie, pas traiter les 24 cartes comme toutes distribuées. À chaque nouvelle manche, tirer un nouveau sous-ensemble du paquet du mode sans hybridation et avec une graine reproductible.

Préserver deux chemins API : la réserve pour les parties/campagnes et `cards` injectées directement pour les scénarios unitaires. Ne pas relâcher les contrôles d’incompatibilité mode, d’identifiants uniques ou de faisabilité du deal. Vérifier le coût de l’énumération des sous-ensembles faisables à taille 8 ; si une optimisation est nécessaire, comparer ses résultats et sa reproductibilité au contrat exhaustif avant adoption.

Fichiers : `rules/card_pool.py::CardPool`, `validate_for`, `validate_setup`, `draw_usable`; `rules/config.py::GameConfig.validate`, `_complete_setup_possible`; `engine/setup.py::create_game`, `_deal_valid_hands`; `engine/transitions.py::_start_new_round`; nouveau module de données de cartes/configuration, sans réécrire `specifications/catalogue_cartes_reference.md`.

### Étape 3 — Exprimer exactement les conditions du catalogue

Étendre les données de règles afin de représenter les prédicats composés et exclusions explicites, et valider que chaque association B respecte la sémantique du catalogue, notamment CD (minimum, majorité stricte et plafond), DP (paire complémentaire seulement si la défaite propre est fausse), ACC (concentration avec total sous le seuil), ainsi que les 12 variantes et leurs exemplaires. Garder l’évaluation de défaite multiple et son événement de contrôle unique.

Fichiers : `rules/cards.py::Condition`, `Card`, `condition_matches`; `rules/rules.py::evaluate_defeat_conditions`, `evaluate_victory`; `rules/config.py::_validate_condition`, `_conditions_overlap`, `GameConfig.validate`; intégration avec `rules/card_pool.py`. Définir le schéma de données avant d’adapter les transitions.

### Étape 4 — Ajouter le suivi contextuel de l’objectif 4C

Après stabilisation du modèle de cartes, suivre pour chaque manche l’effectif initial, l’ordre/groupe de rang des éliminations et leur cause. Lors d’une élimination causée par la défaite 4C, vérifier le barème catalogue propre à 4–8 joueurs. Ne pas évaluer cet objectif pendant le setup ni sur une élimination due à une autre condition. Préserver les priorités terminales existantes. Avant de définir l’effet d’une simultanéité/rang partagé, obtenir l’arbitrage ouvert sur plusieurs bénéficiaires 4C ; isoler ce traitement afin de ne pas imposer une interprétation.

Fichiers : `engine/state.py::GameState`, `PlayerState` ou état de manche dédié ; `engine/transitions.py::_eliminate`, `_check_recipient`, `_finish_game`; `rules/cards.py` / modèle de carte ; `simulation/runner.py` pour cause/rang descriptifs si retenus dans les résultats. L’objectif générique d’élimination précoce reste distinct et ne doit pas être inventé dans cette étape.

### Étape 5 — Appliquer les règles de victoire C

1. Centraliser la fin d’une manche C afin que chaque chemin d’arrêt passe par un même décideur après la priorité zéro survivant et après le contrôle du seuil.
2. Si le seuil est atteint, conserver le premier joueur dont le compteur atteint le seuil, y compris s’il a été éliminé dans la résolution, et lui attribuer le bonus prévu.
3. Si le seuil n’est pas atteint et la manche prend fin, déterminer le score maximal sur tous les joueurs, y compris éliminés, puis enregistrer ce vainqueur et lui attribuer le bonus.
4. Ne choisir aucune issue d’égalité au score maximal : la décision reste ouverte entre victoire partagée et manche supplémentaire. Empêcher qu’un comportement silencieux ou l’ordre des joueurs décide arbitrairement de l’égalité ; le contrat de configuration/implémentation de ce cas attend l’arbitrage.
5. Préserver C1 (trois manches cumulées, tiebreak de partie existant) et C2 (objectif vérifié après la fin de manche et son bonus) comme formats exclusifs.

La priorité v67 de chaîne reste : égalité terminale à zéro survivant ; crédit/contrôle du seuil ; contrôle du dernier survivant ; poursuivre seulement si plusieurs survivants et aucune fin. En mode C, le dernier survivant déclenche la fin de résolution/fin de manche quand le seuil n’est pas atteint, mais ne devient pas de ce fait le gagnant. Une égalité terminale de l’action initiale conserve ses règles actuelles sans point ni bonus pour cette action.

Fichiers : `engine/transitions.py::_decide`, `_succession_a`, `_clockwise_chain`, `_finish_round`, `_threshold_player`, `_leaders`; `rules/rules.py::round_threshold_reached`, helpers C; `engine/state.py::round_winner`, événement `round_finished`. La v67 §6.3 et `specifications/game_flow.md` §§8–10 sont contradictoires avec la nouvelle règle ; leur harmonisation de rédaction doit être une modification séparée explicitement autorisée.

### Étape 6 — Propager les résultats vers campagnes et rapports

Réutiliser `RoundRun.winner_id` et `PlayerRun.round_result`, `round_score`, `round_credited_eliminations` lorsque leur sémantique suffit. Vérifier qu’un joueur déjà éliminé peut être `round_winner` sans être vivant, que son score final de manche inclut le bonus, et que les compteurs d’éliminations restent séparés du score bonus. Étendre les agrégats/colonnes ou le texte Markdown seulement si le résultat utile n’est pas déjà accessible ; préserver la distinction fin de manche / victoire de partie / égalité terminale. Ne jamais exposer les charges utiles secrètes des événements.

Fichiers : `simulation/runner.py::_player_results`, `run_game`, `RoundRun`; `simulation/statistics.py::summarize`; `simulation/reporting.py::write_campaign`; documentation de mesures `simulation/README.md` uniquement si son contrat de mesure devient obsolète.

## 5. Décisions ouvertes et impact sur l’ordre des travaux

| Décision encore ouverte | Classement | Pourquoi / limite d’implémentation |
|---|---|---|
| Égalité au score maximal en fin d’une manche C sans seuil : partage ou manche de départage | **Bloquante pour finaliser l’étape 5 et toute campagne C interprétable** ; reportable pour les autres modes et les étapes 1–4 | Il faut décider comment désigner le ou les gagnants et traiter le bonus. Le tiebreak C1 de fin de partie ne s’applique pas automatiquement à cette égalité de manche. Développer le chemin du score leader avec un cas d’égalité explicitement suspendu est possible ; ne pas le remplacer par un choix de programmation arbitraire. |
| Plusieurs victoires 4C qualifiantes dans un rang partagé | **Reportable pour le cœur non-4C ; bloquante pour terminer le contrat contextuel 4C et la simulation B finale** | Le catalogue permet à plusieurs porteurs de satisfaire le rang, sans fixer si la partie a plusieurs vainqueurs immédiats ni l’ordre d’enregistrement. |
| Maintien d’un objectif générique d’élimination précoce distinct de 4C | **Reportable pendant la mise en conformité ; à résoudre avant une campagne B représentant toutes les cartes** | Le catalogue définit le cas spécial 4C, mais ne tranche pas si l’objectif générique v67 reste une victoire distincte. Ne pas l’ajouter implicitement. |
| Pouvoirs secrets | **Différé ; non bloquant pour la configuration de référence sans pouvoirs** | La v67 renvoie leur conception à une phase ultérieure et aucun effet de référence n’est fourni. Exclure explicitement les pouvoirs des premières campagnes. |

Les seuils et la règle du meilleur score en l’absence de seuil sont validés ; ne pas les requalifier en questions ouvertes. La priorité zéro survivant / seuil / dernier survivant de B est également établie. La simultanéité de franchissement de seuil n’est pas un chemin normal du moteur actuel : les éliminations de chaîne sont traitées une par une et le premier franchissement arrête la chaîne.

## 6. Tests existants vérifiés et tests à prévoir

Les noms ci-dessous sont présents dans les fichiers de tests actuels. Les critères signalés « à créer/adopter » ne sont pas présentés comme déjà testés. Les nouveaux tests doivent rester déterministes par injection directe de cartes et de mains lorsque cela isole le moteur ; les tests de réserve doivent couvrir séparément le tirage physique du catalogue.

### Mise en place, configurations et paquet

**Déjà présents :**

- `tests/test_config.py::test_t55_insufficient_stock_and_impossible_initial_collection_are_rejected` et `test_t78_reference_values_are_scenario_values_not_engine_constants`.
- `tests/test_setup.py::test_t01_reference_deal_and_stock_conservation`, `test_t06_same_configuration_and_seed_reproduce_deal_and_events`, `test_t82_impossible_setup_is_rejected_before_game_creation`, `test_t82_retry_limit_uses_feasible_fallback_after_random_dead_ends`.
- `tests/test_card_pool.py::test_t55_valid_sufficient_pool_distributes_unique_compatible_cards`, `test_t55_impossible_card_subsets_are_filtered_when_usable_subsets_exist`, `test_t55_same_seed_reproduces_card_selection_and_initial_deal`, `test_t55_explicit_card_injection_remains_supported`, `test_t55_new_round_draws_a_fresh_unique_selection_from_the_configured_pool`.

**À créer/adopter :**

- Paramétrer un test de configuration complète aux effectifs 4, 5, 6, 7, 8 avec sac 13×4 et main de trois ; vérifier sommes distribuées/restantes (40, 37, 34, 31, 28 avant reprises), conservation des 52 identifiants et cartes distinctes.
- Ajouter les cinq seuils C et cinq objectifs C2 attendus ; vérifier que la valeur vient de l’effectif initial et ne change pas au fil des éliminations.
- Charger chaque paquet de référence séparément ; vérifier 24 identifiants, 12 variantes ×2, associations et absence de mélange A/C–B. Pour chaque N=4…8, sélectionner N cartes sans doublon, avec même graine même sélection et nouvelle manche nouvel échantillon reproductible.
- Garder des tests d’injection directe N cartes : ils doivent continuer à éviter les tirages du catalogue et à permettre les cas construits irréalisables depuis une réserve.
- Construire des sélections dont une carte est individuellement impossible et des réserves où seules certaines combinaisons sont faisables ; attendre une erreur explicite au bon niveau et aucune sélection aléatoire impossible lorsqu’une combinaison valide existe.
- Vérifier la faisabilité complète de mains 3 jetons pour toutes tailles 4–8 et pour les deux paquets, sans supprimer les contrôles, déclencher des victoires/pertes à l’installation, ou appliquer l’objectif 4C contextuel au setup.

### Conditions, succession et mode C

**Déjà présents :**

- Conditions : `tests/test_config.py::test_t12_color_threshold_below_at_and_above`, `test_t13_two_pairs_explicit_colors_exact_and_minimum`, `test_t14_total_count_counts_all_colors`, et tests de validation/chevauchement T15/T55.
- Succession et pioches : `tests/test_eliminations.py::test_t27_t28_responsible_replay_empty_hand_draw_visibility_and_empty_bag`, `test_t31_clockwise_chain_eliminates_empty_successors_then_selects_next_live_player`; `tests/test_scoring.py::test_t64_t73_variant_b_stops_at_threshold_before_another_successor`, `test_t73_terminal_tie_is_distinct_from_last_survivor_and_preserves_prior_points`, `test_t39_t73_clockwise_chain_continues_and_credits_each_nonterminal_elimination`.
- Score C : `tests/test_scoring.py::test_t35_points_and_counter_for_recipient_eliminated_after_acceptance`, `test_t36_points_and_counter_for_recipient_eliminated_after_refusal_draw`, `test_t40_threshold_bonus_goes_to_responsible_even_if_eliminated`, `test_t41_last_survivor_round_bonus_is_awarded`, `test_t75_terminal_initial_action_does_not_increment_points_or_counters`.
- Modes : `tests/test_modes.py::test_t42_new_round_resets_elimination_counters_but_keeps_scores_and_redeals`, `test_t43_c1_ends_after_three_rounds_using_cumulative_scores`, `test_t44_c1_tiebreak_round_shares_persistent_tie_or_accepts_new_leader`, `test_t46_c2_below_threshold_can_begin_another_round`, `test_t49_c2_terminal_tie_ends_regardless_of_scores`, `test_t62_complete_c2_pilot_finishes_after_elimination_point_and_last_survivor_bonus`.

**À créer/adopter :**

- Exerciser l’acceptation, le refus avec pioche, contrôle donneur on/off et les deux successions en mode C ; vérifier points attribués et motif, compteur, phase, joueur actif et ordre des événements.
- Pour B, couvrir une élimination forcée simple et plusieurs éliminations en chaîne : crédit à l’initiateur même éliminé, contrôle de seuil dès le premier franchissement, arrêt avant l’élimination suivante ; vérifier zéro survivant prioritaire sans point/bonus terminal, et last survivor comme arrêt de chaîne seulement.
- Construire un cas où un joueur éliminé mène au score, seuil non atteint : il doit devenir gagnant C et recevoir le bonus ; le dernier vivant ne gagne pas de façon automatique. C’est le test d’acceptation principal actuellement manquant.
- Construire le cas opposé où le seuil est atteint : le joueur qui l’atteint gagne par seuil et reçoit le bonus même s’il est éliminé ; ne pas substituer le score leader à la règle de seuil.
- Tester actions initiales et chemins de fin par A et B lorsque dernière élimination A/successeur vide conduit à un survivant ; tous doivent arriver au même décideur C. Ne pas changer les règles de succession A en le faisant.
- Pour égalité de score maximal sans seuil, ne figer aucun résultat avant arbitrage. Après décision, ajouter un test pour chacune des options retenues. Le terminal tie à zéro survivant continue d’être couvert indépendamment.
- Tester C1 sur trois manches cumulées et la manche supplémentaire seulement pour égalité finale ; tester C2 si l’objectif est franchi pendant une chaîne, continuer selon les fins de manche, puis vérifier l’objectif après bonus ; vérifier C1/C2 non cumulés.

### Catalogue de cartes et cas 4C

**Déjà présents :** la couverture porte sur des Conditions génériques (`tests/test_config.py`, `tests/test_setup.py`, `tests/test_card_pool.py`) et un objectif secret déterministe (`tests/test_modes.py::test_t61_complete_deterministic_secret_objective_pilot_wins_on_authorized_gift`). Aucun test du catalogue complet ni du rang 4C n’a été trouvé.

**À créer/adopter :**

- Table de vérité par carte : seuil exact/minimum, dessous/au seuil/au-dessus, autres couleurs, toutes partitions DP, pluralité stricte CD, exclusion de défaite propre DP/ACC. Critère : résultat exactement conforme aux exemples et formules du catalogue.
- Validation statique des deux paquets : effectifs, identifiants, variante et association B exacts ; rejeter doublons/mauvais mode et prédicats contradictoires selon la sémantique composée.
- Pour 4C, tester l’élimination due à 4C contre cause différente, barème aux effectifs 4–8, reset du rang à chaque manche, et classement des éliminations groupées. La conséquence multi-vainqueur dépend de la décision ouverte : ne pas écrire le résultat attendu avant arbitrage.
- Tests de non-régression prouvant que les conditions collection ordinaires gardent leur fenêtre de contrôle, qu’aucune victoire n’a lieu au setup pour un futur rang, et que l’élimination révèle la carte au même moment qu’actuellement.

### Simulations, statistiques et exports

**Déjà présents :** `tests/test_simulation.py::test_mode_c_terminal_tie_runs_through_real_runner_stats_and_exports`; `tests/test_simulation_experiments.py::test_mode_c_player_round_records_use_captured_round_end_state_not_final_game_state`, `test_terminal_ties_and_shared_game_wins_remain_separate_from_round_results`, `test_exports_reconcile_player_round_rows_card_counts_and_summary_metrics`, `test_saved_report_contains_campaign_profiles_configurations_and_summary_files`, ainsi que les tests de graine, configuration expérimentale et campagne.

**À créer/adopter :** monter une courte campagne fonctionnelle déterministe (pas une campagne d’équilibrage) où un joueur éliminé est gagnant C faute de seuil. Vérifier :

- `RoundRun.winner_id` et scores de fin après bonus dans `summary.json` et `games.csv::round_summaries_json` ;
- `players.csv` : vainqueur `round_result=round_winner`, `round_eliminated=true`, score cumulé de manche correct, compteurs d’éliminations distincts du bonus ;
- statistiques `round_wins_by_carrier` attribuées à la carte de ce joueur, avec dénominateur des manches terminées explicite ; aucune victoire inventée pour une manche terminale sans résultat ;
- `summary.csv` agrégats et dénominateurs cohérents avec les observations joueurs-manche ; si aucun agrégat de gagnants ou de score de manche utile n’y est présent, ajouter seulement le champ justifié par le besoin analytique ;
- `report.md` décrit correctement les vainqueurs de manche potentiellement éliminés, distingue égalité terminale, victoire partagée et égalité de score de manche non résolue ; ne donne pas le taux de victoire carte comme mesure d’équilibre sans limites/échantillons.

Contrôler aussi qu’aucune couleur d’une pioche secrète (ou charge utile privée générale) n’apparaît dans JSON/CSV/Markdown. Les exports actuels ne sérialisent que les nombres d’événements côté partie ; conserver cette séparation.

## 7. Classement des décisions et dépendances

| Catégorie | Sujets | Précondition / date limite |
|---|---|---|
| Bloquant pour implémenter entièrement le comportement concerné | Égalité de score maximal d’une manche C sans seuil : partage vs manche supplémentaire. | Le chemin unique gagnant au score peut être adapté en isolant le cas, mais le comportement d’égalité et le bonus ne peuvent pas être finalisés sans décision. À trancher avant d’accepter les transitions C et toute campagne finale C. |
| Reportable sans compromettre les autres changements | Plusieurs objectifs 4C admissibles simultanément ; objectif générique d’élimination précoce ; pouvoirs secrets. | Implémenter les cartes non concernées et la règle de score C séparément. Obtenir la décision sur plusieurs 4C avant de déclarer le paquet B complet ; décider sur l’objectif générique avant simulation B complète. Pouvoirs explicitement absents des campagnes initiales. |
| À résoudre avant les simulations finales d’équilibrage | Égalité C sans seuil ; conséquence d’un rang 4C partagé ; maintien ou exclusion de l’objectif générique ; paquet final intégré, profil 4–8 et exports d’acceptation. | Un résultat sans ces décisions ne mesure pas la configuration de référence complète. Pouvoirs exclus si leur report est confirmé par le périmètre de campagne. |

Les décisions déjà validées — B de référence, configurations matérielles, seuils C et classement au score en l’absence de seuil — ne sont pas réouvertes dans ce plan.

## 8. Étapes d’implémentation indépendantes et critères d’acceptation

1. **Contrat de configuration de référence.** Ajouter profil explicite sans modifier les benchmarks ; vérifier effectifs 4–8, sac, main, seuil C/C2, options de succession et visibilité. Acceptation : chaque configuration sérialisée correspond à la référence et au nombre initial.
2. **Réserve physique/catalogue.** Modéliser et construire les deux réserves de 24 ; échantillonnage sans doublon, reproductible, à chaque nouvelle manche ; garder l’injection N cartes. Acceptation : tous paquets et effectifs passent validation/faisabilité complète, aucun paquet hybride.
3. **Expressions de conditions.** Ajouter prédicats composés/exclusions aux données et validateurs puis valider chaque carte du catalogue. Acceptation : table de vérité déterministe et tests absence de chevauchement contraire à l’association.
4. **Objectif 4C.** Ajouter cause/rang et réinitialisation de manche, en laissant la conséquence simultanée conditionnelle à la décision. Acceptation : les cas solo qualifiés gagnent seulement par cause et rang; pas de victoire au setup.
5. **Fin de manche C selon seuil puis score.** Garder l’égalité terminale prioritaire, utiliser seuil, sinon score maximal parmi tous les joueurs, accorder le bonus au gagnant identifié ; suspendre le cas ex aequo jusqu’à arbitrage. Acceptation : tests dédiés actions initiales, A, B, joueur éliminé leader, threshold winner éliminé, zero-survivor tie.
6. **Chaînes C1/C2, nouveaux tours et stats.** Vérifier cumul, reset compteur, cartes/mains renouvelées, C1 tiebreak final, C2 après bonus/fin de manche. Acceptation : aucune fin C2 au milieu d’une action/chaîne ; formats exclusifs.
7. **Runner, agrégats et exports.** Ajouter ou ajuster uniquement les champs justifiés par le résultat C si les structures existantes ne suffisent pas. Acceptation : JSON/CSV/Markdown réconcilient mêmes manches, scores, vainqueur éliminé, bonus, dénominateurs et terminal ties.
8. **Gate de validation fonctionnelle.** Exécuter les tests unitaires, intégration, reproductibilité et non-régression ; vérifier les effectifs 4–8 et les options A/B. Aucune campagne longue avant réussite et résolution des décisions nécessaires.

## 9. Stratégie de validation d’équilibrage (à exécuter plus tard)

1. **Tests fonctionnels et non-régression :** règles, setup faisable, cartes, priorités, options de confidentialité, transitions A/B, C1/C2 et invariants.
2. **Tests d’intégration et d’export :** mêmes résultats confrontés aux événements, `GameRun`/`RoundRun`, statistiques puis JSON, CSV et Markdown ; reproduction avec graines fixes.
3. **Campagnes séparées pour 4, 5, 6, 7, 8 joueurs :** configuration de référence identique à toutes les décisions retenues, profils d’agents équilibrés et documentés, séquences de graines et starters contrôlés. Garder les effectifs, modes, cartes et variantes explicitement étiquetés.
4. **Priorité d’analyse à six joueurs :** examiner ensuite les autres tailles pour détecter interaction entre effectif, seuils, réserve et durée ; ne pas agréger les taux de tailles différentes comme un score unique.
5. **Bras expérimentaux séparés :** comparer A à B, les politiques d’agents et options de visibilité/contrôle du donneur contre le même profil de référence, avec graines appariées. Les profils artificiels actuels ne se substituent pas à la référence.

Indicateurs à examiner : fréquence de victoire par joueur, position, profil et carte ; part des victoires par seuil vs score ; bonus et points d’élimination séparés ; éliminations par cause et rang, y compris 4C ; égalités terminales et partagées ; durée en manches/cadeaux ; fréquence de nouvelles manches, scores finaux et atteinte C2 ; échecs, limites d’actions, tailles d’échantillon et intervalles d’incertitude. Vérifier que les dénominateurs excluent les parties/manches incomplètes comme défini.

Les simulations restent descriptives et conditionnelles aux agents, règles, cartes, positions et graines. Un profil d’agent n’est pas une stratégie optimale ; des différences n’établissent pas la causalité et des taux proches ne prouvent pas l’équilibre. Compléter l’analyse statistique par essais de jeu réel lorsque possible. Aucune conclusion d’équilibre avant que le paquet final, les égalités de manche C, les cas 4C simultanés pertinents et le contenu de campagne soient verrouillés.

## 10. Critères de conformité du moteur

Le moteur pourra être déclaré conforme à la configuration de référence après acceptation documentée de chacun des points suivants :

- profils distincts A/C et B de 24 cartes, stock 52, main trois, nombres 4–8, distribution initiale complète et nouvelle distribution reproductible à chaque manche ;
- les contrôles de setup et d’impossibilité restent actifs et empêchent une partie seulement due à une sélection de paquet inutilisable ; l’injection directe déterministe reste disponible ;
- les prédicats et associations de toutes les cartes correspondent au catalogue, dont causes/rangs 4C selon décisions prises ;
- succession B de référence et A expérimentale, avec contrôles de visibilité et donneur de référence exacts ; aucune fuite publique de secrets ;
- ordre de fin inchangé : égalité terminale d’abord, seuil C ensuite, dernier survivant ensuite ; poursuite seulement sans fin ; points B crédités à la bonne personne et au bon moment ;
- mode C : valeurs de seuil fondées sur l’effectif de début ; premier franchissement gagne par seuil ; sans seuil, meilleur score tous joueurs confondus gagne, même éliminé, et reçoit le bonus ; la branche d’égalité respecte la décision ultérieure ;
- C1/C2 exclusifs ; C1 cumul et départage final préservés ; C2 cible initiale et vérification après fin de manche/bonus ;
- la runner et les exports restituent les gagnants, scores/bonus, éliminations et égalités de manière cohérente et reproductible ; tous les tests pertinents passent, aucun nouveau comportement n’est seulement affirmé dans la matrice sans test réel.

## 11. Fichiers et commandes de vérification consultés

Fichiers principaux vérifiés :

- Règles/documents : `C'est cadeau !.docx` version 67, `specifications/configuration_reference.md`, `specifications/audit_decisions_ouvertes.md`, `specifications/catalogue_cartes_reference.md`, `specifications/game_flow.md`, `specifications/rules_spec.md`, `specifications/audit_final_coherence.md`.
- Configuration/règles : `rules/config.py`, `rules/cards.py`, `rules/card_pool.py`, `rules/rules.py`.
- Moteur : `engine/setup.py`, `engine/state.py`, `engine/transitions.py`, `engine/selection.py`.
- Simulation/export : `simulation/experiments.py`, `simulation/__main__.py`, `simulation/runner.py`, `simulation/statistics.py`, `simulation/reporting.py`, `simulation/README.md`.
- Tests : `tests/test_config.py`, `test_setup.py`, `test_card_pool.py`, `test_gifts.py`, `test_privacy.py`, `test_eliminations.py`, `test_scoring.py`, `test_modes.py`, `test_regressions_point2.py`, `test_simulation.py`, `test_simulation_experiments.py`.

Commandes de repérage utilisées : `rg --files rules engine agents simulation tests specifications`, `rg -n` sur fonctions, exports et noms de tests, lecture ciblée de source/tests et extraction des paragraphes pertinents du document Word. Le plan est préparatoire : aucun test, aucune simulation, campagne, modification moteur ou décision de conception supplémentaire n’est effectué ici.
