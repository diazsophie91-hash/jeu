"""Validated, immutable game configuration."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Mapping

from .cards import Card, ConditionKind
from .card_pool import CardPool


class ConfigurationError(ValueError):
    """The requested rules or starting position cannot be used."""


class GameMode(str, Enum):
    LAST_SURVIVOR = "A"
    SECRET_OBJECTIVE = "B"
    POINTS = "C"


class Succession(str, Enum):
    REPLAY_RESPONSIBLE = "A"
    CLOCKWISE = "B"


class PointsFormat(str, Enum):
    FIXED_ROUNDS = "C1"
    POINTS_THRESHOLD = "C2"


@dataclass(frozen=True, slots=True)
class GameConfig:
    colors: Mapping[str, int]
    mode: GameMode
    cards: tuple[Card, ...] = ()
    succession: Succession = Succession.REPLAY_RESPONSIBLE
    points_format: PointsFormat = PointsFormat.FIXED_ROUNDS
    donor_defeat_after_removal: bool = False
    reveal_refusal_draw: bool = False
    reveal_replay_draw: bool = False
    elimination_threshold: int | None = None
    points_threshold: int | None = None
    fixed_rounds: int = 3
    bonus_points: int = 1
    initial_hand_size: int = 3
    max_setup_attempts: int = 100
    experimental_options: Mapping[str, object] = field(default_factory=dict)
    card_pool: CardPool | None = None

    def validate(self, player_count: int) -> None:
        if not isinstance(self.mode, GameMode):
            raise ConfigurationError("Le mode de jeu doit être un GameMode connu.")
        if not isinstance(self.succession, Succession):
            raise ConfigurationError("La variante de succession doit être A ou B.")
        if not isinstance(self.points_format, PointsFormat):
            raise ConfigurationError("Le format de points doit être C1 ou C2.")
        if player_count < 2:
            raise ConfigurationError("Il faut au moins deux joueurs.")
        if not self.colors or any(not isinstance(c, str) or not c or not isinstance(n, int) or isinstance(n, bool) or n < 0 for c, n in self.colors.items()):
            raise ConfigurationError("La composition du stock est invalide.")
        if sum(self.colors.values()) < player_count * self.initial_hand_size:
            raise ConfigurationError("Le stock contient moins de trois jetons par joueur.")
        if self.initial_hand_size < 1 or self.max_setup_attempts < 1:
            raise ConfigurationError("Les paramètres de mise en place doivent être positifs.")
        if self.card_pool is not None:
            if self.cards:
                raise ConfigurationError("Choisissez les cartes injectées ou une réserve, pas les deux.")
            cards = self.card_pool.cards
            try:
                self.card_pool.validate_for(player_count)
            except ValueError as exc:
                raise ConfigurationError(str(exc)) from exc
        else:
            cards = self.cards
            if len(cards) != player_count:
                raise ConfigurationError(f"Fournissez exactement une carte par joueur ({player_count} attendues, {len(cards)} fournies), ou configurez une réserve suffisante.")
        if len({card.id for card in cards}) != len(cards):
            raise ConfigurationError("Les identifiants des cartes doivent être uniques.")
        if self.mode is GameMode.POINTS:
            if self.elimination_threshold is None or self.elimination_threshold < 1:
                raise ConfigurationError("Le seuil d'éliminations de manche doit être configuré en mode C.")
            if self.points_format is PointsFormat.POINTS_THRESHOLD and (self.points_threshold is None or self.points_threshold < 1):
                raise ConfigurationError("Le seuil de points doit être configuré pour le format C2.")
            if self.fixed_rounds < 1 or self.bonus_points < 0:
                raise ConfigurationError("Paramètres de score invalides.")
        for card in cards:
            if not card.id:
                raise ConfigurationError("Une carte n'a pas d'identifiant.")
            if (card.victory is not None) != (self.mode is GameMode.SECRET_OBJECTIVE):
                raise ConfigurationError(f"La carte {card.id!r} est incompatible avec le mode {self.mode.value}.")
            for condition in (*card.defeat_conditions, card.victory):
                if condition is None:
                    continue
                _validate_condition(card.id, condition)
                if any(self.colors.get(c, 0) <= 0 for c in condition.colors) or any(self.colors.get(c, 0) <= 0 for c, _ in condition.composition):
                    raise ConfigurationError(f"La carte {card.id!r} référence une couleur absente du stock.")
                if condition.kind is ConditionKind.TWO_PAIRS and condition.colors and len(condition.colors) != 2:
                    raise ConfigurationError(f"La carte {card.id!r} a une condition de deux paires invalide.")
                if condition.kind is ConditionKind.EQUAL_COUNTS and len(condition.colors) != 2:
                    raise ConfigurationError(f"La carte {card.id!r} doit désigner deux couleurs.")
            if card.victory and any(_conditions_overlap(defeat, card.victory, self.colors)
                                    for defeat in card.defeat_conditions):
                raise ConfigurationError(f"La carte {card.id!r} peut gagner et perdre simultanément.")
        if self.card_pool is None:
            if not _complete_setup_possible(cards, self.colors, self.mode, self.initial_hand_size):
                raise ConfigurationError("Aucune attribution complète de collections de départ valides n'est possible avec ces cartes et ce stock.")
        else:
            try:
                self.card_pool.validate_setup(player_count, self.colors, self.mode, self.initial_hand_size)
            except ValueError as exc:
                raise ConfigurationError(str(exc)) from exc


def _conditions_overlap(a, b, stock):
    """Return whether both conditions match one physically possible collection."""
    from .cards import condition_matches

    colors = tuple(stock)
    counts = [0] * len(colors)

    def visit(index, remaining):
        if index == len(colors):
            collection = dict(zip(colors, counts))
            return condition_matches(a, collection) and condition_matches(b, collection)

        # Bound each color by its actual stock and the total stock left.
        for quantity in range(min(stock[colors[index]], remaining) + 1):
            counts[index] = quantity
            if visit(index + 1, remaining - quantity):
                return True
        counts[index] = 0
        return False

    return visit(0, sum(stock.values()))


def _validate_condition(card_id, condition):
    from .cards import ConditionKind, MajorityBasis
    kind = condition.kind
    if len(set(condition.colors)) != len(condition.colors):
        raise ConfigurationError(
            f"La condition {kind.value!r} de la carte {card_id!r} répète une couleur ; chaque couleur ne peut apparaître qu'une fois."
        )
    if kind is ConditionKind.MAJORITY and condition.majority_basis is not None and not isinstance(condition.majority_basis, MajorityBasis):
        raise ConfigurationError(f"La définition de majorité de la carte {card_id!r} est inconnue.")
    valid = {
        ConditionKind.COLOR_COUNT: len(condition.colors) == 1 and condition.threshold is not None,
        ConditionKind.TOTAL_COUNT: condition.threshold is not None,
        ConditionKind.TWO_PAIRS: len(condition.colors) in (0, 2),
        ConditionKind.COMPOSITION: bool(condition.composition),
        ConditionKind.EQUAL_COUNTS: len(condition.colors) == 2 and condition.minimum is not None,
        ConditionKind.DIVERSITY: bool(condition.colors) and condition.minimum is not None and condition.minimum <= len(condition.colors),
        ConditionKind.SAME_COLOR_COUNT: condition.threshold is not None,
        ConditionKind.MAJORITY: len(condition.colors) <= 1 and condition.majority_basis is not None and condition.minimum is not None,
    }.get(kind, False)
    if not valid:
        raise ConfigurationError(f"La condition {kind!r} de la carte {card_id!r} est incomplète ou invalide.")


def _complete_setup_possible(cards, stock, mode, hand_size):
    names = tuple(stock)
    initial = tuple(stock[c] for c in names)
    from .cards import condition_matches
    options = []
    for card in cards:
        valid = []
        def combos(i, left, values):
            if i == len(names) - 1:
                vec = values + (left,)
                counts = dict(zip(names, vec))
                if sum(vec) == hand_size and not any(condition_matches(defeat, counts)
                                                     for defeat in card.defeat_conditions) and not (
                    mode is GameMode.SECRET_OBJECTIVE and condition_matches(card.victory, counts)):
                    valid.append(vec)
                return
            for n in range(left + 1): combos(i + 1, left - n, values + (n,))
        combos(0, hand_size, ())
        if not valid:
            return False
        options.append(valid)
    memo = set()
    def assign(i, remaining):
        if i == len(options): return True
        key = (i, remaining)
        if key in memo: return False
        memo.add(key)
        for vec in options[i]:
            if all(v <= r for v, r in zip(vec, remaining)) and assign(i + 1, tuple(r-v for r, v in zip(remaining, vec))):
                return True
        return False
    return assign(0, initial)
