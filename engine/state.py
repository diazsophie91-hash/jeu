"""Internal state and privacy-filtered views."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from rules.cards import Card, Token
from rules.card_pool import CardPool
from rules.config import GameConfig


class Phase(str, Enum):
    CHOOSE_RECIPIENT = "choose_recipient"
    CHOOSE_TOKEN = "choose_token"
    DECISION = "decision"
    ROUND_OVER = "round_over"
    GAME_OVER = "game_over"


@dataclass
class PlayerState:
    id: str
    hand: list[Token] = field(default_factory=list)
    card: Card | None = None
    alive: bool = True
    revealed: bool = False
    score: int = 0
    credited_eliminations: int = 0


@dataclass(frozen=True, slots=True)
class Event:
    sequence: int
    kind: str
    round_number: int
    data: dict[str, Any]
    public_data: dict[str, Any]


@dataclass(frozen=True, slots=True)
class VisibleEvent:
    sequence: int
    kind: str
    round_number: int
    data: dict[str, Any]


@dataclass
class Proposal:
    donor_id: str
    recipient_id: str
    token: Token | None
    donor_was_eliminated: bool = False
    origin: str = "initial"


@dataclass
class GameState:
    config: GameConfig
    players: list[PlayerState]
    common_bag: list[Token]
    active_player_id: str | None
    phase: Phase
    round_number: int = 1
    proposal: Proposal | None = None
    result: str | None = None
    winners: tuple[str, ...] = ()
    round_winner: str | None = None
    rounds_completed: int = 0
    c1_tiebreak_round: bool = False
    round_threshold_reached: bool = False
    events: list[Event] = field(default_factory=list)
    resolution_eliminated: set[str] = field(default_factory=set)
    card_pool: CardPool | None = None

    def emit(self, kind: str, *, public_data: dict[str, Any] | None = None, **data: Any) -> None:
        self.events.append(Event(len(self.events) + 1, kind, self.round_number, data,
                                dict(data) if public_data is None else public_data))

    def player(self, player_id: str) -> PlayerState:
        for player in self.players:
            if player.id == player_id:
                return player
        raise KeyError(player_id)

    def assert_invariants(self) -> None:
        tokens = list(self.common_bag)
        for p in self.players:
            tokens.extend(p.hand)
            if not p.alive and p.hand:
                raise AssertionError(f"Éliminé {p.id} conserve des jetons personnels")
        if self.proposal:
            if self.phase is Phase.DECISION and self.proposal.token is None:
                raise AssertionError("Une décision est attendue sans jeton proposé.")
            if self.proposal.token is not None:
                tokens.append(self.proposal.token)
        ids = [t.id for t in tokens]
        if len(ids) != len(set(ids)):
            raise AssertionError("Un jeton est présent dans plusieurs emplacements")
        expected = sum(self.config.colors.values())
        if len(ids) != expected:
            raise AssertionError(f"Conservation des jetons violée : {len(ids)} au lieu de {expected}")


@dataclass(frozen=True, slots=True)
class PublicPlayer:
    id: str
    alive: bool
    hand_size: int
    revealed_card: Card | None
    score: int
    credited_eliminations: int


@dataclass(frozen=True, slots=True)
class PublicView:
    mode: str
    phase: Phase
    active_player_id: str | None
    players: tuple[PublicPlayer, ...]
    common_bag_nonempty: bool | None
    possible_common_colors: tuple[str, ...]
    proposal: tuple[str, str] | None
    result: str | None
    winners: tuple[str, ...]
    round_number: int


@dataclass(frozen=True, slots=True)
class PrivateView:
    public: PublicView
    player_id: str
    hand: tuple[Token, ...]
    card: Card
    common_bag_colors: tuple[str, ...] | None
    offered_token: Token | None
    can_refuse: bool | None

