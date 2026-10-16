import pytest

from engine import AcceptGift, ChooseRecipient, ProposeGift, RefuseGift
from engine.state import Phase
from rules import Condition, ConditionKind, GameMode, PointsFormat, Succession
from tests.helpers import ScriptedRNG, build_game


def begin(game, token_id, recipient="b"):
    game.submit(ChooseRecipient(recipient))
    game.submit(ProposeGift(token_id))


def test_t35_points_and_counter_for_recipient_eliminated_after_acceptance():
    defeat = Condition(ConditionKind.COLOR_COUNT, colors=("rouge",), threshold=1)
    game, state = build_game(mode=GameMode.POINTS, order=["a", "b", "c"],
                             hands={"a": ["rouge"], "b": ["bleu"], "c": ["vert"]},
                             bag=["jaune"], defeats={"b": defeat},
                             succession=Succession.CLOCKWISE, elimination_threshold=9)
    begin(game, "a-t0")
    game.submit(AcceptGift())
    assert not state.player("b").alive
    assert state.player("a").score == state.player("a").credited_eliminations == 1
    assert state.active_player_id == "c"
    state.assert_invariants()


def test_t36_points_and_counter_for_recipient_eliminated_after_refusal_draw():
    defeat = Condition(ConditionKind.COLOR_COUNT, colors=("rouge",), threshold=1)
    game, state = build_game(mode=GameMode.POINTS, order=["a", "b", "c"],
                             hands={"a": ["vert"], "b": ["bleu"], "c": ["jaune"]},
                             bag=["rouge"], defeats={"b": defeat},
                             succession=Succession.CLOCKWISE,
                             rng=ScriptedRNG(choice_index=0), elimination_threshold=9)
    begin(game, "a-t0")
    game.submit(RefuseGift())
    assert not state.player("b").alive
    assert state.player("a").score == state.player("a").credited_eliminations == 1
    assert state.active_player_id == "c"
    state.assert_invariants()


def test_t37_donor_auto_elimination_does_not_award_a_point():
    defeat = Condition(ConditionKind.COLOR_COUNT, colors=("rouge",), threshold=1)
    game, state = build_game(mode=GameMode.POINTS, order=["a", "b", "c"],
                             hands={"a": ["rouge", "rouge"], "b": ["bleu"], "c": ["vert"]},
                             bag=["jaune"], defeats={"a": defeat}, donor_defeat_after_removal=True,
                             succession=Succession.CLOCKWISE)
    begin(game, "a-t0")
    assert not state.player("a").alive
    assert state.player("a").score == state.player("a").credited_eliminations == 0
    game.submit(AcceptGift())
    assert state.active_player_id == "b"
    assert state.player("a").score == 0
    state.assert_invariants()


def test_t38_eliminated_donor_still_receives_opponent_point_unless_action_is_terminal():
    donor_defeat = Condition(ConditionKind.COLOR_COUNT, colors=("rouge",), threshold=1)
    recipient_defeat = Condition(ConditionKind.COLOR_COUNT, colors=("rouge",), threshold=1)
    game, state = build_game(mode=GameMode.POINTS, order=["a", "b", "c"],
                             hands={"a": ["rouge", "rouge"], "b": ["bleu"], "c": ["vert"]},
                             bag=["jaune"], defeats={"a": donor_defeat, "b": recipient_defeat},
                             donor_defeat_after_removal=True, succession=Succession.CLOCKWISE)
    begin(game, "a-t0")
    game.submit(AcceptGift())
    assert not state.player("a").alive and not state.player("b").alive and state.player("c").alive
    assert state.player("a").score == state.player("a").credited_eliminations == 1
    state.assert_invariants()


