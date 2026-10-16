"""Validated, configurable card reserves; selection is reproducible via the caller's RNG."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from itertools import combinations
from types import MappingProxyType
from typing import Mapping

from .cards import Card, ConditionKind


@dataclass(frozen=True, slots=True)
class CardPool:
    cards: tuple[Card, ...]
    expected_defeat_counts: Mapping[ConditionKind, int]

    def __post_init__(self) -> None:
        object.__setattr__(self, "cards", tuple(self.cards))
        object.__setattr__(self, "expected_defeat_counts", MappingProxyType(dict(self.expected_defeat_counts)))
        if not self.cards:
            raise ValueError("La réserve de cartes ne peut pas être vide.")
        if any(not isinstance(card, Card) for card in self.cards):
            raise ValueError("La réserve ne contient que des cartes valides.")
        if len({card.id for card in self.cards}) != len(self.cards):
            raise ValueError("Les identifiants des cartes de la réserve doivent être uniques.")
        if not self.expected_defeat_counts:
            raise ValueError("Déclarez les familles de défaite attendues dans la réserve.")
        if any(not isinstance(kind, ConditionKind) or count != 2
               for kind, count in self.expected_defeat_counts.items()):
            raise ValueError("La réserve doit déclarer exactement deux exemplaires attendus par type de défaite.")
        actual = Counter(condition.kind for card in self.cards for condition in card.defeat_conditions)
        if actual != Counter(self.expected_defeat_counts):
            raise ValueError(
                f"Composition de réserve invalide : {dict(actual)!r}, "
                f"attendu {dict(self.expected_defeat_counts)!r}."
            )

    def validate_for(self, player_count: int) -> None:
        if len(self.cards) < player_count:
            raise ValueError(f"Réserve insuffisante : {player_count} cartes sont nécessaires, {len(self.cards)} disponibles.")

    def draw(self, count: int, rng) -> tuple[Card, ...]:
        self.validate_for(count)
        selected = tuple(rng.sample(self.cards, count))
        if len({card.id for card in selected}) != count:
            raise RuntimeError("La sélection de cartes a produit un doublon.")
        return selected

    def validate_setup(self, count: int, stock, mode, hand_size: int) -> None:
        """Reject unusable cards and reserves before any random subset is selected."""
        self.validate_for(count)
        from .config import _complete_setup_possible

        for card in self.cards:
            if not _complete_setup_possible((card,), stock, mode, hand_size):
                raise ValueError(
                    f"La carte {card.id!r} ne permet aucune collection initiale valide "
                    "avec le stock et les paramètres configurés."
                )
        if not any(_complete_setup_possible(selection, stock, mode, hand_size)
                   for selection in combinations(self.cards, count)):
            raise ValueError(
                "Aucune combinaison de cartes de la réserve ne permet une distribution "
                "initiale complète et valide avec le stock configuré."
            )

    def draw_usable(self, count: int, rng, stock, mode, hand_size: int) -> tuple[Card, ...]:
        """Choose reproducibly among subsets that can all be dealt validly."""
        self.validate_for(count)
        from .config import _complete_setup_possible

        usable = tuple(selection for selection in combinations(self.cards, count)
                       if _complete_setup_possible(selection, stock, mode, hand_size))
        if not usable:
            raise ValueError(
                "Aucune combinaison de cartes de la réserve ne permet une distribution "
                "initiale complète et valide avec le stock configuré."
            )
        selected = list(usable[rng.randrange(len(usable))])
        rng.shuffle(selected)
        return tuple(selected)
