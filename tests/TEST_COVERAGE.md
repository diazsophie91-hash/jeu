# Matrice de traçabilité des tests

Cette matrice relie chaque scénario `T01` à `T82` de `specifications/test_plan.md` aux tests automatisés. Les tests composés couvrent plusieurs scénarios voisins dans une même fonction. **82 scénarios sont couverts ; 0 n'est partiel.** Pour T73, le plan a été harmonisé : la branche terminale forcée devenue inaccessible n'est plus exigée d'un test artificiel, et ses cas accessibles ainsi que l'égalité initiale T34/T65 sont vérifiés séparément. Les tests de partie complète sont des pilotes déterministes courts, pas une campagne statistique de simulation.

| Scénario | Tests / fichier | État |
|---|---|---|
| T01 | `test_t01_reference_deal_and_stock_conservation` — `test_setup.py` | Couvert |
| T02 | `test_t02_valid_initial_collection_is_kept_and_game_continues` — `test_setup.py` | Couvert |
| T03 | `test_t03_invalid_initial_collection_is_returned_and_redrawn_privately`; `test_t03_t04_t82_public_setup_events_do_not_expose_cards_or_initial_collections` | Couvert |
| T04 | `test_t04_initial_defeat_condition_only_retries_in_modes_a_and_c`, `test_t04_secret_objective_collection_is_retried_without_declaring_victory`, `test_t04_secret_objective_defeat_collection_is_retried_without_eliminating_player` — `test_setup.py`; `test_t03_t04_t82_public_setup_events_do_not_expose_cards_or_initial_collections` — `test_privacy.py` | Couvert |
| T05 | `test_t05_retries_preserve_unique_token_ids_and_total_count` — `test_setup.py` | Couvert |
| T06 | `test_t06_same_configuration_and_seed_reproduce_deal_and_events` — `test_setup.py` | Couvert |
| T07 | `test_t07_acceptance_transfers_the_single_temporary_token_and_reveals_it` — `test_gifts.py` | Couvert |
| T08 | `test_t08_refusal_returns_offer_and_draws_replacement_with_configured_visibility`; `test_t08_t28_hidden_refusal_draw_is_known_to_recipient_but_not_public` | Couvert |
| T09 | `test_t09_empty_bag_refusal_is_rejected_without_mutation_then_acceptance_is_forced` — `test_gifts.py` | Couvert |
| T10 | `test_t10_gift_can_be_proposed_and_resolved_without_any_messages`, `test_t10_spontaneous_written_claim_is_private_scoped_and_does_not_mutate_rules`, `test_t10_recipient_can_question_and_donor_can_answer_truthfully_or_lie`, `test_t10_messages_are_not_commands_and_cannot_override_empty_bag_refusal_rule`, `test_t10_messages_are_bound_to_the_correct_proposal_and_nonparticipants_cannot_send`, `test_t10_configured_truthful_and_deceptive_agent_claims_use_only_donor_private_view` — `test_communication.py`; `test_t10_t63_agents_execute_spontaneous_question_lie_response_and_silence_strategies`, `test_t10_agent_can_ask_a_question_and_choose_not_to_answer`, `test_t63_agents_receive_filtered_views_and_only_their_messages` — `test_simulation.py` | Couvert : messages écrits privés et rattachés à la proposition, silence, annonce, question, réponse, mensonge/vérité configurés et séparation d'avec les commandes. |
| T11 | `test_t11_invalid_recipient_and_wrong_phase_preserve_state` — `test_gifts.py` | Couvert |
| T12 | Seuils — `test_t12_color_threshold_below_at_and_above`; élimination — `test_t12_t14_t23_elimination_reveals_card_and_returns_remaining_hand` | Couvert |
| T13 | `test_t13_two_pairs_explicit_colors_exact_and_minimum`, `test_t13_two_pairs_any_distinct_colors_and_imposed_colors` — `test_config.py` | Couvert |
| T14 | `test_t14_total_count_counts_all_colors`; résolution — `test_t12_t14_t23_elimination_reveals_card_and_returns_remaining_hand` | Couvert |
| T15 | `test_t15_multiple_satisfied_defeat_conditions_eliminate_once_through_engine_api` — `test_eliminations.py`; `test_t15_setup_retries_when_any_of_multiple_defeat_conditions_matches` — `test_setup.py` | Couvert : deux conditions simultanément satisfaites, retour de jetons, score, révélation et succession uniques ; nouvelle tentative privée à la préparation. |
| T16 | `test_t16_donor_removal_defeat_is_checked_before_decision_when_enabled`, `test_t16_disabled_donor_removal_check_does_not_eliminate_donor` — `test_gifts.py` | Couvert |
| T17 | `test_t17_secret_victory_after_accepted_gift_stops_resolution_immediately` — `test_gifts.py` | Couvert |
| T18 | `test_t18_secret_victory_after_refusal_draw_stops_all_later_resolution` — `test_gifts.py` | Couvert |
| T19 | `test_t19_variant_a_responsible_replay_draw_checks_secret_victory_first` — `test_eliminations.py` | Couvert |
| T20 | `test_t20_removing_token_does_not_trigger_donors_secret_victory` — `test_eliminations.py` | Couvert |
| T21 | `test_t21_last_survivor_wins_secret_mode_without_personal_objective` — `test_eliminations.py` | Couvert |
| T22 | `test_t22_and_t55_cards_must_match_selected_mode_and_player_count`, `test_t22_unknown_color_and_unconfigured_majority_are_rejected`, `test_t22_unknown_condition_kind_and_bad_parameter_types_fail_at_construction` — `test_config.py` | Couvert |
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
| T45 | `test_t45_t48_c2_threshold_is_resolved_only_after_round_bonus`, `test_t45_threshold_reached_during_round_does_not_end_it_immediately` — `test_scoring.py` | Couvert |
| T46 | `test_t46_c2_below_threshold_can_begin_another_round` — `test_modes.py`; `test_t46_c2_below_threshold_starts_another_round_and_preserves_score` — `test_scoring.py` | Couvert |
| T47 | `test_t47_c2_ranks_final_scores_not_first_threshold_player` — `test_scoring.py` | Couvert |
| T48 | `test_t45_t48_c2_threshold_is_resolved_only_after_round_bonus` — `test_scoring.py` | Couvert |
| T49 | `test_t49_c2_terminal_tie_ends_regardless_of_scores` — `test_modes.py` | Couvert |
| T50 | Unicité et invariants — tests d’actions, `test_t50_t51_t54_event_order_and_public_history_redacts_hidden_offer` — `test_privacy.py` | Couvert |
| T51 | Conservation et invariants — `test_setup.py`, `test_gifts.py`, `test_eliminations.py`, `test_privacy.py` | Couvert |
| T52 | `test_t52_eliminated_player_cannot_be_selected_or_act` — `test_eliminations.py` | Couvert |
| T53 | `test_t53_t58_action_after_terminal_end_is_rejected_without_changing_result` — `test_eliminations.py` | Couvert |
| T54 | `test_t50_t51_t54_event_order_and_public_history_redacts_hidden_offer`; révélation — `test_privacy.py` | Couvert |
| T55 | `test_t55_valid_sufficient_pool_distributes_unique_compatible_cards`, `test_t55_insufficient_pool_is_rejected_before_setup`, `test_t55_duplicate_card_ids_are_rejected`, `test_t55_mode_incompatible_pool_card_is_rejected`, `test_t55_invalid_contradictory_card_in_pool_is_rejected`, `test_t55_declared_reserve_composition_is_checked`, `test_t55_same_seed_reproduces_card_selection_and_initial_deal`, `test_t55_distribution_never_duplicates_a_card`, `test_t55_explicit_card_injection_remains_supported`, `test_t55_new_round_draws_a_fresh_unique_selection_from_the_configured_pool` — `test_card_pool.py`; `test_t15_t55_multiple_defeat_collection_and_card_fields_are_validated`, `test_t15_t55_victory_contradiction_is_checked_against_every_defeat_condition`, `test_t55_insufficient_stock_and_impossible_initial_collection_are_rejected` — `test_config.py` | Couvert : réserve déclarée par familles (deux conditions par famille), capacité, identifiants, validité/compatibilité, composition, graine, distribution sans doublon, nouvelle manche et injection directe maintenue. |
| T56 | `test_t30_t56_clockwise_succession_skips_eliminated_positions` — `test_eliminations.py` | Couvert |
| T57 | `test_t09_empty_bag_refusal_is_rejected_without_mutation_then_acceptance_is_forced` — `test_gifts.py`; `test_t31_clockwise_chain_eliminates_empty_successors_then_selects_next_live_player`, `test_t71_empty_successor_with_empty_common_bag_is_eliminated_then_succession_continues` — `test_eliminations.py`; égalité initiale sans survivant — `test_initial_resolution_eliminating_everyone_is_terminal_tie_without_awards` — `test_regressions_point2.py` | Couvert |
| T58 | `test_t11_invalid_recipient_and_wrong_phase_preserve_state`; `test_t53_t58_action_after_terminal_end_is_rejected_without_changing_result` | Couvert |
| T59 | `test_t82_retry_limit_exhaustion_is_explicit_and_keeps_cards_private` — `test_setup.py`; `test_t31_clockwise_chain_eliminates_empty_successors_then_selects_next_live_player` — `test_eliminations.py`; `test_t39_t73_clockwise_chain_continues_and_credits_each_nonterminal_elimination` — `test_scoring.py` | Couvert |
| T60 | `test_t60_complete_deterministic_last_survivor_pilot_terminates` — `test_modes.py` | Couvert |
| T61 | `test_t61_complete_deterministic_secret_objective_pilot_wins_on_authorized_gift` — `test_modes.py` | Couvert |
| T62 | `test_t62_complete_c2_pilot_finishes_after_elimination_point_and_last_survivor_bonus`, `test_t43_c1_ends_after_three_rounds_using_cumulative_scores` — `test_modes.py` | Couvert |
| T63 | `test_t63_complete_game_uses_controller_api_and_reproduces_with_same_seed`, `test_t63_campaign_records_configuration_seed_strategies_and_descriptive_statistics`, `test_t63_agents_receive_filtered_views_and_only_their_messages`, `test_t63_invariant_failures_and_action_limits_are_reported_explicitly`, `test_t63_campaign_can_record_failures_without_mixing_them_into_completed_statistics` — `test_simulation.py`; `test_t63_variant_comparison_is_recorded_as_distinct_explicit_configurations` — `test_modes.py` | Couvert : parties déterministes reproductibles, options de règles configurables, profils d'agents séparés, résultats/stratégies/graines enregistrés, statistiques descriptives et erreurs explicites. Les campagnes longues restent séparées de pytest. |
| T64 | `test_t64_t73_variant_b_stops_at_threshold_before_another_successor`; régression — `test_regressions_point2.py` | Couvert |
| T65 | Régression `test_initial_resolution_eliminating_everyone_is_terminal_tie_without_awards`; `test_t75_terminal_initial_action_does_not_increment_points_or_counters` | Couvert |
| T66 | `test_t66_t68_donor_elimination_is_not_undone_by_refusal_or_repeated`, `test_t16_donor_removal_defeat_is_checked_before_decision_when_enabled` — `test_gifts.py` | Couvert |
| T67 | `test_t67_accept_after_donor_elimination_transfers_temporary_token`, `test_t77_secret_victory_after_donor_self_elimination_stops_resolution` — `test_gifts.py` | Couvert |
| T68 | `test_t16_disabled_donor_removal_check_does_not_eliminate_donor`; `test_t77_disabling_donor_removal_check_does_not_block_recipient_victory` | Couvert |
| T69 | `test_t69_elimination_returns_only_personal_tokens_and_keeps_offer_temporary` — `test_gifts.py` | Couvert |
| T70 | `test_t70_empty_successor_draws_and_survives_with_configured_visibility` — `test_eliminations.py` | Couvert |
| T71 | `test_t71_empty_successor_with_empty_common_bag_is_eliminated_then_succession_continues` — `test_eliminations.py` | Couvert |
| T72 | `test_t72_clockwise_variant_makes_surviving_recipient_active_after_donor_elimination` — `test_eliminations.py` | Couvert |
| T73 | `test_t39_t73_clockwise_chain_continues_and_credits_each_nonterminal_elimination`; seuil — `test_t64_t73_variant_b_stops_at_threshold_before_another_successor`; dernier survivant — `test_variant_b_stops_at_last_survivor_and_awards_expected_points_and_bonus`; égalité et conservation — `test_t73_terminal_tie_is_distinct_from_last_survivor_and_preserves_prior_points` | Couvert après harmonisation : les branches accessibles sont testées. Le plan précise qu'une chaîne unitaire s'arrête au seuil ou au dernier survivant ; l'égalité terminale initiale conserve ses points antérieurs et reste distincte (T34/T65). |
| T74 | `test_t74_c2_normal_end_shares_tie_for_highest_total_score` — `test_scoring.py` | Couvert |
| T75 | `test_t75_terminal_initial_action_does_not_increment_points_or_counters`; tests de crédit — `test_scoring.py` | Couvert |
| T76 | `test_t76_only_recipient_gets_possible_common_colors_not_exact_contents` — `test_privacy.py` | Couvert |
| T77 | `test_t77_secret_victory_after_donor_self_elimination_stops_resolution`, `test_t77_disabling_donor_removal_check_does_not_block_recipient_victory` — `test_gifts.py` | Couvert |
| T78 | `test_t78_reference_values_are_scenario_values_not_engine_constants` — `test_config.py`; distribution T01 | Couvert |
| T79 | `test_t79_collective_choice_is_explicit_and_transmitted_to_engine`, `test_t79_recency_tie_resolution_is_audited_in_setup_history`, `test_t79_most_recent_real_gift_selects_unique_latest_recipient`, `test_t79_recency_tie_requires_explicit_consensus_or_resolver`, `test_t79_unknown_player_is_rejected`, `test_t79_recency_requires_data_for_every_participant`, `test_t79_existing_direct_first_player_api_remains_compatible` — `test_selection.py`; `test_t79_first_player_is_explicit_and_engine_does_not_derive_a_tie_break` — `test_privacy.py` | Couvert : choix collectif, récence, égalité nécessitant un consensus, validation des participants, trace d'audit et API `first_player_id` compatible. |
| T80 | `test_t80_empty_successor_draw_triggers_secret_victory_before_defeat` — `test_eliminations.py` | Couvert |
| T81 | `test_t81_refusal_after_donor_elimination_can_draw_offer_or_existing_bag_token` — `test_gifts.py` | Couvert |
| T82 | `test_t82_impossible_setup_is_rejected_before_game_creation`, `test_t82_retry_limit_exhaustion_is_explicit_and_keeps_cards_private` — `test_setup.py`; `test_t03_t04_t82_public_setup_events_do_not_expose_cards_or_initial_collections` — `test_privacy.py` | Couvert |

## Limites de périmètre

- Les tests pytest restent rapides et déterministes. `simulation.run_campaign` permet des campagnes distinctes avec plus de graines ; aucune conclusion d'équilibrage n'est tirée sans données suffisantes.
- Les agents et simulations forment une base fonctionnelle du point 4. Les agents LLM, l'apprentissage, les stratégies avancées et les campagnes longues n'en font pas partie.
