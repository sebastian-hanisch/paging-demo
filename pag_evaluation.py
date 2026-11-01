"""Kennzahlen, Verdikt-Logik und Experimente. Verdikte sind reine Funktionen (Art, Text); tests/test_verdicts.py prüft jede Zahl darin."""

from dataclasses import dataclass

import numpy as np

import pag_algorithm as A
import pag_constants as C
from pag_scenario import make_sequence, page_name

DETERMINISTISCH = ("LRU", "FIFO", "LFU")
REGELN = ("LRU", "FIFO", "LFU", "Marking mit Zufall")
OK_QUOTIENT, WARN_QUOTIENT = 1.5, 3.0          # Verdikt: grün unter 1,5, gelb bis 3, sonst Warnung


@dataclass(frozen=True)
class Settings:
    k: int = C.DEFAULT_K
    n: int = C.DEFAULT_N
    folge: str = C.DEFAULT_FOLGE
    laenge: int = C.DEFAULT_LENGTH
    verfahren: str = C.DEFAULT_VERFAHREN
    seed: int = C.DEFAULT_SEED


@dataclass(frozen=True)
class Analysis:
    settings: Settings
    faults: dict                  # Regel -> Fehler (Marking: Mittel über MARKING_RUNS Läufe), "Optimum" -> Fehler von Belady
    ratios: dict                  # Regel -> Fehler / Optimum
    rates: dict                   # Regel -> Fehlerquote in Prozent der Anfragen
    cumulative: dict              # Name -> kumulierte Fehler je Anfrage (Marking: ein Lauf)
    trace: list                   # Zeilen der Ablauftabelle der ersten Anfragen


def ratio(faults: float, opt: float) -> float:
    """Quotient der Fehlerzahlen; ohne Fehler des Optimums (leere Folge) ist 1 der neutrale Wert."""
    return 1.0 if opt <= 0 else faults / opt


def rate_percent(faults: float, length: int) -> float:
    return 0.0 if length <= 0 else 100.0 * faults / length


def all_faults(seq, k, seed, runs=C.MARKING_RUNS) -> dict:
    """Fehler aller Regeln auf einer Folge; Marking als Mittel über `runs` Läufe."""
    return {
        "LRU": sum(A.run_lru(seq, k)),
        "FIFO": sum(A.run_fifo(seq, k)),
        "LFU": sum(A.run_lfu(seq, k)),
        "Marking mit Zufall": A.marking_mean(seq, k, seed, runs),
        "Optimum": sum(A.run_belady(seq, k)),
    }


def analyse(s: Settings) -> Analysis:
    seq = make_sequence(s.folge, s.n, s.laenge, s.seed)
    faults = all_faults(seq, s.k, s.seed)
    opt = faults["Optimum"]
    ratios = {r: ratio(faults[r], opt) for r in REGELN}
    rates = {r: rate_percent(faults[r], len(seq)) for r in (*REGELN, "Optimum")}
    flags = {"LRU": A.run_lru(seq, s.k), "FIFO": A.run_fifo(seq, s.k), "LFU": A.run_lfu(seq, s.k),
             "Marking (ein Lauf)": A.run_marking(seq, s.k, np.random.default_rng([s.seed, 0])), "Optimum": A.run_belady(seq, s.k)}
    cumulative = {name: np.cumsum(f).tolist() for name, f in flags.items()}
    return Analysis(s, faults, ratios, rates, cumulative, trace_rows(seq, s))


