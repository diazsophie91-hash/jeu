import pytest

from engine import AcceptGift, ChooseRecipient, ProposeGift, RefuseGift, GameFinished, GameEngine, IllegalAction
from engine.state import Phase
from rules import Card, Condition, ConditionKind, GameConfig, GameMode, MajorityBasis, Succession, Token
from tests.helpers import ScriptedRNG, build_game


def offer(game, token_id, recipient="b"):
    game.submit(ChooseRecipient(recipient))
    game.submit(ProposeGift(token_id))


def test_t12_t14_t23_elimination_reveals_card_and_returns_remaining_hand():
    defeat = Condition(ConditionKind.COLOR_COUNT, colors=("rouge",), threshold=2)
    game, state = build_game(mode=GameMode.LAST_SURVIVOR, order=["a", "b", "c"],
                             hands={"a": ["rouge"], "b": ["rouge"], "c": ["vert"]},
                             bag=["rouge", "jaune"], defeats={"b": defeat})
    offer(game, "a-t0")
    game.submit(AcceptGift())
    assert not state.player("b").alive and state.player("b").revealed
    assert not state.player("b").hand
    assert sum(t.color == "rouge" for t in state.common_bag) == 2
    assert len([e for e in state.events if e.kind == "player_eliminated" and e.data["player_id"] == "b"]) == 1
    state.assert_invariants()


def test_t15_single_resolution_eliminates_a_player_only_once():
    defeat = Condition(ConditionKind.COLOR_COUNT, colors=("rouge",), threshold=1)
    game, state = build_game(mode=GameMode.POINTS, order=["a", "b", "c"],
                             hands={"a": ["bleu"], "b": ["rouge"], "c": ["vert"]},
                             bag=["rouge"], defeats={"b": defeat})
    offer(game, "a-t0")
    game.submit(AcceptGift())
    assert len([e for e in state.events if e.kind == "player_eliminated" and e.data["player_id"] == "b"]) == 1
    assert len([e for e in state.events if e.kind == "card_revealed" and e.data["player_id"] == "b"]) == 1
    assert state.player("a").credited_eliminations == 1


def test_t15_multiple_satisfied_defeat_conditions_eliminate_once_through_engine_api():
    from engine import create_game
    from rules.rules import evaluate_defeat_conditions

    first = Condition(ConditionKind.COLOR_COUNT, colors=("rouge",), threshold=1)
    second = Condition(ConditionKind.TOTAL_COUNT, threshold=2)
    cards = (Card("a", Condition(ConditionKind.TOTAL_COUNT, threshold=99)),
             Card("b", (first, second)),
             Card("c", Condition(ConditionKind.TOTAL_COUNT, threshold=99)))
    config = GameConfig({"rouge": 2, "bleu": 2, "vert": 2}, GameMode.POINTS, cards,
                        elimination_threshold=9, initial_hand_size=1)
    game = create_game(["a", "b", "c"], config, first_player_id="a",
                       rng=ScriptedRNG([["rouge"], ["bleu"], ["vert"]]))
    state = game._state
    before_ids = {t.id for t in state.common_bag} | {t.id for p in state.players for t in p.hand}
    assert evaluate_defeat_conditions(state.player("b").card,
                                      [*state.player("b").hand, Token("probe", "rouge")]) == (True, True)
    game.submit(ChooseRecipient("b"))
    game.submit(ProposeGift("t0000"))
    game.submit(AcceptGift())
    assert not state.player("b").alive
    assert len([e for e in state.events if e.kind == "player_eliminated" and e.data["player_id"] == "b"]) == 1
    assert len([e for e in state.events if e.kind == "card_revealed" and e.data["player_id"] == "b"]) == 1
    assert len([e for e in state.events if e.kind == "point_awarded" and e.data["player_id"] == "a"]) == 1
    assert state.player("a").score == state.player("a").credited_eliminations == 1
    eliminated = next(e for e in state.events if e.kind == "player_eliminated" and e.data["player_id"] == "b")
    assert len(eliminated.data["returned_token_ids"]) == 2
    after_ids = {t.id for t in state.common_bag} | {t.id for p in state.players for t in p.hand}
    assert after_ids == before_ids
    assert state.active_player_id == "a"
    assert sum(e.kind == "successor_selected" for e in state.events) == 1
    state.assert_invariants()


