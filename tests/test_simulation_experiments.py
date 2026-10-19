import json
import csv
from dataclasses import replace

import pytest

from agents import (CommunicationChannel, CommunicationIntent, CommunicationKind,
                    RandomDecision, ReferenceDecision)
from engine.actions import ChooseRecipient, ProposeGift, RefuseGift
from engine import create_game
from rules import GameMode
from simulation.experiments import benchmark_config, communication_profiles, reference_configurations
from simulation.reporting import write_campaign
from simulation.runner import AgentPolicy, CampaignRun, run_campaign, run_game
from simulation.statistics import summarize, wilson_interval


PLAYER_IDS = ("a", "b", "c", "d")


def policies(decision):
    return {player_id: AgentPolicy(decision) for player_id in PLAYER_IDS}


def test_random_agent_and_campaign_reproduce_per_game_seed_independent_of_run_order():
    config = benchmark_config(GameMode.LAST_SURVIVOR)
    first = run_game(config, PLAYER_IDS, seed=911, first_player_id="a",
                     policies=policies(RandomDecision()))
    run_game(config, PLAYER_IDS, seed=912, first_player_id="b", policies=policies(RandomDecision()))
    repeated = run_game(config, PLAYER_IDS, seed=911, first_player_id="a",
                        policies=policies(RandomDecision()))
    assert first == repeated
    assert first.duration_seconds >= 0
    assert first.turns > 0 and first.actions == 3 * first.turns


def test_agent_actions_are_legal_and_views_do_not_expose_hidden_opponent_cards():
    observations = []

    class Observer:
        name = "observer"

        def choose_action(self, view, legal_actions, messages):
            assert legal_actions
            assert isinstance(view.hand, tuple)
            observations.append((view.player_id, view.offered_token, view.public.phase,
                                 view.public.proposal,
                                 tuple(player.revealed_card for player in view.public.players)))
            refusal = next((action for action in legal_actions if isinstance(action, RefuseGift)), None)
            return refusal or legal_actions[0]

    config = benchmark_config(GameMode.LAST_SURVIVOR)
    run = run_game(config, PLAYER_IDS, seed=47, first_player_id="a",
                   policies={pid: AgentPolicy(Observer()) for pid in PLAYER_IDS}, max_actions=300)
    assert run.status == "completed"
    assert observations
    initial = observations[0]
    assert all(card is None for card in initial[4])
    assert all(offered is None for player_id, offered, phase, proposal, _ in observations
               if phase.value == "decision" and proposal is not None and proposal[1] == player_id)


def test_game_and_player_records_include_reproducibility_and_card_measurements():
    config = benchmark_config(GameMode.LAST_SURVIVOR)
    run = run_game(config, PLAYER_IDS, seed=82, first_player_id="c",
                   policies=policies(ReferenceDecision()))
    assert run.status == "completed"
    assert run.experience_name == "experiment"
    assert run.configuration["mode"] == "A"
    assert run.configuration["first_player_id"] == "c"
    assert run.first_player_event.data["player_id"] == "c"
    assert len(run.players) == len(PLAYER_IDS)
    assert sum(player.started_game for player in run.players) == 1
    assert all(player.card_id and player.defeat_families and player.decision_profile == "reference"
               for player in run.players)
    assert all(player.round_elimination_reason is None or player.round_eliminated for player in run.players)
    assert run.round_summaries == ()
    assert all(player.round_score is None and player.round_result is None for player in run.players)


