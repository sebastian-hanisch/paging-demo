"""Eigenschaftstests (ORACLE-PLAYBOOK §5.2): Aussagen, die für Paging gelten müssen, ohne das richtige Ergebnis zu kennen.

Jede Eigenschaft folgt aus der Definition: kein Verfahren schlägt das Optimum, ein Online-Verfahren sieht die Zukunft nicht (Präfix-Eigenschaft),
LRU hat die Inklusionseigenschaft (mehr Platz, nie mehr Fehler), Umbenennen der Seiten ändert nichts, Marking-Verfahren sind k-kompetitiv."""

import numpy as np
import pytest

import pag_algorithm as A
import pag_constants as C
from pag_scenario import make_sequence


def _seqs(n_seqs=40, pages=8, length=80, seed=0):
    rng = np.random.default_rng(seed)
    return [[int(x) for x in rng.integers(0, pages, length)] for _ in range(n_seqs)]


ONLINE = (A.run_lru, A.run_fifo, A.run_lfu)


def test_no_rule_beats_the_optimum():
    for seq in _seqs():
        for k in (1, 2, 4, 7):
            opt = sum(A.run_belady(seq, k))
            assert all(sum(run(seq, k)) >= opt for run in ONLINE)
            assert sum(A.run_marking(seq, k, np.random.default_rng(1))) >= opt


def test_online_rules_do_not_see_the_future():
    # die Fehlerflags der ersten m Anfragen sind für jede Fortsetzung dieselben
    for seq in _seqs(20):
        for run in ONLINE:
            full = run(seq, 4)
            for m in (5, 17, 40):
                assert run(seq[:m], 4) == full[:m]
    seq = _seqs(1)[0]
    f_full = A.run_marking(seq, 4, np.random.default_rng(2))
    assert A.run_marking(seq[:30], 4, np.random.default_rng(2)) == f_full[:30]


def test_the_optimum_never_gets_worse_with_more_room_and_neither_does_lru():
    for seq in _seqs():
        for run in (A.run_belady, A.run_lru):
            counts = [sum(run(seq, k)) for k in range(1, 10)]
            assert all(a >= b for a, b in zip(counts, counts[1:])), (run.__name__, counts)


def test_renaming_pages_changes_nothing_for_lru_fifo_lfu_and_belady():
    rng = np.random.default_rng(5)
    for seq in _seqs(20):
        perm = rng.permutation(20)
        renamed = [int(perm[p]) for p in seq]
        for run in (*ONLINE, A.run_belady):
            assert run(seq, 3) == run(renamed, 3)


def test_marking_algorithms_are_k_competitive():
    # je Phase höchstens k Fehler und das Optimum fehlt in jeder Phase (bis auf die erste) mindestens einmal: f ≤ k (OPT + 1)
    for seq in _seqs(30, pages=9, length=200):
        for k in (2, 3, 5, 8):
            opt = sum(A.run_belady(seq, k))
            assert sum(A.run_lru(seq, k)) <= k * (opt + 1)
            assert sum(A.run_marking(seq, k, np.random.default_rng(3))) <= k * (opt + 1)
    for k in (2, 5, 9):
        cyc = [i % (k + 1) for i in range(40 * (k + 1))]
        assert sum(A.run_lru(cyc, k)) <= k * (sum(A.run_belady(cyc, k)) + 1)


def test_lfu_has_no_such_bound_on_a_built_sequence():
    k = 4
    ratios = []
    for reps in (100, 400):
        seq = [p for p in range(k - 1) for _ in range(20)] + [k - 1 + (i % 2) for i in range(reps)]
        assert sum(A.run_lfu(seq, k)) >= reps and sum(A.run_belady(seq, k)) <= k + 2
        ratios.append(sum(A.run_lfu(seq, k)) / sum(A.run_belady(seq, k)))
    assert ratios[1] > 3 * ratios[0]                                  # das Verhältnis wächst mit der Länge: kein festes c genügt


def test_adding_a_request_never_removes_a_fault_for_online_rules():
    for seq in _seqs(15):
        for run in ONLINE:
            assert sum(run(seq + [0, 1], 3)) >= sum(run(seq, 3))


def test_same_cache_content_size_never_exceeds_k():
    for seq in _seqs(10):
        for run in (A.run_lru, A.run_fifo, A.run_lfu, A.run_belady):
            trace = []
            run(seq, 3, trace)
            assert max(len(t) for t in trace) <= 3


def test_cyclic_sequences_are_the_worst_for_lru_among_random_ones():
    k = 6
    cyc = make_sequence("zyklisch", k + 1, 700, 0)
    for seed in range(5):
        rnd = make_sequence("gleichverteilt", k + 1, 700, seed)
        assert sum(A.run_lru(cyc, k)) / sum(A.run_belady(cyc, k)) > sum(A.run_lru(rnd, k)) / sum(A.run_belady(rnd, k))


@pytest.mark.parametrize("kind", C.FOLGEN)
def test_belady_fault_rate_falls_when_k_grows_on_every_sequence_kind(kind):
    seq = make_sequence(kind, 20, 1500, 3)
    rates = [sum(A.run_belady(seq, k)) for k in (2, 4, 8, 16)]
    assert all(a >= b for a, b in zip(rates, rates[1:]))
