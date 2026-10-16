import pytest

from engine import AcceptGift, ChooseRecipient, ProposeGift, create_game
from engine.state import Phase
from rules import Card, Condition, ConditionKind, GameConfig, GameMode, PointsFormat, Succession
from tests.helpers import ScriptedRNG, build_game, safe_card


def take_turn(game, donor_id, recipient_id, token_id):
    game.submit(ChooseRecipient(recipient_id), player_id=donor_id)
    game.submit(ProposeGift(token_id), player_id=donor_id)
    game.submit(AcceptGift(), player_id=recipient_id)


def test_t42_new_round_resets_elimination_counters_but_keeps_scores_and_redeals():
    defeat = Condition(ConditionKind.TOTAL_COUNT, threshold=99)
    config = GameConfig({"rouge": 8, "bleu": 8}, GameMode.POINTS,
                        tuple(Card(f"c{i}", defeat) for i in range(2)),
                        elimination_threshold=3, fixed_rounds=3)
    game = create_game(["a", "b"], config, seed=21, first_player_id="a")
    state = game._state
    old_ids = {t.id for t in state.common_bag} | {t.id for p in state.players for t in p.hand}
    state.player("a").score = 7
    state.player("a").credited_eliminations = 2
    state.player("b").credited_eliminations = 1
    game._finish_round("b")
    game._start_new_round("b")
    new_ids = {t.id for t in state.common_bag} | {t.id for p in state.players for t in p.hand}
    assert state.round_number == 2 and state.phase is Phase.CHOOSE_RECIPIENT
    assert state.player("a").score == 7 and state.player("b").score == 1
    assert all(p.credited_eliminations == 0 and p.alive and not p.revealed for p in state.players)
    assert all(len(p.hand) == 3 for p in state.players)
    assert old_ids.isdisjoint(new_ids)
    state.assert_invariants()


def test_t43_c1_ends_after_three_rounds_using_cumulative_scores():
    cards = tuple(Card(f"c{i}", Condition(ConditionKind.TOTAL_COUNT, threshold=4)) for i in range(2))
    config = GameConfig({"rouge": 6, "bleu": 6}, GameMode.POINTS, cards,
                        points_format=PointsFormat.FIXED_ROUNDS,
                        elimination_threshold=9, fixed_rounds=3, initial_hand_size=3)
    from engine import create_game
    game = create_game(["a", "b"], config, seed=17, first_player_id="a")
    state = game._state
    for round_index in range(3):
        donor = game.active_player_id
        recipient = "b" if donor == "a" else "a"
        token_id = state.player(donor).hand[0].id
        take_turn(game, donor, recipient, token_id)
        assert state.phase is (Phase.GAME_OVER if round_index == 2 else Phase.ROUND_OVER)
        if round_index < 2:
            game._start_new_round(recipient)
    assert state.phase is Phase.GAME_OVER
    assert state.rounds_completed == 3 and state.result == "fixed_rounds"
    assert state.player("a").score == 4 and state.player("b").score == 2
    assert state.winners == ("a",)
    state.assert_invariants()


@pytest.mark.parametrize("surpass", [False, True])
def test_t44_c1_tiebreak_round_shares_persistent_tie_or_accepts_new_leader(surpass):
    game, state = build_game(mode=GameMode.POINTS, order=["a", "b", "c"],
                             hands={"a": ["rouge"], "b": ["bleu"], "c": ["vert"]}, bag=["jaune"],
                             points_format=PointsFormat.FIXED_ROUNDS, fixed_rounds=3,
                             scores={"a": 4, "b": 5, "c": 0})
    state.rounds_completed = 2
    game._finish_round("a")  # Bonus brings A to a tie with B at 5.
    assert state.c1_tiebreak_round and state.phase is Phase.ROUND_OVER
    game._start_new_round("b")
    if surpass:
        for _ in range(5):
            game._credit_elimination("c", "tiebreak scenario")
        game._finish_round("c")
        assert state.winners == ("c",)
    else:
        game._finish_round("c")
        assert state.winners == ("a", "b")
    assert state.phase is Phase.GAME_OVER and state.rounds_completed == 4
    state.assert_invariants()


def test_t46_c2_below_threshold_can_begin_another_round():
    game, state = build_game(mode=GameMode.POINTS, order=["a", "b"],
                             hands={"a": ["rouge"], "b": ["bleu"]}, bag=["vert"],
                             points_format=PointsFormat.POINTS_THRESHOLD, points_threshold=10,
                             elimination_threshold=9)
    game._finish_round("a")
    assert state.phase is Phase.ROUND_OVER and state.player("a").score == 1
    game._start_new_round("b")
    assert state.phase is Phase.CHOOSE_RECIPIENT and state.round_number == 2
    state.assert_invariants()


