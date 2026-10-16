"""Rules and configurable card definitions for C'est cadeau !."""

from .cards import Card, Condition, ConditionKind, MajorityBasis, Token
from .config import GameConfig, GameMode, Succession, PointsFormat, ConfigurationError

__all__ = ["Card", "Condition", "ConditionKind", "MajorityBasis", "Token", "GameConfig", "GameMode", "Succession", "PointsFormat", "ConfigurationError"]
