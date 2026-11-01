"""Verdikte an von Hand gesetzten Werten (DEMO-PLAYBOOK §12): jede Zahl im Text und jede Verzweigung steht hier.

Ein Verdikt ist eine reine Funktion (Art, Text). Die Tests geben ihr Analyse-Objekte mit gesetzten Werten und prüfen die Art und jede genannte Zahl."""

import pytest

import pag_algorithm as A
import pag_evaluation as ev


def _analysis(verfahren="LRU", k=8, q=7.78, faults=2000.0, opt=257.0, rate=100.0, length=2000):
    s = ev.Settings(k=k, n=k + 1, folge="zyklisch", laenge=length, verfahren=verfahren, seed=1)
    ratios = {"LRU": q, "FIFO": q, "LFU": q, "Marking mit Zufall": q}
    f = {"LRU": faults, "FIFO": faults, "LFU": faults, "Marking mit Zufall": faults, "Optimum": opt}
    rates = {**{r: rate for r in ev.REGELN}, "Optimum": 12.8}
    return ev.Analysis(s, f, ratios, rates, {}, [])


def test_kern_lru_names_faults_optimum_ratio_guarantee_and_share():
    kind, text = ev.verdict_kern(_analysis(q=7.78))
    assert kind == "warning"
    assert "**LRU** macht 2000 Fehler (100.0 % der Anfragen), das Optimum mit Vorwissen 257: das **7.78-Fache**" in text
    assert "Die Garantie dieser Regel ist k = 8." in text and "Die Folge nutzt davon 97 %." in text


def test_kern_thresholds_are_one_and_a_half_and_three():
    assert ev.verdict_kern(_analysis(q=1.49))[0] == "success"
    assert ev.verdict_kern(_analysis(q=1.5))[0] == "info"
    assert ev.verdict_kern(_analysis(q=2.99))[0] == "info"
    assert ev.verdict_kern(_analysis(q=3.0))[0] == "warning"


def test_kern_fifo_uses_the_same_guarantee_and_share():
    _, text = ev.verdict_kern(_analysis(verfahren="FIFO", k=4, q=2.0))
    assert text.startswith("**FIFO**") and "Garantie dieser Regel ist k = 4." in text and "nutzt davon 50 %." in text


def test_kern_lfu_has_no_guarantee_and_no_share():
    _, text = ev.verdict_kern(_analysis(verfahren="LFU", q=7.96))
    assert "LFU hat keine Garantie." in text and "nutzt davon" not in text and "k =" not in text


def test_kern_marking_names_the_mean_and_two_h_k():
    _, text = ev.verdict_kern(_analysis(verfahren="Marking mit Zufall", k=4, q=2.1, faults=540.5))
    assert "540.5 Fehler im Mittel" in text and f"2·H_k = {2 * A.harmonic(4):.2f}" in text and "nutzt davon" not in text


def test_guarantee_phrase_values():
    assert ev.guarantee_phrase("LRU", 5) == "Die Garantie dieser Regel ist k = 5."
    assert ev.guarantee_phrase("Marking mit Zufall", 2) == "Die Garantie im Mittel ist 2·H_k = 3.00."
    assert ev.guarantee_phrase("LFU", 5) == "LFU hat keine Garantie."


def test_gegner_names_the_last_row():
    rows = [{"k": 2, "Fehlerquote LRU": 100.0, "LRU": 2.0, "Marking mit Zufall": 1.5, "H_k": 1.5, "2 H_k": 3.0},
            {"k": 32, "Fehlerquote LRU": 100.0, "LRU": 29.73, "Marking mit Zufall": 3.82, "H_k": 4.06, "2 H_k": 8.12}]
    kind, text = ev.verdict_gegner(rows)
    assert kind == "warning"
    assert "Bei k = 32 fehlen LRU, FIFO und LFU bei **100 %**" in text and "Quotient zum Optimum **29.73** (Garantie 32)" in text
    assert "Marking mit Zufall liegt bei 3.82: H_k wäre 4.06, 2·H_k 8.12." in text