def test_t19_variant_a_responsible_replay_draw_checks_secret_victory_first():
    loss = Condition(ConditionKind.COLOR_COUNT, colors=("rouge",), threshold=1)
    victory = Condition(ConditionKind.COLOR_COUNT, colors=("bleu",), threshold=1)
    recipient_victory = Condition(ConditionKind.COLOR_COUNT, colors=("bleu",), threshold=2)
    game, state = build_game(mode=GameMode.SECRET_OBJECTIVE, order=["a", "b", "c"],
                             hands={"a": ["rouge"], "b": ["bleu"], "c": ["vert"]},
                             bag=["bleu"], defeats={"b": loss}, victories={"a": victory, "b": recipient_victory, "c": victory},
                             succession=Succession.REPLAY_RESPONSIBLE, rng=ScriptedRNG(choice_index=0))
    offer(game, "a-t0")
    game.submit(AcceptGift())
    assert state.player("b").alive is False
    assert state.result == "secret_objective" and state.winners == ("a",)
    assert state.player("a").revealed
    checked = [e.data.get("trigger") for e in state.events if e.kind == "condition_checked" and e.data.get("player_id") == "a"]
    assert checked == ["replay_draw"]
    assert not any(e.kind == "player_eliminated" and e.data["player_id"] == "a" for e in state.events)
    state.assert_invariants()


def test_t20_removing_token_does_not_trigger_donors_secret_victory():
    victory = Condition(ConditionKind.MAJORITY, colors=("rouge",), minimum=1,
                        majority_basis=MajorityBasis.PLURALITY)
    game, state = build_game(mode=GameMode.SECRET_OBJECTIVE, order=["a", "b", "c"],
                             hands={"a": ["rouge", "bleu"], "b": ["vert"], "c": ["jaune"]},
                             bag=["noir"], victories={"a": victory, "b": victory, "c": victory})
    offer(game, "a-t1")
    assert state.player("a").alive
    assert state.phase is Phase.DECISION
    assert state.result is None and state.winners == ()
    assert not any(e.kind == "condition_checked" and e.data.get("player_id") == "a" for e in state.events)
    game.submit(AcceptGift())
    assert state.player("a").alive and state.result is None
    state.assert_invariants()


def test_t21_last_survivor_wins_secret_mode_without_personal_objective():
    loss = Condition(ConditionKind.COLOR_COUNT, colors=("rouge",), threshold=2)
    victory = Condition(ConditionKind.COLOR_COUNT, colors=("vert",), threshold=99)
    game, state = build_game(mode=GameMode.SECRET_OBJECTIVE, order=["a", "b", "c"],
                             hands={"a": ["rouge", "rouge"], "b": ["rouge"], "c": ["vert"]},
                             bag=["rouge"], defeats={"a": Condition(ConditionKind.COLOR_COUNT, colors=("rouge",), threshold=1), "b": loss},
                             victories={"a": victory, "b": victory, "c": victory},
                             succession=Succession.CLOCKWISE, donor_defeat_after_removal=True)
    offer(game, "a-t0")
    game.submit(AcceptGift())
    assert state.result == "last_survivor" and state.winners == ("c",)
    state.assert_invariants()


def test_t25_variant_a_replays_responsible_after_recipient_elimination():
    loss = Condition(ConditionKind.COLOR_COUNT, colors=("rouge",), threshold=1)
    game, state = build_game(mode=GameMode.LAST_SURVIVOR, order=["a", "b", "c"],
                             hands={"a": ["rouge"], "b": ["bleu"], "c": ["vert"]},
                             bag=["jaune"], defeats={"b": loss},
                             succession=Succession.REPLAY_RESPONSIBLE)
    offer(game, "a-t0")
    game.submit(AcceptGift())
    assert not state.player("b").alive
    assert state.active_player_id == "a"
    assert any(e.kind == "token_drawn" and e.data.get("reason") == "replay" for e in state.events)
    state.assert_invariants()


def test_t26_variant_a_uses_surviving_recipient_when_donor_was_eliminated():
    donor_defeat = Condition(ConditionKind.COLOR_COUNT, colors=("rouge",), threshold=1)
    game, state = build_game(mode=GameMode.LAST_SURVIVOR, order=["a", "b", "c"],
                             hands={"a": ["rouge", "rouge"], "b": ["bleu"], "c": ["vert"]},
                             bag=["jaune"], defeats={"a": donor_defeat},
                             donor_defeat_after_removal=True,
                             succession=Succession.REPLAY_RESPONSIBLE)
    offer(game, "a-t0")
    assert not state.player("a").alive and state.proposal is not None
    game.submit(AcceptGift())
    assert state.player("b").alive and state.active_player_id == "b"
    assert state.result is None
    state.assert_invariants()


