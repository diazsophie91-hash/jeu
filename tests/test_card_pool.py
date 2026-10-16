import random

import pytest

from engine import create_game, start_new_round
from rules import Card, CardPool, Condition, ConditionKind, ConfigurationError, GameConfig, GameMode, PointsFormat


def valid_pool():
    red = Condition(ConditionKind.COLOR_COUNT, colors=("rouge",), threshold=99)
    total = Condition(ConditionKind.TOTAL_COUNT, threshold=99)
    cards = (Card("red-1", red), Card("red-2", red), Card("total-1", total), Card("total-2", total))
    return CardPool(cards, {ConditionKind.COLOR_COUNT: 2, ConditionKind.TOTAL_COUNT: 2})


def pool_config(pool, *, mode=GameMode.LAST_SURVIVOR, **options):
    return GameConfig({"rouge": 8, "bleu": 8}, mode, card_pool=pool, **options)


def test_t55_valid_sufficient_pool_distributes_unique_compatible_cards():
    pool = valid_pool()
    pool.validate_for(3)
    selected = pool.draw(3, random.Random(12))
    assert len(selected) == 3
    assert len({card.id for card in selected}) == 3
    config = pool_config(pool)
    game = create_game(["a", "b", "c"], config, seed=12, first_player_id="a")
    assert len(game._state.config.cards) == 3
    assert {card.id for card in game._state.config.cards} <= {card.id for card in pool.cards}


def test_t55_insufficient_pool_is_rejected_before_setup():
    with pytest.raises(ConfigurationError, match="Réserve insuffisante"):
        create_game(["a", "b", "c", "d", "e"], pool_config(valid_pool()), seed=1, first_player_id="a")


def test_t55_duplicate_card_ids_are_rejected():
    card = Card("same", Condition(ConditionKind.TOTAL_COUNT, threshold=99))
    with pytest.raises(ValueError, match="identifiants.*uniques"):
        CardPool((card, card), {ConditionKind.TOTAL_COUNT: 2})


def test_t55_mode_incompatible_pool_card_is_rejected():
    with pytest.raises(ConfigurationError, match="incompatible avec le mode"):
        pool_config(valid_pool(), mode=GameMode.SECRET_OBJECTIVE).validate(2)


def test_t55_invalid_contradictory_card_in_pool_is_rejected():
    same = Condition(ConditionKind.COLOR_COUNT, colors=("rouge",), threshold=1)
    pool = CardPool((Card("a", same, same), Card("b", same)), {ConditionKind.COLOR_COUNT: 2})
    with pytest.raises(ConfigurationError, match="gagner et perdre simultanément"):
        pool_config(pool, mode=GameMode.SECRET_OBJECTIVE).validate(2)


def test_t55_declared_reserve_composition_is_checked():
    cards = (Card("a", Condition(ConditionKind.TOTAL_COUNT, threshold=99)),
             Card("b", Condition(ConditionKind.TOTAL_COUNT, threshold=98)))
    with pytest.raises(ValueError, match="Composition de réserve invalide"):
        CardPool(cards, {ConditionKind.COLOR_COUNT: 2})


def test_t55_same_seed_reproduces_card_selection_and_initial_deal():
    config = pool_config(valid_pool())
    def snapshot():
        game = create_game(["a", "b"], config, seed=431, first_player_id="a")
        return (tuple(card.id for card in game._state.config.cards),
                tuple(tuple(token.color for token in p.hand) for p in game._state.players))
    assert snapshot() == snapshot()


def test_t55_distribution_never_duplicates_a_card():
    pool = valid_pool()
    for seed in range(10):
        cards = pool.draw(4, random.Random(seed))
        assert len({card.id for card in cards}) == 4


def test_t55_explicit_card_injection_remains_supported():
    cards = (Card("a", Condition(ConditionKind.TOTAL_COUNT, threshold=99)),
             Card("b", Condition(ConditionKind.TOTAL_COUNT, threshold=99)))
    game = create_game(["a", "b"], GameConfig({"rouge": 4, "bleu": 4}, GameMode.LAST_SURVIVOR, cards),
                       seed=4, first_player_id="a")
    assert {card.id for card in game._state.config.cards} == {"a", "b"}
    assert game._state.card_pool is None


def test_t55_new_round_draws_a_fresh_unique_selection_from_the_configured_pool():
    config = pool_config(valid_pool(), mode=GameMode.POINTS,
                         points_format=PointsFormat.FIXED_ROUNDS, fixed_rounds=2,
                         elimination_threshold=9, initial_hand_size=1)
    game = create_game(["a", "b"], config, seed=91, first_player_id="a")
    assert game._state.card_pool is not None
    game._finish_round("a")
    start_new_round(game, "b")
    active_cards = game._state.config.cards
    assert game._state.round_number == 2
    assert len(active_cards) == 2 and len({card.id for card in active_cards}) == 2
    assert {card.id for card in active_cards} <= {card.id for card in valid_pool().cards}
    game.assert_invariants()
