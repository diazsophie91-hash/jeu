"""Explicit, auditable selection of the first player outside rule resolution."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import isfinite
from typing import Callable, Mapping, Sequence


class FirstPlayerMethod(str, Enum):
    COLLECTIVE = "collective_choice"
    MOST_RECENT_GIFT = "most_recent_real_gift"


class UnresolvedTie(ValueError):
    def __init__(self, candidates: Sequence[str]):
        self.candidates = tuple(candidates)
        super().__init__(f"Égalité de récence non départagée par le groupe : {self.candidates!r}.")


@dataclass(frozen=True, slots=True)
class FirstPlayerSelection:
    player_id: str
    method: FirstPlayerMethod
    tied_candidates: tuple[str, ...] = ()
    resolution: str = "direct"

    def __post_init__(self) -> None:
        if not isinstance(self.player_id, str) or not self.player_id:
            raise ValueError("L'identifiant du premier joueur est obligatoire.")
        if not isinstance(self.method, FirstPlayerMethod):
            raise ValueError("La méthode de sélection du premier joueur est inconnue.")
        object.__setattr__(self, "tied_candidates", tuple(self.tied_candidates))
        if len(set(self.tied_candidates)) != len(self.tied_candidates):
            raise ValueError("Les candidats à égalité doivent être uniques.")
        if self.resolution not in {"collective_choice", "most_recent_gift", "group_consensus"}:
            raise ValueError("La méthode de résolution doit être explicite.")
        if self.resolution == "group_consensus":
            if self.method is not FirstPlayerMethod.MOST_RECENT_GIFT or len(self.tied_candidates) < 2 or self.player_id not in self.tied_candidates:
                raise ValueError("Un consensus doit résoudre une égalité de récence et choisir l'un des candidats.")
        elif self.tied_candidates:
            raise ValueError("Des candidats à égalité exigent une résolution de consensus explicite.")
        if self.resolution == "collective_choice" and self.method is not FirstPlayerMethod.COLLECTIVE:
            raise ValueError("La trace de choix collectif ne correspond pas à la méthode sélectionnée.")
        if self.resolution == "most_recent_gift" and self.method is not FirstPlayerMethod.MOST_RECENT_GIFT:
            raise ValueError("La trace de récence ne correspond pas à la méthode sélectionnée.")


def select_first_player(
    player_ids: Sequence[str],
    method: FirstPlayerMethod,
    *,
    collective_choice: str | None = None,
    gift_recency: Mapping[str, float] | None = None,
    consensus_choice: str | None = None,
    consensus: Callable[[tuple[str, ...]], str] | None = None,
) -> FirstPlayerSelection:
    ids = tuple(player_ids)
    if len(ids) < 2 or len(set(ids)) != len(ids) or any(not isinstance(pid, str) or not pid for pid in ids):
        raise ValueError("Les joueurs participants doivent être au moins deux, uniques et identifiés.")
    if not isinstance(method, FirstPlayerMethod):
        raise ValueError("La méthode de sélection du premier joueur est inconnue.")
    if method is FirstPlayerMethod.COLLECTIVE:
        if gift_recency is not None or consensus_choice is not None or consensus is not None:
            raise ValueError("Les données de récence et de consensus ne s'appliquent pas au choix collectif.")
        selected = collective_choice
        resolution = "collective_choice"
        tied: tuple[str, ...] = ()
    else:
        if collective_choice is not None:
            raise ValueError("Le choix collectif ne s'applique pas à la méthode de récence.")
        if gift_recency is None or set(gift_recency) != set(ids):
            raise ValueError("La récence des cadeaux réels doit être fournie pour chaque joueur participant.")
        values = tuple(gift_recency[pid] for pid in ids)
        if any(not isinstance(value, (int, float)) or isinstance(value, bool) or not isfinite(value) for value in values):
            raise ValueError("Les valeurs de récence doivent être des nombres finis.")
        latest = max(values)
        tied = tuple(pid for pid in ids if gift_recency[pid] == latest)
        if len(tied) == 1:
            selected = tied[0]
            resolution = "most_recent_gift"
            tied = ()
        else:
            if consensus_choice is not None and consensus is not None:
                raise ValueError("Fournissez un choix de consensus ou un mécanisme de consensus, pas les deux.")
            selected = consensus_choice if consensus_choice is not None else (consensus(tied) if consensus else None)
            if selected is None:
                raise UnresolvedTie(tied)
            resolution = "group_consensus"
    if selected not in ids:
        raise ValueError("Le premier joueur sélectionné doit participer à la partie.")
    return FirstPlayerSelection(selected, method, tied, resolution)


def create_game_with_selection(player_ids, config, selection: FirstPlayerSelection, **game_options):
    """Pass a resolved, auditable selection to the existing engine setup API."""
    if selection.player_id not in player_ids:
        raise ValueError("Le premier joueur sélectionné doit participer à la partie.")
    from .setup import create_game
    return create_game(player_ids, config, first_player_id=selection.player_id,
                       first_player_method=selection.method.value,
                       first_player_resolution=selection.resolution,
                       first_player_tied_candidates=selection.tied_candidates,
                       **game_options)
