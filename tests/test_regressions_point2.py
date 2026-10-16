"""Focused deterministic regressions for the point 2 engine corrections."""
import random
import unittest

from engine import AcceptGift, ChooseRecipient, GameEngine, ProposeGift
from engine.state import GameState, Phase, PlayerState
from rules import (
    Card,
    Condition,
    ConditionKind,
    ConfigurationError,
    GameConfig,
    GameMode,
    PointsFormat,
    Succession,
    Token,
)
from rules.cards import condition_matches
from rules.config import _conditions_overlap


def card(card_id, defeat, victory=None):
    return Card(card_id, defeat, victory)


def points_config(cards, stock, *, threshold=10, donor_defeat_after_removal=False):
    return GameConfig(
        stock,
        GameMode.POINTS,
        tuple(cards),
        succession=Succession.CLOCKWISE,
        points_format=PointsFormat.FIXED_ROUNDS,
        elimination_threshold=threshold,
        donor_defeat_after_removal=donor_defeat_after_removal,
        fixed_rounds=3,
        bonus_points=1,
        initial_hand_size=1,
    )


class ConditionValidationTests(unittest.TestCase):
    def test_repeated_candidate_colors_are_rejected_by_configuration(self):
        cases = (
            Condition(ConditionKind.TWO_PAIRS, colors=("rouge", "rouge")),
            Condition(ConditionKind.EQUAL_COUNTS, colors=("rouge", "rouge"), minimum=1),
            Condition(ConditionKind.DIVERSITY, colors=("rouge", "bleu", "rouge"), minimum=2),
        )
        for condition in cases:
            with self.subTest(kind=condition.kind):
                config = GameConfig(
                    {"rouge": 4, "bleu": 4}, GameMode.LAST_SURVIVOR,
                    (card("a", condition), card("b", condition)),
                )
                with self.assertRaisesRegex(ConfigurationError, "répète une couleur"):
                    config.validate(2)

    def test_majority_rejects_multiple_target_colors(self):
        from rules import MajorityBasis

        majority = Condition(
            ConditionKind.MAJORITY,
            colors=("rouge", "bleu"),
            minimum=1,
            majority_basis=MajorityBasis.PLURALITY,
        )
        config = GameConfig(
            {"rouge": 4, "bleu": 4}, GameMode.LAST_SURVIVOR,
            (card("a", majority), card("b", majority)),
        )
        with self.assertRaisesRegex(ConfigurationError, "incomplète ou invalide"):
            config.validate(2)

    def test_diversity_counts_minimum_present_candidates_and_enforces_cap(self):
        condition = Condition(
            ConditionKind.DIVERSITY,
            colors=("rouge", "bleu", "vert"),
            minimum=2,
        )
        self.assertTrue(condition_matches(condition, {"rouge": 1, "bleu": 1, "vert": 0}))
        self.assertFalse(condition_matches(condition, {"rouge": 1, "bleu": 0, "vert": 0}))
        self.assertTrue(condition_matches(condition, {"rouge": 1, "bleu": 1, "violet": 5}))

        capped = Condition(
            ConditionKind.DIVERSITY,
            colors=("rouge", "bleu", "vert"),
            minimum=2,
            max_per_color=2,
        )
        self.assertFalse(condition_matches(capped, {"rouge": 3, "bleu": 1, "vert": 0}))

    def test_diversity_rejects_minimum_larger_than_candidate_set(self):
        condition = Condition(ConditionKind.DIVERSITY, colors=("rouge", "bleu"), minimum=3)
        config = GameConfig(
            {"rouge": 4, "bleu": 4}, GameMode.LAST_SURVIVOR,
            (card("a", condition), card("b", condition)),
        )
        with self.assertRaisesRegex(ConfigurationError, "incomplète ou invalide"):
            config.validate(2)

    def test_overlap_uses_physical_stock_bounds(self):
        defeat = Condition(ConditionKind.TOTAL_COUNT, threshold=4)
        victory = Condition(ConditionKind.COLOR_COUNT, colors=("rouge",), threshold=2)

        # Only one red exists, so the nominal overlap cannot occur physically.
        self.assertFalse(_conditions_overlap(defeat, victory, {"rouge": 1, "bleu": 5}))
        cards = (card("a", defeat, victory), card("b", defeat, victory))
        GameConfig({"rouge": 1, "bleu": 5}, GameMode.SECRET_OBJECTIVE, cards).validate(2)

        # Two red and two blue satisfy both conditions within this stock.
        self.assertTrue(_conditions_overlap(defeat, victory, {"rouge": 3, "bleu": 3}))
        cards = (card("a", defeat, victory), card("b", defeat, victory))
        with self.assertRaisesRegex(ConfigurationError, "gagner et perdre simultanément"):
            GameConfig({"rouge": 3, "bleu": 3}, GameMode.SECRET_OBJECTIVE, cards).validate(2)


