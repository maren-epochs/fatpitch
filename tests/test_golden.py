"""The default test harness blocks the network and freezes the clock."""

import socket

import golden
import pytest

from fatpitch import dates


def test_network_blocked_by_default():
    with pytest.raises(golden.NetworkBlocked):
        socket.create_connection(("127.0.0.1", 9), timeout=0.1)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        with pytest.raises(golden.NetworkBlocked):
            s.connect(("127.0.0.1", 9))
    finally:
        s.close()
    with pytest.raises(golden.NetworkBlocked):
        socket.getaddrinfo("example.com", 80)


def test_clock_frozen():
    assert dates.today() == golden.TODAY
