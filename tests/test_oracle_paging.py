"""Orakel-Test paging-demo / paging: unabhängige Rechenwege gegen den Kern.

Orakel 1: Belady (Kern) gegen die vollständige Aufzählung aller Cache-Zustände (dynamische Programmierung über Mengen), unabhängig vom Greedy-Prinzip.
Orakel 2: LRU über Stapelabstände: eine Anfrage ist ein Fehler genau dann, wenn die Seite noch nie angefragt wurde oder mehr als k
verschiedene Seiten seit ihrer letzten Anfrage vorkamen. Rechenweg ohne Speicher.
Orakel 3: FIFO und LFU in zweiten, plumperen Fassungen (Listen statt Mengen und Wörterbücher).
Orakel 4: Marking mit Zufall gegen eine Phasenzählung: bei jedem Lauf ist ein Verdrängen nie eine in der Phase schon angefragte Seite."""

import numpy as np
import pytest

import pag_algorithm as A


def opt_dp(seq, k):
    states = {frozenset(): 0}
    for p in seq:
        new = {}
        for st, c in states.items():
            if p in st:
                cand = [(st, c)]
            elif len(st) < k:
                cand = [(st | {p}, c + 1)]
            else:
                cand = [((st - {q}) | {p}, c + 1) for q in st]
            for s2, c2 in cand:
                if s2 not in new or c2 < new[s2]:
                    new[s2] = c2
        states = new
    return min(states.values())


def _random_small(seed):
    rng = np.random.default_rng(seed)
    k = int(rng.integers(1, 5))
    pages = int(rng.integers(k, k + 4))
    return [int(x) for x in rng.integers(0, pages, int(rng.integers(5, 15)))], k


def test_belady_equals_exhaustive_optimum():
    for seed in range(200):
        seq, k = _random_small(seed)
        assert sum(A.run_belady(seq, k)) == opt_dp(seq, k), (seed, seq, k)


def lru_by_stack_distance(seq, k):
    faults, history = [], []
    for p in seq:
        if p not in history:
            faults.append(1)
        else:
            last = len(history) - 1 - history[::-1].index(p)
            faults.append(1 if len(set(history[last + 1:])) >= k else 0)
        history.append(p)
    return faults


def test_lru_equals_the_stack_distance_rule():
    for seed in range(200):
        seq, k = _random_small(seed + 1000)
        assert A.run_lru(seq, k) == lru_by_stack_distance(seq, k), (seq, k)


def fifo_by_lists(seq, k):
    queue, faults = [], []
    for p in seq:
        if p in queue:
            faults.append(0)
        else:
            faults.append(1)
            if len(queue) == k:
                queue.pop(0)
            queue.append(p)
    return faults


def lfu_by_lists(seq, k):
    cache, faults = [], []
    counts, last = {}, {}
    for t, p in enumerate(seq):
        if p in cache:
            faults.append(0)
        else:
            faults.append(1)
            if len(cache) == k:
                worst = sorted(cache, key=lambda q: (counts[q], last[q]))[0]
                cache.remove(worst)
            cache.append(p)
            counts[p] = 0
        counts[p] += 1
        last[p] = t
    return faults


def test_fifo_and_lfu_equal_their_second_versions():
    for seed in range(200):
        seq, k = _random_small(seed + 2000)
        assert A.run_fifo(seq, k) == fifo_by_lists(seq, k), (seq, k)
        assert A.run_lfu(seq, k) == lfu_by_lists(seq, k), (seq, k)


def test_marking_never_evicts_a_page_requested_in_the_current_phase():
    """Phasen von Hand gezählt: eine Phase endet, sobald die (k+1)-te verschiedene Seite kommt. Eine in der laufenden Phase schon angefragte Seite
    darf bei einem Fehler nicht fliegen; das prüft ein Beobachter, der den Speicher nachführt."""
    for seed in range(60):
        seq, k = _random_small(seed + 3000)
        trace = []
        flags = A.run_marking(seq, k, np.random.default_rng(seed), trace)
        phase_pages: set = set()
        prev: set = set()
        for i, p in enumerate(seq):
            if p not in phase_pages and len(phase_pages) == k:
                phase_pages = set()                               # neue Phase beginnt mit dieser Anfrage
            phase_pages.add(p)
            now = set(trace[i])
            gone = prev - now
            assert not (gone & (phase_pages - {p})), (seed, i, gone, phase_pages)
            assert len(now) <= k
            prev = now
        assert len(flags) == len(seq)


def test_marking_with_a_fixed_seed_equals_a_second_run():
    seq = [i % 6 for i in range(500)]
    assert A.run_marking(seq, 5, np.random.default_rng(9)) == A.run_marking(seq, 5, np.random.default_rng(9))
