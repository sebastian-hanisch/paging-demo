"""Gemeinsame Fixtures: die Mini-Instanz, an der jede Einheit von Hand geprüft wird (DEMO-PLAYBOOK §1b)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


@pytest.fixture
def mini():
    """Zwei Plätze, drei Seiten, Folge a b c a b c (als 0 1 2 0 1 2).

    Handrechnung: LRU, FIFO und LFU fehlen bei jeder Anfrage (6 Fehler). Das Optimum: a, b, c fehlen (3 Fehler), bei c fliegt b, weil b nach a
    am spätesten wiederkommt; a trifft; b fehlt (a fliegt, es kommt nie wieder), c trifft: 4 Fehler."""
    return [0, 1, 2, 0, 1, 2], 2