def test_t27_t28_responsible_replay_empty_hand_draw_visibility_and_empty_bag():
    for reveal in (False, True):
        game, state = build_game(mode=GameMode.LAST_SURVIVOR, order=["a", "b", "c"],
                                 hands={"a": ["bleu"], "b": ["rouge"], "c": ["vert"]},
                                 bag=["jaune"], defeats={"b": Condition(ConditionKind.COLOR_COUNT, colors=("bleu",), threshold=1)},
                                 succession=Succession.REPLAY_RESPONSIBLE, reveal_replay_draw=reveal,
                                 rng=ScriptedRNG(choice_index=0))
        offer(game, "a-t0")
        game.submit(AcceptGift())
        draw = next(e for e in game.public_event_history() if e.kind == "token_drawn" and e.data.get("reason") == "replay")
        assert ("color" in draw.data) is reveal
        assert state.active_player_id == "a"
        state.assert_invariants()

    # Exercise the explicit empty-common-bag fallback from a coherent rare state.
    from engine.state import GameState, PlayerState
    a, b, c = (PlayerState(pid, [], None, alive=pid != "b") for pid in ("a", "b", "c"))
    safe = Condition(ConditionKind.TOTAL_COUNT, threshold=99)
    # Use actual cards and a one-token stock held by the sole survivor.
    cards = [Card(pid, safe) for pid in ("a", "b", "c")]
    a.card, b.card, c.card = cards
    c.hand.append(Token("c-t0", "vert"))
    config = GameConfig({"vert": 1}, GameMode.POINTS, tuple(cards),
                        elimination_threshold=5, initial_hand_size=1)
    state = GameState(config, [a, b, c], [], "a", Phase.CHOOSE_RECIPIENT,
                      resolution_eliminated={"b"})
    game = GameEngine(state, ScriptedRNG())
    game._succession_a("a", "b", True)
    assert not state.player("a").alive and state.player("a").score == 0
    assert state.round_winner == "c"
    assert state.active_player_id is None
    state.assert_invariants()


def test_t29_replay_draw_elimination_has_no_separate_point():
    game, state = build_game(mode=GameMode.POINTS, order=["a", "b", "c"],
                             hands={"a": ["rouge"], "b": ["bleu"], "c": ["vert"]},
                             bag=["rouge"], defeats={
                                 "a": Condition(ConditionKind.COLOR_COUNT, colors=("rouge",), threshold=1),
                                 "b": Condition(ConditionKind.COLOR_COUNT, colors=("rouge",), threshold=1),
                             }, succession=Succession.REPLAY_RESPONSIBLE,
                             rng=ScriptedRNG(choice_index=0))
    offer(game, "a-t0")
    game.submit(AcceptGift())
    assert not state.player("a").alive and not state.player("b").alive
    assert state.player("a").score == 1 and state.player("a").credited_eliminations == 1
    assert state.round_winner == "c"
    state.assert_invariants()


def test_t30_t56_clockwise_succession_skips_eliminated_positions():
    loss = Condition(ConditionKind.COLOR_COUNT, colors=("rouge",), threshold=1)
    game, state = build_game(mode=GameMode.LAST_SURVIVOR, order=["a", "b", "c", "d"],
                             hands={"a": ["rouge"], "b": ["bleu"], "c": ["vert"], "d": ["jaune"]},
                             bag=["noir"], defeats={"b": loss}, succession=Succession.CLOCKWISE,
                             revealed={"c"})
    offer(game, "a-t0")
    game.submit(AcceptGift())
    assert not state.player("b").alive
    assert state.active_player_id == "d"
    assert not state.player("c").alive
    state.assert_invariants()


def test_t31_clockwise_chain_eliminates_empty_successors_then_selects_next_live_player():
    loss = Condition(ConditionKind.COLOR_COUNT, colors=("rouge",), threshold=1)
    game, state = build_game(mode=GameMode.POINTS, order=["a", "b", "c", "d", "e"],
                             hands={"a": ["rouge"], "b": ["rouge"], "c": [], "d": [], "e": ["vert"]},
                             bag=["jaune"], defeats={"b": loss}, succession=Succession.CLOCKWISE)
    offer(game, "a-t0")
    game.submit(AcceptGift())
    assert not state.player("b").alive and not state.player("c").alive and not state.player("d").alive
    assert state.active_player_id == "e"
    assert state.player("a").score == 3 and state.player("a").credited_eliminations == 3
    state.assert_invariants()


