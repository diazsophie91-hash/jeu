import pytest

from engine import create_game, SetupError
from engine.state import Phase
from rules import Card, Condition, ConditionKind, GameConfig, GameMode
from tests.helpers import ScriptedRNG, safe_card


def safe_cards(n):
    defeat = Condition(ConditionKind.TOTAL_COUNT, threshold=99)
    return tuple(Card(f"c{i}", defeat) for i in range(n))


def test_t01_reference_deal_and_stock_conservation():
    colors = {"rouge": 10, "bleu": 10, "vert": 10, "jaune": 10}
    game = create_game([f"p{i}" for i in range(8)], GameConfig(colors, GameMode.LAST_SURVIVOR, safe_cards(8)), seed=78, first_player_id="p0")
    state = game._state
    assert [len(p.hand) for p in state.players] == [3] * 8
    assert len(state.common_bag) == 16
    state.assert_invariants()


def test_t02_valid_initial_collection_is_kept_and_game_continues():
    game = create_game(["a", "b"], GameConfig({"rouge": 4, "bleu": 4}, GameMode.LAST_SURVIVOR, safe_cards(2)), seed=2, first_player_id="a")
    assert all(len(p.hand) == 3 and p.alive and not p.revealed for p in game._state.players)
    assert game.phase is Phase.CHOOSE_RECIPIENT
    assert not any(e.kind in {"player_eliminated", "card_revealed", "point_awarded"} for e in game._state.events)
    game._state.assert_invariants()


def test_t03_invalid_initial_collection_is_returned_and_redrawn_privately():
    cards = (
        Card("red-risk", Condition(ConditionKind.COLOR_COUNT, colors=("rouge",), threshold=3)),
        safe_card("safe"),
    )
    config = GameConfig({"rouge": 3, "bleu": 3, "vert": 2}, GameMode.LAST_SURVIVOR, cards)
    rng = ScriptedRNG([["rouge", "rouge", "rouge"], ["bleu", "bleu", "bleu"]])
    game = create_game(["a", "b"], config, first_player_id="a", rng=rng)
    state = game._state
    assert [t.color for t in state.player("a").hand] == ["bleu"] * 3
    assert state.player("a").alive and not state.player("a").revealed
    assert not any(e.kind in {"condition_checked", "player_eliminated", "card_revealed", "point_awarded"} for e in state.events)
    assert all("red-risk" not in repr(e.data) for e in game.public_event_history())
    state.assert_invariants()


@pytest.mark.parametrize("mode", [GameMode.LAST_SURVIVOR, GameMode.POINTS])
def test_t04_initial_defeat_condition_only_retries_in_modes_a_and_c(mode):
    cards = tuple(Card(f"c{i}", Condition(ConditionKind.COLOR_COUNT, colors=("rouge",), threshold=3)) for i in range(2))
    config = GameConfig({"rouge": 3, "bleu": 3, "vert": 2}, mode, cards,
                        elimination_threshold=5 if mode is GameMode.POINTS else None)
    rng = ScriptedRNG([["rouge", "rouge", "rouge"], ["bleu", "bleu", "bleu"]])
    game = create_game(["a", "b"], config, first_player_id="a", rng=rng)
    assert game._state.player("a").alive
    assert game._state.player("a").hand == [t for t in game._state.player("a").hand if t.color == "bleu"]
    assert not any(e.kind == "card_revealed" for e in game.public_event_history())
    game._state.assert_invariants()


def test_t04_secret_objective_collection_is_retried_without_declaring_victory():
    cards = tuple(Card(f"c{i}", Condition(ConditionKind.TOTAL_COUNT, threshold=99),
                       Condition(ConditionKind.COLOR_COUNT, colors=("rouge",), threshold=3)) for i in range(2))
    config = GameConfig({"rouge": 3, "bleu": 3, "vert": 2}, GameMode.SECRET_OBJECTIVE, cards)
    rng = ScriptedRNG([["rouge", "rouge", "rouge"], ["bleu", "bleu", "bleu"]])
    game = create_game(["a", "b"], config, first_player_id="a", rng=rng)
    assert game.phase is Phase.CHOOSE_RECIPIENT and game._state.result is None
    assert game._state.player("a").alive and not game._state.player("a").revealed
    assert not any(e.kind in {"game_finished", "card_revealed", "player_eliminated"} for e in game.public_event_history())
    game._state.assert_invariants()


