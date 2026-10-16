"""Save reproducible campaign data and human-readable summaries using stdlib only."""
from __future__ import annotations

import csv
import hashlib
import dataclasses
import json
import math
import subprocess
from collections import defaultdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path


def to_jsonable(value):
    if dataclasses.is_dataclass(value):
        return {field.name: to_jsonable(getattr(value, field.name)) for field in dataclasses.fields(value)}
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict) or hasattr(value, "items"):
        return {str(key): to_jsonable(item) for key, item in value.items()}
    if isinstance(value, (tuple, list, set, frozenset)):
        return [to_jsonable(item) for item in value]
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return repr(value)


def _git_revision():
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                              text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def _git_metadata():
    try:
        status = subprocess.run(["git", "status", "--short", "--untracked-files=all"],
                                capture_output=True, text=True, check=True).stdout
        paths = subprocess.run(["git", "ls-files", "-co", "--exclude-standard"],
                               capture_output=True, text=True, check=True).stdout.splitlines()
    except (OSError, subprocess.CalledProcessError):
        return {"working_tree_dirty": None, "working_tree_status": None,
                "source_fingerprint_sha256": None}
    digest = hashlib.sha256()
    for relative in sorted(paths):
        normalized = relative.replace("\\", "/")
        if not normalized.endswith(".py") or not normalized.startswith(
                ("agents/", "engine/", "rules/", "simulation/")):
            continue
        path = Path(relative)
        if not path.is_file():
            continue
        digest.update(normalized.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return {"working_tree_dirty": bool(status.strip()), "working_tree_status": status.splitlines(),
            "source_fingerprint_sha256": digest.hexdigest()}


def _csv_write(path, rows, columns):
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def _ci_text(interval):
    if interval is None:
        return "n/a"
    return f"[{interval[0]:.3f}, {interval[1]:.3f}]"


def _paired_differences(campaign):
    """Paired gift-count comparisons for explicitly named controlled variants."""
    pairs = (
        ("succession-A", "succession-B"),
        ("donor-check-off", "donor-check-on"),
        ("refusal-draw-hidden", "refusal-draw-visible"),
        ("replay-draw-hidden", "replay-draw-visible"),
    )
    by_name = defaultdict(dict)
    for run in campaign.runs:
        base = run.configuration_name.split("::", 1)[0]
        by_name[base][run.seed] = run
    output = []
    for left, right in pairs:
        if left not in by_name or right not in by_name:
            continue
        common = sorted(set(by_name[left]) & set(by_name[right]))
        diffs = [by_name[right][seed].turns - by_name[left][seed].turns for seed in common]
        if not diffs:
            continue
        mean = sum(diffs) / len(diffs)
        if len(diffs) > 1:
            variance = sum((value - mean) ** 2 for value in diffs) / (len(diffs) - 1)
            margin = 1.96 * math.sqrt(variance / len(diffs))
            interval = (mean - margin, mean + margin)
        else:
            interval = None
        first_player = campaign.parameters.get("player_ids", (None,))[0]
        win_diffs = [int(first_player in by_name[right][seed].winners)
                     - int(first_player in by_name[left][seed].winners) for seed in common]
        win_mean = sum(win_diffs) / len(win_diffs)
        if len(win_diffs) > 1:
            win_variance = sum((value - win_mean) ** 2 for value in win_diffs) / (len(win_diffs) - 1)
            win_margin = 1.96 * math.sqrt(win_variance / len(win_diffs))
            win_interval = (win_mean - win_margin, win_mean + win_margin)
        else:
            win_interval = None
        output.append({"baseline": left, "variant": right, "paired_seeds": common,
                       "difference_mean_gifts_variant_minus_baseline": mean,
                       "difference_ci95_normal": interval,
                       "first_player_win_rate_difference": win_mean,
                       "first_player_win_difference_ci95_normal": win_interval,
                       "note": "Interval normal approximatif sur les différences appariées; descriptif, pas une preuve causale."})
    return output


def write_campaign(campaign, statistics, output_dir):
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=False)
    generated_at = datetime.now(timezone.utc).isoformat()
    records = {
        "generated_at_utc": generated_at,
        "git_revision": _git_revision(),
        "git": _git_metadata(),
        "parameters": to_jsonable(campaign.parameters),
        "statistics": to_jsonable(statistics),
        "completed_games": [to_jsonable(run) for run in campaign.runs],
        "failures": [to_jsonable(failure) for failure in campaign.failures],
        "paired_variant_comparisons": to_jsonable(_paired_differences(campaign)),
    }
    (output / "summary.json").write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")

    summary_rows = []
    for name, item in statistics.by_configuration.items():
        gift = item.get("gifts_proposed", {})
        early = item.get("early_eliminations", {})
        duration = item.get("simulation_seconds", {})
        summary_rows.append({
            "configuration_profile": name, "mode": item.get("mode"),
            "games_completed": item.get("games_completed"), "games_failed": item.get("games_failed", 0),
            "terminal_tie_games": item.get("terminal_tie_games", 0),
            "average_actions": item.get("actions", {}).get("mean"),
            "average_gifts": gift.get("mean"), "median_gifts": gift.get("median"),
            "p90_gifts": gift.get("p90"), "p95_gifts": gift.get("p95"),
            "min_gifts": gift.get("min"), "max_gifts": gift.get("max"),
            "average_rounds": item.get("rounds_played", {}).get("mean"),
            "average_simulation_seconds": duration.get("mean"),
            "early_eliminations": early.get("eliminated_early"),
            "early_elimination_denominator": early.get("player_round_denominator"),
            "early_elimination_rate": early.get("proportion_of_player_rounds"),
            "early_elimination_ci95": json.dumps(early.get("proportion_ci95")),
            "message_count": item.get("message_count"),
        })
    columns = ["configuration_profile", "mode", "games_completed", "games_failed", "terminal_tie_games",
               "average_actions", "average_gifts", "median_gifts", "p90_gifts", "p95_gifts", "min_gifts",
               "max_gifts", "average_rounds", "average_simulation_seconds", "early_eliminations",
               "early_elimination_denominator", "early_elimination_rate", "early_elimination_ci95",
               "message_count"]
    _csv_write(output / "summary.csv", summary_rows, columns)

    game_rows = []
    for run in campaign.runs:
        game_rows.append({
            "experience": run.experience_name, "configuration_profile": run.configuration_name,
            "simulation_index": run.simulation_index, "seed": run.seed, "status": run.status,
            "mode": run.configuration.get("mode"), "configuration_json": json.dumps(to_jsonable(run.configuration), ensure_ascii=False),
            "first_player_id": run.configuration.get("first_player_id"),
            "first_player_method": run.configuration.get("first_player_method"),
            "first_player_resolution": run.configuration.get("first_player_resolution"),
            "player_count": len(run.strategy_names), "strategies_json": json.dumps(to_jsonable(run.strategy_names), ensure_ascii=False),
            "communication_modes_json": json.dumps(to_jsonable(run.communication_modes), ensure_ascii=False),
            "agent_seeds_json": json.dumps(to_jsonable(run.agent_seeds), ensure_ascii=False),
            "actions": run.actions, "gifts_proposed": run.turns, "rounds_played": run.rounds,
            "rounds_completed": run.rounds_completed,
            "outcome": run.outcome, "winners_json": json.dumps(run.winners),
            "terminal_ties": run.terminal_ties, "score_ties": run.score_ties,
            "score_tiebreaks": run.score_tiebreaks,
            "messages": len(run.messages), "message_types_json": json.dumps(run.message_counts),
            "duration_seconds": run.duration_seconds, "diagnostic": "",
        })
    for failure in campaign.failures:
        base_name = failure.configuration_name.split("::", 1)[0]
        config = campaign.parameters.get("configurations", {}).get(base_name, {})
        game_rows.append({
            "experience": campaign.parameters.get("experience_name"),
            "configuration_profile": failure.configuration_name,
            "simulation_index": failure.simulation_index, "seed": failure.seed,
            "status": "failed", "mode": config.get("mode"),
            "configuration_json": json.dumps(to_jsonable(config), ensure_ascii=False),
            "player_count": len(campaign.parameters.get("player_ids", ())),
            "duration_seconds": failure.duration_seconds,
            "diagnostic": failure.error,
        })
    game_columns = ["experience", "configuration_profile", "simulation_index", "seed", "status", "mode",
                    "configuration_json", "first_player_id", "first_player_method", "first_player_resolution",
                    "player_count", "strategies_json", "communication_modes_json", "actions", "gifts_proposed",
                    "agent_seeds_json", "rounds_played", "rounds_completed", "outcome", "winners_json", "terminal_ties", "score_ties",
                    "score_tiebreaks", "messages",
                    "message_types_json", "duration_seconds", "diagnostic"]
    _csv_write(output / "games.csv", game_rows, game_columns)

    player_rows = []
    for run in campaign.runs:
        for player in run.players:
            player_rows.append({**to_jsonable(player),
                                "configuration_profile": run.configuration_name,
                                "simulation_index": run.simulation_index, "seed": run.seed,
                                "mode": run.configuration["mode"]})
    player_columns = ["configuration_profile", "simulation_index", "seed", "mode", "player_id", "position",
                      "round_number", "first_player", "round_starter_id", "card_id", "defeat_families",
                      "victory_condition", "decision_profile", "communication_profile", "result", "eliminated",
                      "elimination_turn", "elimination_game_turn", "elimination_reason", "turns_played",
                      "final_score", "credited_eliminations"]
    _csv_write(output / "players.csv", player_rows, player_columns)

    lines = [
        f"# Rapport de simulation — {campaign.parameters.get('experience_name', 'expérience')}", "",
        f"Campagne UTC : {generated_at}", f"Révision Git : {records['git_revision'] or 'indisponible'}", "",
        f"Arbre de travail modifié : {records['git']['working_tree_dirty']}; empreinte des sources : {records['git']['source_fingerprint_sha256']}", "",
        "## Définition des mesures", "",
        "`actions` compte les commandes légales soumises au moteur; `gifts_proposed` compte les propositions de cadeau et sert de numéro de tour; `rounds_played` compte les manches effectivement commencées. La durée est le temps informatique par partie, dépendant du matériel. Les éliminations précoces sont ici celles qui surviennent au plus tard au seuil expérimental configuré, par défaut les trois premiers cadeaux proposés.", "",
        "Les proportions indiquent leur dénominateur et un intervalle de Wilson à 95 %. Les intervalles des moyennes utilisent une approximation normale à 1,96 erreur standard. Les différences de variantes sont appariées par graine et utilisent un intervalle normal approximatif. Ces résumés sont descriptifs et ne démontrent pas de causalité.", "",
        "## Résultats par configuration et profil", "",
    ]
    for name, item in statistics.by_configuration.items():
        gifts = item.get("gifts_proposed", {})
        early = item.get("early_eliminations", {})
        lines.extend([
            f"### {name} — mode {item.get('mode', 'n/a')}", "",
            f"Parties terminées : {item.get('games_completed', 0)}; échecs : {item.get('games_failed', 0)}; résultats : `{item.get('outcomes', {})}`; égalités terminales : {item.get('terminal_tie_games', 0)}; victoires partagées : {item.get('shared_victory_games', 0)}.",
            f"Cadeaux proposés : moyenne {gifts.get('mean')}, médiane {gifts.get('median')}, p90 {gifts.get('p90')}, p95 {gifts.get('p95')}, min {gifts.get('min')}, max {gifts.get('max')}; manches moyennes : {item.get('rounds_played', {}).get('mean')}; secondes de simulation moyennes : {item.get('simulation_seconds', {}).get('mean')}.",
            f"Éliminations précoces (≤ {early.get('experimental_threshold_gifts', statistics.early_elimination_threshold)} cadeaux) : {early.get('eliminated_early', 0)} / {early.get('player_round_denominator', 0)} joueur-manches, taux {early.get('proportion_of_player_rounds')}, IC95 Wilson {_ci_text(early.get('proportion_ci95'))}; motifs : `{early.get('reason_counts', {})}`.",
            f"Messages : {item.get('message_count', 0)}; types : `{item.get('message_types', {})}`.",
            "",
            "| Carte | Attributions | Victoires du porteur | Éliminations | Tours moyens avant fin | Alerte échantillon |",
            "|---|---:|---:|---:|---:|---|",
        ])
        for card_id, card in item.get("cards", {}).items():
            mean_turns = card["mean_turns_before_end"].get("mean")
            lines.append(f"| {card_id} ({', '.join(card['families'])}) | {card['assignments']} | {card['wins_by_carrier']} | {card['eliminations']} | {mean_turns} | {'insuffisant (<30)' if card['insufficient_sample'] else '—'} |")
        lines.append("")
    paired = records["paired_variant_comparisons"]
    if paired:
        lines.extend(["## Comparaisons appariées de variantes", "",
                      "| Référence | Variante | Graines communes | Diff. cadeaux (IC95) | Diff. victoire joueur 1 (IC95) |",
                      "|---|---|---:|---|---|"])
        for item in paired:
            lines.append(f"| {item['baseline']} | {item['variant']} | {len(item['paired_seeds'])} | {item['difference_mean_gifts_variant_minus_baseline']:.3f} ({_ci_text(item['difference_ci95_normal'])}) | {item['first_player_win_rate_difference']:.3f} ({_ci_text(item['first_player_win_difference_ci95_normal'])}) |")
        lines.append("")
    lines.extend([
        "## Limites et interprétation", "",
        "Les configurations de cartes et seuils signalées dans `experimental_options` sont des benchmarks expérimentaux, pas des règles ni un paquet officiel. Les profils sont des politiques simples de comparaison et ne sont pas optimaux. Les fréquences sont conditionnelles aux configurations, graines, positions de départ et agents enregistrés. Une carte avec moins de 30 attributions est signalée comme insuffisamment observée; même au-delà, des taux semblables ou différents ne suffisent pas à établir l'équilibre ou une causalité.",
        "Les données des cartes et éliminations sont collectées par l'orchestrateur après la partie; elles ne sont pas fournies aux décisions des agents. Une simulation échouée est enregistrée comme échec sans ligne de joueur ni résultat inventé.", "",
        "Fichiers : `summary.json` contient les paramètres et parties terminées, `summary.csv` les agrégats, `games.csv` une ligne par partie terminée ou échouée, et `players.csv` une ligne par joueur et manche observée.",
    ])
    (output / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output