def test_typisch_names_range_best_and_worst():
    rows = [{"Folge": "zyklisch", "LRU": 2.74, "LFU": 2.74}, {"Folge": "Zipf", "LRU": 2.16, "LFU": 1.80}, {"Folge": "Arbeitsmengen", "LRU": 2.05, "LFU": 5.11},
            {"Folge": "Scan mit heißen Seiten", "LRU": 1.42, "LFU": 1.17}]
    kind, text = ev.verdict_typisch(rows, 8)
    assert kind == "info"
    assert "zwischen 1.42 und 2.74 (Garantie k = 8), am schlechtesten bei „zyklisch“" in text
    assert "LFU ist bei „Scan mit heißen Seiten“ am besten (1.17) und bei „Arbeitsmengen“ am schlechtesten (5.11)" in text


def test_platz_formel_takes_the_last_row_with_less_room():
    rows = [{"k": 16, "h": 16, "LRU(k) / Optimum(h)": 15.45, "k / (k − h + 1)": 16.0}, {"k": 16, "h": 8, "LRU(k) / Optimum(h)": 1.775, "k / (k − h + 1)": 1.778},
            {"k": 16, "h": 4, "LRU(k) / Optimum(h)": 1.23, "k / (k − h + 1)": 1.231}]
    kind, text = ev.verdict_platz_formel(rows)
    assert kind == "info"
    assert "LRU mit 16 Plätzen gegen das Optimum mit nur 4 Plätzen: das **1.23-Fache**; die Formel k/(k − h + 1) gibt 1.23." in text


def test_platz_quote_says_whether_the_ratio_falls():
    rows = [{"k": 2, "Fehlerquote LRU": 95.8, "Quotient": 1.12}, {"k": 64, "Fehlerquote LRU": 40.2, "Quotient": 1.95}]
    _, text = ev.verdict_platz_quote(rows)
    assert "Von k = 2 auf k = 64 Plätze sinkt die Fehlerquote von LRU von 95.8 % auf 40.2 %" in text and "Quotient zum Optimum sinkt nicht: 1.12 → 1.95" in text
    rows = [{"k": 2, "Fehlerquote LRU": 95.8, "Quotient": 2.0}, {"k": 64, "Fehlerquote LRU": 40.2, "Quotient": 1.5}]
    assert "Quotient zum Optimum sinkt: 2.00 → 1.50" in ev.verdict_platz_quote(rows)[1]


def test_anomalie_names_book_counts_and_shares():
    book = {"FIFO": {3: 9, 4: 10}, "LRU": {3: 10, 4: 8}, "Optimum": {3: 7, 4: 6}}
    freq = {"FIFO": 0.55, "LRU": 0.0, "LFU": 0.3}
    kind, text = ev.verdict_anomalie(book, freq)
    assert kind == "warning"
    assert "FIFO macht 9 Fehler mit 3 Plätzen und 10 mit 4; LRU 10 und 8, das Optimum 7 und 6" in text
    assert "FIFO in 0.6 %" in text and "LFU in 0.3 %" in text and "LRU in 0.0 %" in text and "2000 Zufallsfolgen" in text
    book["FIFO"][4] = 9
    assert ev.verdict_anomalie(book, freq)[0] == "info"


def test_delta_text_is_mine_minus_reference_with_inverse_colour():
    assert ev.delta_text(7.78, 8.0, "Garantie k") == ("-0.22 gegen Garantie k", "inverse")
    assert ev.delta_text(8.5, 8.0, "Garantie k") == ("+0.50 gegen Garantie k", "inverse")
    assert ev.delta_text(2.0, 2.003, "Garantie k") == ("gleich wie Garantie k", "off")


def test_ratio_and_rate_guards():
    assert ev.ratio(10, 0) == 1.0 and ev.ratio(10, 4) == 2.5
    assert ev.rate_percent(5, 0) == 0.0 and ev.rate_percent(5, 20) == pytest.approx(25.0)
