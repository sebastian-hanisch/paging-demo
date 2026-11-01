"""Paging – wer muss weichen, wenn der Platz knapp ist? - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Zweites Stück der Reihe „Online-Algorithmen“: viele Dinge gleichzeitig vorhalten, jede Verdrängung ohne Kenntnis der künftigen Anfragen.
Aufbau und Regeln stehen im DEMO-PLAYBOOK.md (§2).

Lauffähig mit: streamlit run app.py
"""

import pandas as pd
import streamlit as st

import pag_algorithm as A
import pag_constants as C
from pag_evaluation import (
    Settings,
    adversary_rows,
    analyse,
    anomalie_buch,
    anomalie_haeufigkeit,
    delta_text,
    platz_formel_rows,
    platz_quote_rows,
    typisch_rows,
    verdict_anomalie,
    verdict_gegner,
    verdict_kern,
    verdict_platz_formel,
    verdict_platz_quote,
    verdict_typisch,
)
from pag_layout import dunkles_design, kopf_css
from pag_presets import (
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    randomize_seed,
    sidebar_presets,
    sync_query_params,
)
from pag_visualization import (
    build_adversary,
    build_anomalie,
    build_cumulative,
    build_platz_formel,
    build_platz_quote,
    build_rates,
    build_typisch,
)

