"""Jede Zahl aus der README wird hier nachgerechnet (DEMO-PLAYBOOK §4): über dieselben Auswertungsfunktionen wie die App.

Feste Seeds und Längen wie in den Presets und Experimenten der App; Rundung wie in der README (zwei oder drei Nachkommastellen)."""

import pytest

import pag_algorithm as A
import pag_constants as C
import pag_evaluation as ev


def _preset(name):
    return ev.analyse(ev.Settings(**C.PRESETS[name]))


# --- Gegner-Folge (Experiment 1) --------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize("k,lru,marking,h", [(2, 1.997, 1.502, 1.5), (4, 3.976, 2.083, 2.083), (8, 7.877, 2.702, 2.718), (12, 11.685, 3.048, 3.103), (32, 29.73, 3.822, 4.058)])
def test_adversary_table(k, lru, marking, h):
    row = next(r for r in ev.adversary_rows() if r["k"] == k)
    assert row["LRU"] == pytest.approx(lru, abs=5e-4) and row["FIFO"] == row["LRU"] == row["LFU"]
    assert row["Marking mit Zufall"] == pytest.approx(marking, abs=5e-4) and row["H_k"] == pytest.approx(h, abs=5e-4)
    assert row["Fehlerquote LRU"] == 100.0 and row["2 H_k"] == pytest.approx(2 * h, abs=1e-3)
    assert row["LRU"] < k                                       # nähert sich k von unten (endliche Länge)


def test_marking_stays_between_h_k_minus_ten_percent_and_h_k_plus_two_percent_on_the_cyclic_sequence():
    for r in ev.adversary_rows():
        assert 0.9 * r["H_k"] < r["Marking mit Zufall"] < 1.02 * r["H_k"], r["k"]


# --- Presets (Ergebnis) ------------------------------------------------------------------------------------------------------------------


def test_mini_instance():
    a = _preset("Mini-Instanz von Hand (k = 2)")
    assert (a.faults["LRU"], a.faults["Optimum"], a.ratios["LRU"]) == (6, 4, 1.5) and a.ratios["Marking mit Zufall"] == pytest.approx(1.235, abs=5e-4)


def test_adversary_preset():
    a = _preset("Gegner: zyklisch über k + 1")
    assert a.faults["LRU"] == 2000 and a.faults["Optimum"] == 257 and a.ratios["LRU"] == pytest.approx(7.782, abs=5e-4)
    assert a.rates["Optimum"] == pytest.approx(12.85, abs=5e-3) and a.ratios["Marking mit Zufall"] == pytest.approx(2.659, abs=5e-4)


def test_random_adversary_preset_every_rule_is_close_to_h_k():
    a = _preset("Zufalls-Gegner: gleichverteilt über k + 1")
    assert [round(a.ratios[r], 3) for r in ev.REGELN] == [2.625, 2.769, 2.678, 2.657]
    assert all(abs(q - A.harmonic(8)) / A.harmonic(8) < 0.06 for q in a.ratios.values())          # H_8 = 2,718, alle innerhalb von 6 %
    assert a.rates["Optimum"] == pytest.approx(4.16, abs=5e-3)


def test_zipf_preset_lfu_wins():
    a = _preset("Zipf: stabile Beliebtheit")
    assert [round(a.ratios[r], 3) for r in ev.REGELN] == [1.383, 1.407, 1.230, 1.391]
    assert a.ratios["LFU"] == min(a.ratios.values())


def test_working_sets_preset_lfu_loses_by_a_multiple():
    a = _preset("Arbeitsmengen: Sortiment wechselt")
    assert [round(a.ratios[r], 3) for r in ev.REGELN] == [2.093, 2.040, 7.956, 2.118]
    assert a.ratios["LFU"] > 3 * a.ratios["LRU"]


def test_loop_preset_fifo_collapses_lru_does_not():
    a = _preset("Schleife mit Fremdzugriffen")
    assert [round(a.ratios[r], 3) for r in ev.REGELN] == [1.219, 2.923, 1.045, 1.652]
    assert a.ratios["FIFO"] > 2 * a.ratios["LRU"]


