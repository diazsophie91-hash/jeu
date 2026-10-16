import copy

import pytest

from engine import AcceptGift, ChooseRecipient, ProposeGift, RefuseGift, GameFinished, IllegalAction
from engine.state import Phase
from rules import Condition, ConditionKind, GameMode, Succession
from tests.helpers import ScriptedRNG, build_game


def state_snapshot(state):
    return (
        state.phase, state.active_player_id, state.result, state.winners,
        tuple((p.id, p.alive, p.score, p.credited_eliminations, tuple((t.id, t.color) for t in p.hand)) for p in state.players),
        tuple((t.id, t.color) for t in state.common_bag),
        None if state.proposal is None else (state.proposal.donor_id, state.proposal.recipient_id,
                                             None if state.proposal.token is None else state.proposal.token.id),
        len(state.events),
    )


def start_offer(game, token_index=0, recipient="b"):
    donor = game._state.player(game.active_player_id)
    game.submit(ChooseRecipient(recipient))
    game.submit(ProposeGift(donor.hand[token_index].id))


def test_t07_acceptance_transfers_the_single_temporary_token_and_reveals_it(game_factory):
    game, state = game_factory(mode=GameMode.LAST_SURVIVOR, order=["a", "b"],
                             hands={"a": ["rouge"], "b": ["bleu"]}, bag=["vert"])
    start_offer(game)
    offered = state.proposal.token
    result = game.submit(AcceptGift())
    assert offered in state.player("b").hand and offered not in state.player("a").hand
    assert state.proposal is None and state.active_player_id == "b"
    assert any(e.kind == "token_revealed" and e.data.get("token_id") == offered.id for e in result.events)
    state.assert_invariants()


@pytest.mark.parametrize("reveal", [False, True])
def test_t08_refusal_returns_offer_and_draws_replacement_with_configured_visibility(reveal):
    game, state = build_game(mode=GameMode.LAST_SURVIVOR, order=["a", "b"],
                             hands={"a": ["rouge"], "b": ["vert"]}, bag=["bleu"],
                             reveal_refusal_draw=reveal, rng=ScriptedRNG(choice_index=0))
    start_offer(game)
    offered = state.proposal.token
    result = game.submit(RefuseGift())
    draw = next(e for e in result.events if e.kind == "token_drawn")
    internal_draw = next(e for e in state.events if e.kind == "token_drawn")
    assert offered in state.player("a").hand and offered not in state.player("b").hand
    assert internal_draw.data["token_id"] != offered.id
    assert ("color" in draw.data) is reveal
    assert not any(e.kind == "token_revealed" and e.data.get("token_id") == offered.id for e in result.events)
    state.assert_invariants()


def test_t09_empty_bag_refusal_is_rejected_without_mutation_then_acceptance_is_forced():
    game, state = build_game(mode=GameMode.LAST_SURVIVOR, order=["a", "b"],
                             hands={"a": ["rouge"], "b": ["bleu"]}, bag=[])
    start_offer(game)
    before = state_snapshot(state)
    assert game.legal_actions() == (AcceptGift(),)
    with pytest.raises(IllegalAction, match="refus est impossible"):
        game.submit(RefuseGift())
    assert state_snapshot(state) == before
    offered = state.proposal.token
    result = game.submit(AcceptGift())
    assert offered in state.player("b").hand
    assert any(e.kind == "gift_accepted" for e in result.events)
    assert not any(e.kind == "token_drawn" for e in result.events)
    state.assert_invariants()


def test_t10_announcements_are_not_engine_actions_and_true_token_identity_is_authoritative():
    game, state = build_game(mode=GameMode.LAST_SURVIVOR, order=["a", "b"],
                             hands={"a": ["rouge"], "b": ["bleu"]}, bag=["vert"])
    start_offer(game)
    offered = state.proposal.token
    assert offered.color == "rouge"
    game.submit(AcceptGift())
    assert next(e for e in game.public_event_history() if e.kind == "token_revealed").data["color"] == "rouge"