st.set_page_config(page_title="Paging – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _analysis(settings):
    return analyse(settings)


@st.cache_data(show_spinner="Rechne die Gegner-Folgen …")
def _adversary():
    return adversary_rows()


@st.cache_data(show_spinner="Rechne die sechs Folgen über fünf Seeds …")
def _typisch(k, n):
    return typisch_rows(k, n)


@st.cache_data(show_spinner=False)
def _platz_formel():
    return platz_formel_rows()


@st.cache_data(show_spinner=False)
def _platz_quote(settings):
    return platz_quote_rows(settings)


@st.cache_data(show_spinner="Rechne die Zufallsfolgen …")
def _anomalie():
    return anomalie_buch(), anomalie_haeufigkeit()


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in pag_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("🗄️ Paging – wer muss weichen, wenn der Platz knapp ist?")
st.markdown(
    """
**Zweites Stück der Reihe „Online-Algorithmen“** (Entscheiden ohne Kenntnis der Zukunft; Nachfolger von Ski-Rental). Ein Vorwärtslager hat **k Schnellzugriffsplätze**, die Artikel werden **nacheinander angefragt**; fehlt einer, kostet der Nachschub 1, und ein anderer muss weichen.
Wer, entscheidet eine **Regel** ohne Wissen über die kommenden Anfragen. Gemessen wird sie am **Optimum mit Vorwissen**: Das **Wettbewerbsverhältnis** ist der Quotient der Fehlerzahlen.

Weiter unten: die **Kernfrage**, vier Experimente (**Gegner-Folge**, **typische Folgen**, **mehr Platz statt Glück**, **mehr Platz, mehr Fehler**), **🚧 Wo die Annahmen enden**, **⚠️ Annahmen, Grenzen und bekannte Probleme** und **📐 Mathematische Formulierung**.
"""
)

with st.expander("So funktioniert Paging", expanded=True):
    st.markdown(
        """
1. **Der Speicher hat k Plätze.** Jede Anfrage nennt einen Artikel (eine Seite). Liegt er im Speicher, ist das ein Treffer und kostet nichts. Sonst ist es ein **Fehler**: Der Nachschub kostet 1, und ist der Speicher voll, muss eine Seite weichen.
2. **Die Regel entscheidet, wer weicht:** **LRU** verdrängt die Seite, die am längsten nicht angefragt wurde, **FIFO** die, die am längsten im Speicher liegt, **LFU** die am seltensten angefragte, **Marking mit Zufall** eine zufällige unter den Seiten, die in dieser Phase noch nicht angefragt wurden.
3. **Das Optimum mit Vorwissen (Belady)** verdrängt die Seite, die am spätesten wieder gebraucht wird; es kennt die ganze Folge.
4. **Die Garantie:** LRU und FIFO machen höchstens k-mal so viele Fehler wie das Optimum (bis auf eine Konstante), und keine feste Regel kann besser sein. Mit Zufall sinkt der Faktor auf etwa H_k (die harmonische Zahl, sie wächst wie ln k), Marking mit Zufall garantiert 2·H_k.
5. **Garantie ist nicht Erwartung:** auf welchen Folgen die Regeln wirklich nahe an ihre Garantie kommen und auf welchen sie weit darunter bleiben, zeigen die Experimente.
        """
    )

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("⚙️ Einstellungen")
    st.markdown("**Speicher und Bestand**")
    k = st.slider("Plätze k", *bounds("k_slider"), key="k_slider", help="So viele Artikel passen gleichzeitig in den Schnellzugriff.")
    n = st.slider("Aktiver Bestand N (Seiten)", *bounds("n_slider"), key="n_slider",
                  help="Wie viele verschiedene Seiten die Folge regelmäßig anfragt (bei „Arbeitsmengen“: je Phase). N = k + 1 ist die schwierigste Größe.")
    st.markdown("**Anfragefolge**")
    folge = st.selectbox("Folge", C.FOLGEN, key="folge_select", help="Wie die Anfragen aufeinander folgen; die Regeln kennen die Folge nicht.")
    st.caption(C.FOLGEN_HILFE[folge])
    laenge = st.select_slider("Länge L (Anfragen)", options=C.LENGTHS, key="laenge_select")
    st.markdown("**Regel**")
    verfahren = st.selectbox("Regel (hervorgehoben)", C.VERFAHREN, key="verfahren_select", help="Alle Regeln laufen mit; die gewählte steht im Ergebnis und im Verdikt.")
    st.caption(C.VERFAHREN_HILFE[verfahren])
    seed = st.number_input("Zufalls-Seed", *bounds("seed_input"), key="seed_input", step=1)
    st.button("🎲 Neue Folge ziehen", width="stretch", on_click=randomize_seed)

sync_query_params({"k_slider": int(k), "n_slider": int(n), "folge_select": folge, "laenge_select": int(laenge), "verfahren_select": verfahren, "seed_input": int(seed)})

settings = Settings(int(k), int(n), folge, int(laenge), verfahren, int(seed))
a = _analysis(settings)

# --- Ergebnis ------------------------------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 Ergebnis")
st.caption(f"k = {k} Plätze · N = {n} Seiten · Folge „{folge}“ mit {laenge} Anfragen · hervorgehoben: {verfahren}")
q = a.ratios[verfahren]
f_sel, f_opt = a.faults[verfahren], a.faults["Optimum"]
m1, m2, m3, m4 = st.columns(4)
fehler_label = f"{f_sel:.1f}" if verfahren == "Marking mit Zufall" else f"{f_sel:.0f}"
diff = f_sel - f_opt
d1, c1 = ("gleich wie Optimum", "off") if abs(diff) < 0.05 else (f"{diff:+.0f} gegen Optimum", "inverse")
m1.metric("Fehler der Regel", fehler_label, delta=d1, delta_color=c1, help=f"Fehler (Nachschub) der hervorgehobenen Regel ({verfahren}); bei „Marking mit Zufall“ das Mittel über 50 Läufe.")
m2.metric("Fehler Optimum", f"{f_opt:.0f}", delta="Referenz", delta_color="off", help="Fehler des Optimums (Belady), das die ganze Folge kennt.")
if verfahren in ("LRU", "FIFO"):
    guarantee, g_label = float(k), "Garantie k"
elif verfahren == "Marking mit Zufall":
    guarantee, g_label = 2 * A.harmonic(k), "Garantie 2·H_k"
else:
    guarantee, g_label = None, ""
if guarantee is None:
    m3.metric("Quotient", f"{q:.2f}", delta="LFU: keine Garantie", delta_color="off")
else:
    d3, c3 = delta_text(q, guarantee, g_label)
    m3.metric("Quotient", f"{q:.2f}", delta=d3, delta_color=c3, help="Fehler der Regel geteilt durch Fehler des Optimums (das Wettbewerbsverhältnis auf dieser Folge).")
m4.metric("Fehlerquote", f"{a.rates[verfahren]:.1f} %", delta=f"Optimum {a.rates['Optimum']:.1f} %", delta_color="off", help="Anteil der Anfragen, die einen Fehler auslösen.")

st.plotly_chart(build_cumulative(a.cumulative, verfahren), width="stretch", key="cumulative_chart")
st.caption(
    "Fehler bisher über die Anfragen. Das Optimum (blau) wächst am langsamsten; der Abstand zur gewählten Regel ist der Preis der Unwissenheit. "
    "Gepunktet: die übrigen Regeln (Marking mit Zufall als ein einzelner Lauf)."
)
st.plotly_chart(build_rates(a.rates, verfahren), width="stretch", key="rates_chart")
with st.expander("Ablauf der ersten 24 Anfragen: gewählte Regel gegen das Optimum"):
    st.caption("Speicherinhalt nach jeder Anfrage; ✗ = Fehler. Bei Folgen mit mehr als 26 Seiten heißen die Seiten ab der siebenundzwanzigsten S27, S28, …")
    st.dataframe(pd.DataFrame(a.trace), hide_index=True, width="stretch")

# --- Kernfrage -----------------------------------------------------------------------------------------------------------------------------

st.markdown("## ❓ Kernfrage: Was kostet die Regel gegen das Optimum?")
kind, text = verdict_kern(a)
getattr(st, kind)(text)

st.markdown("---")

# --- Experimente ---------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment 1: Die Folge, die gegen die Regel gebaut ist")
rows_adv = _adversary()
st.caption(
    f"Zyklisch über k + 1 Seiten, {C.ADV_CYCLES} Durchläufe: Wer gerade weichen musste, wird als Nächstes gebraucht. Marking mit Zufall: Mittel über {C.ADV_RUNS} Läufe. "
    "Gestrichelt: die Garantie k, gepunktet 2·H_k und H_k."
)
st.plotly_chart(build_adversary(rows_adv), width="stretch", key="adversary_chart")
kind, text = verdict_gegner(rows_adv)
getattr(st, kind)(text)
with st.expander("Tabelle zum Diagramm"):
    st.dataframe(pd.DataFrame(rows_adv), hide_index=True, width="stretch",
                 column_config={c: st.column_config.NumberColumn(format="%.2f") for c in ("Fehlerquote LRU", "LRU", "FIFO", "LFU", "Marking mit Zufall", "H_k", "2 H_k")})

st.markdown("---")

st.subheader("🔬 Experiment 2: Und auf typischen Folgen?")
rows_typ = _typisch(int(k), int(n))
st.caption(
    f"Alle sechs Folgen mit k = {k} Plätzen und N = {n}, Länge {C.SWEEP_LEN}, Mittel über {len(C.SWEEP_SEEDS)} feste Seeds; Zahlen sind Fehler geteilt durch Fehler des Optimums. "
    "Marking mit Zufall: ein Lauf je Seed."
)
st.plotly_chart(build_typisch(rows_typ), width="stretch", key="typisch_chart")
kind, text = verdict_typisch(rows_typ, int(k))
getattr(st, kind)(text)
with st.expander("Tabelle zum Diagramm"):
    st.dataframe(pd.DataFrame(rows_typ), hide_index=True, width="stretch",
                 column_config={c: st.column_config.NumberColumn(format="%.2f") for c in ("Fehlerquote Optimum", "LRU", "FIFO", "LFU", "Marking mit Zufall")})

st.markdown("---")

st.subheader("🔬 Experiment 3: Mehr Platz statt Glück")
rows_pf = _platz_formel()
st.caption(
    f"LRU mit k Plätzen gegen das Optimum mit nur h ≤ k Plätzen, auf der zyklischen Folge über k + 1 Seiten ({C.ADV_CYCLES} Durchläufe). Die Formel k/(k − h + 1) sagt voraus, wie viel das Glück-Argument noch trägt."
)
st.plotly_chart(build_platz_formel(rows_pf), width="stretch", key="platz_formel_chart")
kind, text = verdict_platz_formel(rows_pf)
getattr(st, kind)(text)
st.markdown("**Und im Betrieb?** Dieselbe Folge wie oben im Ergebnis, nur mit wachsender Platzzahl:")
rows_pq = _platz_quote(settings)
st.plotly_chart(build_platz_quote(rows_pq), width="stretch", key="platz_quote_chart")
kind, text = verdict_platz_quote(rows_pq)
getattr(st, kind)(text)

st.markdown("---")

st.subheader("🔬 Experiment 4: Mehr Platz, mehr Fehler?")
book, freq = _anomalie()
st.caption("Die Lehrbuchfolge 1 2 3 4 1 2 5 1 2 3 4 5 (Belady-Anomalie): mit einem Platz mehr macht FIFO mehr Fehler.")
st.plotly_chart(build_anomalie(book), width="stretch", key="anomalie_chart")
kind, text = verdict_anomalie(book, freq)
getattr(st, kind)(text)

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    """
| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| **Alle Seiten sind gleich groß und jeder Fehler kostet 1** | Mit Seitengrößen oder unterschiedlichen Nachschubkosten ist es ein anderes Problem; nicht modelliert. | – |
| **Ein Fehler kostet überall gleich viel** | Müssen Fahrzeuge zu Anfragen fahren, kostet jeder Fehler eine Wegstrecke; aus der Auswahl wird eine Wegewahl im Netz. | k-Server |
| **Die Folge ist ganz unbekannt** | Ein Wissen über die kommenden Anfragen, auch ein unsicheres, lässt sich nutzen; Experiment 2 zeigt, wie unterschiedlich die Regeln auf gleichen Folgen sind. | Vorhersagen |
| **Ein einziger Speicher** | Mehrere Stufen, Vorabladen und Schreibzugriffe fehlen. | – |
| **Die Folgen sind erfunden** | Zipf, Arbeitsmengen und Schleife sind Modelle, keine Messung echter Anfragen. | – |
"""
)