def trace_rows(seq, s: Settings, limit: int = C.TRACE_LEN) -> list[dict]:
    """Ablauf der ersten Anfragen: Speicherinhalt und Fehler der gewählten Regel und des Optimums."""
    part = list(seq[:limit])
    t_rule, t_opt = [], []
    if s.verfahren == "LRU":
        f_rule = A.run_lru(part, s.k, t_rule)
    elif s.verfahren == "FIFO":
        f_rule = A.run_fifo(part, s.k, t_rule)
    elif s.verfahren == "LFU":
        f_rule = A.run_lfu(part, s.k, t_rule)
    else:
        f_rule = A.run_marking(part, s.k, np.random.default_rng([s.seed, 0]), t_rule)
    f_opt = A.run_belady(part, s.k, t_opt)
    rows = []
    for i, p in enumerate(part):
        rows.append({
            "Anfrage": i + 1, "Seite": page_name(p),
            s.verfahren: " ".join(page_name(q) for q in t_rule[i]) + ("  ✗" if f_rule[i] else ""),
            "Optimum": " ".join(page_name(q) for q in t_opt[i]) + ("  ✗" if f_opt[i] else ""),
        })
    return rows


# ---------------------------------------------------------------------------------------------------------------------------------
# Experimente mit festen Folgen und Seeds


def adversary_rows(ks=C.ADV_KS, cycles=C.ADV_CYCLES, runs=C.ADV_RUNS) -> list[dict]:
    """Zyklische Folge über k + 1 Seiten: Quotient zu Belady je Regel, dazu H_k und 2 H_k."""
    rows = []
    for k in ks:
        length = cycles * (k + 1)
        seq = make_sequence("zyklisch", k + 1, length, 0)
        opt = sum(A.run_belady(seq, k))
        f_lru, f_fifo, f_lfu = sum(A.run_lru(seq, k)), sum(A.run_fifo(seq, k)), sum(A.run_lfu(seq, k))
        mark = A.marking_mean(seq, k, k, runs)
        rows.append({
            "k": k, "Fehlerquote LRU": rate_percent(f_lru, length), "LRU": ratio(f_lru, opt), "FIFO": ratio(f_fifo, opt),
            "LFU": ratio(f_lfu, opt), "Marking mit Zufall": ratio(mark, opt), "H_k": A.harmonic(k), "2 H_k": 2 * A.harmonic(k),
        })
    return rows


def typisch_rows(k: int, n: int, length=C.SWEEP_LEN, seeds=C.SWEEP_SEEDS) -> list[dict]:
    """Mittel über feste Seeds: Fehlerquote des Optimums und Quotient je Regel auf jeder der sechs Folgen. Marking: ein Lauf je Seed."""
    rows = []
    for folge in C.FOLGEN:
        acc = {r: [] for r in REGELN}
        opt_rates = []
        for sd in seeds:
            seq = make_sequence(folge, n, length, sd)
            opt = sum(A.run_belady(seq, k))
            opt_rates.append(rate_percent(opt, length))
            acc["LRU"].append(ratio(sum(A.run_lru(seq, k)), opt))
            acc["FIFO"].append(ratio(sum(A.run_fifo(seq, k)), opt))
            acc["LFU"].append(ratio(sum(A.run_lfu(seq, k)), opt))
            acc["Marking mit Zufall"].append(ratio(sum(A.run_marking(seq, k, np.random.default_rng([sd, 0]))), opt))
        rows.append({"Folge": folge, "Fehlerquote Optimum": float(np.mean(opt_rates)), **{r: float(np.mean(v)) for r, v in acc.items()}})
    return rows


def platz_formel_rows(ks=(8, 16), fractions=C.PLATZ_HS, cycles=C.ADV_CYCLES) -> list[dict]:
    """LRU mit k Plätzen gegen das Optimum mit h <= k Plätzen auf der zyklischen Folge über k + 1 Seiten; Formel k/(k − h + 1)."""
    rows = []
    for k in ks:
        seq = make_sequence("zyklisch", k + 1, cycles * (k + 1), 0)
        lru_faults = sum(A.run_lru(seq, k))
        for frac in fractions:
            h = max(1, int(round(frac * k)))
            rows.append({"k": k, "h": h, "LRU(k) / Optimum(h)": ratio(lru_faults, sum(A.run_belady(seq, h))), "k / (k − h + 1)": k / (k - h + 1)})
    return rows


