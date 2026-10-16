"""The sole mutation boundary: validation, actions, rules, and transitions."""
from __future__ import annotations

import random
from dataclasses import dataclass
from typing import TypeAlias

from rules.cards import Token, condition_matches
from rules.config import GameMode, Succession, PointsFormat, ConfigurationError
from rules.rules import evaluate_defeat, evaluate_victory
from .actions import AcceptGift, RefuseGift, ChooseRecipient, ProposeGift
from .state import GameState, Phase, Proposal, PublicView, PublicPlayer, PrivateView, VisibleEvent


class EngineError(RuntimeError):
    """Base error for invalid engine operations or internal game state."""


class IllegalAction(EngineError):
    """The command is not legal for the current actor or state."""


class PhaseError(IllegalAction):
    """The command is invalid during the current game phase."""


class GameFinished(IllegalAction):
    """A command was submitted after the game reached a terminal state."""

Action: TypeAlias = ChooseRecipient | ProposeGift | AcceptGift | RefuseGift


@dataclass(frozen=True, slots=True)
class ActionResult:
    action_type: str
    events: tuple[VisibleEvent, ...]
    phase: Phase
    active_player_id: str | None


class GameEngine:
    """A game instance. Submit commands here; treat ``_state`` as private."""
    def __init__(self, state: GameState, rng: random.Random):
        self._state = state
        self._rng = rng

    @property
    def phase(self): return self._state.phase
    @property
    def active_player_id(self): return self._state.active_player_id
    @property
    def finished(self): return self._state.phase is Phase.GAME_OVER

    def public_view(self) -> PublicView:
        s = self._state
        proposal = None if s.proposal is None else (s.proposal.donor_id, s.proposal.recipient_id)
        return PublicView(s.config.mode.value, s.phase, s.active_player_id,
            tuple(PublicPlayer(p.id, p.alive, len(p.hand), p.card if p.revealed else None,
                               p.score, p.credited_eliminations) for p in s.players),
            None, (), proposal, s.result, s.winners, s.round_number)

    def private_view(self, player_id: str) -> PrivateView:
        p = self._state.player(player_id)
        if p.card is None: raise EngineError("Carte du joueur absente.")
        proposal = self._state.proposal
        offered = proposal.token if proposal and proposal.donor_id == player_id else None
        # Only the current gift recipient knows which colors may exist in the common bag.
        bag_colors = tuple(c for c,n in self._state.config.colors.items() if n > 0) if proposal and proposal.recipient_id == player_id else None
        can_refuse = bool(self._state.common_bag) if proposal and proposal.recipient_id == player_id else None
        return PrivateView(self.public_view(), player_id, tuple(p.hand), p.card, bag_colors, offered, can_refuse)

    def controller(self, player_id: str) -> "PlayerController":
        """Create an actor-bound API handle for an orchestrator to give one player."""
        self._state.player(player_id)
        return PlayerController(self, player_id)

    def public_event_history(self) -> tuple[VisibleEvent, ...]:
        return tuple(VisibleEvent(e.sequence, e.kind, e.round_number, dict(e.public_data)) for e in self._state.events)

    def legal_actions(self, player_id: str | None = None) -> tuple[Action, ...]:
        s = self._state
        actor = player_id or s.active_player_id
        if actor != s.active_player_id or actor is None or s.phase in (Phase.GAME_OVER, Phase.ROUND_OVER): return ()
        p = s.player(actor)
        if not p.alive: return ()
        if s.phase is Phase.CHOOSE_RECIPIENT:
            if not p.hand: return ()
            return tuple(ChooseRecipient(q.id) for q in s.players if q.alive and q.id != actor)
        if s.phase is Phase.CHOOSE_TOKEN:
            return tuple(ProposeGift(t.id) for t in p.hand)
        if s.phase is Phase.DECISION:
            return (AcceptGift(), RefuseGift()) if s.common_bag else (AcceptGift(),)
        return ()

    def submit(self, action: Action, player_id: str | None = None) -> ActionResult:
        s = self._state
        if s.phase is Phase.GAME_OVER: raise GameFinished("La partie est terminée.")
        if s.phase is Phase.ROUND_OVER: raise PhaseError("La manche est terminée ; commencez la manche suivante si les règles l'autorisent.")
        actor = player_id or s.active_player_id
        if actor != s.active_player_id: raise IllegalAction("Seul le joueur actif peut agir.")
        if actor is None or not s.player(actor).alive: raise IllegalAction("Aucun joueur actif valide.")
        before = len(s.events)
        if isinstance(action, ChooseRecipient): self._choose_recipient(actor, action)
        elif isinstance(action, ProposeGift): self._propose(actor, action)
        elif isinstance(action, AcceptGift): self._decide(actor, accept=True)
        elif isinstance(action, RefuseGift): self._decide(actor, accept=False)
        else: raise IllegalAction(f"Action inconnue : {type(action).__name__}")
        s.assert_invariants()
        visible = tuple(VisibleEvent(e.sequence, e.kind, e.round_number, dict(e.public_data)) for e in s.events[before:])
        return ActionResult(type(action).__name__, visible, s.phase, s.active_player_id)

    def _choose_recipient(self, actor, action):
        s = self._state
        if s.phase is not Phase.CHOOSE_RECIPIENT: raise PhaseError("Le choix du destinataire n'est pas attendu.")
        try:
            target = s.player(action.recipient_id)
        except KeyError as exc:
            raise IllegalAction(f"Destinataire inconnu : {action.recipient_id!r}.") from exc
        if not target.alive or target.id == actor: raise IllegalAction("Le destinataire doit être un autre joueur encore en jeu.")
        if not s.player(actor).hand: raise IllegalAction("Le donneur ne possède aucun jeton à proposer.")
        s.proposal = Proposal(actor, target.id, token=None)
        s.phase = Phase.CHOOSE_TOKEN
        s.emit("recipient_chosen", donor_id=actor, recipient_id=target.id)

    def _propose(self, actor, action):
        s = self._state
        if s.phase is not Phase.CHOOSE_TOKEN or not s.proposal: raise PhaseError("Aucune proposition n'attend de jeton.")
        if s.proposal.donor_id != actor: raise IllegalAction("Seul le donneur peut choisir le jeton.")
        donor = s.player(actor)
        token = next((t for t in donor.hand if t.id == action.token_id), None)
        if token is None: raise IllegalAction("Ce jeton n'appartient pas au sac personnel du donneur.")
        donor.hand.remove(token)
        s.proposal.token = token
        s.phase = Phase.DECISION
        s.active_player_id = s.proposal.recipient_id
        s.emit("token_removed", public_data={"donor_id": actor}, donor_id=actor,
               token_id=token.id, color=token.color)
        s.emit("gift_proposed", donor_id=actor, recipient_id=s.proposal.recipient_id)
        if s.config.donor_defeat_after_removal:
            s.emit("condition_checked", player_id=actor, trigger="donor_removal", revealed=False)
            if evaluate_defeat(donor.card, donor.hand):
                self._eliminate(actor, "donor_removal")
                s.proposal.donor_was_eliminated = True

    def _decide(self, actor, accept):
        s = self._state
        if s.phase is not Phase.DECISION or not s.proposal: raise PhaseError("Aucune décision de cadeau n'est attendue.")
        prop = s.proposal
        if prop.token is None: raise EngineError("Jeton proposé manquant dans la résolution.")
        if prop.recipient_id != actor: raise IllegalAction("Seul le destinataire peut décider.")
        if not accept and not s.common_bag:
            raise IllegalAction("Le sac commun est vide : le refus est impossible.")
        donor = s.player(prop.donor_id)
        recipient = s.player(prop.recipient_id)
        s.emit("gift_accepted" if accept or not s.common_bag else "gift_refused",
               donor_id=prop.donor_id, recipient_id=prop.recipient_id,
               forced=not accept and not s.common_bag)
        if accept or not s.common_bag:
            s.emit("token_revealed", token_id=prop.token.id, color=prop.token.color)
            recipient.hand.append(prop.token)
            s.emit("token_transferred", token_id=prop.token.id, recipient_id=recipient.id)
            won = self._check_recipient(recipient.id, "accepted_gift")
            eliminated_target = recipient.id in s.resolution_eliminated
        else:
            if prop.donor_was_eliminated:
                s.common_bag.append(prop.token)
                s.emit("token_returned", public_data={"destination": "common_bag", "revealed": False},
                       token_id=prop.token.id, destination="common_bag", revealed=False)
            else:
                donor.hand.append(prop.token)
                s.emit("token_returned", public_data={"destination": "donor_hand", "revealed": False},
                       token_id=prop.token.id, destination="donor_hand", revealed=False)
            drawn = self._draw(recipient.id, "refusal", s.config.reveal_refusal_draw)
            won = self._check_recipient(recipient.id, "refusal_draw") if drawn else False
            eliminated_target = recipient.id in s.resolution_eliminated
        s.proposal = None
        if won:
            return
        alive = [p for p in s.players if p.alive]
        # An action that itself eliminates everyone is a terminal tie and awards nothing.
        if not alive:
            self._terminal_tie()
            return
        if eliminated_target and donor.id != recipient.id and s.config.mode is GameMode.POINTS:
            self._credit_elimination(donor.id, "recipient_elimination")
        if self._round_threshold_was_hit():
            self._finish_round(s.player(self._threshold_player()).id)
            return
        if len(alive) == 1:
            if s.config.mode is GameMode.POINTS:
                self._finish_round(alive[0].id)
            else:
                self._finish_game("last_survivor", (alive[0].id,))
            return
        if s.config.succession is Succession.CLOCKWISE:
            if s.resolution_eliminated:
                if recipient.alive:
                    self._activate(recipient.id, "recipient_survived_donor_elimination")
                else:
                    self._clockwise_chain(recipient.id, donor.id)
            else:
                self._activate(recipient.id, "normal_recipient_turn")
        else:
            self._succession_a(donor.id, recipient.id, bool(s.resolution_eliminated))
        s.resolution_eliminated.clear()

    def _check_recipient(self, player_id, trigger):
        s = self._state
        p = s.player(player_id)
        if not p.alive: return False
        s.emit("condition_checked", player_id=player_id, trigger=trigger, revealed=False)
        if s.config.mode is GameMode.SECRET_OBJECTIVE and evaluate_victory(p.card, p.hand):
            p.revealed = True
            s.emit("card_revealed", player_id=player_id, card=p.card)
            self._finish_game("secret_objective", (player_id,))
            return True
        if evaluate_defeat(p.card, p.hand): self._eliminate(player_id, trigger)
        return False

    def _draw(self, player_id, reason, reveal):
        s = self._state
        if not s.common_bag: return False
        token = self._rng.choice(s.common_bag)
        s.common_bag.remove(token)
        s.player(player_id).hand.append(token)
        public = {"player_id": player_id, "reason": reason}
        if reveal: public.update(token_id=token.id, color=token.color)
        s.emit("token_drawn", public_data=public, player_id=player_id, token_id=token.id,
               color=token.color if reveal else None, reason=reason)
        return True

    def _eliminate(self, player_id, reason):
        s = self._state
        p = s.player(player_id)
        if not p.alive or player_id in s.resolution_eliminated: return False
        p.alive = False
        s.resolution_eliminated.add(player_id)
        returned = [t.id for t in p.hand]
        s.common_bag.extend(p.hand); p.hand.clear()
        p.revealed = True
        s.emit("player_eliminated", public_data={"player_id": player_id, "reason": reason},
               player_id=player_id, reason=reason, returned_token_ids=tuple(returned))
        s.emit("card_revealed", player_id=player_id, card=p.card)
        return True

    def _credit_elimination(self, player_id, reason):
        p = self._state.player(player_id)
        p.score += 1
        p.credited_eliminations += 1
        self._state.emit("point_awarded", player_id=player_id, points=1, reason=reason)

    def _round_threshold_was_hit(self):
        s = self._state
        if s.config.mode is not GameMode.POINTS: return False
        return any(p.credited_eliminations >= s.config.elimination_threshold for p in s.players)

    def _threshold_player(self):
        return next(p.id for p in self._state.players if p.credited_eliminations >= self._state.config.elimination_threshold)

    def _finish_round(self, winner_id):
        s = self._state
        s.round_winner = winner_id
        if winner_id is not None:
            s.player(winner_id).score += s.config.bonus_points
            s.emit("round_bonus", player_id=winner_id, points=s.config.bonus_points)
        s.rounds_completed += 1
        s.result = "round_complete"
        s.phase = Phase.ROUND_OVER
        s.active_player_id = None
        s.emit("round_finished", winner_id=winner_id, scores={p.id:p.score for p in s.players})
        if s.config.points_format is PointsFormat.POINTS_THRESHOLD:
            if max(p.score for p in s.players) >= s.config.points_threshold:
                self._finish_game("points_threshold", self._leaders())
        else:
            target = s.config.fixed_rounds + (1 if s.c1_tiebreak_round else 0)
            if s.rounds_completed >= target:
                leaders = self._leaders()
                if len(leaders) > 1 and not s.c1_tiebreak_round:
                    s.c1_tiebreak_round = True
                    s.emit("tiebreak_required", player_ids=leaders)
                else:
                    self._finish_game("fixed_rounds", leaders)

    def _leaders(self):
        high = max(p.score for p in self._state.players)
        return tuple(p.id for p in self._state.players if p.score == high)

    def _finish_game(self, result, winners=()):
        s = self._state
        s.result = result
        s.winners = tuple(winners)
        s.phase = Phase.GAME_OVER
        s.active_player_id = None
        s.emit("game_finished", result=result, winners=tuple(winners))

    def _terminal_tie(self):
        self._finish_game("terminal_tie", ())

    def _next_alive(self, after_id):
        players = self._state.players
        start = next(i for i,p in enumerate(players) if p.id == after_id)
        for step in range(1, len(players)+1):
            p = players[(start+step) % len(players)]
            if p.alive: return p
        return None

    def _activate(self, player_id, reason):
        self._state.active_player_id = player_id
        self._state.emit("successor_selected", player_id=player_id, reason=reason)

    def _succession_a(self, donor_id, recipient_id, any_elimination):
        s = self._state
        if not any_elimination:
            self._activate(recipient_id, "normal_recipient_turn")
            return
        # The elimination's responsible player replays; on donor self-elimination,
        # the surviving recipient takes the next turn.
        both_eliminated = donor_id in s.resolution_eliminated and recipient_id in s.resolution_eliminated
        responsible = donor_id if recipient_id in s.resolution_eliminated else recipient_id
        if both_eliminated:
            responsible = recipient_id
            start_after = recipient_id
        else:
            start_after = responsible
        actor = s.player(responsible)
        if actor.alive:
            if not actor.hand:
                if self._draw(responsible, "replay", s.config.reveal_replay_draw):
                    if self._check_recipient(responsible, "replay_draw"):
                        return
                else:
                    self._eliminate(responsible, "empty_hand_replay")
            if actor.alive:
                self._activate(responsible, "responsible_replay")
                return
        alive = [p for p in s.players if p.alive]
        if not alive:
            self._terminal_tie(); return
        if len(alive) == 1:
            if s.config.mode is GameMode.POINTS: self._finish_round(alive[0].id)
            else: self._finish_game("last_survivor", (alive[0].id,))
            return
        cursor = start_after
        while True:
            nxt = self._next_alive(cursor)
            if nxt is None:
                self._terminal_tie(); return
            if not nxt.hand:
                if not self._draw(nxt.id, "successor_activation", s.config.reveal_replay_draw):
                    self._eliminate(nxt.id, "empty_hand_successor")
                elif self._check_recipient(nxt.id, "successor_draw"):
                    return
            if nxt.alive:
                self._activate(nxt.id, "clockwise_after_replay_elimination")
                return
            alive = [p for p in s.players if p.alive]
            if not alive:
                self._terminal_tie(); return
            if len(alive) == 1:
                if s.config.mode is GameMode.POINTS: self._finish_round(alive[0].id)
                else: self._finish_game("last_survivor", (alive[0].id,))
                return
            cursor = nxt.id

    def _clockwise_chain(self, after_id, responsible_id):
        s = self._state
        cursor = after_id
        while True:
            nxt = self._next_alive(cursor)
            if nxt is None:
                self._terminal_tie(); return
            if nxt.hand:
                self._activate(nxt.id, "clockwise_successor")
                return
            self._eliminate(nxt.id, "empty_hand_successor")
            alive = [p for p in s.players if p.alive]
            if not alive:
                self._terminal_tie(); return
            # Each nonterminal forced elimination in the B chain belongs to the
            # player whose initial action started the chain, even if eliminated.
            if s.config.mode is GameMode.POINTS and nxt.id != responsible_id:
                self._credit_elimination(responsible_id, "forced_successor_elimination")
                if self._round_threshold_was_hit():
                    self._finish_round(self._threshold_player()); return
            if len(alive) == 1:
                if s.config.mode is GameMode.POINTS: self._finish_round(alive[0].id)
                else: self._finish_game("last_survivor", (alive[0].id,))
                return
            cursor = nxt.id

    def _start_new_round(self, first_player_id=None):
        s = self._state
        if s.phase is not Phase.ROUND_OVER or s.phase is Phase.GAME_OVER:
            raise PhaseError("Aucune nouvelle manche n'est autorisée maintenant.")
        if first_player_id is None:
            raise IllegalAction("Le groupe doit désigner le premier joueur de la nouvelle manche.")
        ids = [p.id for p in s.players]
        starter=first_player_id or ids[s.round_number % len(ids)]
        if starter not in ids: raise IllegalAction("Le premier joueur doit participer à la partie.")
        if s.result == "round_complete":
            # C2 with no threshold reached continues; C1 continues through three rounds/tiebreak.
            if s.config.points_format is PointsFormat.POINTS_THRESHOLD and max(p.score for p in s.players) >= s.config.points_threshold:
                raise PhaseError("Le seuil de points est atteint ; la partie est terminée.")
            if s.config.points_format is PointsFormat.FIXED_ROUNDS:
                target = s.config.fixed_rounds + (1 if s.c1_tiebreak_round else 0)
                if s.rounds_completed >= target and not s.c1_tiebreak_round:
                    # A tie after regular rounds requires the tiebreak that is already marked.
                    if len(self._leaders()) == 1: raise PhaseError("Le format C1 est terminé.")
        cards = list(s.config.cards); self._rng.shuffle(cards)
        tokens = [Token(f"r{s.round_number+1}-t{i:04d}", c) for i,c in enumerate(
            color for color,n in s.config.colors.items() for _ in range(n))]
        self._rng.shuffle(tokens)
        from .setup import _deal_valid_hands
        from .state import PlayerState
        candidates = [PlayerState(p.id, card=card) for p,card in zip(s.players,cards)]
        allocation, common_bag = _deal_valid_hands(candidates, tokens, s.config, self._rng)
        for p, card in zip(s.players, cards):
            p.alive=True; p.revealed=False; p.hand.clear(); p.card=card; p.credited_eliminations=0
        for p, hand in zip(s.players, allocation): p.hand.extend(hand)
        s.common_bag=common_bag
        s.round_number += 1; s.proposal=None; s.resolution_eliminated.clear(); s.round_winner=None
        s.result=None; s.phase=Phase.CHOOSE_RECIPIENT
        s.active_player_id=starter
        s.emit("round_started", first_player_id=starter, round_number=s.round_number)
        for player in s.players:
            s.emit("initial_tokens_drawn",
                   public_data={"player_id": player.id, "count": len(player.hand)},
                   player_id=player.id, tokens=tuple((t.id, t.color) for t in player.hand))
        s.assert_invariants()


class PlayerController:
    """Actor-scoped facade; distribute one controller to each future agent."""
    __slots__ = ("__engine", "__player_id")

    def __init__(self, engine: GameEngine, player_id: str):
        self.__engine = engine
        self.__player_id = player_id

    @property
    def player_id(self) -> str:
        return self.__player_id

    def view(self) -> PrivateView:
        return self.__engine.private_view(self.__player_id)

    def public_view(self) -> PublicView:
        return self.__engine.public_view()

    def legal_actions(self) -> tuple[Action, ...]:
        return self.__engine.legal_actions(self.__player_id)

    def submit(self, action: Action) -> ActionResult:
        return self.__engine.submit(action, self.__player_id)