with st.expander("⚠️ Annahmen, Grenzen und bekannte Probleme"):
    st.markdown(
        f"""
**Annahmen.** k Plätze, gleich große Seiten, Fehlerkosten 1, Anfragen nacheinander. Das Optimum (Belady) kennt die ganze Folge. Die Folgen sind erfunden: Zipf mit Exponent {str(C.ZIPF_ALPHA).replace('.', ',')}, Arbeitsmengen mit Phasen von {C.PHASE_LEN} Anfragen aus einem Bestand von {C.UNIVERSE_FACTOR} N Seiten, Schleife mit {C.FOREIGN_SHARE * 100:.0f} % Fremdzugriffen, Scan mit {C.SCAN_SHARE * 100:.0f} % Durchlaufanfragen.

**Grenzen.** Die Demo ist nur an erfundenen Folgen geprüft. „Marking mit Zufall“ ist im Ergebnis das Mittel über {C.MARKING_RUNS} Läufe und rauscht leicht; in Experiment 2 ist es ein einzelner Lauf je Seed. Die Quotienten in Experiment 1 und 3 hängen an der Länge der Folge (endliche Länge, Anlaufphase mit k Fehlern): sie nähern sich der Garantie von unten, wenn die Folge länger wird.

**Bekannte Probleme und Unsicherheiten.** Mit einem Bestand N ≤ k fehlen nur die ersten Anfragen jeder Seite, dann sind alle Regeln gleich gut. Bei LFU entscheidet bei Gleichstand die am längsten nicht angefragte Seite; andere Gleichstandsregeln geben andere Zahlen. Die Belady-Anomalie ist selten (Experiment 4 nennt die Häufigkeit in Zufallsfolgen).
        """
    )

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Lesehilfe.** Gegeben sind $k$ Plätze und eine Anfragefolge $\sigma = (p_1, \dots, p_L)$; die Regel kennt nur die bisherigen Anfragen. Gesucht ist, wie viel mehr Fehler sie macht als das Optimum mit Vorwissen.