@pytest.mark.parametrize("succession", [Succession.REPLAY_RESPONSIBLE, Succession.CLOCKWISE])
def test_t32_donor_and_recipient_elimination_resolves_before_successor_selection(succession):
    donor_defeat = Condition(ConditionKind.COLOR_COUNT, colors=("rouge",), threshold=1)
    target_defeat = Condition(ConditionKind.COLOR_COUNT, colors=("rouge",), threshold=1)
    game, state = build_game(mode=GameMode.LAST_SURVIVOR, order=["a", "b", "c", "d"],
                             hands={"a": ["rouge", "rouge"], "b": ["bleu"], "c": ["vert"], "d": ["jaune"]},
                             bag=["noir"], defeats={"a": donor_defeat, "b": target_defeat},
                             donor_defeat_after_removal=True, succession=succession)
    offer(game, "a-t0")
    game.submit(AcceptGift())
    assert not state.player("a").alive and not state.player("b").alive
    assert len([e for e in state.events if e.kind == "card_revealed" and e.data["player_id"] in {"a", "b"}]) == 2
    assert state.active_player_id == ("c" if succession is Succession.CLOCKWISE else "c")
    assert state.player(state.active_player_id).alive
    state.assert_invariants()


def test_t33_all_initial_eliminations_precede_turn_selection():
    defeat = Condition(ConditionKind.COLOR_COUNT, colors=("rouge",), threshold=1)
    game, state = build_game(mode=GameMode.LAST_SURVIVOR, order=["a", "b", "c", "d"],
                             hands={"a": ["rouge", "rouge"], "b": ["bleu"], "c": ["vert"], "d": ["jaune"]},
                             bag=["noir"], defeats={"a": defeat, "b": defeat},
                             donor_defeat_after_removal=True, succession=Succession.CLOCKWISE)
    offer(game, "a-t0")
    game.submit(AcceptGift())
    eliminated = [e.data["player_id"] for e in state.events if e.kind == "player_eliminated"]
    assert eliminated[:2] == ["a", "b"]
    assert state.active_player_id == "c"
    assert all(state.player(pid).alive for pid in ("c", "d"))
    state.assert_invariants()


def test_t52_eliminated_player_cannot_be_selected_or_act():
    game, state = build_game(mode=GameMode.LAST_SURVIVOR, order=["a", "b", "c"],
                             hands={"a": ["rouge"], "b": ["bleu"], "c": ["vert"]}, bag=["jaune"],
                             revealed={"c"})
    with pytest.raises(IllegalAction):
        game.submit(ChooseRecipient("c"))
    with pytest.raises(IllegalAction):
        game.submit(ChooseRecipient("b"), player_id="c")
    assert state.active_player_id == "a"
    state.assert_invariants()


def test_t53_t58_action_after_terminal_end_is_rejected_without_changing_result():
    loss = Condition(ConditionKind.COLOR_COUNT, colors=("rouge",), threshold=1)
    game, state = build_game(mode=GameMode.LAST_SURVIVOR, order=["a", "b"],
                             hands={"a": ["bleu"], "b": ["rouge"]}, bag=[], defeats={"b": loss})
    offer(game, "a-t0")
    game.submit(AcceptGift())
    snapshot = (state.result, state.winners, tuple((p.id, p.score, p.alive) for p in state.players), len(state.events))
    with pytest.raises(GameFinished):
        game.submit(ChooseRecipient("a"))
    assert snapshot == (state.result, state.winners, tuple((p.id, p.score, p.alive) for p in state.players), len(state.events))
    state.assert_invariants()


@pytest.mark.parametrize("reveal", [False, True])
def test_t70_empty_successor_draws_and_survives_with_configured_visibility(reveal):
    game, state = build_game(mode=GameMode.SECRET_OBJECTIVE, order=["a", "b", "c", "d"],
                             hands={"a": ["rouge"], "b": ["bleu"], "c": [], "d": ["violet"]},
                             bag=["jaune", "vert"],
                             defeats={"a": Condition(ConditionKind.COLOR_COUNT, colors=("jaune",), threshold=1),
                                      "b": Condition(ConditionKind.COLOR_COUNT, colors=("rouge",), threshold=1)},
                             victories={"a": Condition(ConditionKind.TOTAL_COUNT, threshold=99),
                                        "b": Condition(ConditionKind.TOTAL_COUNT, threshold=99),
                                        "c": Condition(ConditionKind.TOTAL_COUNT, threshold=99),
                                        "d": Condition(ConditionKind.TOTAL_COUNT, threshold=99)},
                             succession=Succession.REPLAY_RESPONSIBLE, reveal_replay_draw=reveal,
                             rng=ScriptedRNG(choice_index=0))
    assert not any(e.kind == "condition_checked" and e.data.get("player_id") == "c" for e in state.events)
    game.submit(ChooseRecipient("b"))
    game.submit(ProposeGift("a-t0"))
    game.submit(AcceptGift())
    assert state.player("a").alive is False and state.player("b").alive is False
    assert state.player("c").alive and state.active_player_id == "c"
    draw = next(e for e in game.public_event_history() if e.kind == "token_drawn" and e.data.get("reason") == "successor_activation")
    assert ("color" in draw.data) is reveal
    assert [e.data.get("trigger") for e in state.events if e.kind == "condition_checked" and e.data.get("player_id") == "c"] == ["successor_draw"]
    state.assert_invariants()


