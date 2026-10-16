"""Pure rule evaluation and score/end-condition helpers."""
from __future__ import annotations

from collections import Counter
from typing import Iterable

from .cards import Card, Token, condition_matches
from .config import GameConfig, GameMode, PointsFormat


def token_counts(tokens: Iterable[Token]) -> Counter[str]:
    return Counter(t.color for t in tokens)


def evaluate_defeat(card: Card | None, tokens: Iterable[Token]) -> bool:
    if card is None: raise ValueError("Carte secrète manquante.")
    return condition_matches(card.defeat, token_counts(tokens))


def evaluate_victory(card: Card | None, tokens: Iterable[Token]) -> bool:
    if card is None or card.victory is None: return False
    return condition_matches(card.victory, token_counts(tokens))


def can_refuse(common_bag_size: int) -> bool:
    if common_bag_size < 0: raise ValueError("La taille du sac ne peut pas être négative.")
    return common_bag_size > 0


def awarded_point_allowed(config: GameConfig, alive_count_after_action: int, is_opponent: bool) -> bool:
    """Whether an initial action elimination can earn a point (terminal tie takes precedence)."""
    return config.mode is GameMode.POINTS and is_opponent and alive_count_after_action > 0


def round_threshold_reached(config: GameConfig, credited_eliminations: int) -> bool:
    if config.mode is not GameMode.POINTS: return False
    return credited_eliminations >= config.elimination_threshold


def points_game_should_end(config: GameConfig, scores: Iterable[int], round_finished: bool) -> bool:
    if config.mode is not GameMode.POINTS or not round_finished: return False
    if config.points_format is PointsFormat.POINTS_THRESHOLD:
        return max(scores, default=0) >= config.points_threshold
    return False
