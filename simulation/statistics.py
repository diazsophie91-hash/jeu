"""Descriptive, configuration-separated summaries for reproducible campaigns."""
from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CampaignStatistics:
    by_configuration: dict[str, dict]
    errors: tuple[tuple[str, int, int, str], ...]


def summarize(campaign) -> CampaignStatistics:
    grouped = defaultdict(list)
    for run in campaign.runs:
        grouped[run.configuration_name].append(run)
    summaries = {}
    for name, runs in grouped.items():
        outcomes = Counter(run.outcome for run in runs)
        winners = Counter(winner for run in runs for winner in run.winners)
        message_counts = Counter(kind for run in runs for kind, count in run.message_counts.items()
                                 for _ in range(count))
        messages_by_author = defaultdict(Counter)
        messages_by_claim_mode = defaultdict(Counter)
        for run in runs:
            for message in run.messages:
                messages_by_author[message.author_id][message.kind.value] += 1
                mode = run.communication_modes.get(message.author_id, "unspecified")
                messages_by_claim_mode[mode][message.kind.value] += 1
        summaries[name] = {
            "games_completed": len(runs),
            "outcomes": dict(outcomes),
            "winner_appearances": dict(winners),
            "terminal_ties": outcomes.get("terminal_tie", 0),
            "average_actions": sum(run.actions for run in runs) / len(runs),
            "average_turns": sum(run.turns for run in runs) / len(runs),
            "average_rounds": sum(run.rounds for run in runs) / len(runs),
            "average_messages": sum(len(run.messages) for run in runs) / len(runs),
            "message_counts": dict(message_counts),
            "messages_by_agent": {pid: dict(counts) for pid, counts in messages_by_author.items()},
            "messages_by_truthfulness_mode": {mode: dict(counts) for mode, counts in messages_by_claim_mode.items()},
            "seeds": tuple(run.seed for run in runs),
            "strategies": runs[0].strategy_names,
            "communication_modes": runs[0].communication_modes,
        }
    for name, _, _, _ in campaign.errors:
        summaries.setdefault(name, {
            "games_completed": 0, "outcomes": {}, "winner_appearances": {},
            "terminal_ties": 0, "average_actions": None, "average_turns": None, "average_rounds": None,
            "average_messages": None, "message_counts": {}, "seeds": (), "strategies": {},
            "communication_modes": {}, "messages_by_agent": {}, "messages_by_truthfulness_mode": {},
        })["errors"] = sum(error[0] == name for error in campaign.errors)
    return CampaignStatistics(summaries, campaign.errors)
