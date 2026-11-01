"""Anfragefolgen: Seiten sind ganze Zahlen 0, 1, 2, ...; jede Folge ist eine Liste und hängt nur von (Art, N, Länge, Seed) ab."""

import numpy as np

import pag_constants as C


def make_sequence(kind: str, n: int, length: int, seed: int) -> list[int]:
    rng = np.random.default_rng([seed, length, n])
    if kind == "zyklisch":
        return [i % n for i in range(length)]
    if kind == "gleichverteilt":
        return [int(x) for x in rng.integers(0, n, length)]
    if kind == "Zipf":
        w = 1.0 / np.arange(1, n + 1) ** C.ZIPF_ALPHA
        return [int(x) for x in rng.choice(n, size=length, p=w / w.sum())]
    if kind == "Arbeitsmengen":
        universe = C.UNIVERSE_FACTOR * n
        out: list[int] = []
        while len(out) < length:
            pool = rng.choice(universe, size=n, replace=False)
            out += [int(x) for x in rng.choice(pool, size=C.PHASE_LEN)]
        return out[:length]
    if kind == "Schleife mit Fremdzugriffen":
        foreign = rng.random(length) < C.FOREIGN_SHARE
        pages = rng.integers(n, n + C.FOREIGN_RANGE, length)
        return [int(pages[i]) if foreign[i] else i % n for i in range(length)]
    if kind == "Scan mit heißen Seiten":
        scan = rng.random(length) < C.SCAN_SHARE
        hot = rng.integers(0, n, length)
        out, s = [], 0
        for i in range(length):
            if scan[i]:
                out.append(n + s)
                s = (s + 1) % C.SCAN_RANGE
            else:
                out.append(int(hot[i]))
        return out
    raise ValueError(f"unbekannte Folge: {kind}")


def page_name(p: int) -> str:
    """Kurzer Name einer Seite für Tabellen: a, b, c, ... für die ersten 26, danach S27, S28, ..."""
    return chr(ord("a") + p) if 0 <= p < 26 else f"S{p + 1}"
