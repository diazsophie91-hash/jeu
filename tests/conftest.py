import pytest

from tests.helpers import build_game


@pytest.fixture
def game_factory():
    """Build an explicit invariant-checked test state and its public engine API."""
    return build_game