| Symbol | Bedeutung |
|---|---|
| $k$ | Zahl der Plätze im Speicher |
| $\sigma$ | Anfragefolge von Seiten |
| $f_A(\sigma)$ | Zahl der Fehler der Regel $A$ auf $\sigma$ |
| $f_{\mathrm{OPT}}(\sigma)$ | Fehler des Optimums (Belady) auf $\sigma$ |
| $H_k$ | harmonische Zahl $1 + \tfrac12 + \dots + \tfrac1k$ |
| $h$ | Plätze des Optimums beim Vergleich mit weniger Platz |

**Wettbewerbsverhältnis.** $A$ ist $c$-kompetitiv, wenn $f_A(\sigma) \le c \cdot f_{\mathrm{OPT}}(\sigma) + b$ für alle $\sigma$ mit einer Konstanten $b$ gilt.

**Deterministisch.** LRU und FIFO sind $k$-kompetitiv, und kein deterministisches Verfahren ist besser als $k$. LFU ist für kein $c$ kompetitiv. Die schwierigste Folge für LRU und FIFO ist die zyklische über $k+1$ Seiten: jede Anfrage ist ein Fehler, das Optimum verdrängt nur etwa jede $k$-te.

**Zufall.** Das Marking mit Zufall ist $2H_k$-kompetitiv im Mittel, und kein Zufallsverfahren ist besser als $H_k$. Die untere Schranke zeigt die gleichverteilte Folge über $k+1$ Seiten: Jede Regel fehlt dort bei jeder Anfrage mit der Wahrscheinlichkeit $1/(k+1)$, weil genau eine Seite im Speicher fehlt; das Optimum macht, weil es die Folge kennt, in der Messung etwa $H_k$-mal weniger Fehler.

