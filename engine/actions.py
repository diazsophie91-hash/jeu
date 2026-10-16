"""Commands accepted by the engine; agents never mutate state directly."""
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ChooseRecipient:
    recipient_id: str


@dataclass(frozen=True, slots=True)
class ProposeGift:
    token_id: str


@dataclass(frozen=True, slots=True)
class AcceptGift:
    """Accept the pending gift; an empty common bag forces this action."""


@dataclass(frozen=True, slots=True)
class RefuseGift:
    """Refuse the pending gift when the common bag is nonempty."""