class SuccessionRegressionTests(unittest.TestCase):
    def test_variant_b_stops_at_last_survivor_and_awards_expected_points_and_bonus(self):
        cards = (
            card("a", Condition(ConditionKind.COLOR_COUNT, colors=("rouge",), threshold=1)),
            card("b", Condition(ConditionKind.COLOR_COUNT, colors=("rouge",), threshold=3)),
            card("c", Condition(ConditionKind.COLOR_COUNT, colors=("bleu",), threshold=99)),
            card("d", Condition(ConditionKind.COLOR_COUNT, colors=("bleu",), threshold=99)),
        )
        config = points_config(cards, {"rouge": 4, "bleu": 3}, donor_defeat_after_removal=True)
        players = [
            PlayerState("a", [Token("r0", "rouge"), Token("r1", "rouge")], cards[0]),
            PlayerState("b", [Token("r2", "rouge"), Token("r3", "rouge")], cards[1]),
            PlayerState("c", [], cards[2]),
            PlayerState("d", [], cards[3]),
        ]
        state = GameState(
            config, players,
            [Token(f"b{i}", "bleu") for i in range(3)],
            "a", Phase.CHOOSE_RECIPIENT,
        )
        game = GameEngine(state, random.Random(7))

        game.submit(ChooseRecipient("b"))
        game.submit(ProposeGift("r0"))  # A is eliminated after the removal.
        game.submit(AcceptGift())       # B is eliminated; C is forced out; D remains.

        self.assertEqual(game.phase, Phase.ROUND_OVER)
        self.assertEqual(state.round_winner, "d")
        self.assertEqual(state.player("d").score, 1)  # Last-survivor round bonus.
        self.assertEqual(state.player("a").score, 2)  # B and C eliminations are credited.
        self.assertEqual(state.player("a").credited_eliminations, 2)
        self.assertTrue(state.player("d").alive)
        self.assertEqual(sum(p.alive for p in state.players), 1)
        state.assert_invariants()

    def test_initial_resolution_eliminating_everyone_is_terminal_tie_without_awards(self):
        cards = (
            card("a", Condition(ConditionKind.COLOR_COUNT, colors=("rouge",), threshold=1)),
            card("b", Condition(ConditionKind.COLOR_COUNT, colors=("rouge",), threshold=2)),
        )
        config = points_config(cards, {"rouge": 3}, threshold=1, donor_defeat_after_removal=True)
        players = [
            PlayerState("a", [Token("r0", "rouge"), Token("r1", "rouge")], cards[0]),
            PlayerState("b", [Token("r2", "rouge")], cards[1]),
        ]
        state = GameState(config, players, [], "a", Phase.CHOOSE_RECIPIENT)
        game = GameEngine(state, random.Random(11))

        game.submit(ChooseRecipient("b"))
        game.submit(ProposeGift("r0"))
        game.submit(AcceptGift())

        self.assertEqual(game.phase, Phase.GAME_OVER)
        self.assertEqual(state.result, "terminal_tie")
        self.assertEqual(state.winners, ())
        self.assertTrue(all(not p.alive for p in state.players))
        self.assertTrue(all(p.score == 0 and p.credited_eliminations == 0 for p in state.players))
        self.assertIsNone(state.active_player_id)
        state.assert_invariants()


if __name__ == "__main__":
    unittest.main()