def test_t71_empty_successor_with_empty_common_bag_is_eliminated_then_succession_continues():
    from engine.state import GameState, PlayerState

    cards = [Card(pid, Condition(ConditionKind.TOTAL_COUNT, threshold=99)) for pid in "abcd"]
    players = [PlayerState("a", [], cards[0], alive=False, revealed=True),
               PlayerState("b", [], cards[1], alive=False, revealed=True),
               PlayerState("c", [], cards[2]),
               PlayerState("d", [Token("d-t0", "vert")], cards[3])]
    config = GameConfig({"vert": 1}, GameMode.LAST_SURVIVOR, tuple(cards),
                        succession=Succession.REPLAY_RESPONSIBLE, initial_hand_size=1)
    state = GameState(config, players, [], "a", Phase.CHOOSE_RECIPIENT,
                      resolution_eliminated={"a", "b"})
    game = GameEngine(state, ScriptedRNG())
    game._succession_a("a", "b", True)
    assert not state.player("c").alive and state.player("c").revealed
    assert state.player("d").alive and state.phase is Phase.GAME_OVER
    assert state.result == "last_survivor" and state.winners == ("d",)
    assert not any(e.kind == "token_drawn" for e in state.events)
    assert not any(e.kind == "point_awarded" for e in state.events)
    state.assert_invariants()


def test_t80_empty_successor_draw_triggers_secret_victory_before_defeat():
    game, state = build_game(mode=GameMode.SECRET_OBJECTIVE, order=["a", "b", "c", "d"],
                             hands={"a": ["rouge"], "b": ["bleu"], "c": [], "d": ["violet"]},
                             bag=["jaune", "vert"],
                             defeats={"a": Condition(ConditionKind.COLOR_COUNT, colors=("jaune",), threshold=1),
                                      "b": Condition(ConditionKind.COLOR_COUNT, colors=("rouge",), threshold=1),
                                      "c": Condition(ConditionKind.COLOR_COUNT, colors=("vert",), threshold=1)},
                             victories={"a": Condition(ConditionKind.TOTAL_COUNT, threshold=99),
                                        "b": Condition(ConditionKind.TOTAL_COUNT, threshold=99),
                                        "c": Condition(ConditionKind.COLOR_COUNT, colors=("vert",), threshold=1),
                                        "d": Condition(ConditionKind.TOTAL_COUNT, threshold=99)},
                             succession=Succession.REPLAY_RESPONSIBLE,
                             rng=ScriptedRNG(choice_index=0))
    game.submit(ChooseRecipient("b"))
    game.submit(ProposeGift("a-t0"))
    assert not any(e.kind == "condition_checked" and e.data.get("player_id") == "c" for e in state.events)
    game.submit(AcceptGift())
    assert state.result == "secret_objective" and state.winners == ("c",)
    assert state.player("c").revealed and state.player("c").alive
    checks = [e.data["trigger"] for e in state.events if e.kind == "condition_checked" and e.data.get("player_id") == "c"]
    assert checks == ["successor_draw"]
    assert not any(e.kind == "player_eliminated" and e.data["player_id"] == "c" for e in state.events)
    state.assert_invariants()


def test_t72_clockwise_variant_makes_surviving_recipient_active_after_donor_elimination():
    game, state = build_game(mode=GameMode.LAST_SURVIVOR, order=["a", "b", "c"],
                             hands={"a": ["rouge", "rouge"], "b": ["bleu"], "c": ["vert"]},
                             bag=["jaune"],
                             defeats={"a": Condition(ConditionKind.COLOR_COUNT, colors=("rouge",), threshold=1)},
                             donor_defeat_after_removal=True, succession=Succession.CLOCKWISE)
    offer(game, "a-t0")
    assert not state.player("a").alive and state.proposal is not None
    game.submit(AcceptGift())
    assert state.player("b").alive and state.active_player_id == "b"
    assert state.result is None
    state.assert_invariants()

