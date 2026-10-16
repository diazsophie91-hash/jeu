"""Explicit experimental benchmark configurations and comparable agent profiles."""
from __future__ import annotations

from collections import Counter

from agents import (AlwaysAcceptDecision, AlwaysRefuseDecision, CautiousDecision,
                    ColorClaimCommunication, RandomDecision, ScriptedDecision, SilentCommunication)
from agents import ReferenceDecision
from rules import Card, CardPool, Condition, ConditionKind, GameConfig, GameMode, PointsFormat, Succession
from .runner import AgentPolicy


EXPERIMENTAL_LABEL = "benchmark expérimental, non officiel"


def benchmark_config(mode: GameMode, *, succession=Succession.REPLAY_RESPONSIBLE,
                     donor_defeat_after_removal=False, reveal_refusal_draw=False,
                     reveal_replay_draw=False) -> GameConfig:
    """Small four-player benchmark pack; deliberately not an official card set."""
    if mode is GameMode.LAST_SURVIVOR:
        defeats = (
            Condition(ConditionKind.COLOR_COUNT, colors=("rouge",), threshold=3),
            Condition(ConditionKind.COLOR_COUNT, colors=("rouge",), threshold=4),
            Condition(ConditionKind.TOTAL_COUNT, threshold=3),
            Condition(ConditionKind.TOTAL_COUNT, threshold=4),
        )
        victories = (None,) * 4
    elif mode is GameMode.SECRET_OBJECTIVE:
        # Exactly three red tokens wins; four or more loses, so the two
        # objectives cannot be satisfied simultaneously. High total-count
        # defeats remain intentionally unreachable control cards.
        defeats = (
            Condition(ConditionKind.COLOR_COUNT, colors=("rouge",), threshold=4),
            Condition(ConditionKind.COLOR_COUNT, colors=("rouge",), threshold=5),
            Condition(ConditionKind.TOTAL_COUNT, threshold=100),
            Condition(ConditionKind.TOTAL_COUNT, threshold=101),
        )
        victories = tuple(Condition(ConditionKind.COLOR_COUNT, colors=("rouge",),
                                    threshold=3, exact=True) for _ in defeats)
    else:
        defeats = (
            Condition(ConditionKind.TOTAL_COUNT, threshold=3),
            Condition(ConditionKind.TOTAL_COUNT, threshold=4),
            Condition(ConditionKind.COLOR_COUNT, colors=("bleu",), threshold=3),
            Condition(ConditionKind.COLOR_COUNT, colors=("bleu",), threshold=4),
        )
        victories = (None,) * 4
    cards = tuple(Card(f"{mode.value}-experimental-{index + 1}", defeat, victory)
                  for index, (defeat, victory) in enumerate(zip(defeats, victories)))
    expected = Counter(condition.kind for card in cards for condition in card.defeat_conditions)
    pool = CardPool(cards, expected)
    points = mode is GameMode.POINTS
    config = GameConfig(
        {"rouge": 8, "bleu": 8}, mode, succession=succession,
        donor_defeat_after_removal=donor_defeat_after_removal,
        reveal_refusal_draw=reveal_refusal_draw,
        reveal_replay_draw=reveal_replay_draw,
        points_format=PointsFormat.FIXED_ROUNDS,
        elimination_threshold=1 if points else None,
        fixed_rounds=2 if points else 3,
        initial_hand_size=2,
        card_pool=pool,
        experimental_options={"benchmark": EXPERIMENTAL_LABEL},
    )
    config.validate(4)
    return config


def reference_configurations() -> dict[str, GameConfig]:
    return {f"mode-{mode.value}": benchmark_config(mode)
            for mode in (GameMode.LAST_SURVIVOR, GameMode.SECRET_OBJECTIVE, GameMode.POINTS)}


def variant_configurations() -> dict[str, GameConfig]:
    baseline = benchmark_config(GameMode.LAST_SURVIVOR)
    return {
        "succession-A": baseline,
        "succession-B": benchmark_config(GameMode.LAST_SURVIVOR, succession=Succession.CLOCKWISE),
        "donor-check-off": baseline,
        "donor-check-on": benchmark_config(GameMode.LAST_SURVIVOR, donor_defeat_after_removal=True),
        "refusal-draw-hidden": baseline,
        "refusal-draw-visible": benchmark_config(GameMode.LAST_SURVIVOR, reveal_refusal_draw=True),
        "replay-draw-hidden": baseline,
        "replay-draw-visible": benchmark_config(GameMode.LAST_SURVIVOR, reveal_replay_draw=True),
    }


def _make_policy(decision_name: str, communication_name: str) -> AgentPolicy:
    decisions = {
        "deterministic": ReferenceDecision(),
        "random": RandomDecision(),
        "cautious": CautiousDecision(),
        "always_accept": AlwaysAcceptDecision(),
        "always_refuse": AlwaysRefuseDecision(),
    }
    communications = {
        "silent": SilentCommunication(),
        "truthful": ColorClaimCommunication(("rouge", "bleu"), truthful=True,
                                             name="truthful_announcements"),
        "bluff": ColorClaimCommunication(("rouge", "bleu"), truthful=False,
                                          name="bluff"),
        "questioning": ColorClaimCommunication(("rouge", "bleu"), truthful=True,
                                               spontaneous=False, question_text="Quelle couleur ?",
                                               name="questioning_truthful"),
        "mixed": ColorClaimCommunication(("rouge", "bleu"), truthful=False,
                                         question_text="Le cadeau est-il rouge ?", name="mixed_bluff_question"),
    }
    return AgentPolicy(decisions[decision_name], communications[communication_name])


def decision_profiles(player_ids: tuple[str, ...]) -> dict[str, dict[str, AgentPolicy]]:
    profiles = {"deterministic-reference": {
        pid: _make_policy("deterministic", "silent") for pid in player_ids}}
    for name in ("random", "cautious", "always_accept", "always_refuse"):
        profiles[f"{name}-vs-reference"] = {
            pid: _make_policy("deterministic", "silent") for pid in player_ids}
        profiles[f"{name}-vs-reference"][player_ids[0]] = _make_policy(name, "silent")
    return profiles


def communication_profiles(player_ids: tuple[str, ...]) -> dict[str, dict[str, AgentPolicy]]:
    return {name: {pid: _make_policy("deterministic", name) for pid in player_ids}
            for name in ("silent", "truthful", "bluff", "questioning", "mixed")}


def mixed_profiles(player_ids: tuple[str, ...]) -> dict[str, dict[str, AgentPolicy]]:
    decision_names = ("deterministic", "random", "cautious", "always_accept")
    comm_names = ("truthful", "bluff", "questioning", "mixed")
    return {
        "mixed-agents-and-messages": {
            pid: _make_policy(decision_names[index % len(decision_names)],
                              comm_names[index % len(comm_names)])
            for index, pid in enumerate(player_ids)
        }
    }
