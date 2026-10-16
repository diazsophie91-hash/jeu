import pytest

from engine import create_game
from engine.selection import (FirstPlayerMethod, UnresolvedTie, create_game_with_selection,
                              select_first_player)
from rules import Card, Condition, ConditionKind, GameConfig, GameMode


def test_t79_collective_choice_is_explicit_and_transmitted_to_engine():
    selection = select_first_player(["a", "b"], FirstPlayerMethod.COLLECTIVE, collective_choice="b")
    game = create_game_with_selection(["a", "b"], config(), selection, seed=8)
    assert game.active_player_id == "b"
    event = next(event for event in game.public_event_history() if event.kind == "first_player_selected")
    assert event.data == {"player_id": "b", "method": "collective_choice",
                          "resolution": "collective_choice", "tied_candidates": ()}


def test_t79_recency_tie_resolution_is_audited_in_setup_history():
    selection = select_first_player(["a", "b"], FirstPlayerMethod.MOST_RECENT_GIFT,
                                    gift_recency={"a": 2, "b": 2}, consensus_choice="b")
    game = create_game_with_selection(["a", "b"], config(), selection, seed=10)
    event = next(e for e in game.public_event_history() if e.kind == "first_player_selected")
    assert event.data["resolution"] == "group_consensus"
    assert event.data["tied_candidates"] == ("a", "b")


def test_t79_most_recent_real_gift_selects_unique_latest_recipient():
    selection = select_first_player(["a", "b", "c"], FirstPlayerMethod.MOST_RECENT_GIFT,
                                    gift_recency={"a": 2, "b": 8, "c": 3})
    assert selection.player_id == "b" and selection.resolution == "most_recent_gift"


def test_t79_recency_tie_requires_explicit_consensus_or_resolver():
    recency = {"a": 5, "b": 5, "c": 2}
    with pytest.raises(UnresolvedTie) as error:
        select_first_player(["a", "b", "c"], FirstPlayerMethod.MOST_RECENT_GIFT, gift_recency=recency)
    assert error.value.candidates == ("a", "b")
    chosen = select_first_player(["a", "b", "c"], FirstPlayerMethod.MOST_RECENT_GIFT,
                                 gift_recency=recency, consensus=lambda candidates: candidates[1])
    assert chosen.player_id == "b" and chosen.tied_candidates == ("a", "b")
    assert chosen.resolution == "group_consensus"


@pytest.mark.parametrize("choice", ["missing", ""])
def test_t79_unknown_player_is_rejected(choice):
    with pytest.raises(ValueError, match="participer"):
        select_first_player(["a", "b"], FirstPlayerMethod.COLLECTIVE, collective_choice=choice)


def test_t79_recency_requires_data_for_every_participant():
    with pytest.raises(ValueError, match="chaque joueur"):
        select_first_player(["a", "b"], FirstPlayerMethod.MOST_RECENT_GIFT,
                            gift_recency={"a": 1})


def test_t79_existing_direct_first_player_api_remains_compatible():
    game = create_game(["a", "b"], config(), seed=9, first_player_id="a")
    assert game.active_player_id == "a"
    event = next(e for e in game.public_event_history() if e.kind == "first_player_selected")
    assert event.data["method"] == "direct_input" and event.data["player_id"] == "a"


def config():
    defeat = Condition(ConditionKind.TOTAL_COUNT, threshold=99)
    return GameConfig({"rouge": 5, "bleu": 5}, GameMode.LAST_SURVIVOR,
                      (Card("a", defeat), Card("b", defeat)))
