"""Composable deterministic decision and message strategies for agent pilots."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from engine.actions import AcceptGift, ChooseRecipient, ProposeGift, RefuseGift
from engine.state import PrivateView
from .communication import CommunicationIntent, CommunicationKind, Message


class DecisionStrategy(Protocol):
    name: str

    def choose_action(self, view: PrivateView, legal_actions: tuple, messages: tuple[Message, ...]):
        """Choose from the supplied legal actions without receiving engine internals."""


class CommunicationStrategy(Protocol):
    name: str

    def after_proposal(self, view: PrivateView, messages: tuple[Message, ...]) -> CommunicationIntent | None: ...

    def answer_questions(self, view: PrivateView, questions: tuple[Message, ...],
                         messages: tuple[Message, ...]) -> CommunicationIntent | None: ...


@dataclass(frozen=True, slots=True)
class ScriptedDecision:
    """Simple policy: choose a configured recipient/token and accept or refuse."""
    recipient_id: str | None = None
    token_index: int = 0
    accept: bool = True
    name: str = "scripted"

    def choose_action(self, view, legal_actions, messages=()):
        if not legal_actions:
            raise RuntimeError(f"Aucune action légale pour {view.player_id}.")
        if isinstance(legal_actions[0], ChooseRecipient):
            return next((a for a in legal_actions if a.recipient_id == self.recipient_id), legal_actions[0])
        if isinstance(legal_actions[0], ProposeGift):
            index = max(0, min(self.token_index, len(legal_actions) - 1))
            own_ids = [token.id for token in view.hand]
            preferred = own_ids[index] if index < len(own_ids) else None
            return next((a for a in legal_actions if a.token_id == preferred), legal_actions[0])
        wanted = AcceptGift if self.accept else RefuseGift
        return next((a for a in legal_actions if isinstance(a, wanted)), legal_actions[0])


@dataclass(frozen=True, slots=True)
class SilentCommunication:
    name: str = "silent"

    def after_proposal(self, view, messages):
        return None

    def answer_questions(self, view, questions, messages):
        return None


@dataclass(frozen=True, slots=True)
class ScriptedCommunication:
    """Configured spontaneous statement, question, and optional response text.

    Text is intentionally opaque: the channel never checks whether claims are true.
    Set any field to None to remain silent at that opportunity.
    """
    spontaneous_text: str | None = None
    question_text: str | None = None
    response_text: str | None = None
    name: str = "scripted_messages"
    truthfulness_mode: str = "unspecified"

    def __post_init__(self):
        if self.truthfulness_mode not in {"truthful", "deceptive", "unspecified"}:
            raise ValueError("Le mode de véracité doit être truthful, deceptive ou unspecified.")

    def after_proposal(self, view, messages):
        proposal = view.public.proposal
        if proposal is None:
            return None
        donor_id, recipient_id = proposal
        if view.player_id == donor_id and self.spontaneous_text is not None:
            return CommunicationIntent(CommunicationKind.SPONTANEOUS, self.spontaneous_text)
        if view.player_id == recipient_id and self.question_text is not None:
            return CommunicationIntent(CommunicationKind.QUESTION, self.question_text)
        return None

    def answer_questions(self, view, questions: tuple[Message, ...], messages):
        if self.response_text is None or not questions:
            return None
        already_answered = {m.reply_to for m in messages if m.kind is CommunicationKind.RESPONSE}
        question = next((q for q in reversed(questions) if q.sequence not in already_answered), None)
        if question is None:
            return None
        return CommunicationIntent(CommunicationKind.RESPONSE, self.response_text, question.sequence)


@dataclass(frozen=True, slots=True)
class ColorClaimCommunication:
    """Make a deterministic color claim from the donor's private offered-token view."""
    known_colors: tuple[str, ...]
    truthful: bool = True
    spontaneous: bool = True
    question_text: str | None = None
    respond_to_questions: bool = True
    name: str = "color_claim"

    def __post_init__(self):
        object.__setattr__(self, "known_colors", tuple(self.known_colors))
        if any(not isinstance(color, str) or not color for color in self.known_colors):
            raise ValueError("Les couleurs d'une stratégie de message doivent être des identifiants non vides.")
        if len(set(self.known_colors)) < 2:
            raise ValueError("Une stratégie de couleur exige au moins deux couleurs possibles.")
        if any(not isinstance(color, str) or not color for color in self.known_colors):
            raise ValueError("Les couleurs d'une stratégie de message doivent être des identifiants non vides.")

    @property
    def truthfulness_mode(self) -> str:
        return "truthful" if self.truthful else "deceptive"

    def _claim(self, view, reply_to=None):
        if view.offered_token is None:
            return None
        actual = view.offered_token.color
        claimed = actual if self.truthful else next(color for color in self.known_colors if color != actual)
        kind = CommunicationKind.SPONTANEOUS if reply_to is None else CommunicationKind.RESPONSE
        text = f"Le jeton est {claimed}."
        return CommunicationIntent(kind, text, reply_to)

    def after_proposal(self, view, messages):
        proposal = view.public.proposal
        if proposal is None:
            return None
        donor_id, recipient_id = proposal
        if view.player_id == donor_id and self.spontaneous:
            return self._claim(view)
        if view.player_id == recipient_id and self.question_text is not None:
            return CommunicationIntent(CommunicationKind.QUESTION, self.question_text)
        return None

    def answer_questions(self, view, questions, messages):
        if not self.respond_to_questions:
            return None
        answered = {message.reply_to for message in messages if message.kind is CommunicationKind.RESPONSE}
        question = next((item for item in reversed(questions) if item.sequence not in answered), None)
        return self._claim(view, question.sequence) if question is not None else None


@dataclass
class Agent:
    """Actor-bound bot. Its policies receive only the player's filtered view."""
    controller: object
    decision_strategy: DecisionStrategy
    communication_strategy: CommunicationStrategy = SilentCommunication()

    @property
    def player_id(self) -> str:
        return self.controller.player_id

    def decide(self, messages: tuple[Message, ...] = ()):
        view = self.controller.view()
        legal = self.controller.legal_actions()
        action = self.decision_strategy.choose_action(view, legal, messages)
        if action not in legal:
            raise ValueError(f"La stratégie {self.decision_strategy.name!r} a choisi une action illégale.")
        return self.controller.submit(action)