**Mehr Platz.** Hat LRU $k$ Plätze und das Optimum nur $h \le k$, so gilt $f_{\mathrm{LRU}}^{(k)}(\sigma) \le \tfrac{k}{k-h+1}\, f_{\mathrm{OPT}}^{(h)}(\sigma) + h$; auf der zyklischen Folge wird die Zahl bis auf die Anlaufphase erreicht.

**Literatur (nicht nachgebaut, nicht im Volltext eingesehen, außer wo angegeben).** A. Fiat, R. M. Karp, M. Luby, L. A. McGeoch, D. D. Sleator, N. E. Young: *Competitive Paging Algorithms* (arXiv cs/0205038): $2H_k$ für das Marking mit Zufall, untere Schranke $H_k$, $k$ für LRU und FIFO (als Auszug bestätigt). D. D. Sleator, R. E. Tarjan (1985) für $k$ und die Platz-Erweiterung, L. A. Belady (1966) für das Optimum und die Anomalie: aus dem Gedächtnis zitiert. Hier belegt sind die Zahlen durch vollständiges Durchrechnen der Folgen.
        """
    )

st.markdown("---")
st.caption(
    "Verwandte Demos: [Ski-Rental](https://github.com/sebastian-hanisch/ski-rental-demo) (die Kaufentscheidung ohne Kenntnis der Dauer, Vorgänger), "
    "[Online-Matching](https://sebastianhanisch-online-matching-demo.streamlit.app/) (Zuordnen ohne Kenntnis der Zukunft), "
    "[No-Regret-Lernen](https://sebastianhanisch-noregret-demo.streamlit.app/) (Lernen aus Erfahrung mit dem Regret als Maß), "
    "Lagerplatz- und Torzuordnung (`blockzuweisung-demo`, `dock_door-demo`; dort eine feste Zuordnung statt einer Folge von Anfragen)."
)
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html)."
)
