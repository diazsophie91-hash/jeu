"""Run games through the public engine/controller APIs with seeded agent policies."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Mapping, Sequence

from agents import Agent, CommunicationChannel, CommunicationIntent, CommunicationKind, ScriptedDecision, SilentCommunication
from engine import start_new_round
from engine.selection import FirstPlayerSelection
from engine.state import Phase, VisibleEvent
from rules import GameConfig as RulesConfig


class SimulationError(RuntimeError):
    """A simulated game failed; the original exception is available as the cause."""


class SimulationLimitError(SimulationError):
    pass


@dataclass(frozen=True, slots=True)
class AgentPolicy:
    decision: object
    communication: object = SilentCommunication()


@dataclass(frozen=True, slots=True)
class GameRun:
    configuration_name: str
    simulation_index: int
    seed: int
    configuration: dict
    strategy_names: dict[str, tuple[str, str]]
    communication_modes: dict[str, str]
    outcome: str
    winners: tuple[str, ...]
    actions: int
    turns: int
    rounds: int
    messages: tuple
    first_player_event: VisibleEvent

    @property
    def message_counts(self) -> dict[str, int]:
        return dict(Counter(message.kind.value for message in self.messages))


@dataclass(frozen=True, slots=True)
class CampaignRun:
    runs: tuple[GameRun, ...]
    errors: tuple[tuple[str, int, int, str], ...] = ()


def _configuration_record(config: RulesConfig) -> dict:
    return {
        "mode": config.mode.value,
        "succession": config.succession.value,
        "donor_defeat_after_removal": config.donor_defeat_after_removal,
        "reveal_refusal_draw": config.reveal_refusal_draw,
        "reveal_replay_draw": config.reveal_replay_draw,
        "points_format": config.points_format.value,
        "elimination_threshold": config.elimination_threshold,
        "points_threshold": config.points_threshold,
        "fixed_rounds": config.fixed_rounds,
        "bonus_points": config.bonus_points,
        "initial_hand_size": config.initial_hand_size,
        "colors": tuple(sorted(config.colors.items())),
        "cards": tuple((card.id, tuple(repr(c) for c in card.defeat_conditions), repr(card.victory))
                       for card in config.cards),
        "pool_cards": tuple(card.id for card in config.card_pool.cards) if config.card_pool else (),
        "pool_expected_defeat_counts": tuple(sorted(
            ((kind.value, count) for kind, count in config.card_pool.expected_defeat_counts.items())
        )) if config.card_pool else (),
    }


def _send_intent(channel, author_id, intent):
    if intent is not None:
        if not isinstance(intent, CommunicationIntent):
            raise TypeError("Une stratégie doit retourner CommunicationIntent ou None.")
        channel.send(author_id, intent)


def run_game(
    config: RulesConfig,
    player_ids: Sequence[str],
    *,
    seed: int,
    first_player_id: str | None = None,
    selection: FirstPlayerSelection | None = None,
    policies: Mapping[str, AgentPolicy] | None = None,
    configuration_name: str = "default",
    simulation_index: int = 0,
    max_actions: int = 1000,
) -> GameRun:
    ids = tuple(player_ids)
    if selection is not None:
        if first_player_id is not None and first_player_id != selection.player_id:
            raise ValueError("Le premier joueur fourni et la sélection résolue diffèrent.")
        first_player_id = selection.player_id
    if max_actions < 1:
        raise ValueError("La limite d'actions doit être positive.")
    policies = dict(policies or {})
    unknown = set(policies) - set(ids)
    if unknown:
        raise ValueError(f"Des stratégies concernent des joueurs absents : {sorted(unknown)!r}.")
    from engine import create_game
    game = create_game(ids, config, seed=seed, first_player_id=first_player_id,
                       first_player_method=selection.method.value if selection else None,
                       first_player_resolution=selection.resolution if selection else None,
                       first_player_tied_candidates=selection.tied_candidates if selection else ())
    agents = {}
    for player_id in ids:
        policy = policies.get(player_id, AgentPolicy(ScriptedDecision()))
        agents[player_id] = Agent(game.controller(player_id), policy.decision, policy.communication)
    channel = CommunicationChannel(game)
    observed_proposals: set[int] = set()
    actions = 0

    try:
        while not game.finished:
            game.assert_invariants()
            if game.phase is Phase.ROUND_OVER:
                # The simulation harness uses a deterministic rotating starter policy.
                next_round = game.public_view().round_number + 1
                start_id = ids[(next_round - 1) % len(ids)]
                start_new_round(game, start_id)
                game.assert_invariants()
                continue
            if actions >= max_actions:
                raise SimulationLimitError(f"Limite de {max_actions} actions atteinte sans fin de partie.")
            actor = game.active_player_id
            if actor is None:
                raise SimulationError(f"Aucun joueur actif en phase {game.phase.value}.")
            if game.phase is Phase.DECISION:
                proposal_id = channel.current_proposal_id
                if proposal_id not in observed_proposals:
                    donor_id, recipient_id = game.public_view().proposal
                    donor, recipient = agents[donor_id], agents[recipient_id]
                    donor_view = donor.controller.view()
                    _send_intent(channel, donor_id, donor.communication_strategy.after_proposal(
                        donor_view, channel.messages_for(donor_id, proposal_id)))
                    recipient_view = recipient.controller.view()
                    _send_intent(channel, recipient_id, recipient.communication_strategy.after_proposal(
                        recipient_view, channel.messages_for(recipient_id, proposal_id)))
                    messages = channel.messages_for(donor_id, proposal_id)
                    questions = tuple(m for m in messages if m.kind is CommunicationKind.QUESTION)
                    _send_intent(channel, donor_id, donor.communication_strategy.answer_questions(
                        donor.controller.view(), questions, messages))
                    observed_proposals.add(proposal_id)
                messages = channel.messages_for(actor, proposal_id)
            else:
                messages = ()
            try:
                agents[actor].decide(messages)
            except Exception as exc:
                raise SimulationError(f"Échec d'action pour {actor!r} en phase {game.phase.value}.") from exc
            actions += 1
            game.assert_invariants()
    except SimulationError:
        raise
    except Exception as exc:
        raise SimulationError(f"Échec de simulation {simulation_index} ({configuration_name}, graine {seed}).") from exc

    public = game.public_view()
    strategies = {pid: (agents[pid].decision_strategy.name, agents[pid].communication_strategy.name)
                  for pid in ids}
    communication_modes = {pid: getattr(agents[pid].communication_strategy, "truthfulness_mode", "unspecified")
                            for pid in ids}
    run_configuration = _configuration_record(config)
    run_configuration["first_player_id"] = first_player_id
    run_configuration["first_player_method"] = selection.method.value if selection else "direct_input"
    run_configuration["first_player_resolution"] = selection.resolution if selection else "direct"
    run_configuration["round_starter_policy"] = "rotate_by_round_number"
    first_player_event = next(event for event in game.public_event_history()
                              if event.kind == "first_player_selected")
    return GameRun(configuration_name, simulation_index, seed, run_configuration,
                   strategies, communication_modes, public.result or "unknown", public.winners, actions,
                   sum(event.kind == "gift_proposed" for event in game.public_event_history()),
                   public.round_number, channel._message_history(), first_player_event)


def run_campaign(
    configurations: Mapping[str, RulesConfig],
    player_ids: Sequence[str],
    *,
    seeds: Sequence[int],
    first_player_id: str,
    policies: Mapping[str, AgentPolicy] | None = None,
    policy_profiles: Mapping[str, Mapping[str, AgentPolicy]] | None = None,
    max_actions: int = 1000,
    continue_on_error: bool = False,
) -> CampaignRun:
    """Compare separately named rules/strategy profiles using the same seed list."""
    runs = []
    errors = []
    profiles = dict(policy_profiles or {"default": policies or {}})
    for config_name, config in configurations.items():
        for profile_name, profile in profiles.items():
            result_name = f"{config_name}::{profile_name}"
            for index, seed in enumerate(seeds):
                try:
                    runs.append(run_game(config, player_ids, seed=seed, first_player_id=first_player_id,
                                         policies=profile, configuration_name=result_name,
                                         simulation_index=index, max_actions=max_actions))
                except Exception as exc:
                    if not continue_on_error:
                        raise
                    errors.append((result_name, index, seed, f"{type(exc).__name__}: {exc}"))
    return CampaignRun(tuple(runs), tuple(errors))
