# Matrice de traçabilité des tests

Cette matrice relie chaque scénario `T01` à `T82` de `specifications/test_plan.md` aux tests automatisés. Les tests composés couvrent plusieurs scénarios voisins dans une même fonction. **76 scénarios sont couverts dans le périmètre du moteur ; 6 sont partiels**, avec leur limite explicitée ci-dessous. Les tests de partie complète sont des pilotes déterministes courts, pas une campagne statistique de simulation.

| Scénario | Tests / fichier | État |
|---|---|---|
| T01 | `test_t01_reference_deal_and_stock_conservation` — `test_setup.py` | Couvert |
| T02 | `test_t02_valid_initial_collection_is_kept_and_game_continues` — `test_setup.py` | Couvert |
| T03 | `test_t03_invalid_initial_collection_is_returned_and_redrawn_privately`; `test_t03_t04_t82_public_setup_events_do_not_expose_cards_or_initial_collections` | Couvert |
| T04 | `test_t04_*` — `test_setup.py`; confidentialité de préparation — `test_privacy.py` | Couvert |
| T05 | `test_t05_retries_preserve_unique_token_ids_and_total_count` — `test_setup.py` | Couvert |
| T06 | `test_t06_same_configuration_and_seed_reproduce_deal_and_events` — `test_setup.py` | Couvert |
| T07 | `test_t07_acceptance_transfers_the_single_temporary_token_and_reveals_it` — `test_gifts.py` | Couvert |
| T08 | `test_t08_refusal_returns_offer_and_draws_replacement_with_configured_visibility`; `test_t08_t28_hidden_refusal_draw_is_known_to_recipient_but_not_public` | Couvert |
| T09 | `test_t09_empty_bag_refusal_is_rejected_without_mutation_then_acceptance_is_forced` — `test_gifts.py` | Couvert |
| T10 | `test_t10_announcements_are_not_engine_actions_and_true_token_identity_is_authoritative` — `test_gifts.py` | Partiel : le moteur n’a pas d’API d’annonce verbale ; le test vérifie l’identité réelle du jeton et sa révélation. |
| T11 | `test_t11_invalid_recipient_and_wrong_phase_preserve_state` — `test_gifts.py` | Couvert |
| T12 | Seuils — `test_t12_color_threshold_below_at_and_above`; élimination — `test_t12_t14_t23_elimination_reveals_card_and_returns_remaining_hand` | Couvert |
| T13 | `test_t13_*` — `test_config.py` | Couvert |
| T14 | `test_t14_total_count_counts_all_colors`; résolution — `test_t12_t14_t23_elimination_reveals_card_and_returns_remaining_hand` | Couvert |
| T15 | `test_t15_single_resolution_eliminates_a_player_only_once` — `test_eliminations.py` | Partiel : une élimination unique est vérifiée ; `Card` ne permet qu’une condition de défaite, donc pas de combinaison simultanée de plusieurs conditions. |
| T16 | `test_t16_*` — `test_gifts.py` | Couvert |
| T17 | `test_t17_secret_victory_after_accepted_gift_stops_resolution_immediately` — `test_gifts.py` | Couvert |
| T18 | `test_t18_secret_victory_after_refusal_draw_stops_all_later_resolution` — `test_gifts.py` | Couvert |
| T19 | `test_t19_variant_a_responsible_replay_draw_checks_secret_victory_first` — `test_eliminations.py` | Couvert |
| T20 | `test_t20_removing_token_does_not_trigger_donors_secret_victory` — `test_eliminations.py` | Couvert |
| T21 | `test_t21_last_survivor_wins_secret_mode_without_personal_objective` — `test_eliminations.py` | Couvert |
| T22 | `test_t22_*` — `test_config.py` | Couvert |
| T23 | `test_t12_t14_t23_elimination_reveals_card_and_returns_remaining_hand` — `test_eliminations.py` | Couvert |
| T24 | Acceptation et passage du tour — `test_t07_acceptance_transfers_the_single_temporary_token_and_reveals_it` | Couvert |
| T25 | `test_t25_variant_a_replays_responsible_after_recipient_elimination` — `test_eliminations.py` | Couvert |
| T26 | `test_t26_variant_a_uses_surviving_recipient_when_donor_was_eliminated` — `test_eliminations.py` | Couvert |
| T27 | `test_t27_t28_responsible_replay_empty_hand_draw_visibility_and_empty_bag` — `test_eliminations.py` | Couvert |
| T28 | `test_t27_t28_responsible_replay_empty_hand_draw_visibility_and_empty_bag`; confidentialité — `test_privacy.py` | Couvert |
| T29 | `test_t29_replay_draw_elimination_has_no_separate_point` — `test_eliminations.py` | Couvert |
| T30 | `test_t30_t56_clockwise_succession_skips_eliminated_positions` — `test_eliminations.py` | Couvert |
| T31 | `test_t31_clockwise_chain_eliminates_empty_successors_then_selects_next_live_player` — `test_eliminations.py` | Couvert |
| T32 | `test_t32_donor_and_recipient_elimination_resolves_before_successor_selection` — `test_eliminations.py` | Couvert |
| T33 | `test_t33_all_initial_eliminations_precede_turn_selection` — `test_eliminations.py` | Couvert |
| T34 | `test_initial_resolution_eliminating_everyone_is_terminal_tie_without_awards` — `test_regressions_point2.py` | Couvert |
| T35 | `test_t35_points_and_counter_for_recipient_eliminated_after_acceptance` — `test_scoring.py` | Couvert |
| T36 | `test_t36_points_and_counter_for_recipient_eliminated_after_refusal_draw` — `test_scoring.py` | Couvert |
| T37 | `test_t37_donor_auto_elimination_does_not_award_a_point` — `test_scoring.py` | Couvert |
| T38 | `test_t38_eliminated_donor_still_receives_opponent_point_unless_action_is_terminal` — `test_scoring.py` | Couvert |
| T39 | `test_t39_t73_clockwise_chain_continues_and_credits_each_nonterminal_elimination` — `test_scoring.py` | Couvert |
| T40 | `test_t40_threshold_bonus_goes_to_responsible_even_if_eliminated` — `test_scoring.py` | Couvert |
| T41 | `test_t41_last_survivor_round_bonus_is_awarded` — `test_scoring.py` | Couvert |
| T42 | `test_t42_new_round_resets_elimination_counters_but_keeps_scores_and_redeals` — `test_modes.py` | Couvert |
| T43 | `test_t43_c1_ends_after_three_rounds_using_cumulative_scores` — `test_modes.py` | Couvert |
| T44 | `test_t44_c1_tiebreak_round_shares_persistent_tie_or_accepts_new_leader` — `test_modes.py` | Couvert |
| T45 | `test_t45_*` — `test_scoring.py` | Couvert |
| T46 | `test_t46_*` — `test_modes.py`, `test_scoring.py` | Couvert |
| T47 | `test_t47_c2_ranks_final_scores_not_first_threshold_player` — `test_scoring.py` | Couvert |
| T48 | `test_t45_t48_c2_threshold_is_resolved_only_after_round_bonus` — `test_scoring.py` | Couvert |
| T49 | `test_t49_c2_terminal_tie_ends_regardless_of_scores` — `test_modes.py` | Couvert |
| T50 | Unicité et invariants — tests d’actions, `test_t50_t51_t54_event_order_and_public_history_redacts_hidden_offer` — `test_privacy.py` | Couvert |
| T51 | Conservation et invariants — `test_setup.py`, `test_gifts.py`, `test_eliminations.py`, `test_privacy.py` | Couvert |
| T52 | `test_t52_eliminated_player_cannot_be_selected_or_act` — `test_eliminations.py` | Couvert |
| T53 | `test_t53_t58_action_after_terminal_end_is_rejected_without_changing_result` — `test_eliminations.py` | Couvert |
| T54 | `test_t50_t51_t54_event_order_and_public_history_redacts_hidden_offer`; révélation — `test_privacy.py` | Couvert |
| T55 | `test_t22_and_t55_*`; `test_t55_insufficient_stock_and_impossible_initial_collection_are_rejected` — `test_config.py` | Partiel : les validations de structure, compatibilité et stock sont testées ; le moteur reçoit les cartes injectées et ne gère pas de paquet physique à inventorier. |
| T56 | `test_t30_t56_clockwise_succession_skips_eliminated_positions` — `test_eliminations.py` | Couvert |
| T57 | Cas sac personnel/sac commun vides — `test_t09_*`, `test_t31_*`, `test_t71_*`; égalité sans survivant — régression T34 | Couvert |
| T58 | `test_t11_invalid_recipient_and_wrong_phase_preserve_state`; `test_t53_t58_action_after_terminal_end_is_rejected_without_changing_result` | Couvert |
| T59 | Limite de tentatives — `test_t82_retry_limit_exhaustion_is_explicit_and_keeps_cards_private`; chaînes — `test_t31_*`, `test_t39_*` | Couvert |
| T60 | `test_t60_complete_deterministic_last_survivor_pilot_terminates` — `test_modes.py` | Couvert |
| T61 | `test_t61_complete_deterministic_secret_objective_pilot_wins_on_authorized_gift` — `test_modes.py` | Couvert |
| T62 | `test_t62_complete_c2_pilot_finishes_after_elimination_point_and_last_survivor_bonus`; C1 — `test_t43_*` | Couvert |
| T63 | `test_t63_variant_comparison_is_recorded_as_distinct_explicit_configurations` — `test_modes.py` | Partiel : comparaison déterministe A/B ; pas de comparaison statistique, ni de matrice complète des options transversales. |
| T64 | `test_t64_t73_variant_b_stops_at_threshold_before_another_successor`; régression — `test_regressions_point2.py` | Couvert |
| T65 | Régression `test_initial_resolution_eliminating_everyone_is_terminal_tie_without_awards`; `test_t75_terminal_initial_action_does_not_increment_points_or_counters` | Couvert |
| T66 | `test_t66_t68_donor_elimination_is_not_undone_by_refusal_or_repeated`; `test_t16_*` — `test_gifts.py` | Couvert |
| T67 | `test_t67_accept_after_donor_elimination_transfers_temporary_token`; `test_t77_*` — `test_gifts.py` | Couvert |
| T68 | `test_t16_disabled_donor_removal_check_does_not_eliminate_donor`; `test_t77_disabling_donor_removal_check_does_not_block_recipient_victory` | Couvert |
| T69 | `test_t69_elimination_returns_only_personal_tokens_and_keeps_offer_temporary` — `test_gifts.py` | Couvert |
| T70 | `test_t70_empty_successor_draws_and_survives_with_configured_visibility` — `test_eliminations.py` | Couvert |
| T71 | `test_t71_empty_successor_with_empty_common_bag_is_eliminated_then_succession_continues` — `test_eliminations.py` | Couvert |
| T72 | `test_t72_clockwise_variant_makes_surviving_recipient_active_after_donor_elimination` — `test_eliminations.py` | Couvert |
| T73 | `test_t39_t73_clockwise_chain_continues_and_credits_each_nonterminal_elimination`; seuil — `test_t64_t73_variant_b_stops_at_threshold_before_another_successor` | Partiel : continuation et arrêt au seuil couverts. La sous-branche « élimination forcée terminale de la chaîne » n’est pas atteignable telle que formulée : la résolution s’arrête dès qu’il reste un seul survivant ; l’égalité terminale directe est couverte en T34/T65. |
| T74 | `test_t74_c2_normal_end_shares_tie_for_highest_total_score` — `test_scoring.py` | Couvert |
| T75 | `test_t75_terminal_initial_action_does_not_increment_points_or_counters`; tests de crédit — `test_scoring.py` | Couvert |
| T76 | `test_t76_only_recipient_gets_possible_common_colors_not_exact_contents` — `test_privacy.py` | Couvert |
| T77 | `test_t77_*` — `test_gifts.py` | Couvert |
| T78 | `test_t78_reference_values_are_scenario_values_not_engine_constants` — `test_config.py`; distribution T01 | Couvert |
| T79 | `test_t79_first_player_is_explicit_and_engine_does_not_derive_a_tie_break` — `test_privacy.py` | Partiel : le moteur exige un premier joueur fourni ; l’accord du groupe et le critère du cadeau récent relèvent du choix humain, hors moteur. |
| T80 | `test_t80_empty_successor_draw_triggers_secret_victory_before_defeat` — `test_eliminations.py` | Couvert |
| T81 | `test_t81_refusal_after_donor_elimination_can_draw_offer_or_existing_bag_token` — `test_gifts.py` | Couvert |
| T82 | `test_t82_*` — `test_setup.py`; confidentialité — `test_privacy.py` | Couvert |

## Limites de périmètre

- Aucun composant de simulation de production, agent autonome, interface d’annonce orale ou gestion physique d’un paquet de cartes n’est implémenté par cette suite.
- Les scénarios T60–T62 sont des parties pilotes déterministes utilisant l’API normale du moteur ; ils valident leur terminaison et leurs invariants sans prétendre mesurer des fréquences ou équilibres statistiques.
- Les six lignes partielles sont T10, T15, T55, T63, T73 et T79. Elles correspondent aux limites explicitées dans le tableau, pas à des tests omis silencieusement.
