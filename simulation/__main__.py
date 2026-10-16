"""Command-line entry point: ``py -m simulation``."""
from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

from agents import RandomDecision, ReferenceDecision
from .runner import AgentPolicy
from rules import GameMode
from .experiments import (benchmark_config, communication_profiles, decision_profiles,
                         mixed_profiles, reference_configurations, variant_configurations)
from .reporting import write_campaign
from .runner import run_campaign
from .statistics import summarize


DECISIONS = ("deterministic", "random", "cautious", "always_accept", "always_refuse")
COMMUNICATIONS = ("silent", "truthful", "bluff", "questioning", "mixed")


def _parser():
    parser = argparse.ArgumentParser(prog="py -m simulation",
        description="Lance des campagnes reproductibles pour C'est cadeau !")
    commands = parser.add_subparsers(dest="command", required=True)
    run = commands.add_parser("run", help="lancer une expérience et enregistrer ses résultats")
    run.add_argument("--suite", choices=("reference", "variants", "agents", "cards"), default="reference")
    run.add_argument("--games", type=int, default=3, help="parties par configuration et profil (défaut rapide : 3)")
    run.add_argument("--seed", type=int, default=20261016, help="première graine; les suivantes sont consécutives")
    run.add_argument("--players", type=int, choices=range(2, 5), default=4)
    run.add_argument("--decision-profile", choices=("suite", *DECISIONS), default="suite")
    run.add_argument("--communication-profile", choices=("suite", *COMMUNICATIONS), default="suite")
    run.add_argument("--early-threshold", type=int, default=3,
                     help="seuil expérimental en cadeaux proposés (défaut : trois)")
    run.add_argument("--max-actions", type=int, default=1000)
    run.add_argument("--output", type=Path, help="dossier neuf de sortie; défaut reports/simulations/<nom-horodatage>")
    run.add_argument("--continue-on-error", action="store_true",
                     help="enregistrer les échecs et poursuivre; par défaut, arrêter au premier échec")
    run.add_argument("--experiment-name", default=None)
    return parser


def _selected_profiles(args, player_ids):
    if args.decision_profile == "suite" and args.communication_profile == "suite":
        if args.suite == "agents":
            profiles = decision_profiles(player_ids)
            profiles.update(communication_profiles(player_ids))
            profiles.update(mixed_profiles(player_ids))
            return profiles
        if args.suite == "cards":
            return {"card-balance-seeded-random": {
                pid: AgentPolicy(RandomDecision()) for pid in player_ids}}
        return {"deterministic-reference": {
            pid: AgentPolicy(ReferenceDecision()) for pid in player_ids}}
    decision_names = DECISIONS if args.decision_profile == "suite" else (args.decision_profile,)
    communication_names = COMMUNICATIONS if args.communication_profile == "suite" else (args.communication_profile,)
    profiles = {}
    for decision in decision_names:
        for communication in communication_names:
            name = f"{decision}+{communication}"
            profiles[name] = {}
            for pid in player_ids:
                from .experiments import _make_policy
                profiles[name][pid] = _make_policy(decision, communication)
    return profiles


def main(argv=None):
    args = _parser().parse_args(argv)
    if args.command != "run":
        return 2
    if args.games < 1 or args.max_actions < 1 or args.early_threshold < 0:
        _parser().error("--games et --max-actions doivent être positifs; --early-threshold doit être positif ou nul")
    player_ids = tuple(f"joueur-{index + 1}" for index in range(args.players))
    if args.suite == "reference":
        configurations = reference_configurations()
    elif args.suite == "variants":
        configurations = variant_configurations()
    elif args.suite == "agents":
        configurations = {"mode-A-agents": benchmark_config(GameMode.LAST_SURVIVOR)}
    else:
        configurations = {"mode-A-card-balance": benchmark_config(GameMode.LAST_SURVIVOR)}
    for name, config in configurations.items():
        try:
            config.validate(args.players)
        except Exception as exc:
            raise SystemExit(f"Configuration expérimentale invalide ({name}) : {exc}") from exc
    profiles = _selected_profiles(args, player_ids)
    seeds = tuple(args.seed + index for index in range(args.games))
    experience_name = args.experiment_name or f"point4-{args.suite}"
    planned = len(configurations) * len(profiles) * len(seeds)
    interval = max(1, planned // 20)

    def progress(done, total, completed, failures):
        if done == total or done % interval == 0:
            print(f"Progression {done}/{total} — terminées {completed}, échecs {failures}", flush=True)

    print(f"Expérience {experience_name}: {planned} parties prévues; graines {seeds[0]}–{seeds[-1]}.", flush=True)
    try:
        campaign = run_campaign(configurations, player_ids, seeds=seeds,
                                policy_profiles=profiles, max_actions=args.max_actions,
                                continue_on_error=args.continue_on_error,
                                experience_name=experience_name, progress_callback=progress)
    except Exception as exc:
        print(f"Campagne interrompue: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    statistics = summarize(campaign, early_threshold=args.early_threshold)
    output = args.output or (Path("reports") / "simulations" /
                             f"{experience_name}-{datetime.now().strftime('%Y%m%d-%H%M%S')}")
    try:
        output = write_campaign(campaign, statistics, output)
    except FileExistsError:
        print(f"Le dossier de sortie existe déjà : {output}", file=sys.stderr)
        return 2
    completed = len(campaign.runs)
    failures = len(campaign.failures)
    print(f"Campagne terminée — prévues {planned}, lancées {completed + failures}, "
          f"terminées {completed}, échecs {failures}.")
    for failure in campaign.failures[:5]:
        print(f"Échec {failure.configuration_name} graine {failure.seed}: {failure.error}")
    print(f"Résultats : {output.resolve()}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
