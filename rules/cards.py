"""Structured tokens, cards, and conditions. No rule is encoded as free text."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Mapping


class ConditionKind(str, Enum):
    COLOR_COUNT = "color_count"
    TOTAL_COUNT = "total_count"
    TWO_PAIRS = "two_pairs"
    COMPOSITION = "composition"
    EQUAL_COUNTS = "equal_counts"
    DIVERSITY = "diversity"
    SAME_COLOR_COUNT = "same_color_count"
    MAJORITY = "majority"


class MajorityBasis(str, Enum):
    PLURALITY = "plurality"
    MORE_THAN_HALF = "more_than_half"


@dataclass(frozen=True, slots=True)
class Token:
    id: str
    color: str


@dataclass(frozen=True, slots=True)
class Condition:
    kind: ConditionKind
    threshold: int | None = None
    colors: tuple[str, ...] = ()
    exact: bool = False
    composition: tuple[tuple[str, int], ...] = ()
    minimum: int | None = None
    max_per_color: int | None = None
    majority_basis: MajorityBasis | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.kind, ConditionKind):
            raise ValueError(f"Type de condition invalide : {self.kind!r}")
        if not isinstance(self.colors, (tuple, list)) or any(not isinstance(color, str) or not color for color in self.colors):
            raise ValueError("Les couleurs d'une condition doivent être des identifiants non vides.")
        object.__setattr__(self, "colors", tuple(self.colors))
        if not isinstance(self.composition, (tuple, list)):
            raise ValueError("La composition d'une condition doit être une suite de couples couleur/quantité.")
        normalized_composition = tuple(self.composition)
        if any(not isinstance(pair, (tuple, list)) or len(pair) != 2
               or not isinstance(pair[0], str) or not pair[0]
               or not isinstance(pair[1], int) or isinstance(pair[1], bool)
               for pair in normalized_composition):
            raise ValueError("Chaque entrée de composition doit contenir une couleur et une quantité entière.")
        object.__setattr__(self, "composition", tuple((color, amount) for color, amount in normalized_composition))
        if not isinstance(self.exact, bool):
            raise ValueError("Le paramètre exact doit être booléen.")
        if self.majority_basis is not None and not isinstance(self.majority_basis, MajorityBasis):
            raise ValueError("La définition de majorité est invalide.")
        if self.threshold is not None and (not isinstance(self.threshold, int) or isinstance(self.threshold, bool)):
            raise ValueError("Le seuil d'une condition doit être un entier.")
        if self.threshold is not None and self.threshold < 1:
            raise ValueError("Le seuil d'une condition doit être positif.")
        if self.minimum is not None and (not isinstance(self.minimum, int) or isinstance(self.minimum, bool)):
            raise ValueError("Le minimum d'une condition doit être un entier.")
        if self.minimum is not None and self.minimum < 1:
            raise ValueError("Le minimum d'une condition doit être positif.")
        if self.max_per_color is not None and (not isinstance(self.max_per_color, int) or isinstance(self.max_per_color, bool)):
            raise ValueError("La limite par couleur doit être un entier.")
        if self.max_per_color is not None and self.max_per_color < 1:
            raise ValueError("La limite par couleur doit être positive.")
        if any(n < 1 for _, n in self.composition):
            raise ValueError("Les quantités de composition doivent être positives.")
        if len(dict(self.composition)) != len(self.composition):
            raise ValueError("Une couleur apparaît plusieurs fois dans une composition.")


@dataclass(frozen=True, slots=True)
class Card:
    id: str
    defeat: Condition | tuple[Condition, ...]
    victory: Condition | None = None

    def __post_init__(self) -> None:
        if self.victory is not None and not isinstance(self.victory, Condition):
            raise ValueError("La condition de victoire doit être une Condition ou None.")
        conditions = normalize_defeat_conditions(self.defeat)
        # Keep the historical single-condition attribute shape for existing callers.
        object.__setattr__(self, "defeat", conditions[0] if len(conditions) == 1 else conditions)

    @property
    def defeat_conditions(self) -> tuple[Condition, ...]:
        """Uniform immutable form used by validation, setup, and rule evaluation."""
        return normalize_defeat_conditions(self.defeat)


def normalize_defeat_conditions(value: Condition | Iterable[Condition]) -> tuple[Condition, ...]:
    if isinstance(value, Condition):
        conditions = (value,)
    elif isinstance(value, (tuple, list)):
        conditions = tuple(value)
    else:
        raise ValueError("Une carte doit porter une ou plusieurs conditions de défaite.")
    if not conditions:
        raise ValueError("Une carte doit porter au moins une condition de défaite.")
    if any(not isinstance(condition, Condition) for condition in conditions):
        raise ValueError("Chaque condition de défaite doit être une Condition.")
    return conditions


def condition_matches(condition: Condition, counts: Mapping[str, int]) -> bool:
    total = sum(counts.values())
    kind = condition.kind
    if kind is ConditionKind.COLOR_COUNT:
        if len(condition.colors) != 1 or condition.threshold is None:
            raise ValueError("COLOR_COUNT exige une couleur et un seuil.")
        n = counts.get(condition.colors[0], 0)
        return n == condition.threshold if condition.exact else n >= condition.threshold
    if kind is ConditionKind.TOTAL_COUNT:
        if condition.threshold is None:
            raise ValueError("TOTAL_COUNT exige un seuil.")
        return total == condition.threshold if condition.exact else total >= condition.threshold
    if kind is ConditionKind.TWO_PAIRS:
        if condition.threshold is not None:
            pair_n = condition.threshold
        else:
            pair_n = 2
        colors = condition.colors or tuple(counts)
        if len(condition.colors) not in (0, 2):
            raise ValueError("TWO_PAIRS accepte zéro ou deux couleurs explicites.")
        pairs = [(a, b) for i, a in enumerate(colors) for b in colors[i + 1:]
                 if (counts.get(a, 0) == pair_n if condition.exact else counts.get(a, 0) >= pair_n)
                 and (counts.get(b, 0) == pair_n if condition.exact else counts.get(b, 0) >= pair_n)]
        return bool(pairs)
    if kind is ConditionKind.COMPOSITION:
        if not condition.composition:
            raise ValueError("COMPOSITION exige une composition.")
        matches = all((counts.get(c, 0) == n if condition.exact else counts.get(c, 0) >= n)
                      for c, n in condition.composition)
        if condition.exact:
            # An exact composition defines the whole collection: no unlisted
            # color (or extra token) may be present.
            return matches and total == sum(n for _, n in condition.composition)
        return matches
    if kind is ConditionKind.EQUAL_COUNTS:
        if len(condition.colors) != 2 or condition.minimum is None:
            raise ValueError("EQUAL_COUNTS exige deux couleurs et un minimum explicite.")
        a, b = condition.colors
        return counts.get(a, 0) == counts.get(b, 0) and counts.get(a, 0) >= condition.minimum
    if kind is ConditionKind.DIVERSITY:
        required = condition.colors or tuple(counts)
        if condition.minimum is None or not required or condition.minimum > len(required):
            raise ValueError("DIVERSITY exige des couleurs candidates et un minimum compris entre un et leur nombre.")
        if condition.max_per_color is not None and any(
            counts.get(c, 0) > condition.max_per_color for c in required
        ):
            return False
        return sum(counts.get(c, 0) > 0 for c in required) >= condition.minimum
    if kind is ConditionKind.SAME_COLOR_COUNT:
        if condition.threshold is None:
            raise ValueError("SAME_COLOR_COUNT exige un seuil.")
        vals = counts.values()
        return any(v == condition.threshold if condition.exact else v >= condition.threshold for v in vals)
    if kind is ConditionKind.MAJORITY:
        candidates = condition.colors or tuple(counts)
        if len(condition.colors) > 1 or condition.majority_basis is None or condition.minimum is None:
            raise ValueError("MAJORITY exige au plus une couleur cible, un minimum et une définition explicites.")
        return any(counts.get(c, 0) >= condition.minimum
                   and (all(counts.get(c, 0) > counts.get(other, 0) for other in counts if other != c)
                        if condition.majority_basis is MajorityBasis.PLURALITY
                        else counts.get(c, 0) * 2 > total)
                   and (condition.max_per_color is None or counts.get(c, 0) <= condition.max_per_color)
                   for c in candidates)
    raise ValueError(f"Type de condition inconnu : {kind!r}")