def test_t49_c2_terminal_tie_ends_regardless_of_scores():
    loss_a = Condition(ConditionKind.COLOR_COUNT, colors=("rouge",), threshold=1)
    loss_b = Condition(ConditionKind.COLOR_COUNT, colors=("rouge",), threshold=2)
    game, state = build_game(mode=GameMode.POINTS, order=["a", "b"],
                             hands={"a": ["rouge", "rouge"], "b": ["rouge"]}, bag=[],
                             defeats={"a": loss_a, "b": loss_b}, donor_defeat_after_removal=True,
                             points_format=PointsFormat.POINTS_THRESHOLD, points_threshold=1,
                             scores={"a": 12, "b": 11}, elimination_threshold=1)
    take_turn(game, "a", "b", "a-t0")
    assert state.phase is Phase.GAME_OVER and state.result == "terminal_tie" and not state.winners
    assert state.player("a").score == 12 and state.player("b").score == 11
    state.assert_invariants()


@pytest.mark.parametrize("player_count", [2, 3])
def test_t60_complete_deterministic_last_survivor_pilot_terminates(player_count):
    order = [f"p{i}" for i in range(player_count)]
    hands = {"p0": ["rouge"], "p1": ["bleu"]}
    if player_count == 3:
        hands["p2"] = ["vert"]
    defeat = Condition(ConditionKind.COLOR_COUNT, colors=("rouge",), threshold=1)
    game, state = build_game(mode=GameMode.LAST_SURVIVOR, order=order, hands=hands,
                             bag=["rouge"], defeats={"p0": defeat, "p1": defeat},
                             succession=Succession.REPLAY_RESPONSIBLE, rng=ScriptedRNG(choice_index=0))
    take_turn(game, "p0", "p1", "p0-t0")
    assert game.finished and state.result in {"last_survivor", "terminal_tie"}
    assert state.phase is Phase.GAME_OVER and state.active_player_id is None
    state.assert_invariants()


def test_t61_complete_deterministic_secret_objective_pilot_wins_on_authorized_gift():
    game, state = build_game(mode=GameMode.SECRET_OBJECTIVE, order=["a", "b"],
                             hands={"a": ["rouge"], "b": ["bleu"]}, bag=[],
                             victories={"a": Condition(ConditionKind.COLOR_COUNT, colors=("vert",), threshold=1),
                                        "b": Condition(ConditionKind.COLOR_COUNT, colors=("rouge",), threshold=1)})
    take_turn(game, "a", "b", "a-t0")
    assert game.finished and state.result == "secret_objective" and state.winners == ("b",)
    assert state.player("b").revealed and state.active_player_id is None
    state.assert_invariants()


def test_t62_complete_c2_pilot_finishes_after_elimination_point_and_last_survivor_bonus():
    defeat = Condition(ConditionKind.COLOR_COUNT, colors=("rouge",), threshold=1)
    game, state = build_game(mode=GameMode.POINTS, order=["a", "b"],
                             hands={"a": ["rouge"], "b": ["bleu"]}, bag=[], defeats={"b": defeat},
                             points_format=PointsFormat.POINTS_THRESHOLD, points_threshold=2,
                             elimination_threshold=10, succession=Succession.CLOCKWISE)
    take_turn(game, "a", "b", "a-t0")
    assert game.finished and state.result == "points_threshold" and state.winners == ("a",)
    assert state.player("a").score == 2 and state.player("a").credited_eliminations == 1
    state.assert_invariants()


def test_t63_variant_comparison_is_recorded_as_distinct_explicit_configurations():
    loss = Condition(ConditionKind.COLOR_COUNT, colors=("rouge",), threshold=1)
    results = {}
    for succession in (Succession.REPLAY_RESPONSIBLE, Succession.CLOCKWISE):
        game, state = build_game(mode=GameMode.LAST_SURVIVOR, order=["a", "b", "c"],
                                 hands={"a": ["rouge"], "b": ["bleu"], "c": ["jaune"]}, bag=["vert"],
                                 defeats={"b": loss}, succession=succession)
        take_turn(game, "a", "b", "a-t0")
        results[succession.value] = (state.config.succession.value, state.active_player_id,
                                    tuple(e.kind for e in state.events))
    assert results["A"][0] == "A" and results["B"][0] == "B"
    assert results["A"][1] == "a"  # The responsible player replays after an elimination.
    assert results["B"][1] == "c"  # The clockwise variant selects the next living player.
    assert results["A"][2] != results["B"][2]