def test_mode_c_player_round_records_use_captured_round_end_state_not_final_game_state():
    run = run_game(benchmark_config(GameMode.POINTS), PLAYER_IDS, seed=20261016,
                   first_player_id="a", policies=policies(ReferenceDecision()))
    assert run.rounds == run.rounds_completed == 3
    assert run.outcome == "fixed_rounds" and run.winners == ("c",)
    assert [(r.round_number, r.winner_id, r.scores, r.credited_eliminations)
            for r in run.round_summaries] == [
        (1, "d", {"a": 0, "b": 0, "c": 0, "d": 2}, {"a": 0, "b": 0, "c": 0, "d": 1}),
        (2, "c", {"a": 0, "b": 0, "c": 2, "d": 2}, {"a": 0, "b": 0, "c": 1, "d": 0}),
        (3, "c", {"a": 0, "b": 0, "c": 4, "d": 2}, {"a": 0, "b": 0, "c": 1, "d": 0}),
    ]
    by_player_round = {(row.player_id, row.round_number): row for row in run.players}
    c_round_1 = by_player_round["c", 1]
    d_round_1 = by_player_round["d", 1]
    d_round_2 = by_player_round["d", 2]
    assert (c_round_1.card_id, c_round_1.round_result, c_round_1.round_score,
            c_round_1.round_credited_eliminations) == (
                "C-experimental-3", "round_non_winner", 0, 0)
    assert (c_round_1.game_result, c_round_1.game_player_result, c_round_1.game_final_score,
            c_round_1.game_final_credited_eliminations) == ("fixed_rounds", "winner", 4, 1)
    assert (d_round_1.card_id, d_round_1.round_result, d_round_1.round_score,
            d_round_1.round_credited_eliminations, d_round_1.game_player_result) == (
                "C-experimental-4", "round_winner", 2, 1, "non_winner")
    assert (d_round_2.card_id, d_round_2.round_eliminated,
            d_round_2.round_elimination_reason, d_round_2.round_elimination_turn,
            d_round_2.round_turns_played, d_round_2.round_score,
            d_round_2.round_credited_eliminations) == (
                "C-experimental-1", True, "refusal_draw", 2, 0, 2, 0)
    assert all(row.round_score == run.round_summaries[row.round_number - 1].scores[row.player_id]
               for row in run.players)
    assert all(row.round_credited_eliminations ==
               run.round_summaries[row.round_number - 1].credited_eliminations[row.player_id]
               for row in run.players)

    card_stats = summarize(CampaignRun((run,))).by_configuration["default"]["cards"]
    assert card_stats["C-experimental-3"]["game_wins_by_carrier"] is None
    assert card_stats["C-experimental-3"]["game_carrier_win_rate"] is None
    assert card_stats["C-experimental-3"]["round_wins_by_carrier"] == 0
    assert card_stats["C-experimental-3"]["round_win_denominator"] == 3
    assert card_stats["C-experimental-4"]["round_wins_by_carrier"] == 1


@pytest.mark.parametrize("mode", [GameMode.LAST_SURVIVOR, GameMode.SECRET_OBJECTIVE])
def test_modes_a_and_b_keep_single_round_carrier_game_win_measure(mode):
    config = benchmark_config(mode)
    campaign = run_campaign({f"mode-{mode.value}": config}, PLAYER_IDS,
                            seeds=(20261016, 20261017, 20261018),
                            policy_profiles={"reference": policies(ReferenceDecision())})
    assert len(campaign.runs) == 3 and not campaign.failures
    for run in campaign.runs:
        assert run.rounds == 1
        assert run.round_summaries == ()
        assert all(score is None for score in run.final_scores.values())
        assert all(value is None for value in run.final_credited_eliminations.values())
        assert all(row.round_result is None and row.round_score is None for row in run.players)
        assert all(row.game_final_score is None and row.game_final_credited_eliminations is None
                   for row in run.players)
        if mode is GameMode.SECRET_OBJECTIVE:
            assert run.outcome == "secret_objective" and len(run.winners) == 1
        for row in run.players:
            expected_result = ("winner" if len(run.winners) == 1 else "shared_winner") \
                if row.player_id in run.winners else "non_winner"
            assert row.game_player_result == expected_result
    stats = summarize(campaign).by_configuration[f"mode-{mode.value}::reference"]
    for card_id, card in stats["cards"].items():
        source_rows = [row for run in campaign.runs for row in run.players if row.card_id == card_id]
        expected_wins = sum(row.game_player_result in {"winner", "shared_winner"}
                             for row in source_rows)
        assert card["game_wins_by_carrier"] == expected_wins
        assert card["game_win_denominator"] == len(source_rows)
        assert card["round_wins_by_carrier"] is None
        assert card["round_win_denominator"] is None


def test_terminal_ties_and_shared_game_wins_remain_separate_from_round_results():
    config = benchmark_config(GameMode.POINTS)
    tied_run = run_game(config, PLAYER_IDS, seed=20261016, first_player_id="a",
                        policies=policies(ReferenceDecision()))
    tied_players = tuple(replace(row, game_result="terminal_tie", game_player_result="tied",
                                 round_result=None, round_completed=False, round_score=None,
                                 round_credited_eliminations=None)
                         for row in tied_run.players)
    terminal_tie = replace(tied_run, outcome="terminal_tie", winners=(), terminal_ties=1,
                           score_ties=0, players=tied_players)
    shared_run = run_game(config, PLAYER_IDS, seed=20261017, first_player_id="b",
                          policies=policies(ReferenceDecision()))
    assert len(shared_run.winners) == 3
    stats = summarize(CampaignRun((terminal_tie, shared_run))).by_configuration
    tie_summary = stats["default"]
    assert tie_summary["terminal_tie_games"] == 1
    assert tie_summary["shared_victory_games"] == 1
    assert tie_summary["winner_appearances"] == {player: 1 for player in shared_run.winners}
    assert tie_summary["by_agent_profile_game"]["reference+silent"]["appearances"] == 8
    assert tie_summary["by_agent_profile_game"]["reference+silent"]["wins"] == 3
    assert tie_summary["cards"]["C-experimental-1"]["game_carrier_win_rate"] is None
    assert all(row.round_result is None for row in tied_players)