def test_t40_threshold_bonus_goes_to_responsible_even_if_eliminated():
    donor_defeat = Condition(ConditionKind.COLOR_COUNT, colors=("rouge",), threshold=1)
    recipient_defeat = Condition(ConditionKind.COLOR_COUNT, colors=("rouge",), threshold=1)
    game, state = build_game(mode=GameMode.POINTS, order=["a", "b", "c"],
                             hands={"a": ["rouge", "rouge"], "b": ["bleu"], "c": ["vert"]},
                             bag=["jaune"], defeats={"a": donor_defeat, "b": recipient_defeat},
                             donor_defeat_after_removal=True, succession=Succession.CLOCKWISE,
                             elimination_threshold=1)
    begin(game, "a-t0")
    game.submit(AcceptGift())
    assert state.phase is Phase.ROUND_OVER and state.round_winner == "a"
    assert not state.player("a").alive
    assert state.player("a").credited_eliminations == 1 and state.player("a").score == 2
    assert state.player("a").score - state.player("a").credited_eliminations == 1
    state.assert_invariants()


def test_t41_last_survivor_round_bonus_is_awarded():
    loss = Condition(ConditionKind.COLOR_COUNT, colors=("rouge",), threshold=1)
    game, state = build_game(mode=GameMode.POINTS, order=["a", "b"],
                             hands={"a": ["rouge"], "b": ["bleu"]}, bag=[], defeats={"b": loss},
                             succession=Succession.CLOCKWISE, elimination_threshold=10)
    begin(game, "a-t0")
    game.submit(AcceptGift())
    assert state.phase is Phase.ROUND_OVER and state.round_winner == "a"
    assert state.player("a").score == 2  # One elimination point and one round bonus.
    state.assert_invariants()


def test_t64_t73_variant_b_stops_at_threshold_before_another_successor():
    loss = Condition(ConditionKind.COLOR_COUNT, colors=("rouge",), threshold=2)
    game, state = build_game(mode=GameMode.POINTS, order=["a", "b", "c", "d", "e"],
                             hands={"a": ["rouge"], "b": ["rouge"], "c": [], "d": [], "e": ["vert"]},
                             bag=["jaune"], defeats={"b": loss}, succession=Succession.CLOCKWISE,
                             elimination_threshold=2)
    begin(game, "a-t0")
    game.submit(AcceptGift())
    assert state.phase is Phase.ROUND_OVER and state.round_winner == "a"
    assert state.player("a").credited_eliminations == 2
    assert state.player("c").alive is False
    assert state.player("d").alive is True, "Threshold must stop before the next forced elimination."
    assert state.player("e").alive and state.active_player_id is None
    state.assert_invariants()


def test_t39_t73_clockwise_chain_continues_and_credits_each_nonterminal_elimination():
    loss = Condition(ConditionKind.COLOR_COUNT, colors=("rouge",), threshold=1)
    game, state = build_game(mode=GameMode.POINTS, order=["a", "b", "c", "d", "e"],
                             hands={"a": ["rouge"], "b": ["bleu"], "c": [], "d": [], "e": ["vert"]},
                             bag=["jaune"], defeats={"b": loss}, succession=Succession.CLOCKWISE,
                             elimination_threshold=9)
    begin(game, "a-t0")
    game.submit(AcceptGift())
    assert state.player("b").alive is False
    assert state.player("c").alive is False and state.player("d").alive is False
    assert state.player("a").credited_eliminations == 3
    assert state.active_player_id == "e"
    state.assert_invariants()


@pytest.mark.parametrize("initial,expected_phase", [(4, Phase.GAME_OVER), (0, Phase.ROUND_OVER)])
def test_t45_t48_c2_threshold_is_resolved_only_after_round_bonus(initial, expected_phase):
    game, state = build_game(mode=GameMode.POINTS, order=["a", "b"],
                             hands={"a": ["rouge"], "b": ["bleu"]}, bag=["vert"],
                             points_format=PointsFormat.POINTS_THRESHOLD, points_threshold=5,
                             scores={"a": initial}, elimination_threshold=10)
    game._finish_round("a")
    assert game.phase is expected_phase
    assert state.player("a").score == initial + 1
    if initial == 4:
        assert state.result == "points_threshold" and state.winners == ("a",)
    state.assert_invariants()


