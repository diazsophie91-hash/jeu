import pytest

from rules import Card, Condition, ConditionKind, ConfigurationError, GameConfig, GameMode, MajorityBasis
from rules.cards import condition_matches
from tests.helpers import safe_card


@pytest.mark.parametrize("exact,expected", [(False, [False, True, True]), (True, [False, True, False])])
def test_t12_color_threshold_below_at_and_above(exact, expected):
    condition = Condition(ConditionKind.COLOR_COUNT, colors=("rouge",), threshold=2, exact=exact)
    assert [condition_matches(condition, {"rouge": n}) for n in (1, 2, 3)] == expected


@pytest.mark.parametrize("exact,expected", [(False, [True, True]), (True, [True, False])])
def test_t13_two_pairs_explicit_colors_exact_and_minimum(exact, expected):
    condition = Condition(ConditionKind.TWO_PAIRS, colors=("rouge", "bleu"), exact=exact)
    assert [condition_matches(condition, counts) for counts in (
        {"rouge": 2, "bleu": 2}, {"rouge": 3, "bleu": 2},
    )] == expected


def test_t13_two_pairs_any_distinct_colors_and_imposed_colors():
    any_two = Condition(ConditionKind.TWO_PAIRS)
    imposed = Condition(ConditionKind.TWO_PAIRS, colors=("rouge", "bleu"))
    counts = {"rouge": 0, "bleu": 2, "vert": 2}
    assert condition_matches(any_two, counts)
    assert not condition_matches(imposed, counts)


@pytest.mark.parametrize("exact,expected", [(False, [False, True, True]), (True, [False, True, False])])
def test_t14_total_count_counts_all_colors(exact, expected):
    condition = Condition(ConditionKind.TOTAL_COUNT, threshold=3, exact=exact)
    collections = ({"rouge": 1, "bleu": 1}, {"rouge": 1, "bleu": 2}, {"rouge": 2, "bleu": 2})
    assert [condition_matches(condition, counts) for counts in collections] == expected


def test_t22_and_t55_cards_must_match_selected_mode_and_player_count():
    defeat = Condition(ConditionKind.TOTAL_COUNT, threshold=99)
    objective = Condition(ConditionKind.COLOR_COUNT, colors=("bleu",), threshold=2)
    no_objective_cards = (safe_card("a", defeat=defeat), safe_card("b", defeat=defeat))
    GameConfig({"rouge": 4, "bleu": 4}, GameMode.LAST_SURVIVOR, no_objective_cards).validate(2)
    with pytest.raises(ConfigurationError, match="incompatible avec le mode"):
        GameConfig({"rouge": 4, "bleu": 4}, GameMode.LAST_SURVIVOR,
                   (safe_card("a", defeat=defeat, victory=objective), no_objective_cards[1])).validate(2)
    with pytest.raises(ConfigurationError, match="exactement une carte par joueur"):
        GameConfig({"rouge": 4, "bleu": 4}, GameMode.LAST_SURVIVOR, (no_objective_cards[0],)).validate(2)


def test_t22_unknown_color_and_unconfigured_majority_are_rejected():
    unknown = Condition(ConditionKind.COLOR_COUNT, colors=("violet",), threshold=2)
    config = GameConfig({"rouge": 6}, GameMode.LAST_SURVIVOR,
                        (safe_card("a", defeat=unknown), safe_card("b", defeat=unknown)))
    with pytest.raises(ConfigurationError, match="couleur absente"):
        config.validate(2)

    majority = Condition(ConditionKind.MAJORITY, colors=("rouge",), minimum=1,
                         majority_basis=MajorityBasis.PLURALITY)
    GameConfig({"rouge": 4, "bleu": 4}, GameMode.SECRET_OBJECTIVE,
               (Card("a", Condition(ConditionKind.TOTAL_COUNT, threshold=99), majority),
                Card("b", Condition(ConditionKind.TOTAL_COUNT, threshold=99), majority))).validate(2)


def test_t22_unknown_condition_kind_and_bad_parameter_types_fail_at_construction():
    with pytest.raises(ValueError, match="Type de condition invalide"):
        Condition("unregistered-kind")
    with pytest.raises(ValueError, match="seuil.*entier"):
        Condition(ConditionKind.COLOR_COUNT, colors=("rouge",), threshold="three")


def test_t55_insufficient_stock_and_impossible_initial_collection_are_rejected():
    with pytest.raises(ConfigurationError, match="moins de trois jetons par joueur"):
        GameConfig({"rouge": 5}, GameMode.LAST_SURVIVOR,
                   (safe_card("a"), safe_card("b"))).validate(2)

    red_triplet = Condition(ConditionKind.COLOR_COUNT, colors=("rouge",), threshold=1)
    impossible = GameConfig({"rouge": 3, "bleu": 3}, GameMode.LAST_SURVIVOR,
                            (safe_card("a", defeat=red_triplet), safe_card("b", defeat=red_triplet)))
    with pytest.raises(ConfigurationError, match="Aucune attribution complète"):
        impossible.validate(2)


def test_t78_reference_values_are_scenario_values_not_engine_constants():
    eight = GameConfig({"rouge": 10, "bleu": 10, "vert": 10, "jaune": 10},
                       GameMode.LAST_SURVIVOR, tuple(safe_card(f"c{i}") for i in range(8)))
    other = GameConfig({"rouge": 5, "bleu": 7}, GameMode.LAST_SURVIVOR,
                       tuple(safe_card(f"x{i}") for i in range(3)))
    eight.validate(8)
    other.validate(3)
    assert sum(eight.colors.values()) == 40 and len(eight.cards) == 8
    assert sum(other.colors.values()) == 12 and len(other.cards) == 3
