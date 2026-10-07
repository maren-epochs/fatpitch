"""Test harness: frozen clock and blocked network.

Ported from multi-strategy ``tests/golden.py``. Kept: the frozen "today" and the socket block.
Stripped: the CBP golden-master fixture (price cache, NAREIT/Shiller/World Bank downloads,
pandas_datareader recording, engine run comparison) — fund-specific; fatpitch golden fixtures
will be added when an engine exists (E3+).

``offline()`` pins ``fatpitch.dates.today()`` to ``TODAY`` and makes every outbound connection and
DNS lookup raise. ``tests/conftest.py`` applies it to every test by default; a test marked
``@pytest.mark.allow_network`` opts out.
"""

from __future__ import annotations

import contextlib
import datetime as _dt
import socket

TODAY = _dt.date(2026, 10, 6)


class NetworkBlocked(RuntimeError):
    pass


def _blocked(*_a, **_k):
    raise NetworkBlocked("network access blocked in tests (tests/golden.py)")


@contextlib.contextmanager
def offline(today: _dt.date | None = TODAY):
    """Block the network; freeze ``fatpitch.dates.today()`` when ``today`` is not None."""
    from fatpitch import dates

    patches: list[tuple[object, str, object]] = []

    def setattr_(obj, name, val):
        patches.append((obj, name, getattr(obj, name)))
        setattr(obj, name, val)

    real_socket = socket.socket

    class _NoNet(real_socket):
        def connect(self, *a, **k):
            _blocked()

        def connect_ex(self, *a, **k):
            _blocked()

    setattr_(socket, "socket", _NoNet)
    setattr_(socket, "create_connection", _blocked)
    setattr_(socket, "getaddrinfo", _blocked)
    if today is not None:
        setattr_(dates, "today", lambda: today)
    try:
        yield
    finally:
        for obj, name, val in reversed(patches):
            setattr(obj, name, val)