def test_t11_invalid_recipient_and_wrong_phase_preserve_state():
    game, state = build_game(mode=GameMode.LAST_SURVIVOR, order=["a", "b", "c"],
                             hands={"a": ["rouge"], "b": ["bleu"], "c": ["vert"]}, bag=["jaune"])
    for recipient in ("a", "missing"):
        before = state_snapshot(state)
        with pytest.raises(IllegalAction):
            game.submit(ChooseRecipient(recipient))
        assert state_snapshot(state) == before
    game._state.player("b").alive = False
    before = state_snapshot(state)
    with pytest.raises(IllegalAction):
        game.submit(ChooseRecipient("b"))
    assert state_snapshot(state) == before
    state.player("b").alive = True
    game.submit(ChooseRecipient("b"))
    before = state_snapshot(state)
    with pytest.raises(IllegalAction):
        game.submit(AcceptGift())
    assert state_snapshot(state) == before
    state.assert_invariants()


@pytest.mark.parametrize("mode", [GameMode.LAST_SURVIVOR, GameMode.SECRET_OBJECTIVE, GameMode.POINTS])
def test_t16_donor_removal_defeat_is_checked_before_decision_when_enabled(mode):
    defeat_a = Condition(ConditionKind.COLOR_COUNT, colors=("rouge",), threshold=1)
    defeat_b = Condition(ConditionKind.TOTAL_COUNT, threshold=99)
    victory_a = Condition(ConditionKind.COLOR_COUNT, colors=("vert",), threshold=1)
    game, state = build_game(mode=mode, order=["a", "b", "c"],
                             hands={"a": ["rouge", "rouge"], "b": ["bleu"], "c": ["vert"]},
                             bag=["jaune"], defeats={"a": defeat_a, "b": defeat_b, "c": defeat_b},
                             victories={"a": victory_a, "b": victory_a, "c": victory_a} if mode is GameMode.SECRET_OBJECTIVE else {},
                             donor_defeat_after_removal=True)
    start_offer(game)
    assert not state.player("a").alive and state.player("a").revealed
    assert state.proposal is not None and state.proposal.token is not None
    assert len(state.player("a").hand) == 0
    assert any(e.kind == "card_revealed" and e.data["player_id"] == "a" for e in state.events)
    assert len([e for e in state.events if e.kind == "condition_checked" and e.data.get("trigger") == "donor_removal"]) == 1
    assert state.active_player_id == "b"
    state.assert_invariants()


@pytest.mark.parametrize("mode", [GameMode.LAST_SURVIVOR, GameMode.SECRET_OBJECTIVE, GameMode.POINTS])
def test_t16_disabled_donor_removal_check_does_not_eliminate_donor(mode):
    defeat = Condition(ConditionKind.COLOR_COUNT, colors=("rouge",), threshold=1)
    victory = Condition(ConditionKind.COLOR_COUNT, colors=("vert",), threshold=1)
    game, state = build_game(mode=mode, order=["a", "b", "c"],
                             hands={"a": ["rouge", "rouge"], "b": ["bleu"], "c": ["vert"]},
                             bag=["jaune"], defeats={"a": defeat},
                             victories={"a": victory} if mode is GameMode.SECRET_OBJECTIVE else {},
                             donor_defeat_after_removal=False)
    start_offer(game)
    assert state.player("a").alive and not state.player("a").revealed
    assert not any(e.kind == "condition_checked" and e.data.get("trigger") == "donor_removal" for e in state.events)
    assert state.phase is Phase.DECISION and state.proposal is not None
    state.assert_invariants()


def test_t66_t68_donor_elimination_is_not_undone_by_refusal_or_repeated():
    defeat = Condition(ConditionKind.COLOR_COUNT, colors=("rouge",), threshold=1)
    game, state = build_game(mode=GameMode.POINTS, order=["a", "b", "c"],
                             hands={"a": ["rouge", "rouge"], "b": ["bleu"], "c": ["vert"]},
                             bag=["jaune"], defeats={"a": defeat}, donor_defeat_after_removal=True,
                             reveal_refusal_draw=False)
    start_offer(game)
    offered = state.proposal.token
    game.submit(RefuseGift())
    assert not state.player("a").alive
    assert offered in state.player("b").hand or offered in state.common_bag
    assert len([e for e in state.events if e.kind == "condition_checked" and e.data.get("trigger") == "donor_removal"]) == 1
    assert state.player("a").score == 0
    state.assert_invariants()