# --- Typische Folgen (Experiment 2) ------------------------------------------------------------------------------------------------------


TYPISCH_K8_N12 = {
    "zyklisch": (2.741, 2.741, 2.741, 2.240),
    "gleichverteilt": (2.270, 2.253, 2.274, 2.237),
    "Zipf": (2.156, 2.464, 1.803, 2.296),
    "Arbeitsmengen": (2.053, 2.029, 5.111, 2.056),
    "Schleife mit Fremdzugriffen": (2.481, 2.481, 2.481, 2.124),
    "Scan mit heißen Seiten": (1.421, 1.438, 1.165, 1.426),
}


def test_typical_sweep_table():
    rows = {r["Folge"]: r for r in ev.typisch_rows(8, 12)}
    for folge, expected in TYPISCH_K8_N12.items():
        assert [round(rows[folge][r], 3) for r in C.VERFAHREN] == pytest.approx(list(expected), abs=1.5e-3), folge


def test_typical_sweep_lru_stays_far_from_the_guarantee():
    rows = ev.typisch_rows(8, 12)
    assert max(r["LRU"] for r in rows) < 3.0 and min(r["LRU"] for r in rows) > 1.4                # Garantie k = 8
    lfu = {r["Folge"]: r["LFU"] for r in rows}
    assert min(lfu, key=lfu.get) == "Scan mit heißen Seiten" and max(lfu, key=lfu.get) == "Arbeitsmengen"


# --- Platz statt Glück (Experiment 3) ----------------------------------------------------------------------------------------------------


@pytest.mark.parametrize("k,h,measured,formula", [(8, 8, 7.877, 8.0), (8, 6, 2.657, 2.667), (8, 4, 1.598, 1.6), (8, 2, 1.142, 1.143),
                                                  (16, 16, 15.455, 16.0), (16, 12, 3.184, 3.2), (16, 8, 1.775, 1.778), (16, 4, 1.230, 1.231)])
def test_resource_augmentation_table(k, h, measured, formula):
    row = next(r for r in ev.platz_formel_rows() if (r["k"], r["h"]) == (k, h))
    assert row["LRU(k) / Optimum(h)"] == pytest.approx(measured, abs=1e-3) and row["k / (k − h + 1)"] == pytest.approx(formula, abs=1e-3)
    assert row["LRU(k) / Optimum(h)"] < row["k / (k − h + 1)"]                               # von unten erreicht (Anlaufphase)


def test_more_room_lowers_the_fault_rate_but_not_the_ratio_on_zipf():
    rows = ev.platz_quote_rows(ev.Settings(**C.PRESETS["Zipf: stabile Beliebtheit"]))
    assert [r["k"] for r in rows] == list(C.PLATZ_KS)
    assert rows[0]["Fehlerquote LRU"] == pytest.approx(95.8, abs=0.05) and rows[-1]["Fehlerquote LRU"] == pytest.approx(40.16, abs=0.05)
    assert rows[0]["Quotient"] == pytest.approx(1.119, abs=1e-3) and rows[-1]["Quotient"] == pytest.approx(1.948, abs=1e-3)
    assert all(a["Fehlerquote LRU"] > b["Fehlerquote LRU"] for a, b in zip(rows, rows[1:]))
    assert all(a["Quotient"] < b["Quotient"] for a, b in zip(rows, rows[1:]))


# --- Anomalie (Experiment 4) ------------------------------------------------------------------------------------------------------------


def test_belady_anomaly():
    book = ev.anomalie_buch()
    assert book == {"FIFO": {3: 9, 4: 10}, "LRU": {3: 10, 4: 8}, "Optimum": {3: 7, 4: 6}}
    freq = ev.anomalie_haeufigkeit()
    assert freq["FIFO"] == pytest.approx(0.55, abs=1e-9) and freq["LFU"] == pytest.approx(0.30, abs=1e-9) and freq["LRU"] == 0.0
    assert C.ANOMALY_TRIALS == 2000
