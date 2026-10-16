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
        eliminated = [player for player in player_runs if player.eliminated]
        early = [player for player in eliminated
                 if player.elimination_turn is not None and player.elimination_turn <= early_threshold]
        reasons = Counter(player.elimination_reason for player in eliminated)
        eliminated_before_first_turn = sum(player.turns_played == 0 for player in eliminated)
        card_rows = defaultdict(list)
        by_position = defaultdict(list)
        by_profile = defaultdict(list)
        by_family = defaultdict(list)
        by_player_id = defaultdict(list)
        for player in player_runs:
            card_rows[(player.card_id, player.defeat_families)].append(player)
            by_position[player.position].append(player)
            by_profile[(player.decision_profile, player.communication_profile)].append(player)
            by_player_id[player.player_id].append(player)
            for family in player.defeat_families:
                by_family[family].append(player)
        cards = {}
        for (card_id, families), rows in sorted(card_rows.items()):
            card_wins = sum(row.result in {"winner", "shared_winner"} for row in rows)
            card_eliminations = sum(row.eliminated for row in rows)
            survival = [row.turns_played for row in rows]
            cards[card_id] = {
                "families": families,
                "assignments": len(rows),
                "wins_by_carrier": card_wins,
                "carrier_win_rate": card_wins / len(rows),
                "carrier_win_rate_ci95": wilson_interval(card_wins, len(rows)),
                "eliminations": card_eliminations,
                "elimination_rate": card_eliminations / len(rows),
                "elimination_rate_ci95": wilson_interval(card_eliminations, len(rows)),
                "mean_turns_before_end": _mean_summary(survival),
                "elimination_reasons": dict(Counter(row.elimination_reason for row in rows if row.eliminated)),
                "positions": dict(Counter(row.position for row in rows)),
                "insufficient_sample": len(rows) < 30,
            }
        total_player_rounds = len(player_runs)
        summaries[name] = {
            "mode": runs[0].configuration["mode"],
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
                    row.elimination_turn for row in eliminated if row.elimination_turn is not None]),
                "elimination_turn_distribution": dict(Counter(
                    row.elimination_turn for row in eliminated if row.elimination_turn is not None)),
                "reason_counts": dict(reasons),
                "denominator_note": "Une observation par joueur et par manche commencée; éliminations au plus tard au seuil inclus.",
            },
            "cards": cards,
            "by_position": {str(position): {
                "appearances": len(rows),
                "wins": sum(row.result in {"winner", "shared_winner"} for row in rows),
                "eliminations": sum(row.eliminated for row in rows),
                "win_rate": sum(row.result in {"winner", "shared_winner"} for row in rows) / len(rows),
                "win_rate_ci95": wilson_interval(
                    sum(row.result in {"winner", "shared_winner"} for row in rows), len(rows)),
            } for position, rows in by_position.items()},
            "by_agent_profile": {f"{decision}+{communication}": {
                "appearances": len(rows),
                "wins": sum(row.result in {"winner", "shared_winner"} for row in rows),
                "eliminations": sum(row.eliminated for row in rows),
                "win_rate": sum(row.result in {"winner", "shared_winner"} for row in rows) / len(rows),
                "win_rate_ci95": wilson_interval(
                    sum(row.result in {"winner", "shared_winner"} for row in rows), len(rows)),
            } for (decision, communication), rows in by_profile.items()},
            "by_player_id": {player_id: {
                "appearances": len(rows),
                "wins": sum(row.result in {"winner", "shared_winner"} for row in rows),
                "win_rate": sum(row.result in {"winner", "shared_winner"} for row in rows) / len(rows),
                "win_rate_ci95": wilson_interval(
                    sum(row.result in {"winner", "shared_winner"} for row in rows), len(rows)),
                "eliminations": sum(row.eliminated for row in rows),
            } for player_id, rows in by_player_id.items()},
            "by_defeat_family": {family: {
                "assignments": len(rows),
                "carrier_wins": sum(row.result in {"winner", "shared_winner"} for row in rows),
                "carrier_eliminations": sum(row.eliminated for row in rows),
                "mean_turns_played": _mean_summary([row.turns_played for row in rows]),
                "elimination_reasons": dict(Counter(row.elimination_reason for row in rows if row.eliminated)),
            } for family, rows in by_family.items()},
            "score_distribution": _mean_summary([player.final_score for player in player_runs]),
            "players_observed": total_player_rounds,
            "win_rate_denominator_note": "Victoires individuelles / présences joueur-manche; les égalités terminales ne sont pas des victoires.",
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
            "cards": {}, "by_position": {}, "by_agent_profile": {},
            "early_eliminations": {"experimental_threshold_gifts": early_threshold,
                                   "player_round_denominator": 0, "eliminated_early": 0,
                                   "all_eliminations": 0, "proportion_of_player_rounds": None,
                                   "proportion_ci95": None, "reason_counts": {}},
            "message_count": 0, "message_types": {},
        }).setdefault("games_failed", failure_by_name[failure.configuration_name])
        summaries[failure.configuration_name]["errors"] = failure_by_name[failure.configuration_name]
    return CampaignStatistics(summaries, campaign.errors, early_threshold)
