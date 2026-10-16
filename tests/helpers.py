"""Small builders for explicit, deterministic engine states in tests."""
from __future__ import annotations

import random

from engine import GameEngine
from engine.state import GameState, Phase, PlayerState
from rules import Card, Condition, ConditionKind, GameConfig, GameMode, PointsFormat, Succession, Token


def safe_card(card_id: str, *, defeat: Condition | None = None, victory: Condition | None = None) -> Card:
    return Card(card_id, defeat or Condition(ConditionKind.TOTAL_COUNT, threshold=99), victory)


def points_config(cards, stock, *, succession=Succession.REPLAY_RESPONSIBLE,
                  points_format=PointsFormat.FIXED_ROUNDS, elimination_threshold=99,
                  points_threshold=None, fixed_rounds=3, bonus_points=1, **options):
    return GameConfig(
        stock, GameMode.POINTS, tuple(cards), succession=succession,
        points_format=points_format, elimination_threshold=elimination_threshold,
        points_threshold=points_threshold, fixed_rounds=fixed_rounds,
        bonus_points=bonus_points, initial_hand_size=1, **options,
    )


def build_game(*, mode, order, hands, bag, defeats=None, victories=None,
               succession=Succession.REPLAY_RESPONSIBLE, points_format=PointsFormat.FIXED_ROUNDS,
               elimination_threshold=99, points_threshold=None, fixed_rounds=3, bonus_points=1,
               donor_defeat_after_removal=False, reveal_refusal_draw=False,
               reveal_replay_draw=False, phase=Phase.CHOOSE_RECIPIENT, active=None,
               scores=None, credited=None, revealed=None, rng=None):
    defeats = defeats or {}
    victories = victories or {}
    scores = scores or {}
    credited = credited or {}
    revealed = revealed or set()
    players = []
    all_tokens = []
    returned_to_bag = []
    for player_id in order:
        hand = [Token(f"{player_id}-t{i}", color) for i, color in enumerate(hands.get(player_id, ()))]
        if player_id in revealed:
            returned_to_bag.extend(hand)
            hand = []
        all_tokens.extend(hand)
        players.append(PlayerState(
            player_id, hand, safe_card(player_id, defeat=defeats.get(player_id),
                                        victory=victories.get(player_id)),
            alive=player_id not in revealed, revealed=player_id in revealed,
            score=scores.get(player_id, 0), credited_eliminations=credited.get(player_id, 0),
        ))
    common = [Token(f"bag-t{i}", color) for i, color in enumerate(bag)]
    common.extend(returned_to_bag)
    all_tokens.extend(common)
    stock = {}
    for token in all_tokens:
        stock[token.color] = stock.get(token.color, 0) + 1
    if not stock:
        stock = {"rouge": 0}
    cards = tuple(player.card for player in players)
    config = GameConfig(
        stock, mode, cards, succession=succession, points_format=points_format,
        donor_defeat_after_removal=donor_defeat_after_removal,
        reveal_refusal_draw=reveal_refusal_draw, reveal_replay_draw=reveal_replay_draw,
        elimination_threshold=elimination_threshold, points_threshold=points_threshold,
        fixed_rounds=fixed_rounds, bonus_points=bonus_points, initial_hand_size=1,
    )
    state = GameState(config, players, common, active or order[0], phase)
    return GameEngine(state, rng or random.Random(0)), state


class ScriptedRNG(random.Random):
    """A Random that leaves shuffles alone and supplies requested color samples first."""

    def __init__(self, sample_colors=(), *, choice_index=0):
        super().__init__(0)
        self.sample_colors = list(sample_colors)
        self.choice_index = choice_index

    def shuffle(self, x):
        return None

    def sample(self, population, k, *, counts=None):
        if self.sample_colors:
            wanted = self.sample_colors.pop(0)
            selected = []
            for color in wanted:
                token = next((t for t in population if t.color == color and t not in selected), None)
                if token is None:
                    raise AssertionError(f"Scripted sample cannot find color {color!r} in {population!r}")
                selected.append(token)
            if len(selected) != k:
                raise AssertionError(f"Scripted sample expected {k} colors, got {wanted!r}")
            return selected
        return super().sample(population, k, counts=counts)

    def choice(self, seq):
        return seq[self.choice_index % len(seq)]
