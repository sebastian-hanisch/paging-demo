"""Randfälle: kürzeste Folge, Extremwerte der Regler, jede Folge hat die gewünschte Gestalt."""

import numpy as np
import pytest

import pag_algorithm as A
import pag_constants as C
import pag_evaluation as ev
from pag_scenario import make_sequence, page_name


@pytest.mark.parametrize("kind", C.FOLGEN)
@pytest.mark.parametrize("n,length", [(2, 6), (9, 100), (200, 500)])
def test_sequences_have_the_wanted_length_and_are_reproducible(kind, n, length):
    seq = make_sequence(kind, n, length, 5)
    assert len(seq) == length and all(isinstance(p, int) and p >= 0 for p in seq)
    assert seq == make_sequence(kind, n, length, 5)


def test_sequences_do_not_depend_on_k():
    # die Folge hängt nur von (Art, N, Länge, Seed) ab: ein Vergleich über k nutzt dieselbe Folge
    s1 = ev.Settings(k=4, n=12, folge="Zipf", laenge=500, seed=3)
    s2 = ev.Settings(k=16, n=12, folge="Zipf", laenge=500, seed=3)
    assert make_sequence(s1.folge, s1.n, s1.laenge, s1.seed) == make_sequence(s2.folge, s2.n, s2.laenge, s2.seed)


def test_cyclic_sequence_by_hand():
    assert make_sequence("zyklisch", 3, 7, 0) == [0, 1, 2, 0, 1, 2, 0]


def test_pages_stay_in_their_ranges():
    n = 10
    assert set(make_sequence("gleichverteilt", n, 2000, 1)) <= set(range(n))
    assert set(make_sequence("Zipf", n, 2000, 1)) <= set(range(n))
    loop = make_sequence("Schleife mit Fremdzugriffen", n, 3000, 1)
    foreign = [p for i, p in enumerate(loop) if p != i % n]
    assert foreign and all(n <= p < n + C.FOREIGN_RANGE for p in foreign)
    scan = make_sequence("Scan mit heißen Seiten", n, 3000, 1)
    assert all(p < n or n <= p < n + C.SCAN_RANGE for p in scan) and any(p >= n for p in scan) and any(p < n for p in scan)
    work = make_sequence("Arbeitsmengen", n, 2 * C.PHASE_LEN, 1)
    assert all(p < C.UNIVERSE_FACTOR * n for p in work)
    assert len(set(work[: C.PHASE_LEN])) <= n and len(set(work[C.PHASE_LEN:])) <= n         # je Phase höchstens N verschiedene Seiten


def test_working_sets_change_between_phases():
    work = make_sequence("Arbeitsmengen", 10, 2 * C.PHASE_LEN, 1)
    assert set(work[: C.PHASE_LEN]) != set(work[C.PHASE_LEN:])


def test_zipf_prefers_low_pages():
    seq = make_sequence("Zipf", 50, 20000, 2)
    counts = np.bincount(seq, minlength=50)
    assert counts[0] > counts[10] > counts[40]


def test_page_names():
    assert [page_name(p) for p in (0, 1, 25, 26, 100)] == ["a", "b", "z", "S27", "S101"]


def test_extreme_settings_run():
    for s in (ev.Settings(C.K_MIN, C.N_MIN, "gleichverteilt", C.LENGTHS[0], "LRU", 0),
              ev.Settings(C.K_MAX, C.N_MAX, "Arbeitsmengen", C.LENGTHS[-1], "Marking mit Zufall", C.SEED_MAX),
              ev.Settings(C.K_MAX, C.K_MAX + 1, "zyklisch", C.LENGTHS[-1], "LFU", 1)):
        a = ev.analyse(s)
        assert all(q >= 1.0 - 1e-9 for q in a.ratios.values()), s
        assert len(a.trace) == min(C.TRACE_LEN, s.laenge)


def test_when_everything_fits_all_rules_are_equal():
    a = ev.analyse(ev.Settings(k=8, n=5, folge="gleichverteilt", laenge=500, verfahren="LRU", seed=1))
    assert set(a.ratios.values()) == {1.0}


def test_trace_rows_mark_faults_and_name_the_rule():
    rows = ev.analyse(ev.Settings(2, 3, "zyklisch", 6, "LRU", 7)).trace
    assert [r["Seite"] for r in rows] == list("abcabc")
    assert [r["LRU"] for r in rows] == ["a  ✗", "a b  ✗", "b c  ✗", "a c  ✗", "a b  ✗", "b c  ✗"]
    assert [r["Optimum"].endswith("✗") for r in rows] == [True, True, True, False, True, False]


def test_cumulative_ends_at_the_fault_totals():
    a = ev.analyse(ev.Settings(4, 9, "zyklisch", 200, "LRU", 1))
    assert a.cumulative["LRU"][-1] == a.faults["LRU"] and a.cumulative["Optimum"][-1] == a.faults["Optimum"]
    assert all(b >= a_ for a_, b in zip(a.cumulative["LFU"], a.cumulative["LFU"][1:]))


def test_belady_never_exceeds_the_distinct_pages_when_k_is_huge():
    seq = make_sequence("Zipf", 30, 1000, 4)
    assert sum(A.run_belady(seq, 100)) == len(set(seq))
