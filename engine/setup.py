"""Reproducible setup and round initialization."""
from __future__ import annotations

import random
from dataclasses import replace
from itertools import combinations
from rules.cards import Token, condition_matches
from rules.config import GameConfig, GameMode, ConfigurationError, _complete_setup_possible
from rules.rules import evaluate_defeat_conditions
from .state import GameState, PlayerState, Phase


class SetupError(RuntimeError):
    """A valid game cannot be dealt from this particular accepted draw sequence."""


def create_game(player_ids: list[str] | tuple[str, ...], config: GameConfig, seed: int | None = None,
                first_player_id: str | None = None, rng: random.Random | None = None,
                first_player_method: str | None = None,
                first_player_resolution: str | None = None,
                first_player_tied_candidates: tuple[str, ...] = ()) -> "GameEngine":
    from .transitions import GameEngine
    ids = tuple(player_ids)
    if len(ids) != len(set(ids)) or any(not p for p in ids):
        raise ConfigurationError("Les identifiants des joueurs doivent être uniques et non vides.")
    config.validate(len(ids))
    if first_player_id is None:
        raise ConfigurationError("Le premier joueur doit être désigné par le groupe et fourni à la mise en place.")
    if rng is not None and seed is not None:
        raise ConfigurationError("Fournissez une graine ou un générateur aléatoire, pas les deux.")
    rng = rng if rng is not None else random.Random(seed)
    cards = list(config.card_pool.draw_usable(len(ids), rng, config.colors, config.mode,
                                               config.initial_hand_size)
                 if config.card_pool is not None else config.cards)
    if config.card_pool is None:
        rng.shuffle(cards)
    active_config = replace(config, cards=tuple(cards), card_pool=None) if config.card_pool is not None else config
    active_config.validate(len(ids))
    tokens = [Token(f"t{i:04d}", color) for i, color in enumerate(
        color for color, n in config.colors.items() for _ in range(n))]
    rng.shuffle(tokens)
    players = [PlayerState(pid, card=cards[i]) for i, pid in enumerate(ids)]
    allocation, bag = _deal_valid_hands(players, tokens, active_config, rng,
                                        ensure_feasible=config.card_pool is not None)
    for player, hand in zip(players, allocation):
        player.hand.extend(hand)
    active = first_player_id
    if active not in ids:
        raise ConfigurationError("Le premier joueur doit participer à la partie.")
    state = GameState(active_config, players, bag, active, Phase.CHOOSE_RECIPIENT, card_pool=config.card_pool)
    state.emit("game_started", public_data={"player_ids": ids, "mode": config.mode.value},
               player_ids=ids, mode=config.mode.value, seed=seed)
    state.emit("first_player_selected", player_id=active,
               method=first_player_method or "direct_input",
               resolution=first_player_resolution or "direct",
               tied_candidates=tuple(first_player_tied_candidates))
    state.emit("round_started", first_player_id=active, round_number=1)
    for player in players:
        state.emit("initial_tokens_drawn",
                   public_data={"player_id": player.id, "count": len(player.hand)},
                   player_id=player.id, tokens=tuple((t.id, t.color) for t in player.hand))
    state.assert_invariants()
    return GameEngine(state, rng)


def _deal_valid_hands(players, tokens, config, rng, *, ensure_feasible=False):
    """Deal one hand at a time; rejected hands return to the opaque common bag."""
    common = list(tokens)
    rng.shuffle(common)
    hands = []
    for index, player in enumerate(players):
        accepted = False
        for _ in range(config.max_setup_attempts):
            if len(common) < config.initial_hand_size:
                raise SetupError("La préparation est devenue impossible : le sac ne contient plus assez de jetons pour un joueur restant.")
            drawn = rng.sample(common, config.initial_hand_size)
            draw_ids = {t.id for t in drawn}
            remaining = [t for t in common if t.id not in draw_ids]
            counts = {c: sum(t.color == c for t in drawn) for c in config.colors}
            defeat_results = evaluate_defeat_conditions(player.card, drawn)
            invalid = any(defeat_results) or (
                config.mode is GameMode.SECRET_OBJECTIVE and condition_matches(player.card.victory, counts))
            if invalid:
                common = remaining + drawn
                rng.shuffle(common)
                continue
            remaining_stock = {c: sum(t.color == c for t in remaining) for c in config.colors}
            if not _complete_setup_possible([p.card for p in players[index+1:]], remaining_stock,
                                            config.mode, config.initial_hand_size):
                if not ensure_feasible:
                    raise SetupError("La mise en place s'arrête : les collections déjà tirées ne laissent aucune distribution complète valide.")
                common = remaining + drawn
                rng.shuffle(common)
                continue
            hands.append(drawn)
            common = remaining
            accepted = True
            break
        if not accepted and ensure_feasible:
            remaining_cards = [p.card for p in players[index+1:]]
            feasible_hands = []
            for candidate in combinations(common, config.initial_hand_size):
                counts = {c: sum(t.color == c for t in candidate) for c in config.colors}
                if any(evaluate_defeat_conditions(player.card, candidate)) or (
                    config.mode is GameMode.SECRET_OBJECTIVE
                    and condition_matches(player.card.victory, counts)
                ):
                    continue
                candidate_ids = {t.id for t in candidate}
                remaining = [t for t in common if t.id not in candidate_ids]
                remaining_stock = {c: sum(t.color == c for t in remaining) for c in config.colors}
                if _complete_setup_possible(remaining_cards, remaining_stock, config.mode,
                                            config.initial_hand_size):
                    feasible_hands.append(candidate)
            if feasible_hands:
                drawn = feasible_hands[rng.randrange(len(feasible_hands))]
                draw_ids = {t.id for t in drawn}
                hands.append(list(drawn))
                common = [t for t in common if t.id not in draw_ids]
                accepted = True
        if not accepted:
            raise SetupError(f"La mise en place s'arrête après {config.max_setup_attempts} tirages invalides pour un joueur ; aucune carte ni condition n'a été révélée.")
    return hands, common


def start_new_round(engine: "GameEngine", first_player_id: str | None = None) -> None:
    engine._start_new_round(first_player_id)