def test_exports_reconcile_player_round_rows_card_counts_and_summary_metrics(tmp_path):
    config = benchmark_config(GameMode.POINTS)
    campaign = run_campaign({"C": config}, PLAYER_IDS, seeds=(20261016, 20261017),
                            policy_profiles={"reference": policies(ReferenceDecision())})
    stats = summarize(campaign)
    output = write_campaign(campaign, stats, tmp_path / "validated-report")
    with (output / "players.csv").open(encoding="utf-8", newline="") as stream:
        players_csv = list(csv.DictReader(stream))
    with (output / "games.csv").open(encoding="utf-8", newline="") as stream:
        games_csv = list(csv.DictReader(stream))
    with (output / "summary.csv").open(encoding="utf-8", newline="") as stream:
        summary_csv = list(csv.DictReader(stream))
    saved = json.loads((output / "summary.json").read_text(encoding="utf-8"))
    expected_rows = sum(len(run.players) for run in campaign.runs)
    assert len(players_csv) == expected_rows == sum(run.rounds * len(PLAYER_IDS) for run in campaign.runs)
    assert len(games_csv) == len(campaign.runs)
    item = stats.by_configuration["C::reference"]
    assert int(summary_csv[0]["player_round_observations"]) == expected_rows
    assert float(summary_csv[0]["game_final_score_mean"]) == pytest.approx(
        item["game_final_score_distribution"]["mean"])
    assert saved["statistics"]["by_configuration"]["C::reference"]["players_observed"] == expected_rows
    assert len(saved["completed_games"][0]["round_summaries"]) == campaign.runs[0].rounds_completed
    for card_id, card in item["cards"].items():
        detailed = [row for row in players_csv if row["card_id"] == card_id]
        assert len(detailed) == card["assignments"]
        assert sum(row["round_eliminated"] == "True" for row in detailed) == card["eliminations"]
        assert card["game_carrier_win_rate"] is None
        assert card["round_win_denominator"] == sum(row["round_result"] != "" for row in detailed)
    report = (output / "report.md").read_text(encoding="utf-8")
    assert "game_final_score" in report and "non applicable" in report


def test_standard_errors_and_early_elimination_threshold_are_reported_with_denominators():
    assert wilson_interval(0, 0) is None
    interval = wilson_interval(5, 10)
    assert interval[0] < 0.5 < interval[1]
    config = benchmark_config(GameMode.LAST_SURVIVOR)
    campaign = run_campaign({"A": config}, PLAYER_IDS, seeds=(1, 2, 3),
                            policy_profiles={"reference": policies(ReferenceDecision())})
    summary = summarize(campaign, early_threshold=2).by_configuration["A::reference"]
    early = summary["early_eliminations"]
    assert early["experimental_threshold_gifts"] == 2
    assert early["player_round_denominator"] == 12
    assert 0 <= early["eliminated_early"] <= early["all_eliminations"]
    assert summary["gifts_proposed"]["median"] is not None
    assert summary["gifts_proposed"]["p95"] >= summary["gifts_proposed"]["p90"]


def test_statistics_do_not_count_terminal_ties_as_wins_and_track_shared_wins_separately():
    config = benchmark_config(GameMode.LAST_SURVIVOR)
    completed = run_game(config, PLAYER_IDS, seed=67, first_player_id="a",
                         policies=policies(ReferenceDecision()), configuration_name="A::fixture")
    terminal_tie = replace(completed, outcome="terminal_tie", winners=(), terminal_ties=1,
                           score_ties=0, configuration_name="A::fixture-tie")
    shared = replace(completed, outcome="fixed_rounds", winners=("a", "b"), score_ties=1,
                     configuration_name="A::fixture-shared")
    campaign = CampaignRun((terminal_tie, shared))
    summaries = summarize(campaign).by_configuration
    assert summaries["A::fixture-tie"]["terminal_tie_games"] == 1
    assert summaries["A::fixture-tie"]["winner_appearances"] == {}
    assert summaries["A::fixture-shared"]["shared_victory_games"] == 1
    assert summaries["A::fixture-shared"]["winner_appearances"] == {"a": 1, "b": 1}


def test_reference_campaign_rotates_starter_equally_and_keeps_modes_separate():
    campaign = run_campaign(reference_configurations(), PLAYER_IDS, seeds=(31, 32, 33, 34),
                            policy_profiles={"reference": policies(ReferenceDecision())})
    assert len(campaign.runs) == 12 and not campaign.failures
    for mode in ("A", "B", "C"):
        runs = [run for run in campaign.runs if run.configuration["mode"] == mode]
        assert len(runs) == 4
        assert [run.configuration["first_player_id"] for run in runs] == list(PLAYER_IDS)
    stats = summarize(campaign).by_configuration
    assert {stats[key]["mode"] for key in stats} == {"A", "B", "C"}


