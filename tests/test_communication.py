import pytest

from agents.communication import CommunicationChannel, CommunicationIntent, CommunicationKind
from agents.strategies import ColorClaimCommunication
from engine import AcceptGift, ChooseRecipient, ProposeGift, RefuseGift, IllegalAction
from engine.state import Phase
from rules import GameMode
from tests.helpers import build_game


def propose(game, donor="a", recipient="b", token_id="a-t0"):
    game.submit(ChooseRecipient(recipient), player_id=donor)
    game.submit(ProposeGift(token_id), player_id=donor)


def test_t10_gift_can_be_proposed_and_resolved_without_any_messages():
    game, state = build_game(mode=GameMode.LAST_SURVIVOR, order=["a", "b"],
                             hands={"a": ["rouge"], "b": ["bleu"]}, bag=[])
    propose(game)
    channel = CommunicationChannel(game)
    proposal_id = channel.current_proposal_id
    assert channel.messages_for("a", proposal_id) == ()
    game.submit(AcceptGift(), player_id="b")
    assert not game.finished and game.phase is Phase.CHOOSE_RECIPIENT
    assert game.active_player_id == "b" and channel.messages_for("a", proposal_id) == ()
    state.assert_invariants()


def test_t10_spontaneous_written_claim_is_private_scoped_and_does_not_mutate_rules():
    game, state = build_game(mode=GameMode.LAST_SURVIVOR, order=["a", "b", "c"],
                             hands={"a": ["rouge"], "b": ["bleu"], "c": ["vert"]}, bag=["jaune"])
    propose(game)
    channel = CommunicationChannel(game)
    proposal_id = channel.current_proposal_id
    before = (game.public_view(), game.legal_actions(), game.public_event_history(), len(state.events))
    message = channel.send("a", CommunicationIntent(CommunicationKind.SPONTANEOUS,
                                                       "Le cadeau est bleu."))
    assert message.proposal_id == proposal_id and message.author_id == "a"
    assert channel.messages_for("b") == (message,)
    assert channel.messages_for("c") == ()
    assert (game.public_view(), game.legal_actions(), game.public_event_history(), len(state.events)) == before
    assert game.controller("a").view().offered_token.color == "rouge"
    assert game.controller("b").view().offered_token is None
    game.submit(AcceptGift(), player_id="b")
    revealed = next(e for e in game.public_event_history() if e.kind == "token_revealed")
    assert revealed.data["color"] == "rouge"
    state.assert_invariants()


def test_t10_recipient_can_question_and_donor_can_answer_truthfully_or_lie():
    for response in ("Le jeton est rouge.", "Le jeton est bleu."):
        game, _ = build_game(mode=GameMode.LAST_SURVIVOR, order=["a", "b"],
                             hands={"a": ["rouge"], "b": ["bleu"]}, bag=["jaune"])
        propose(game)
        channel = CommunicationChannel(game)
        question = channel.send("b", CommunicationIntent(CommunicationKind.QUESTION,
                                                           "Quelle est sa couleur ?"))
        answer = channel.send("a", CommunicationIntent(CommunicationKind.RESPONSE, response,
                                                         reply_to=question.sequence))
        assert question.sequence < answer.sequence
        assert question.proposal_id == answer.proposal_id == channel.current_proposal_id
        assert answer.reply_to == question.sequence
        assert tuple(m.kind for m in channel.messages_for("b")) == (
            CommunicationKind.QUESTION, CommunicationKind.RESPONSE)
        assert game.controller("b").view().offered_token is None
        assert game.public_event_history()[-1].kind == "gift_proposed"


def test_t10_messages_are_not_commands_and_cannot_override_empty_bag_refusal_rule():
    game, state = build_game(mode=GameMode.LAST_SURVIVOR, order=["a", "b"],
                             hands={"a": ["rouge"], "b": ["bleu"]}, bag=[])
    propose(game)
    channel = CommunicationChannel(game)
    channel.send("a", CommunicationIntent(CommunicationKind.SPONTANEOUS, "Tu peux refuser."))
    assert game.legal_actions() == (AcceptGift(),)
    before = (game.public_view(), game.public_event_history(), len(state.events))
    with pytest.raises(IllegalAction, match="refus est impossible"):
        game.submit(RefuseGift(), player_id="b")
    assert (game.public_view(), game.public_event_history(), len(state.events)) == before
    state.assert_invariants()


def test_t10_messages_are_bound_to_the_correct_proposal_and_nonparticipants_cannot_send():
    game, _ = build_game(mode=GameMode.LAST_SURVIVOR, order=["a", "b", "c"],
                         hands={"a": ["rouge"], "b": ["bleu"], "c": ["vert"]}, bag=["jaune"])
    channel = CommunicationChannel(game)
    propose(game)
    first = channel.send("a", CommunicationIntent(CommunicationKind.SPONTANEOUS, "Premier cadeau."))
    game.submit(AcceptGift(), player_id="b")
    game.submit(ChooseRecipient("c"), player_id="b")
    game.submit(ProposeGift("b-t0"), player_id="b")
    second_id = channel.current_proposal_id
    second = channel.send("b", CommunicationIntent(CommunicationKind.SPONTANEOUS, "Autre cadeau."))
    assert first.proposal_id != second.proposal_id
    assert channel.messages_for("c") == (second,)
    assert channel.messages_for("c", first.proposal_id) == ()
    assert channel.messages_for("a", second_id) == ()
    with pytest.raises(ValueError, match="participants"):
        channel.send("a", CommunicationIntent(CommunicationKind.SPONTANEOUS, "Non autorisé."))


def test_t10_configured_truthful_and_deceptive_agent_claims_use_only_donor_private_view():
    game, _ = build_game(mode=GameMode.LAST_SURVIVOR, order=["a", "b"],
                         hands={"a": ["rouge"], "b": ["bleu"]}, bag=["jaune"])
    propose(game)
    view = game.controller("a").view()
    true_strategy = ColorClaimCommunication(("rouge", "bleu", "jaune"), truthful=True)
    false_strategy = ColorClaimCommunication(("rouge", "bleu", "jaune"), truthful=False)
    true_message = true_strategy.after_proposal(view, ())
    false_message = false_strategy.after_proposal(view, ())
    actual = view.offered_token.color
    assert true_message.text == f"Le jeton est {actual}."
    assert false_message.text != true_message.text
    assert false_strategy.truthfulness_mode == "deceptive"
