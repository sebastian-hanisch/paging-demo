"""Kern: Paging mit k Plätzen. Jede Regel liefert je Anfrage ein Fehler-Flag (1 = Seite fehlte, Nachschub kostet 1).

Optional sammelt `trace` den Speicherinhalt nach jeder Anfrage (nur für die Ablauftabelle der ersten Anfragen).
Belady ist das Optimum mit Vorwissen: verdränge die Seite, die am spätesten wieder angefragt wird."""

from collections import OrderedDict, deque

import numpy as np


def run_lru(seq, k, trace=None):
    cache: OrderedDict = OrderedDict()
    flags = []
    for p in seq:
        if p in cache:
            cache.move_to_end(p)
            flags.append(0)
        else:
            flags.append(1)
            if len(cache) == k:
                cache.popitem(last=False)
            cache[p] = True
        if trace is not None:
            trace.append(sorted(cache))
    return flags


def run_fifo(seq, k, trace=None):
    cache, order, flags = set(), deque(), []
    for p in seq:
        if p in cache:
            flags.append(0)
        else:
            flags.append(1)
            if len(cache) == k:
                cache.discard(order.popleft())
            cache.add(p)
            order.append(p)
        if trace is not None:
            trace.append(sorted(cache))
    return flags


def run_lfu(seq, k, trace=None):
    """Verdränge die Seite mit den wenigsten Anfragen seit dem Laden; bei Gleichstand die am längsten nicht angefragte."""
    cache, count, last, flags = set(), {}, {}, []
    for t, p in enumerate(seq):
        if p in cache:
            flags.append(0)
        else:
            flags.append(1)
            if len(cache) == k:
                cache.discard(min(cache, key=lambda q: (count[q], last[q])))
            cache.add(p)
            count[p] = 0
        count[p] += 1
        last[p] = t
        if trace is not None:
            trace.append(sorted(cache))
    return flags


def run_marking(seq, k, rng, trace=None):
    """Marking mit Zufall: je Phase werden angefragte Seiten gemerkt; bei einem Fehler fliegt eine zufällige nicht gemerkte Seite.
    Sind alle gemerkt, beginnt eine neue Phase (alle Marken fallen)."""
    cache, marked, flags = set(), set(), []
    un: list = []                       # nicht gemerkte Seiten im Speicher
    pos: dict = {}                      # Seite -> Index in `un`

    def drop(p):
        i = pos.pop(p)
        last = un.pop()
        if last != p:
            un[i] = last
            pos[last] = i

    for p in seq:
        if p in cache:
            flags.append(0)
            if p in pos:
                drop(p)
                marked.add(p)
        else:
            flags.append(1)
            if len(cache) == k:
                if not un:
                    marked.clear()
                    un.extend(cache)
                    pos.clear()
                    pos.update({q: i for i, q in enumerate(un)})
                victim = un[int(rng.integers(len(un)))]
                drop(victim)
                cache.discard(victim)
            cache.add(p)
            marked.add(p)
        if trace is not None:
            trace.append(sorted(cache))
    return flags


def run_belady(seq, k, trace=None):
    n = len(seq)
    nxt = [0] * n
    last: dict = {}
    for i in range(n - 1, -1, -1):
        nxt[i] = last.get(seq[i], n + 1)
        last[seq[i]] = i
    cache: dict = {}                    # Seite -> Zeitpunkt der nächsten Anfrage
    flags = []
    for i, p in enumerate(seq):
        if p in cache:
            flags.append(0)
        else:
            flags.append(1)
            if len(cache) == k:
                del cache[max(cache, key=cache.get)]
        cache[p] = nxt[i]
        if trace is not None:
            trace.append(sorted(cache))
    return flags


def marking_mean(seq, k, seed, runs):
    """Mittlere Fehlerzahl von Marking mit Zufall über `runs` Läufe (Seed je Lauf aus Seed und Laufnummer)."""
    return float(np.mean([sum(run_marking(seq, k, np.random.default_rng([seed, r]))) for r in range(runs)]))


def harmonic(k: int) -> float:
    return float(sum(1.0 / i for i in range(1, k + 1)))
