"""Structured tokens, cards, and conditions. No rule is encoded as free text."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping


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
    defeat: Condition
    victory: Condition | None = None


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
        return all((counts.get(c, 0) == n if condition.exact else counts.get(c, 0) >= n)
                   for c, n in condition.composition)
    if kind is ConditionKind.EQUAL_COUNTS:
        if len(condition.colors) != 2 or condition.minimum is None:
            raise ValueError("EQUAL_COUNTS exige deux couleurs et un minimum explicite.")
        a, b = condition.colors
        return counts.get(a, 0) == counts.get(b, 0) and counts.get(a, 0) >= condition.minimum
    if kind is ConditionKind.DIVERSITY:
        required = condition.colors or tuple(counts)
        if condition.minimum is None: raise ValueError("DIVERSITY exige un minimum explicite.")
        return len(required) >= condition.minimum and all(counts.get(c, 0) >= 1 for c in required) and (
            condition.max_per_color is None or all(counts.get(c, 0) <= condition.max_per_color for c in required))
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
