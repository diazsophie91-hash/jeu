"""Reproducible multi-agent game pilots and comparison campaigns."""

from .runner import AgentPolicy, GameRun, CampaignRun, run_game, run_campaign, SimulationError, SimulationLimitError
from .statistics import CampaignStatistics, summarize

__all__ = ["AgentPolicy", "GameRun", "CampaignRun", "run_game", "run_campaign",
           "SimulationError", "SimulationLimitError", "CampaignStatistics", "summarize"]