def test_failed_simulation_has_no_fabricated_player_rows_and_is_saved(tmp_path):
    config = benchmark_config(GameMode.LAST_SURVIVOR)
    campaign = run_campaign({"A": config}, PLAYER_IDS, seeds=(9,),
                            policy_profiles={"reference": policies(ReferenceDecision())},
                            max_actions=1, continue_on_error=True)
    assert not campaign.runs
    assert len(campaign.failures) == 1
    stats = summarize(campaign)
    assert stats.by_configuration["A::reference"]["errors"] == 1
    output = write_campaign(campaign, stats, tmp_path / "failure")
    games = (output / "games.csv").read_text(encoding="utf-8")
    players = (output / "players.csv").read_text(encoding="utf-8")
    saved = json.loads((output / "summary.json").read_text(encoding="utf-8"))
    assert ",failed," in games
    assert players.count("\n") == 1
    assert saved["failures"][0]["seed"] == 9


def test_saved_report_contains_campaign_profiles_configurations_and_summary_files(tmp_path):
    config = benchmark_config(GameMode.LAST_SURVIVOR)
    campaign = run_campaign({"A": config}, PLAYER_IDS, seeds=(14,),
                            policy_profiles={"reference": policies(ReferenceDecision())})
    stats = summarize(campaign)
    output = write_campaign(campaign, stats, tmp_path / "report")
    assert {path.name for path in output.iterdir()} == {
        "summary.json", "summary.csv", "games.csv", "players.csv", "report.md"}
    data = json.loads((output / "summary.json").read_text(encoding="utf-8"))
    assert data["parameters"]["seeds"] == [14]
    assert data["completed_games"][0]["configuration"]["mode"] == "A"
    assert "IC95" in (output / "report.md").read_text(encoding="utf-8")


def test_benchmark_configurations_are_explicitly_experimental_and_valid():
    for mode in GameMode:
        config = benchmark_config(mode)
        config.validate(4)
        assert "expérimental" in config.experimental_options["benchmark"]


def test_controller_boundary_prevents_agent_direct_mutation():
    game = create_game(PLAYER_IDS, benchmark_config(GameMode.LAST_SURVIVOR), seed=3,
                       first_player_id="a")
    controller = game.controller("a")
    view = controller.view()
    with pytest.raises((AttributeError, TypeError)):
        view.player_id = "b"
    with pytest.raises(AttributeError):
        controller._state


def test_communication_profiles_are_independent_and_emit_expected_message_kinds():
    config = benchmark_config(GameMode.LAST_SURVIVOR)
    profiles = communication_profiles(PLAYER_IDS)
    runs = {name: run_game(config, PLAYER_IDS, seed=96, first_player_id="a", policies=policy)
            for name, policy in profiles.items()}
    assert runs["silent"].messages == ()
    assert runs["truthful"].message_counts["spontaneous"] > 0
    assert runs["truthful"].strategy_names["a"][1] == "truthful_announcements"
    assert runs["bluff"].communication_modes["a"] == "deceptive"
    assert runs["bluff"].strategy_names["a"][1] == "bluff"
    assert runs["questioning"].message_counts["question"] > 0
    assert runs["questioning"].message_counts["response"] > 0
    assert runs["questioning"].strategy_names["a"][1] == "questioning_truthful"
    assert runs["mixed"].message_counts["spontaneous"] > 0
    assert runs["mixed"].message_counts["question"] > 0
    assert runs["mixed"].strategy_names["a"][1] == "mixed_bluff_question"


def test_communication_changes_only_orchestrator_log_not_engine_state():
    game = create_game(PLAYER_IDS, benchmark_config(GameMode.LAST_SURVIVOR), seed=4,
                       first_player_id="a")
    game.submit(ChooseRecipient("b"))
    token_id = game.controller("a").view().hand[0].id
    game.submit(ProposeGift(token_id))
    before = (tuple((player.id, tuple(player.hand), player.alive, player.score)
                    for player in game._state.players), tuple(game._state.common_bag),
              len(game._state.events), game.phase)
    channel = CommunicationChannel(game)
    channel.send("b", CommunicationIntent(CommunicationKind.QUESTION, "Quelle couleur ?"))
    after = (tuple((player.id, tuple(player.hand), player.alive, player.score)
                   for player in game._state.players), tuple(game._state.common_bag),
             len(game._state.events), game.phase)
    assert before == after
    game.assert_invariants()