def platz_quote_rows(s: Settings, ks=C.PLATZ_KS) -> list[dict]:
    """Wächst der Speicher, sinkt die Fehlerquote von LRU; der Quotient zum Optimum nicht unbedingt. Folge und N wie in den Reglern."""
    seq = make_sequence(s.folge, s.n, s.laenge, s.seed)
    rows = []
    for k in ks:
        f_lru, f_opt = sum(A.run_lru(seq, k)), sum(A.run_belady(seq, k))
        rows.append({"k": k, "Fehlerquote LRU": rate_percent(f_lru, len(seq)), "Fehlerquote Optimum": rate_percent(f_opt, len(seq)), "Quotient": ratio(f_lru, f_opt)})
    return rows


def anomalie_buch() -> dict:
    """Die Lehrbuchfolge: Fehler je Regel bei k = 3 und k = 4."""
    seq = list(C.BOOK_SEQUENCE)
    return {name: {k: sum(f(seq, k)) for k in (3, 4)} for name, f in (("FIFO", A.run_fifo), ("LRU", A.run_lru), ("Optimum", A.run_belady))}


def anomalie_haeufigkeit(trials=C.ANOMALY_TRIALS, length=C.ANOMALY_LEN, pages=C.ANOMALY_PAGES, ks=C.ANOMALY_KS) -> dict:
    """Anteil zufälliger Folgen, bei denen mit k + 1 Plätzen MEHR Fehler auftreten als mit k Plätzen (für irgendein k aus ks)."""
    rng = np.random.default_rng(1)
    hits = {"FIFO": 0, "LRU": 0, "LFU": 0}
    runners = {"FIFO": A.run_fifo, "LRU": A.run_lru, "LFU": A.run_lfu}
    for _ in range(trials):
        seq = [int(x) for x in rng.integers(0, pages, length)]
        for name, f in runners.items():
            counts = [sum(f(seq, k)) for k in (*ks, ks[-1] + 1)]
            if any(counts[i + 1] > counts[i] for i in range(len(counts) - 1)):
                hits[name] += 1
    return {name: 100.0 * v / trials for name, v in hits.items()}


# ---------------------------------------------------------------------------------------------------------------------------------
# Verdikte (rein: Art, Text)


def delta_text(value: float, reference: float, label: str) -> tuple[str, str]:
    """Text und Farbregel des Deltas: „mein Wert minus Referenz“. Ein auf zwei Stellen gleicher Wert bekommt keinen Pfeil und keine Farbe."""
    d = value - reference
    if abs(d) < 0.005:
        return f"gleich wie {label}", "off"
    return f"{d:+.2f} gegen {label}", "inverse"


def guarantee_phrase(verfahren: str, k: int) -> str:
    if verfahren in ("LRU", "FIFO"):
        return f"Die Garantie dieser Regel ist k = {k}."
    if verfahren == "Marking mit Zufall":
        return f"Die Garantie im Mittel ist 2·H_k = {2 * A.harmonic(k):.2f}."
    return "LFU hat keine Garantie."


def verdict_kern(a: Analysis) -> tuple[str, str]:
    """Kernfrage: Was kostet die gewählte Regel gegen das Optimum auf dieser Folge?"""
    s = a.settings
    v = s.verfahren
    q = a.ratios[v]
    fehler = a.faults[v]
    fehler_text = f"{fehler:.1f} Fehler im Mittel" if v == "Marking mit Zufall" else f"{fehler:.0f} Fehler"
    text = (f"**{v}** macht {fehler_text} ({a.rates[v]:.1f} % der Anfragen), das Optimum mit Vorwissen {a.faults['Optimum']:.0f}: das **{q:.2f}-Fache**. "
            f"{guarantee_phrase(v, s.k)}")
    if v in ("LRU", "FIFO"):
        text += f" Die Folge nutzt davon {q / s.k * 100:.0f} %."
    kind = "success" if q < OK_QUOTIENT else "info" if q < WARN_QUOTIENT else "warning"
    return kind, text


