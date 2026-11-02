"""Konstanten: Regler-Grenzen, feste Annahmen, Farben und Presets."""

K_MIN, K_MAX, DEFAULT_K = 2, 32, 8             # Plätze im Speicher
N_MIN, N_MAX, DEFAULT_N = 2, 200, 9            # Größe des aktiven Bestands (Zahl der Seiten, die die Folge regelmäßig anfragt)
LENGTHS = (6, 12, 30, 100, 200, 500, 1000, 2000, 5000, 10000, 20000)
DEFAULT_LENGTH = 2000
SEED_MAX, DEFAULT_SEED = 999999, 7

VERFAHREN = ("LRU", "FIFO", "LFU", "Marking mit Zufall")
DEFAULT_VERFAHREN = "LRU"
VERFAHREN_HILFE = {
    "LRU": "Verdrängt die Seite, die am längsten nicht angefragt wurde.",
    "FIFO": "Verdrängt die Seite, die am längsten im Speicher liegt (egal, wie oft sie angefragt wurde).",
    "LFU": "Verdrängt die Seite mit den wenigsten Anfragen seit dem Laden; bei Gleichstand die am längsten nicht angefragte. Keine Garantie.",
    "Marking mit Zufall": "Merkt sich je Phase die angefragten Seiten und verdrängt zufällig eine nicht gemerkte; in der App das Mittel über 50 Läufe.",
}
FOLGEN = ("zyklisch", "gleichverteilt", "Zipf", "Arbeitsmengen", "Schleife mit Fremdzugriffen", "Scan mit heißen Seiten")
DEFAULT_FOLGE = "zyklisch"
FOLGEN_HILFE = {
    "zyklisch": "Die N Seiten werden der Reihe nach angefragt, immer wieder. Mit N = k + 1 die schlimmste Folge für LRU und FIFO.",
    "gleichverteilt": "Jede Anfrage wählt eine der N Seiten gleichwahrscheinlich. Mit N = k + 1 die Folge der unteren Schranke.",
    "Zipf": "Stabile Beliebtheit: Seite i wird mit Gewicht 1/i^0,8 angefragt (wenige Renner, viele Exoten).",
    "Arbeitsmengen": "Wechselndes Sortiment: je 300 Anfragen dreht sich alles um N zufällig gewählte Seiten aus einem Bestand von 50 N.",
    "Schleife mit Fremdzugriffen": "Wie zyklisch über N Seiten, aber jede Anfrage geht mit 10 % Wahrscheinlichkeit auf eine fremde Seite.",
    "Scan mit heißen Seiten": "Jede Anfrage geht mit 50 % Wahrscheinlichkeit auf eine von N heißen Seiten, die übrigen laufen einmal durch 2000 weitere Seiten.",
}
ZIPF_ALPHA = 0.8
PHASE_LEN = 300
UNIVERSE_FACTOR = 50
FOREIGN_SHARE = 0.1
FOREIGN_RANGE = 1000
SCAN_SHARE = 0.5
SCAN_RANGE = 2000

MARKING_RUNS = 50                              # Läufe, über die „Marking mit Zufall“ gemittelt wird
TRACE_LEN = 24                                 # Zeilen der Ablauftabelle

# feste Experimente (nie ein einzelner Seed als Befund)
SWEEP_SEEDS = tuple(range(1000, 1005))
SWEEP_LEN = 5000
ADV_KS = (2, 3, 4, 6, 8, 12, 16, 24, 32)
ADV_CYCLES = 400                               # Länge der Gegner-Folge: so viele Durchläufe über k + 1 Seiten
ADV_RUNS = 20
PLATZ_KS = (2, 4, 8, 16, 32, 64)
PLATZ_HS = (1.0, 0.75, 0.5, 0.25)             # h als Anteil von k im Platz-Experiment
BOOK_SEQUENCE = (1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5)
ANOMALY_TRIALS, ANOMALY_LEN, ANOMALY_PAGES, ANOMALY_KS = 2000, 60, 8, (1, 2, 3, 4, 5, 6)

COLOR_ALG = "#2F6B65"
COLOR_OPT = "#4c78a8"
COLOR_LRU = "#2F6B65"
COLOR_FIFO = "#d97706"
COLOR_LFU = "#c0392b"
COLOR_MARKING = "#7c3aed"
COLOR_GUARANTEE = "rgba(150,150,150,0.8)"
COLORS = {"LRU": COLOR_LRU, "FIFO": COLOR_FIFO, "LFU": COLOR_LFU, "Marking mit Zufall": COLOR_MARKING, "Optimum": COLOR_OPT}

PRESETS = {
    "Gegner: zyklisch über k + 1": {"k": DEFAULT_K, "n": DEFAULT_N, "folge": "zyklisch", "laenge": DEFAULT_LENGTH, "verfahren": "LRU", "seed": DEFAULT_SEED},
    "Mini-Instanz von Hand (k = 2)": {"k": 2, "n": 3, "folge": "zyklisch", "laenge": 6, "verfahren": "LRU", "seed": DEFAULT_SEED},
    "Zufalls-Gegner: gleichverteilt über k + 1": {"k": DEFAULT_K, "n": DEFAULT_N, "folge": "gleichverteilt", "laenge": 5000, "verfahren": "LRU", "seed": DEFAULT_SEED},
    "Zipf: stabile Beliebtheit": {"k": DEFAULT_K, "n": 200, "folge": "Zipf", "laenge": 5000, "verfahren": "LFU", "seed": DEFAULT_SEED},
    "Arbeitsmengen: Sortiment wechselt": {"k": DEFAULT_K, "n": 10, "folge": "Arbeitsmengen", "laenge": 5000, "verfahren": "LFU", "seed": DEFAULT_SEED},
    "Schleife mit Fremdzugriffen": {"k": 16, "n": 12, "folge": "Schleife mit Fremdzugriffen", "laenge": 5000, "verfahren": "FIFO", "seed": DEFAULT_SEED},
}
PRESET_HELP = {
    "Gegner: zyklisch über k + 1": "Acht Plätze, neun Seiten der Reihe nach: LRU und FIFO fehlen bei jeder Anfrage, das Optimum nur bei jeder achten.",
    "Mini-Instanz von Hand (k = 2)": "Zwei Plätze, drei Seiten, sechs Anfragen a b c a b c: LRU macht sechs Fehler, das Optimum vier. Zum Nachrechnen.",
    "Zufalls-Gegner: gleichverteilt über k + 1": "Jede Anfrage trifft zufällig eine von neun Seiten: kein Verfahren, auch nicht mit Zufall, liegt dauerhaft unter dem Faktor H_k.",
    "Zipf: stabile Beliebtheit": "Wenige Renner, viele Exoten, die Beliebtheit bleibt: LFU gewinnt hier, obwohl es keine Garantie hat.",
    "Arbeitsmengen: Sortiment wechselt": "Das Sortiment wechselt alle 300 Anfragen: LFU hält alte Renner fest und verliert um ein Vielfaches.",
    "Schleife mit Fremdzugriffen": "Eine Tour über zwölf Seiten bei sechzehn Plätzen, jede Anfrage mit 10 % Wahrscheinlichkeit fremd: FIFO bricht ein, LRU nicht.",
}
