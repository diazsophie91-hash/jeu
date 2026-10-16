"""Private, proposal-scoped messages that never become game commands."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from engine.state import Phase


class CommunicationKind(str, Enum):
    SPONTANEOUS = "spontaneous"
    QUESTION = "question"
    RESPONSE = "response"


@dataclass(frozen=True, slots=True)
class Message:
    sequence: int
    proposal_id: int
    author_id: str
    kind: CommunicationKind
    text: str
    reply_to: int | None = None


@dataclass(frozen=True, slots=True)
class CommunicationIntent:
    kind: CommunicationKind
    text: str
    reply_to: int | None = None


class CommunicationChannel:
    """Orchestrator-owned channel; messages are only visible to offer participants."""

    def __init__(self, game):
        self._game = game
        self._messages: list[Message] = []
        self._participants: dict[int, tuple[str, str]] = {}

    @property
    def current_proposal_id(self) -> int:
        view = self._game.public_view()
        if view.phase is not Phase.DECISION or view.proposal is None:
            raise ValueError("Les messages sont disponibles uniquement pendant une proposition en attente.")
        for event in reversed(self._game.public_event_history()):
            if event.kind == "gift_proposed":
                donor, recipient = view.proposal
                if event.data.get("donor_id") == donor and event.data.get("recipient_id") == recipient:
                    self._participants[event.sequence] = (donor, recipient)
                    return event.sequence
        raise RuntimeError("Identifiant public de proposition introuvable.")

    def send(self, author_id: str, intent: CommunicationIntent) -> Message:
        proposal_id = self.current_proposal_id
        donor, recipient = self._participants[proposal_id]
        if (not isinstance(intent, CommunicationIntent) or not isinstance(intent.text, str)
                or not intent.text.strip() or not isinstance(intent.kind, CommunicationKind)):
            raise ValueError("Un message écrit doit contenir un texte.")
        if author_id not in (donor, recipient):
            raise ValueError("Seuls les participants au cadeau peuvent communiquer.")
        if intent.kind is CommunicationKind.SPONTANEOUS and author_id != donor:
            raise ValueError("Seul le donneur peut envoyer une annonce spontanée.")
        if intent.kind is CommunicationKind.QUESTION and author_id != recipient:
            raise ValueError("Seul le destinataire peut poser une question.")
        if intent.kind is CommunicationKind.RESPONSE:
            if author_id != donor or intent.reply_to is None:
                raise ValueError("Une réponse doit être envoyée par le donneur en réponse à une question.")
            question = next((m for m in self._messages
                             if m.sequence == intent.reply_to and m.proposal_id == proposal_id), None)
            if question is None or question.proposal_id != proposal_id or question.kind is not CommunicationKind.QUESTION:
                raise ValueError("La réponse doit viser une question de cette proposition.")
        elif intent.reply_to is not None:
            raise ValueError("Seule une réponse peut référencer une question.")
        sequence = 1 + sum(message.proposal_id == proposal_id for message in self._messages)
        message = Message(sequence, proposal_id, author_id,
                          intent.kind, intent.text, intent.reply_to)
        self._messages.append(message)
        return message

    def messages_for(self, player_id: str, proposal_id: int | None = None) -> tuple[Message, ...]:
        target = self.current_proposal_id if proposal_id is None else proposal_id
        participants = self._participants.get(target)
        if participants is None or player_id not in participants:
            return ()
        return tuple(message for message in self._messages if message.proposal_id == target)

    def _message_history(self) -> tuple[Message, ...]:
        """Orchestrator-only audit log; never hand this object to an agent."""
        return tuple(self._messages)
