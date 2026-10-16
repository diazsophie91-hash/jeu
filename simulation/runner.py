"""Reproducible simulation runner using only controller-filtered agent views."""
from __future__ import annotations

import hashlib
import time
from collections import Counter
from dataclasses import dataclass, field, replace
from typing import Mapping, Sequence

from agents import (Agent, CommunicationChannel, CommunicationIntent, CommunicationKind,
                    ScriptedDecision, SilentCommunication)
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
    communication: object = field(default_factory=SilentCommunication)

    def for_game(self, game_seed: int, player_id: str) -> "AgentPolicy":
        decision = _fresh_strategy(self.decision, _derive_seed(game_seed, player_id, "decision"))
        communication = _fresh_strategy(self.communication, _derive_seed(game_seed, player_id, "communication"))
        return AgentPolicy(decision, communication)


@dataclass(frozen=True, slots=True)
class PlayerRun:
    player_id: str
    position: int
    round_number: int
    first_player: bool
    round_starter_id: str
    card_id: str
    defeat_families: tuple[str, ...]
    victory_condition: str | None
    decision_profile: str
    communication_profile: str
    result: str
    eliminated: bool
    elimination_turn: int | None
    elimination_game_turn: int | None
    elimination_reason: str | None
    turns_played: int
    final_score: int
    credited_eliminations: int


@dataclass(frozen=True, slots=True)
class SimulationFailure:
    configuration_name: str
    simulation_index: int
    seed: int
    error: str
    duration_seconds: float


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
    experience_name: str = "experiment"
    duration_seconds: float = field(default=0.0, compare=False)
    status: str = "completed"
    terminal_ties: int = 0
    score_ties: int = 0
    score_tiebreaks: int = 0
    players: tuple[PlayerRun, ...] = ()
    agent_seeds: dict[str, dict[str, int]] = field(default_factory=dict)
    rounds_completed: int = 0

    @property
    def message_counts(self) -> dict[str, int]:
        return dict(Counter(message.kind.value for message in self.messages))


@dataclass(frozen=True, slots=True)
class CampaignRun:
    runs: tuple[GameRun, ...]
    errors: tuple[tuple[str, int, int, str], ...] = ()
    failures: tuple[SimulationFailure, ...] = ()
    parameters: dict = field(default_factory=dict)


def _derive_seed(seed: int, player_id: str, component: str) -> int:
    payload = f"simulation-v1\0{seed}\0{player_id}\0{component}".encode("utf-8")
    return int.from_bytes(hashlib.blake2b(payload, digest_size=8).digest(), "big")


def _fresh_strategy(strategy, seed):
    with_seed = getattr(strategy, "with_seed", None)
    if callable(with_seed):
        return with_seed(seed)
    return replace(strategy) if getattr(strategy, "__dataclass_fields__", None) else strategy


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
        "max_setup_attempts": config.max_setup_attempts,
        "colors": tuple(sorted(config.colors.items())),
        "cards": tuple((card.id, tuple(repr(c) for c in card.defeat_conditions), repr(card.victory))
                       for card in config.cards),
        "pool_cards": tuple((card.id, tuple(repr(c) for c in card.defeat_conditions), repr(card.victory))
                            for card in config.card_pool.cards) if config.card_pool else (),
        "pool_expected_defeat_counts": tuple(sorted(
            ((kind.value, count) for kind, count in config.card_pool.expected_defeat_counts.items())
        )) if config.card_pool else (),
        "experimental_options": tuple(sorted((str(key), repr(value))
                                              for key, value in config.experimental_options.items())),
    }


def _send_intent(channel, author_id, intent):
    if intent is not None:
        if not isinstance(intent, CommunicationIntent):
            raise TypeError("Une stratégie doit retourner CommunicationIntent ou None.")
        channel.send(author_id, intent)


def _round_snapshot(game, round_number, starter_id, player_ids):
    return tuple({
        "player_id": player.id,
        "position": position,
        "round_number": round_number,
        "round_starter_id": starter_id,
        "card": player.card,
    } for position, player in enumerate(game._state.players)
        if player.id in player_ids)


