"""Shared test setup: every test runs offline with a frozen clock (tests/golden.py)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import golden


def pytest_configure(config):
    config.addinivalue_line("markers", "allow_network: opt out of the default network block")


@pytest.fixture(autouse=True)
def _offline(request):
    if request.node.get_closest_marker("allow_network"):
        yield
        return
    with golden.offline():
        yield