def test_t45_threshold_reached_during_round_does_not_end_it_immediately():
    game, state = build_game(mode=GameMode.POINTS, order=["a", "b"],
                             hands={"a": ["rouge"], "b": ["bleu"]}, bag=["vert"],
                             points_format=PointsFormat.POINTS_THRESHOLD, points_threshold=2,
                             scores={"a": 1}, elimination_threshold=10)
    game._credit_elimination("a", "test")
    assert game.phase is Phase.CHOOSE_RECIPIENT
    assert state.player("a").score == 2
    game._finish_round("b")
    assert game.phase is Phase.GAME_OVER and state.result == "points_threshold"
    state.assert_invariants()


def test_t46_c2_below_threshold_starts_another_round_and_preserves_score():
    game, state = build_game(mode=GameMode.POINTS, order=["a", "b"],
                             hands={"a": ["rouge"], "b": ["bleu"]}, bag=["vert"],
                             points_format=PointsFormat.POINTS_THRESHOLD, points_threshold=20,
                             scores={"a": 3}, credited={"a": 2}, elimination_threshold=10)
    game._finish_round("b")
    assert game.phase is Phase.ROUND_OVER
    game._start_new_round("b")
    assert game.phase is Phase.CHOOSE_RECIPIENT and state.round_number == 2
    assert state.player("a").score == 3 and state.player("b").score == 1
    assert all(p.credited_eliminations == 0 and p.alive and len(p.hand) == 1 for p in state.players)
    state.assert_invariants()


def test_t47_c2_ranks_final_scores_not_first_threshold_player():
    game, state = build_game(mode=GameMode.POINTS, order=["a", "b", "c"],
                             hands={"a": ["rouge"], "b": ["bleu"], "c": ["vert"]}, bag=["jaune"],
                             points_format=PointsFormat.POINTS_THRESHOLD, points_threshold=5,
                             scores={"a": 4, "b": 4}, elimination_threshold=10)
    game._credit_elimination("a", "test threshold")
    game._credit_elimination("b", "test overtake")
    game._credit_elimination("b", "test overtake")
    assert game.phase is Phase.CHOOSE_RECIPIENT
    game._finish_round("c")
    assert state.result == "points_threshold" and state.winners == ("b",)
    state.assert_invariants()


def test_t75_terminal_initial_action_does_not_increment_points_or_counters():
    loss_a = Condition(ConditionKind.COLOR_COUNT, colors=("rouge",), threshold=1)
    loss_b = Condition(ConditionKind.COLOR_COUNT, colors=("rouge",), threshold=2)
    game, state = build_game(mode=GameMode.POINTS, order=["a", "b"],
                             hands={"a": ["rouge", "rouge"], "b": ["rouge"]}, bag=[],
                             defeats={"a": loss_a, "b": loss_b}, donor_defeat_after_removal=True,
                             elimination_threshold=1)
    begin(game, "a-t0")
    game.submit(AcceptGift())
    assert state.result == "terminal_tie"
    assert all(p.score == p.credited_eliminations == 0 for p in state.players)
    state.assert_invariants()


def test_t74_c2_normal_end_shares_tie_for_highest_total_score():
    game, state = build_game(mode=GameMode.POINTS, order=["a", "b", "c"],
                             hands={"a": ["rouge"], "b": ["bleu"], "c": ["vert"]}, bag=["jaune"],
                             points_format=PointsFormat.POINTS_THRESHOLD, points_threshold=5,
                             scores={"a": 5, "b": 5, "c": 0}, elimination_threshold=9)
    game._finish_round("c")
    assert state.phase is Phase.GAME_OVER and state.result == "points_threshold"
    assert state.winners == ("a", "b")
    assert state.player("c").score == 1
    state.assert_invariants()
