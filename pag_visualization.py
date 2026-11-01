"""Plotly-Abbildungen. Alle Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen nicht am Diagramm hängen bleiben."""

import plotly.graph_objects as go
from plotly.subplots import make_subplots

import pag_constants as C


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height=360):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=-0.3), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def build_cumulative(cumulative: dict, selected: str):
    """Kumulierte Fehler über die Anfragen; die gewählte Regel dick, das Optimum blau."""
    fig = go.Figure()
    colors = {"LRU": C.COLOR_LRU, "FIFO": C.COLOR_FIFO, "LFU": C.COLOR_LFU, "Marking (ein Lauf)": C.COLOR_MARKING, "Optimum": C.COLOR_OPT}
    for name, ys in cumulative.items():
        is_sel = name == selected or (selected == "Marking mit Zufall" and name == "Marking (ein Lauf)")
        width = 4 if is_sel or name == "Optimum" else 1.5
        xs = list(range(1, len(ys) + 1))
        fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", name=name, line=dict(color=colors[name], width=width, dash="solid" if is_sel or name == "Optimum" else "dot"),
                                 hovertemplate="Anfrage %{x}: %{y} Fehler<extra>" + name + "</extra>"))
    fig.update_xaxes(title_text="Anfrage")
    fig.update_yaxes(title_text="Fehler bisher (Nachschub)")
    return _base(fig)


def build_rates(rates: dict, selected: str):
    names = [*C.VERFAHREN, "Optimum"]
    colors = [C.COLORS[n] for n in names]
    fig = go.Figure(go.Bar(x=names, y=[rates[n] for n in names], marker_color=colors, text=[f"{rates[n]:.1f} %" for n in names], textposition="outside",
                           hovertemplate="%{x}: %{y:.2f} %<extra></extra>"))
    fig.update_yaxes(title_text="Fehlerquote (% der Anfragen)", range=[0, max(rates[n] for n in names) * 1.2 + 1])
    return _base(fig, height=300)


def build_adversary(rows: list[dict]):
    """Quotient zum Optimum über k auf der zyklischen Folge: LRU/FIFO/LFU wachsen mit k, Marking mit Zufall bleibt bei H_k."""
    ks = [r["k"] for r in rows]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ks, y=[r["LRU"] for r in rows], mode="lines+markers", name="LRU, FIFO, LFU", line=dict(color=C.COLOR_LRU, width=3),
                             hovertemplate="k = %{x}: %{y:.2f}<extra>LRU, FIFO, LFU</extra>"))
    fig.add_trace(go.Scatter(x=ks, y=[r["Marking mit Zufall"] for r in rows], mode="lines+markers", name="Marking mit Zufall", line=dict(color=C.COLOR_MARKING, width=3),
                             hovertemplate="k = %{x}: %{y:.2f}<extra>Marking mit Zufall</extra>"))
    fig.add_trace(go.Scatter(x=ks, y=ks, mode="lines", name="Garantie k", line=dict(color=C.COLOR_GUARANTEE, width=2, dash="dash"), hovertemplate="k = %{x}<extra>Garantie k</extra>"))
    fig.add_trace(go.Scatter(x=ks, y=[r["2 H_k"] for r in rows], mode="lines", name="2·H_k", line=dict(color=C.COLOR_GUARANTEE, width=2, dash="dot"), hovertemplate="k = %{x}: %{y:.2f}<extra>2·H_k</extra>"))
    fig.add_trace(go.Scatter(x=ks, y=[r["H_k"] for r in rows], mode="lines", name="H_k", line=dict(color=C.COLOR_OPT, width=2, dash="dot"), hovertemplate="k = %{x}: %{y:.2f}<extra>H_k</extra>"))
    fig.update_xaxes(title_text="Plätze k")
    fig.update_yaxes(title_text="Fehler geteilt durch Fehler des Optimums")
    return _base(fig)


def build_typisch(rows: list[dict]):
    names = [r["Folge"] for r in rows]
    fig = go.Figure()
    for regel in C.VERFAHREN:
        fig.add_trace(go.Bar(x=names, y=[r[regel] for r in rows], name=regel, marker_color=C.COLORS[regel], hovertemplate="%{x}: %{y:.2f}<extra>" + regel + "</extra>"))
    fig.update_layout(barmode="group")
    fig.update_yaxes(title_text="Fehler geteilt durch Fehler des Optimums")
    return _base(fig, height=380)


def build_platz_formel(rows: list[dict]):
    labels = [f"k = {r['k']}, h = {r['h']}" for r in rows]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=labels, y=[r["LRU(k) / Optimum(h)"] for r in rows], name="LRU mit k Plätzen / Optimum mit h Plätzen", marker_color=C.COLOR_LRU,
                         hovertemplate="%{x}: %{y:.2f}<extra>gemessen</extra>"))
    fig.add_trace(go.Bar(x=labels, y=[r["k / (k − h + 1)"] for r in rows], name="k / (k − h + 1)", marker_color=C.COLOR_GUARANTEE, hovertemplate="%{x}: %{y:.2f}<extra>Formel</extra>"))
    fig.update_layout(barmode="group")
    fig.update_yaxes(title_text="Quotient der Fehlerzahlen")
    return _base(fig)


def build_platz_quote(rows: list[dict]):
    ks = [str(r["k"]) for r in rows]
    fig = make_subplots(rows=1, cols=2, subplot_titles=("Fehlerquote", "Quotient zum Optimum"))
    fig.add_trace(go.Scatter(x=ks, y=[r["Fehlerquote LRU"] for r in rows], mode="lines+markers", name="LRU", line=dict(color=C.COLOR_LRU, width=3),
                             hovertemplate="k = %{x}: %{y:.1f} %<extra>LRU</extra>"), row=1, col=1)
    fig.add_trace(go.Scatter(x=ks, y=[r["Fehlerquote Optimum"] for r in rows], mode="lines+markers", name="Optimum", line=dict(color=C.COLOR_OPT, width=3),
                             hovertemplate="k = %{x}: %{y:.1f} %<extra>Optimum</extra>"), row=1, col=1)
    fig.add_trace(go.Scatter(x=ks, y=[r["Quotient"] for r in rows], mode="lines+markers", name="LRU / Optimum", line=dict(color=C.COLOR_FIFO, width=3),
                             hovertemplate="k = %{x}: %{y:.2f}<extra>Quotient</extra>"), row=1, col=2)
    fig.update_xaxes(title_text="Plätze k", type="category")
    fig.update_yaxes(title_text="% der Anfragen", row=1, col=1)
    fig.update_yaxes(title_text="Fehler LRU / Fehler Optimum", row=1, col=2)
    return _base(fig)


def build_anomalie(book: dict):
    fig = go.Figure()
    for name, color in (("FIFO", C.COLOR_FIFO), ("LRU", C.COLOR_LRU), ("Optimum", C.COLOR_OPT)):
        fig.add_trace(go.Bar(x=["3 Plätze", "4 Plätze"], y=[book[name][3], book[name][4]], name=name, marker_color=color, text=[book[name][3], book[name][4]], textposition="outside",
                             hovertemplate="%{x}: %{y} Fehler<extra>" + name + "</extra>"))
    fig.update_layout(barmode="group")
    fig.update_yaxes(title_text="Fehler auf der Lehrbuchfolge", range=[0, 13])
    return _base(fig, height=300)
