"""Configuration-separated descriptive statistics with explicit denominators."""
from __future__ import annotations

import math
from collections import Counter, defaultdict
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CampaignStatistics:
    by_configuration: dict[str, dict]
    errors: tuple[tuple[str, int, int, str], ...]
    early_elimination_threshold: int = 3


def wilson_interval(successes: int, total: int, z: float = 1.96):
    """95% Wilson interval for a binomial proportion; None for no observations."""
    if total <= 0:
        return None
    p = successes / total
    denominator = 1 + z * z / total
    center = (p + z * z / (2 * total)) / denominator
    margin = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / denominator
    return (max(0.0, center - margin), min(1.0, center + margin))


def _quantile(values, q):
    if not values:
        return None
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * q
    lower = int(position)
    fraction = position - lower
    return ordered[lower] * (1 - fraction) + ordered[min(lower + 1, len(ordered) - 1)] * fraction


def _mean_summary(values):
    if not values:
        return {"n": 0, "mean": None, "ci95": None, "min": None, "max": None}
    mean = sum(values) / len(values)
    if len(values) < 2:
        interval = None
    else:
        variance = sum((value - mean) ** 2 for value in values) / (len(values) - 1)
        margin = 1.96 * math.sqrt(variance / len(values))
        interval = (mean - margin, mean + margin)
    return {"n": len(values), "mean": mean, "ci95": interval,
            "min": min(values), "max": max(values)}