def test_t67_accept_after_donor_elimination_transfers_temporary_token():
    defeat = Condition(ConditionKind.COLOR_COUNT, colors=("rouge",), threshold=1)
    game, state = build_game(mode=GameMode.LAST_SURVIVOR, order=["a", "b", "c"],
                             hands={"a": ["rouge", "rouge"], "b": ["bleu"], "c": ["vert"]},
                             bag=["jaune"], defeats={"a": defeat}, donor_defeat_after_removal=True)
    start_offer(game)
    offered = state.proposal.token
    result = game.submit(AcceptGift())
    assert offered in state.player("b").hand and state.proposal is None
    assert any(e.kind == "token_transferred" and e.data.get("token_id") == offered.id for e in result.events)
    assert state.active_player_id == "b"
    state.assert_invariants()


def test_t69_elimination_returns_only_personal_tokens_and_keeps_offer_temporary():
    defeat = Condition(ConditionKind.COLOR_COUNT, colors=("rouge",), threshold=1)
    game, state = build_game(mode=GameMode.LAST_SURVIVOR, order=["a", "b", "c"],
                             hands={"a": ["rouge", "rouge", "bleu"], "b": ["vert"], "c": ["jaune"]},
                             bag=["noir"], defeats={"a": defeat}, donor_defeat_after_removal=True)
    game.submit(ChooseRecipient("b"))
    offered = state.player("a").hand[0]
    game.submit(ProposeGift(offered.id))
    assert not state.player("a").alive
    assert offered is state.proposal.token
    assert all(t not in state.common_bag for t in state.player("a").hand)
    assert {t.color for t in state.common_bag} >= {"rouge", "bleu"}
    state.assert_invariants()


def test_t77_secret_victory_after_donor_self_elimination_stops_resolution():
    donor_defeat = Condition(ConditionKind.COLOR_COUNT, colors=("rouge",), threshold=1)
    recipient_defeat = Condition(ConditionKind.TOTAL_COUNT, threshold=99)
    donor_victory = Condition(ConditionKind.COLOR_COUNT, colors=("vert",), threshold=1)
    recipient_victory = Condition(ConditionKind.COLOR_COUNT, colors=("rouge",), threshold=1)
    game, state = build_game(mode=GameMode.SECRET_OBJECTIVE, order=["a", "b", "c"],
                             hands={"a": ["rouge", "rouge"], "b": ["bleu"], "c": ["vert"]},
                             bag=["jaune"], defeats={"a": donor_defeat, "b": recipient_defeat, "c": recipient_defeat},
                             victories={"a": donor_victory, "b": recipient_victory, "c": donor_victory},
                             donor_defeat_after_removal=True)
    start_offer(game)
    offered = state.proposal.token
    result = game.submit(AcceptGift())
    assert not state.player("a").alive and offered in state.player("b").hand
    assert game.finished and state.result == "secret_objective" and state.winners == ("b",)
    assert state.player("b").revealed
    assert not any(e.kind in {"point_awarded", "successor_selected"} for e in result.events)
    state.assert_invariants()


def test_t77_disabling_donor_removal_check_does_not_block_recipient_victory():
    recipient_victory = Condition(ConditionKind.COLOR_COUNT, colors=("rouge",), threshold=1)
    game, state = build_game(mode=GameMode.SECRET_OBJECTIVE, order=["a", "b", "c"],
                             hands={"a": ["rouge", "rouge"], "b": ["bleu"], "c": ["vert"]},
                             bag=["jaune"],
                             defeats={"a": Condition(ConditionKind.COLOR_COUNT, colors=("rouge",), threshold=1)},
                             victories={"a": Condition(ConditionKind.TOTAL_COUNT, threshold=99),
                                        "b": recipient_victory,
                                        "c": Condition(ConditionKind.TOTAL_COUNT, threshold=99)},
                             donor_defeat_after_removal=False)
    start_offer(game)
    assert state.player("a").alive
    game.submit(AcceptGift())
    assert state.result == "secret_objective" and state.winners == ("b",)
    assert state.player("a").alive
    assert not any(e.kind == "condition_checked" and e.data.get("trigger") == "donor_removal" for e in state.events)
    state.assert_invariants()


