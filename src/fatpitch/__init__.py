"""fatpitch: point-in-time process model and fidelity evaluation (PLAN.md, lift E).

Output is a process model, not any person's view; not affiliated with or endorsed by anyone named
in the source library.
"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("fatpitch")
except PackageNotFoundError:  # running from a source tree without install
    __version__ = "0.0.0+unknown"

from fatpitch.decision import SCHEMA_VERSION, Decision
from fatpitch.engine import evaluate
from fatpitch.lake import AmberLakeSource
from fatpitch.source import AmberSource, FixtureSource, Source

__all__ = [
    "SCHEMA_VERSION", "AmberLakeSource", "AmberSource", "Decision", "FixtureSource", "Source", "__version__",
    "evaluate",
]