def test_t04_secret_objective_defeat_collection_is_retried_without_eliminating_player():
    cards = tuple(Card(f"c{i}", Condition(ConditionKind.COLOR_COUNT, colors=("rouge",), threshold=3),
                       Condition(ConditionKind.COLOR_COUNT, colors=("vert",), threshold=3)) for i in range(2))
    config = GameConfig({"rouge": 3, "bleu": 3, "vert": 2}, GameMode.SECRET_OBJECTIVE, cards)
    rng = ScriptedRNG([["rouge", "rouge", "rouge"], ["bleu", "bleu", "bleu"]])
    game = create_game(["a", "b"], config, first_player_id="a", rng=rng)
    assert game._state.player("a").alive and not game._state.player("a").revealed
    assert [t.color for t in game._state.player("a").hand] == ["bleu"] * 3
    assert game._state.result is None and not any(e.kind == "card_revealed" for e in game.public_event_history())
    game._state.assert_invariants()


def test_t15_setup_retries_when_any_of_multiple_defeat_conditions_matches():
    multi = Card("multi", (
        Condition(ConditionKind.COLOR_COUNT, colors=("rouge",), threshold=2),
        Condition(ConditionKind.COLOR_COUNT, colors=("bleu",), threshold=2),
    ))
    config = GameConfig({"rouge": 2, "bleu": 4}, GameMode.LAST_SURVIVOR,
                        (multi, safe_card("safe")), initial_hand_size=2)
    rng = ScriptedRNG([["rouge", "rouge"], ["rouge", "bleu"], ["bleu", "bleu"]])
    game = create_game(["a", "b"], config, first_player_id="a", rng=rng)
    assert sorted(token.color for token in game._state.player("a").hand) == ["bleu", "rouge"]
    assert game._state.player("a").alive and not game._state.player("a").revealed
    assert not any(event.kind in {"player_eliminated", "card_revealed"} for event in game.public_event_history())
    game.assert_invariants()


def test_t05_retries_preserve_unique_token_ids_and_total_count():
    cards = (Card("risk", Condition(ConditionKind.COLOR_COUNT, colors=("rouge",), threshold=3)), safe_card("safe"))
    config = GameConfig({"rouge": 3, "bleu": 5}, GameMode.LAST_SURVIVOR, cards)
    game = create_game(["a", "b"], config, first_player_id="a", rng=ScriptedRNG([["rouge"] * 3, ["bleu"] * 3]))
    game._state.assert_invariants()
    tokens = list(game._state.common_bag) + [t for p in game._state.players for t in p.hand]
    assert len(tokens) == 8
    assert len({t.id for t in tokens}) == 8


def test_t06_same_configuration_and_seed_reproduce_deal_and_events():
    config = GameConfig({"rouge": 8, "bleu": 8}, GameMode.LAST_SURVIVOR, safe_cards(3))
    def snapshot():
        game = create_game(["a", "b", "c"], config, seed=93, first_player_id="b")
        return ([[(t.id, t.color) for t in p.hand] for p in game._state.players],
                [(t.id, t.color) for t in game._state.common_bag], game.public_event_history())
    assert snapshot() == snapshot()


def test_t82_impossible_setup_is_rejected_before_game_creation():
    cards = (Card("a", Condition(ConditionKind.TOTAL_COUNT, threshold=3)), safe_card("b"))
    config = GameConfig({"rouge": 3, "bleu": 3}, GameMode.LAST_SURVIVOR, cards)
    with pytest.raises(ValueError, match="Aucune attribution complète"):
        create_game(["a", "b"], config, seed=0, first_player_id="a")


def test_t82_retry_limit_exhaustion_is_explicit_and_keeps_cards_private():
    cards = (Card("a", Condition(ConditionKind.COLOR_COUNT, colors=("rouge",), threshold=1)), safe_card("b"))
    config = GameConfig({"rouge": 3, "bleu": 3}, GameMode.LAST_SURVIVOR, cards, max_setup_attempts=2)
    rng = ScriptedRNG([["rouge", "bleu", "bleu"], ["rouge", "bleu", "bleu"]])
    with pytest.raises(SetupError, match="aucune carte ni condition n'a été révélée"):
        create_game(["a", "b"], config, first_player_id="a", rng=rng)
