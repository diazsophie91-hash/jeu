from engine import AcceptGift, ChooseRecipient, ProposeGift, RefuseGift
from engine.state import Phase
from rules import Condition, ConditionKind, GameMode
from tests.helpers import ScriptedRNG, build_game


def propose(game, token_id, recipient="b"):
    game.submit(ChooseRecipient(recipient))
    return game.submit(ProposeGift(token_id))


def test_t03_t04_t82_public_setup_events_do_not_expose_cards_or_initial_collections():
    game, state = build_game(mode=GameMode.SECRET_OBJECTIVE, order=["a", "b"],
                             hands={"a": ["rouge", "bleu"], "b": ["vert"]}, bag=["jaune"],
                             victories={"a": Condition(ConditionKind.COLOR_COUNT, colors=("rouge",), threshold=1),
                                        "b": Condition(ConditionKind.COLOR_COUNT, colors=("bleu",), threshold=1)})
    public = game.public_view()
    assert all(p.revealed_card is None for p in public.players)
    assert game.controller("a").view().card == state.player("a").card
    assert game.controller("b").view().card == state.player("b").card
    assert not any("rouge" in repr(event.data) or "bleu" in repr(event.data) for event in game.public_event_history())


def test_t50_t51_t54_event_order_and_public_history_redacts_hidden_offer():
    game, state = build_game(mode=GameMode.LAST_SURVIVOR, order=["a", "b"],
                             hands={"a": ["rouge"], "b": ["bleu"]}, bag=["vert"])
    propose(game, "a-t0")
    public = game.public_event_history()
    removed = next(e for e in public if e.kind == "token_removed")
    assert "token_id" not in removed.data and "color" not in removed.data
    kinds = [e.kind for e in public]
    assert kinds.index("recipient_chosen") < kinds.index("token_removed") < kinds.index("gift_proposed")
    locations = [state.proposal.token, *state.common_bag, *(t for p in state.players for t in p.hand)]
    assert len(locations) == 3 and len({t.id for t in locations}) == 3
    state.assert_invariants()


def test_t76_only_recipient_gets_possible_common_colors_not_exact_contents():
    game, state = build_game(mode=GameMode.LAST_SURVIVOR, order=["a", "b", "c"],
                             hands={"a": ["rouge"], "b": ["bleu"], "c": ["vert"]},
                             bag=["vert", "vert", "jaune"])
    propose(game, "a-t0")
    recipient = game.controller("b").view()
    donor = game.controller("a").view()
    spectator = game.controller("c").view()
    assert set(recipient.common_bag_colors) == {"rouge", "bleu", "vert", "jaune"}
    assert donor.common_bag_colors is None and spectator.common_bag_colors is None
    assert game.public_view().common_bag_nonempty is None
    assert game.public_view().possible_common_colors == ()
    assert len(state.common_bag) == 3  # Exact composition remains internal.
    state.assert_invariants()


def test_t08_t28_hidden_refusal_draw_is_known_to_recipient_but_not_public():
    game, state = build_game(mode=GameMode.LAST_SURVIVOR, order=["a", "b"],
                             hands={"a": ["rouge"], "b": ["vert"]}, bag=["bleu"],
                             reveal_refusal_draw=False, rng=ScriptedRNG(choice_index=0))
    propose(game, "a-t0")
    result = game.submit(RefuseGift())
    drawn = next(e for e in result.events if e.kind == "token_drawn")
    assert "token_id" not in drawn.data and "color" not in drawn.data
    assert len(game.controller("b").view().hand) == 2
    assert not any(e.kind == "token_revealed" for e in result.events)
    state.assert_invariants()


def test_t54_revealed_card_appears_publicly_only_after_declared_elimination():
    defeat = Condition(ConditionKind.COLOR_COUNT, colors=("rouge",), threshold=1)
    game, state = build_game(mode=GameMode.LAST_SURVIVOR, order=["a", "b", "c"],
                             hands={"a": ["rouge"], "b": ["bleu"], "c": ["vert"]},
                             bag=["jaune"], defeats={"b": defeat})
    assert game.public_view().players[1].revealed_card is None
    propose(game, "a-t0")
    game.submit(AcceptGift())
    assert not state.player("b").alive
    public_b = next(p for p in game.public_view().players if p.id == "b")
    assert public_b.revealed_card == state.player("b").card
    reveal_index = next(i for i, e in enumerate(state.events) if e.kind == "card_revealed" and e.data["player_id"] == "b")
    eliminate_index = next(i for i, e in enumerate(state.events) if e.kind == "player_eliminated" and e.data["player_id"] == "b")
    assert reveal_index == eliminate_index + 1
    state.assert_invariants()


def test_t79_first_player_is_explicit_and_engine_does_not_derive_a_tie_break():
    from engine import create_game
    from rules import Card, GameConfig

    defeat = Condition(ConditionKind.TOTAL_COUNT, threshold=99)
    config = GameConfig({"rouge": 6}, GameMode.LAST_SURVIVOR,
                        (Card("a", defeat), Card("b", defeat)))
    try:
        create_game(["a", "b"], config, seed=3)
    except ValueError as error:
        assert "premier joueur doit être désigné" in str(error)
    else:
        raise AssertionError("create_game must require a group-supplied first player")
    game = create_game(["a", "b"], config, seed=3, first_player_id="b")
    assert game.active_player_id == "b"