def _player_results(game, snapshots, first_player_id, strategies, outcome, winners, initial_turns):
    events = tuple(game._state.events)
    result = []
    for snapshot in snapshots:
        player_id = snapshot["player_id"]
        round_number = snapshot["round_number"]
        round_events = [event for event in events if event.round_number == round_number]
        proposals = [event for event in round_events if event.kind == "gift_proposed"]
        elimination = next((event for event in round_events if event.kind == "player_eliminated"
                           and event.data.get("player_id") == player_id), None)
        if elimination is None:
            turns_played = sum(event.data.get("donor_id") == player_id for event in proposals)
        else:
            turns_played = sum(event.sequence <= elimination.sequence
                               and event.data.get("donor_id") == player_id for event in proposals)
        if elimination is not None:
            player_result = "eliminated"
        elif outcome == "terminal_tie":
            player_result = "tied"
        elif player_id in winners:
            player_result = "shared_winner" if len(winners) > 1 else "winner"
        else:
            player_result = "non_winner"
        card = snapshot["card"]
        state_player = game._state.player(player_id)
        result.append(PlayerRun(
            player_id=player_id,
            position=snapshot["position"],
            round_number=round_number,
            first_player=(round_number == 1 and player_id == first_player_id),
            round_starter_id=snapshot["round_starter_id"],
            card_id=card.id,
            defeat_families=tuple(condition.kind.value for condition in card.defeat_conditions),
            victory_condition=repr(card.victory) if card.victory is not None else None,
            decision_profile=strategies[player_id][0],
            communication_profile=strategies[player_id][1],
            result=player_result,
            eliminated=elimination is not None,
            elimination_turn=(sum(event.kind == "gift_proposed" and event.sequence <= elimination.sequence
                                  for event in round_events) if elimination is not None else None),
            elimination_game_turn=(sum(event.kind == "gift_proposed" and event.sequence <= elimination.sequence
                                       for event in events) if elimination is not None else None),
            elimination_reason=elimination.data.get("reason") if elimination is not None else None,
            turns_played=turns_played,
            final_score=state_player.score,
            credited_eliminations=state_player.credited_eliminations,
        ))
    return tuple(result)


def run_game(
    config: RulesConfig,
    player_ids: Sequence[str],
    *,
    seed: int,
    first_player_id: str | None = None,
    selection: FirstPlayerSelection | None = None,
    policies: Mapping[str, AgentPolicy] | None = None,
    configuration_name: str = "default",
    experience_name: str = "experiment",
    simulation_index: int = 0,
    max_actions: int = 1000,
) -> GameRun:
    started = time.perf_counter()
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
    policies = {player_id: policies.get(player_id, AgentPolicy(ScriptedDecision())).for_game(seed, player_id)
                for player_id in ids}
    agent_seeds = {player_id: {
        "decision": _derive_seed(seed, player_id, "decision"),
        "communication": _derive_seed(seed, player_id, "communication"),
    } for player_id in ids}
    agents = {pid: Agent(game.controller(pid), policies[pid].decision, policies[pid].communication)
              for pid in ids}
    channel = CommunicationChannel(game)
    observed_proposals: set[int] = set()
    actions = 0
    snapshots = list(_round_snapshot(game, 1, first_player_id, set(ids)))
    round_starters = {1: first_player_id}

    try:
        while not game.finished:
            game.assert_invariants()
            if game.phase is Phase.ROUND_OVER:
                next_round = game.public_view().round_number + 1
                start_id = ids[(next_round - 1) % len(ids)]
                start_new_round(game, start_id)
                round_starters[next_round] = start_id
                snapshots.extend(_round_snapshot(game, next_round, start_id, set(ids)))
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
    events = tuple(game._state.events)
    first_player_event = next(event for event in game.public_event_history()
                              if event.kind == "first_player_selected")
    player_results = _player_results(game, snapshots, first_player_id, strategies,
                                    public.result or "unknown", public.winners, 0)
    score_tiebreaks = sum(event.kind == "tiebreak_required" for event in events)
    terminal_ties = sum(event.kind == "game_finished" and event.data.get("result") == "terminal_tie"
                        for event in events)
    return GameRun(
        configuration_name=configuration_name,
        simulation_index=simulation_index,
        seed=seed,
        configuration=run_configuration,
        strategy_names=strategies,
        communication_modes=communication_modes,
        outcome=public.result or "unknown",
        winners=public.winners,
        actions=actions,
        turns=sum(event.kind == "gift_proposed" for event in events),
        rounds=len({event.round_number for event in events if event.kind == "round_started"}),
        messages=channel._message_history(),
        first_player_event=first_player_event,
        experience_name=experience_name,
        duration_seconds=time.perf_counter() - started,
        terminal_ties=terminal_ties,
        score_ties=1 if len(public.winners) > 1 else 0,
        score_tiebreaks=score_tiebreaks,
        players=player_results,
        agent_seeds=agent_seeds,
        rounds_completed=game._state.rounds_completed,
    )