def verdict_gegner(rows: list[dict]) -> tuple[str, str]:
    """Experiment 1: die zyklische Folge über k + 1 Seiten."""
    r = rows[-1]
    return "warning", (f"Bei k = {r['k']} fehlen LRU, FIFO und LFU bei **{r['Fehlerquote LRU']:.0f} %** der Anfragen: Quotient zum Optimum **{r['LRU']:.2f}** (Garantie {r['k']}). "
                       f"Marking mit Zufall liegt bei {r['Marking mit Zufall']:.2f}: H_k wäre {r['H_k']:.2f}, 2·H_k {r['2 H_k']:.2f}.")


def verdict_typisch(rows: list[dict], k: int) -> tuple[str, str]:
    """Experiment 2: Mittel über feste Seeds auf den sechs Folgen."""
    lru = {r["Folge"]: r["LRU"] for r in rows}
    lfu = {r["Folge"]: r["LFU"] for r in rows}
    worst_lru = max(lru, key=lru.get)
    best_lfu, worst_lfu = min(lfu, key=lfu.get), max(lfu, key=lfu.get)
    return "info", (f"LRU liegt auf den sechs Folgen zwischen {min(lru.values()):.2f} und {max(lru.values()):.2f} (Garantie k = {k}), am schlechtesten bei „{worst_lru}“. "
                    f"LFU ist bei „{best_lfu}“ am besten ({lfu[best_lfu]:.2f}) und bei „{worst_lfu}“ am schlechtesten ({lfu[worst_lfu]:.2f}).")


def verdict_platz_formel(rows: list[dict]) -> tuple[str, str]:
    """Experiment 3a: Platz-Erweiterung gegen die Formel k/(k − h + 1)."""
    r = next(x for x in reversed(rows) if x["h"] < x["k"])
    return "info", (f"LRU mit {r['k']} Plätzen gegen das Optimum mit nur {r['h']} Plätzen: das **{r['LRU(k) / Optimum(h)']:.2f}-Fache**; die Formel k/(k − h + 1) gibt {r['k / (k − h + 1)']:.2f}. "
                    "Wer dem Optimum mehr Platz nimmt, braucht von der Regel kaum noch Glück.")


def verdict_platz_quote(rows: list[dict]) -> tuple[str, str]:
    """Experiment 3b: mehr Platz senkt die Fehlerquote, nicht unbedingt den Quotienten."""
    a, b = rows[0], rows[-1]
    sinkt = b["Quotient"] < a["Quotient"]
    kind = "info"
    return kind, (f"Von k = {a['k']} auf k = {b['k']} Plätze sinkt die Fehlerquote von LRU von {a['Fehlerquote LRU']:.1f} % auf {b['Fehlerquote LRU']:.1f} %, "
                  f"der Quotient zum Optimum {'sinkt' if sinkt else 'sinkt nicht'}: {a['Quotient']:.2f} → {b['Quotient']:.2f}.")


def verdict_anomalie(book: dict, freq: dict) -> tuple[str, str]:
    """Experiment 4: Mehr Platz, mehr Fehler."""
    f3, f4 = book["FIFO"][3], book["FIFO"][4]
    kind = "warning" if f4 > f3 else "info"
    return kind, (f"Lehrbuchfolge: FIFO macht {f3} Fehler mit 3 Plätzen und {f4} mit 4; LRU {book['LRU'][3]} und {book['LRU'][4]}, das Optimum {book['Optimum'][3]} und {book['Optimum'][4]}. "
                  f"Auf {C.ANOMALY_TRIALS} Zufallsfolgen tritt so etwas bei FIFO in {freq['FIFO']:.1f} % auf, bei LFU in {freq['LFU']:.1f} %, bei LRU in {freq['LRU']:.1f} %.")