def test_t18_secret_victory_after_refusal_draw_stops_all_later_resolution():
    victory = Condition(ConditionKind.COLOR_COUNT, colors=("jaune",), threshold=1)
    game, state = build_game(mode=GameMode.SECRET_OBJECTIVE, order=["a", "b", "c"],
                             hands={"a": ["rouge"], "b": ["bleu"], "c": ["vert"]}, bag=["jaune"],
                             victories={"a": victory, "b": victory, "c": victory},
                             rng=ScriptedRNG(choice_index=0))
    start_offer(game)
    result = game.submit(RefuseGift())
    assert game.finished and state.winners == ("b",) and state.result == "secret_objective"
    assert state.player("b").revealed
    assert not any(e.kind in {"player_eliminated", "point_awarded", "successor_selected"} for e in result.events)
    state.assert_invariants()


def test_t17_secret_victory_after_accepted_gift_stops_resolution_immediately():
    victory = Condition(ConditionKind.COLOR_COUNT, colors=("rouge",), threshold=1)
    game, state = build_game(mode=GameMode.SECRET_OBJECTIVE, order=["a", "b", "c"],
                             hands={"a": ["rouge"], "b": ["bleu"], "c": ["vert"]}, bag=["jaune"],
                             victories={"a": Condition(ConditionKind.TOTAL_COUNT, threshold=99),
                                        "b": victory,
                                        "c": Condition(ConditionKind.TOTAL_COUNT, threshold=99)})
    start_offer(game)
    result = game.submit(AcceptGift())
    assert state.result == "secret_objective" and state.winners == ("b",)
    assert state.player("b").revealed and state.player("b").alive
    assert not any(e.kind in {"player_eliminated", "point_awarded", "successor_selected"} for e in result.events)
    with pytest.raises(GameFinished):
        game.submit(ChooseRecipient("a"))
    state.assert_invariants()


def test_t81_refusal_after_donor_elimination_can_draw_offer_or_existing_bag_token():
    for choice_index, expect_offer, reveal in ((2, True, False), (0, False, True)):
        donor_loss = Condition(ConditionKind.COLOR_COUNT, colors=("rouge",), threshold=1)
        recipient_loss = Condition(ConditionKind.COLOR_COUNT, colors=("rouge",), threshold=1)
        game, state = build_game(mode=GameMode.POINTS, order=["a", "b", "c"],
                                 hands={"a": ["rouge", "rouge"], "b": ["bleu"], "c": ["vert"]},
                                 bag=["bleu"], defeats={"a": donor_loss, "b": recipient_loss},
                                 donor_defeat_after_removal=True, reveal_refusal_draw=reveal,
                                 succession=Succession.CLOCKWISE, elimination_threshold=9,
                                 rng=ScriptedRNG(choice_index=choice_index))
        start_offer(game)
        offered = state.proposal.token
        assert not state.player("a").alive and state.proposal.token is offered
        expected_ids = {t.id for t in state.common_bag}
        expected_ids.update(t.id for p in state.players for t in p.hand)
        expected_ids.add(offered.id)
        result = game.submit(RefuseGift())
        returned = next(i for i, e in enumerate(state.events) if e.kind == "token_returned" and e.data.get("token_id") == offered.id)
        draw_index = next(i for i, e in enumerate(state.events) if e.kind == "token_drawn" and e.data.get("reason") == "refusal")
        internal_draw = state.events[draw_index]
        assert returned < draw_index, "The offered token must enter the common bag before the draw."
        assert (internal_draw.data["token_id"] == offered.id) is expect_offer
        if expect_offer:
            assert not state.player("b").alive
            assert offered in state.common_bag
            assert state.player("a").credited_eliminations == 1
        else:
            assert state.player("b").alive and internal_draw.data["token_id"] in {t.id for t in state.player("b").hand}
            assert state.player("a").credited_eliminations == 0
        final_ids = {t.id for t in state.common_bag}
        final_ids.update(t.id for p in state.players for t in p.hand)
        assert final_ids == expected_ids
        public_draw = next(e for e in result.events if e.kind == "token_drawn")
        assert ("color" in public_draw.data) is reveal
        if not reveal:
            assert "token_id" not in public_draw.data
        assert offered not in state.player("a").hand
        state.assert_invariants()