def summarize(campaign, early_threshold: int = 3) -> CampaignStatistics:
    if early_threshold < 0:
        raise ValueError("Le seuil d'élimination précoce doit être positif ou nul.")
    grouped = defaultdict(list)
    for run in campaign.runs:
        grouped[run.configuration_name].append(run)
    summaries = {}
    failure_by_name = Counter(failure.configuration_name for failure in campaign.failures)
    for name, runs in grouped.items():
        outcomes = Counter(run.outcome for run in runs)
        winner_appearances = Counter(winner for run in runs for winner in run.winners)
        message_counts = Counter(message.kind.value for run in runs for message in run.messages)
        messages_by_profile = defaultdict(Counter)
        messages_by_agent = defaultdict(Counter)
        messages_by_truthfulness = defaultdict(Counter)
        for run in runs:
            for message in run.messages:
                profile = run.strategy_names.get(message.author_id, ("unknown", "unknown"))[1]
                messages_by_profile[profile][message.kind.value] += 1
                messages_by_agent[message.author_id][message.kind.value] += 1
                truthfulness = run.communication_modes.get(message.author_id, "unspecified")
                messages_by_truthfulness[truthfulness][message.kind.value] += 1
        turns = [run.turns for run in runs]
        actions = [run.actions for run in runs]
        durations = [run.duration_seconds for run in runs]
        rounds = [run.rounds for run in runs]
        player_runs = [player for run in runs for player in run.players]
        # Game-level outcomes are counted once per player-game, using the
        # player's last observed round row only as a game-level carrier.
        game_players = []
        for run in runs:
            last_by_player = {}
            for player in run.players:
                current = last_by_player.get(player.player_id)
                if current is None or player.round_number > current.round_number:
                    last_by_player[player.player_id] = player
            game_players.extend(last_by_player.values())
        eliminated = [player for player in player_runs if player.round_eliminated]
        early = [player for player in eliminated
                 if player.round_elimination_turn is not None
                 and player.round_elimination_turn <= early_threshold]
        reasons = Counter(player.round_elimination_reason for player in eliminated)
        eliminated_before_first_turn = sum(player.round_turns_played == 0 for player in eliminated)
        card_rows = defaultdict(list)
        by_position = defaultdict(list)
        by_profile = defaultdict(list)
        by_family = defaultdict(list)
        by_player_id = defaultdict(list)
        for player in player_runs:
            card_rows[(player.card_id, player.defeat_families)].append(player)
            for family in player.defeat_families:
                by_family[family].append(player)
        for player in game_players:
            by_position[player.position].append(player)
            by_profile[(player.decision_profile, player.communication_profile)].append(player)
            by_player_id[player.player_id].append(player)
        mode = runs[0].configuration["mode"]
        game_carrier_wins_applicable = mode in {"A", "B"} and all(run.rounds == 1 for run in runs)
        cards = {}
        for (card_id, families), rows in sorted(card_rows.items()):
            card_eliminations = sum(row.round_eliminated for row in rows)
            completed_round_rows = [row for row in rows if row.round_completed is True]
            round_wins = sum(row.round_result == "round_winner" for row in completed_round_rows)
            game_card_wins = (sum(row.game_player_result in {"winner", "shared_winner"}
                                  for row in rows) if game_carrier_wins_applicable else None)
            game_card_denominator = len(rows) if game_carrier_wins_applicable else None
            survival = [row.round_turns_played for row in rows]
            cards[card_id] = {
                "families": families,
                "assignments": len(rows),
                "game_wins_by_carrier": game_card_wins,
                "game_carrier_win_measure_applicable": game_carrier_wins_applicable,
                "game_win_denominator": game_card_denominator,
                "game_carrier_win_rate": (game_card_wins / game_card_denominator
                                           if game_card_denominator else None),
                "game_carrier_win_rate_ci95": (wilson_interval(game_card_wins, game_card_denominator)
                                                if game_card_denominator else None),
                "round_wins_by_carrier": round_wins if mode == "C" else None,
                "round_win_denominator": len(completed_round_rows) if mode == "C" else None,
                "round_carrier_win_rate": (round_wins / len(completed_round_rows)
                                            if mode == "C" and completed_round_rows else None),
                "round_carrier_win_rate_ci95": (wilson_interval(round_wins, len(completed_round_rows))
                                                 if mode == "C" and completed_round_rows else None),
                "eliminations": card_eliminations,
                "elimination_rate": card_eliminations / len(rows),
                "elimination_rate_ci95": wilson_interval(card_eliminations, len(rows)),
                "mean_turns_before_end": _mean_summary(survival),
                "elimination_reasons": dict(Counter(row.round_elimination_reason
                                                     for row in rows if row.round_eliminated)),
                "positions": dict(Counter(row.position for row in rows)),
                "insufficient_sample": len(rows) < 30,
            }
        total_player_rounds = len(player_runs)
        summaries[name] = {
            "mode": mode,
            "configuration": runs[0].configuration,
            "games_completed": len(runs),
            "games_failed": failure_by_name[name],
            "outcomes": dict(outcomes),
            "winner_appearances": dict(winner_appearances),
            "shared_victory_games": sum(len(run.winners) > 1 for run in runs),
            "terminal_tie_games": sum(run.outcome == "terminal_tie" for run in runs),
            "score_tiebreaks": sum(run.score_tiebreaks for run in runs),
            "score_tie_games": sum(run.score_ties for run in runs),
            "actions": _mean_summary(actions),
            "average_actions": sum(actions) / len(actions),
            "average_turns": sum(turns) / len(turns),
            "average_rounds": sum(rounds) / len(rounds),
            "average_messages": sum(len(run.messages) for run in runs) / len(runs),
            "gifts_proposed": {
                **_mean_summary(turns),
                "median": _quantile(turns, 0.50), "p90": _quantile(turns, 0.90),
                "p95": _quantile(turns, 0.95),
            },
            "rounds_played": _mean_summary(rounds),
            "simulation_seconds": _mean_summary(durations),
            "reached_action_limit": failure_by_name[name] and sum(
                failure.configuration_name == name and "SimulationLimitError" in failure.error
                for failure in campaign.failures) or 0,
            "message_count": sum(message_counts.values()),
            "message_types": dict(message_counts),
            "message_counts": dict(message_counts),
            "messages_by_agent": {pid: dict(counts) for pid, counts in messages_by_agent.items()},
            "messages_by_truthfulness_mode": {mode: dict(counts)
                                              for mode, counts in messages_by_truthfulness.items()},
            "messages_by_communication_profile": {profile: dict(counts)
                                                  for profile, counts in messages_by_profile.items()},
            "early_eliminations": {
                "experimental_threshold_gifts": early_threshold,
                "player_round_denominator": total_player_rounds,
                "eliminated_early": len(early),
                "all_eliminations": len(eliminated),
                "eliminated_before_first_own_turn": eliminated_before_first_turn,
                "before_first_own_turn_denominator": total_player_rounds,
                "before_first_own_turn_proportion": (eliminated_before_first_turn / total_player_rounds
                                                      if total_player_rounds else None),
                "before_first_own_turn_ci95": wilson_interval(eliminated_before_first_turn,
                                                               total_player_rounds),
                "proportion_of_player_rounds": len(early) / total_player_rounds if total_player_rounds else None,
                "proportion_ci95": wilson_interval(len(early), total_player_rounds),
                "mean_turns_to_elimination": _mean_summary([
                    row.round_elimination_turn for row in eliminated
                    if row.round_elimination_turn is not None]),
                "elimination_turn_distribution": dict(Counter(
                    row.round_elimination_turn for row in eliminated
                    if row.round_elimination_turn is not None)),
                "reason_counts": dict(reasons),
                "denominator_note": "Une observation par joueur et par manche commencée; éliminations au plus tard au seuil inclus.",
            },
            "cards": cards,
            "by_position_game": {str(position): {
                "appearances": len(rows),
                "wins": sum(row.game_player_result in {"winner", "shared_winner"} for row in rows),
                "win_rate": sum(row.game_player_result in {"winner", "shared_winner"} for row in rows) / len(rows),
                "win_rate_ci95": wilson_interval(
                    sum(row.game_player_result in {"winner", "shared_winner"} for row in rows), len(rows)),
                "round_eliminations": sum(row.round_eliminated for row in player_runs
                                           if row.position == position),
                "round_player_observations": sum(row.position == position for row in player_runs),
                "round_elimination_rate": (
                    sum(row.round_eliminated for row in player_runs if row.position == position) /
                    sum(row.position == position for row in player_runs)),
            } for position, rows in by_position.items()},
            "by_agent_profile_game": {f"{decision}+{communication}": {
                "appearances": len(rows),
                "wins": sum(row.game_player_result in {"winner", "shared_winner"} for row in rows),
                "win_rate": sum(row.game_player_result in {"winner", "shared_winner"} for row in rows) / len(rows),
                "win_rate_ci95": wilson_interval(
                    sum(row.game_player_result in {"winner", "shared_winner"} for row in rows), len(rows)),
                "round_eliminations": sum(row.round_eliminated for row in player_runs
                                           if (row.decision_profile, row.communication_profile) ==
                                           (decision, communication)),
                "round_player_observations": sum(
                    (row.decision_profile, row.communication_profile) == (decision, communication)
                    for row in player_runs),
                "round_elimination_rate": (
                    sum(row.round_eliminated for row in player_runs
                        if (row.decision_profile, row.communication_profile) == (decision, communication)) /
                    sum((row.decision_profile, row.communication_profile) == (decision, communication)
                        for row in player_runs)),
            } for (decision, communication), rows in by_profile.items()},
            "by_player_id_game": {player_id: {
                "appearances": len(rows),
                "wins": sum(row.game_player_result in {"winner", "shared_winner"} for row in rows),
                "win_rate": sum(row.game_player_result in {"winner", "shared_winner"} for row in rows) / len(rows),
                "win_rate_ci95": wilson_interval(
                    sum(row.game_player_result in {"winner", "shared_winner"} for row in rows), len(rows)),
            } for player_id, rows in by_player_id.items()},
            "by_defeat_family": {family: {
                "player_round_assignments": len(rows),
                "game_carrier_wins": (sum(row.game_player_result in {"winner", "shared_winner"}
                                           for row in rows) if game_carrier_wins_applicable else None),
                "game_carrier_win_denominator": (len(rows) if game_carrier_wins_applicable else None),
                "game_carrier_win_rate": ((sum(row.game_player_result in {"winner", "shared_winner"}
                                                for row in rows) / len(rows))
                                           if game_carrier_wins_applicable and rows else None),
                "completed_round_observations": sum(row.round_completed is True for row in rows),
                "round_carrier_wins": (sum(row.round_result == "round_winner" for row in rows)
                                       if mode == "C" else None),
                "round_carrier_win_denominator": (sum(row.round_result is not None for row in rows)
                                                   if mode == "C" else None),
                "round_carrier_win_rate": ((sum(row.round_result == "round_winner" for row in rows) /
                                            sum(row.round_result is not None for row in rows))
                                           if mode == "C" and any(row.round_result is not None
                                                                   for row in rows) else None),
                "carrier_eliminations_by_round": sum(row.round_eliminated for row in rows),
                "mean_round_turns_played": _mean_summary([row.round_turns_played for row in rows]),
                "elimination_reasons": dict(Counter(row.round_elimination_reason
                                                     for row in rows if row.round_eliminated)),
            } for family, rows in by_family.items()},
            "game_final_score_distribution": _mean_summary(
                [score for run in runs for score in run.final_scores.values() if score is not None]),
            "round_end_cumulative_score_distribution": _mean_summary(
                [player.round_score for player in player_runs if player.round_score is not None]),
            "round_end_credited_eliminations_distribution": _mean_summary(
                [player.round_credited_eliminations for player in player_runs
                 if player.round_credited_eliminations is not None]),
            "players_observed": total_player_rounds,
            "win_rate_denominator_note": "Taux de victoire finale : joueurs-parties distincts; égalité terminale exclue des victoires. Mode C : les victoires de porteur sont données par manche et seulement si un événement round_finished existe.",
            "seeds": tuple(run.seed for run in runs),
            "errors": failure_by_name[name],
            "strategy_names": runs[0].strategy_names,
            "communication_modes": runs[0].communication_modes,
        }
    for failure in campaign.failures:
        base_name = failure.configuration_name.split("::", 1)[0]
        configuration = campaign.parameters.get("configurations", {}).get(base_name)
        summaries.setdefault(failure.configuration_name, {
            "mode": configuration.get("mode") if configuration else None,
            "configuration": configuration or {},
            "games_completed": 0, "outcomes": {}, "winner_appearances": {},
            "actions": _mean_summary([]), "gifts_proposed": _mean_summary([]),
            "rounds_played": _mean_summary([]), "simulation_seconds": _mean_summary([]),
            "cards": {}, "by_position_game": {}, "by_agent_profile_game": {},
            "early_eliminations": {"experimental_threshold_gifts": early_threshold,
                                   "player_round_denominator": 0, "eliminated_early": 0,
                                   "all_eliminations": 0, "proportion_of_player_rounds": None,
                                   "proportion_ci95": None, "reason_counts": {}},
            "message_count": 0, "message_types": {},
        }).setdefault("games_failed", failure_by_name[failure.configuration_name])
        summaries[failure.configuration_name]["errors"] = failure_by_name[failure.configuration_name]
    return CampaignStatistics(summaries, campaign.errors, early_threshold)
