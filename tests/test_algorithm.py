"""Kern gegen Handrechnung auf der Mini-Instanz und kleinen Folgen von Hand."""

import numpy as np
import pytest

import pag_algorithm as A


def test_mini_instance_by_hand(mini):
    seq, k = mini
    assert A.run_lru(seq, k) == [1] * 6 and A.run_fifo(seq, k) == [1] * 6 and A.run_lfu(seq, k) == [1] * 6
    assert A.run_belady(seq, k) == [1, 1, 1, 0, 1, 0]


def test_small_sequence_by_hand_for_lru_fifo_lfu():
    # k = 2, Folge a b a c b
    seq = [0, 1, 0, 2, 1]
    # LRU: a f, b f, a trifft, c f (b war am längsten nicht dran, fliegt), b f (a fliegt)
    assert A.run_lru(seq, 2) == [1, 1, 0, 1, 1]
    # FIFO: a f, b f, a trifft, c f (a liegt am längsten, fliegt), b trifft (b blieb)
    assert A.run_fifo(seq, 2) == [1, 1, 0, 1, 0]
    # LFU: a f, b f, a trifft (a zweimal), c f (b einmal, fliegt), b f (c einmal, a zweimal: c fliegt)
    assert A.run_lfu(seq, 2) == [1, 1, 0, 1, 1]


def test_textbook_sequence_belady_anomaly_by_hand():
    seq = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]
    # FIFO mit 3 Plätzen: Fehler bei 1 2 3 4 1 2 5 und 3 4: neun; mit 4 Plätzen: 1 2 3 4, dann 5 1 2 3 4 5: zehn
    assert sum(A.run_fifo(seq, 3)) == 9 and sum(A.run_fifo(seq, 4)) == 10
    assert sum(A.run_lru(seq, 3)) == 10 and sum(A.run_lru(seq, 4)) == 8


def test_cold_faults_only_when_everything_fits():
    seq = [0, 1, 2, 3, 0, 1, 2, 3, 3, 2]
    for run in (A.run_lru, A.run_fifo, A.run_lfu, A.run_belady):
        assert sum(run(seq, 4)) == 4 and sum(run(seq, 6)) == 4
    assert sum(A.run_marking(seq, 4, np.random.default_rng(0))) == 4


def test_single_slot_every_change_is_a_fault():
    seq = [0, 0, 1, 1, 1, 0, 2, 2]
    assert A.run_lru(seq, 1) == A.run_fifo(seq, 1) == A.run_lfu(seq, 1) == A.run_belady(seq, 1) == [1, 0, 1, 0, 0, 1, 1, 0]
    assert A.run_marking(seq, 1, np.random.default_rng(0)) == [1, 0, 1, 0, 0, 1, 1, 0]


def test_cyclic_sequence_over_k_plus_one_faults_every_time_for_lru_fifo_lfu():
    for k in (2, 3, 5, 9):
        seq = [i % (k + 1) for i in range(10 * (k + 1))]
        for run in (A.run_lru, A.run_fifo, A.run_lfu):
            assert sum(run(seq, k)) == len(seq), (run.__name__, k)
        assert sum(A.run_belady(seq, k)) < len(seq) / 2 + k


def test_belady_by_hand_on_the_cyclic_sequence():
    # k = 2, a b c a b c a b c: a f, b f, c f (b fliegt: a kommt früher), a trifft, b f (a fliegt: c kommt früher), c trifft,
    # a f (c fliegt: b kommt früher), b trifft, c f: sechs Fehler
    seq = [0, 1, 2, 0, 1, 2, 0, 1, 2]
    assert A.run_belady(seq, 2) == [1, 1, 1, 0, 1, 0, 1, 0, 1]


def test_trace_snapshots_have_at_most_k_pages_and_the_requested_page(mini):
    seq, k = mini
    for run in (A.run_lru, A.run_fifo, A.run_lfu, A.run_belady):
        trace = []
        run(seq, k, trace)
        assert len(trace) == len(seq)
        assert all(len(t) <= k and p in t for t, p in zip(trace, seq))
    trace = []
    A.run_lru(seq, k, trace)
    assert trace == [[0], [0, 1], [1, 2], [0, 2], [0, 1], [1, 2]]


def test_marking_mean_is_reproducible_for_a_seed():
    seq = [i % 5 for i in range(300)]
    assert A.marking_mean(seq, 4, 3, 10) == A.marking_mean(seq, 4, 3, 10)
    assert A.marking_mean(seq, 4, 3, 10) != A.marking_mean(seq, 4, 4, 10)


def test_harmonic_numbers():
    assert A.harmonic(1) == 1.0 and A.harmonic(2) == 1.5 and A.harmonic(4) == pytest.approx(25 / 12)