def run_campaign(
    configurations: Mapping[str, RulesConfig],
    player_ids: Sequence[str],
    *,
    seeds: Sequence[int],
    first_player_id: str | None = None,
    policies: Mapping[str, AgentPolicy] | None = None,
    policy_profiles: Mapping[str, Mapping[str, AgentPolicy]] | None = None,
    max_actions: int = 1000,
    continue_on_error: bool = False,
    experience_name: str = "experiment",
    progress_callback=None,
) -> CampaignRun:
    """Compare named policy profiles with reproducible seeds and a rotating starter."""
    runs = []
    errors = []
    failures = []
    profiles = dict(policy_profiles or {"default": policies or {}})
    ids = tuple(player_ids)
    completed_attempts = 0
    planned_attempts = len(configurations) * len(profiles) * len(seeds)
    stop_requested = False
    for config_name, config in configurations.items():
        config.validate(len(ids))
        for profile_name, profile in profiles.items():
            result_name = f"{config_name}::{profile_name}"
            for index, seed in enumerate(seeds):
                starter = first_player_id or ids[index % len(ids)]
                started = time.perf_counter()
                try:
                    runs.append(run_game(config, ids, seed=seed, first_player_id=starter,
                                         policies=profile, configuration_name=result_name,
                                         experience_name=experience_name,
                                         simulation_index=index, max_actions=max_actions))
                except Exception as exc:
                    duration = time.perf_counter() - started
                    diagnostic = f"{type(exc).__name__}: {exc}"
                    if exc.__cause__ is not None:
                        diagnostic += f"; cause={type(exc.__cause__).__name__}: {exc.__cause__}"
                    errors.append((result_name, index, seed, diagnostic))
                    failures.append(SimulationFailure(result_name, index, seed, diagnostic, duration))
                    if not continue_on_error:
                        completed_attempts += 1
                        if progress_callback is not None:
                            progress_callback(completed_attempts, planned_attempts, len(runs), len(failures))
                        stop_requested = True
                        break
                completed_attempts += 1
                if progress_callback is not None:
                    progress_callback(completed_attempts, planned_attempts, len(runs), len(failures))
            if stop_requested:
                break
        if stop_requested:
            break
    parameters = {
        "experience_name": experience_name,
        "player_ids": ids,
        "seeds": tuple(seeds),
        "max_actions": max_actions,
        "continue_on_error": continue_on_error,
        "first_player_policy": "fixed" if first_player_id else "rotate_by_simulation_index",
        "first_player_id": first_player_id,
        "configurations": {name: _configuration_record(config) for name, config in configurations.items()},
        "profiles": {name: {pid: (getattr(policy.decision, "name", type(policy.decision).__name__),
                                  getattr(policy.communication, "name", type(policy.communication).__name__))
                             for pid, policy in profile.items()}
                     for name, profile in profiles.items()},
    }
    return CampaignRun(tuple(runs), tuple(errors), tuple(failures), parameters)
