# Paging – wer muss weichen, wenn der Platz knapp ist? – Streamlit-Demo

<!-- TODO nach dem Deploy: direkt hierher den Live-Link setzen (Leerzeile davor und danach):
**[→ Demo live ausprobieren](https://sebastianhanisch-paging-demo.streamlit.app/)** -->

Zweites Stück der Reihe **Online-Algorithmen** („Entscheiden ohne Kenntnis der Zukunft“) in der „Konzepte“-Reihe für die Website „Sebastian Hanisch – Operations Research und Machine Learning“, Nachfolger von [ski-rental-demo](https://github.com/sebastian-hanisch/ski-rental-demo).
Anders als die Fall-Demos (ein Anwendungsfall, mehrere Verfahren im Vergleich) zeigt diese Demo **ein** Konzept, die **Wettbewerbsanalyse**, an einem wachsenden Beispiel: von einer Instanz zum Nachrechnen (zwei Plätze, drei Seiten) über die Folge, die gegen eine Regel gebaut ist, bis zu sechs typischen Folgen und der Frage, was mehr Platz kauft.
Kante zum Vorgänger: Ski-Rental hat **eine** Anschaffung, hier gibt es **viele gleichzeitig**; die Kaufentscheidung wird zur Auswahl, wer im Speicher bleibt. Folgestücke der Reihe: k-Server (Paging als einfachster Fall) und Vorhersagen (Marking mit Vorhersage).

**Verwandte bestehende Demos:** `online-matching-demo` (Zuordnen ohne Zukunft), `noregret-demo` (Lernen aus Erfahrung, Maß ist der Regret), `blockzuweisung-demo` und `dock_door-demo` (Lagerplatz- und Torzuordnung als **feste** Zuordnung, nicht als Folge von Anfragen). Keine davon enthält das Verdrängen aus einem Speicher.

## Warum dieses Problem

Ein Vorwärtslager hat k Schnellzugriffsplätze, die Artikel werden nacheinander angefragt. Fehlt ein Artikel, kostet der Nachschub 1, und ein anderer muss weichen. Welche Regel? Die Kernfrage: **Was kostet eine Regel im schlimmsten Fall, was auf typischen Folgen, und was kauft mehr Platz?**

## Modell

k Plätze, N verschiedene Seiten im aktiven Bestand, Anfragefolge der Länge L; eine Anfrage ist ein **Fehler**, wenn die Seite nicht im Speicher liegt (Kosten 1, danach liegt sie im Speicher, bei vollem Speicher weicht eine andere). Vier Regeln ohne Kenntnis der Zukunft: **LRU** (verdrängt die am längsten nicht angefragte Seite), **FIFO** (die am längsten im Speicher liegende), **LFU** (die am seltensten angefragte; bei Gleichstand die am längsten nicht angefragte), **Marking mit Zufall** (merkt je Phase die angefragten Seiten, verdrängt zufällig eine nicht gemerkte). Das **Optimum mit Vorwissen** (Belady) verdrängt die Seite, die am spätesten wieder angefragt wird. Gemessen wird der **Quotient der Fehlerzahlen** zum Optimum. Formeln im 📐-Expander der App.
Sechs Folgen: **zyklisch** (die N Seiten der Reihe nach), **gleichverteilt**, **Zipf** (Gewicht 1/i^0,8), **Arbeitsmengen** (je 300 Anfragen N zufällige Seiten aus 50 N), **Schleife mit Fremdzugriffen** (zyklisch, jede zehnte Anfrage fremd), **Scan mit heißen Seiten** (jede zweite Anfrage auf eine von N heißen Seiten, die übrigen laufen durch 2000 weitere). „Marking mit Zufall“ ist im Ergebnis das Mittel über 50 Läufe.

## Methodik

| Abschnitt der App | Was gerechnet wird |
|---|---|
| Ergebnis | alle Regeln und das Optimum auf der gewählten Folge; kumulierte Fehler; Ablauf der ersten 24 Anfragen |
| Experiment 1 | zyklische Folge über k + 1 Seiten (400 Durchläufe), k = 2 bis 32; Marking als Mittel über 20 Läufe |
| Experiment 2 | alle sechs Folgen mit den Reglern k und N, Länge 5000, Mittel über fünf feste Seeds (Marking: ein Lauf je Seed) |
| Experiment 3 | LRU mit k Plätzen gegen das Optimum mit h ≤ k Plätzen auf der zyklischen Folge; dieselbe Folge wie im Ergebnis mit wachsendem k |
| Experiment 4 | die Lehrbuchfolge der Belady-Anomalie und ihre Häufigkeit auf 2000 Zufallsfolgen |

## Befunde (gemessen, keine Behauptungen)

Alle Zahlen in `tests/test_claims.py` nachgerechnet. „Quotient“ steht für Fehler geteilt durch Fehler des Optimums.

| Frage | Befund |
|---|---|
| Mini-Instanz von Hand (k = 2, a b c a b c) | LRU, FIFO, LFU: 6 Fehler; Optimum 4 (a, b, c, dann b); Quotient 1,5. |
| Zyklische Folge über k + 1 Seiten: LRU, FIFO und LFU? | Fehlen bei **100 %** der Anfragen. Quotient 1,997 (k = 2), 3,976 (k = 4), 7,877 (k = 8), 11,685 (k = 12), 29,73 (k = 32): nähert sich k von unten (endliche Länge). |
| Dieselbe Folge mit Zufall? | Marking mit Zufall 1,502 / 2,083 / 2,702 / 3,048 / 3,822, jeweils nahe bei H_k (1,500 / 2,083 / 2,718 / 3,103 / 4,058; zwischen 0,9 und 1,02 H_k), weit unter 2·H_k und unter k. |
| Gleichverteilte Folge über k + 1 Seiten (k = 8)? | **Alle** Regeln liegen innerhalb von 6 % bei H_8 = 2,718: LRU 2,625, FIFO 2,769, LFU 2,678, Marking 2,657. Das ist die Folge der unteren Schranke: kein Verfahren, auch nicht mit Zufall, kommt dauerhaft darunter. |
| Zipf (k = 8, N = 200)? | **LFU gewinnt**: 1,230 gegen LRU 1,383, FIFO 1,407, Marking 1,391. |
| Arbeitsmengen (k = 8, N = 10)? | **LFU verliert** um ein Vielfaches: 7,956 gegen LRU 2,093, FIFO 2,040, Marking 2,118. Es hält alte Renner fest, wenn das Sortiment wechselt. LFU hat für kein c eine Garantie. |
| Schleife mit Fremdzugriffen (k = 16, N = 12)? | **FIFO bricht ein**: 2,923 gegen LRU 1,219, LFU 1,045, Marking 1,652. |
| Sechs Folgen im Mittel (k = 8, N = 12)? | LRU zwischen 1,421 (Scan mit heißen Seiten) und 2,741 (zyklisch), also weit unter der Garantie k = 8; LFU am besten bei „Scan mit heißen Seiten“ (1,165), am schlechtesten bei „Arbeitsmengen“ (5,111). |
| Mehr Platz für das Optimum, Formel k/(k − h + 1)? | LRU mit 8 Plätzen gegen das Optimum mit 6 / 4 / 2 Plätzen: 2,657 / 1,598 / 1,142 (Formel 2,667 / 1,600 / 1,143); mit 16 Plätzen gegen 12 / 8 / 4: 3,184 / 1,775 / 1,230 (Formel 3,200 / 1,778 / 1,231). Die Formel wird von unten erreicht (Anlaufphase). |
| Mehr Platz für LRU (Zipf, N = 200)? | Die Fehlerquote sinkt von 95,8 % (k = 2) auf 40,2 % (k = 64), der **Quotient zum Optimum steigt** von 1,119 auf 1,948. Mehr Platz hilft absolut, nicht relativ zum Optimum. |
| Belady-Anomalie? | Lehrbuchfolge 1 2 3 4 1 2 5 1 2 3 4 5: FIFO 9 Fehler mit 3 Plätzen und **10 mit 4**; LRU 10 und 8; Optimum 7 und 6. Auf 2000 Zufallsfolgen (Länge 60, 8 Seiten) tritt so etwas bei FIFO in 0,55 % auf, bei LFU in 0,30 %, bei LRU in 0 %. |

## Ehrliche Grenzen

- Die Demo ist **nur an erfundenen Folgen** geprüft; Zipf, Arbeitsmengen, Schleife und Scan sind Modelle, keine Messung echter Anfragen.
- Der Quotient auf der zyklischen Folge hängt an der Länge (Anlaufphase mit k Fehlern): bei 400 Durchläufen liegt er etwas unter der Garantie k.
- „Marking mit Zufall“ rauscht: im Ergebnis ein Mittel über 50 Läufe, in Experiment 2 ein einzelner Lauf je Seed, in Experiment 1 ein Mittel über 20.
- Bei N ≤ k fehlen nur die ersten Anfragen jeder Seite; alle Regeln sind dann gleich gut.
- Die Anomalie ist selten; die App nennt die Häufigkeit und zeigt nicht mehr als die Lehrbuchfolge.
- Gleichstandsregel bei LFU: die am längsten nicht angefragte Seite; eine andere Regel gibt andere Zahlen.

## Verifikation

- **Umfang:** 125 Tests (siehe `pytest --collect-only -q tests`), 45 bis 90 Sekunden lokal je nach Last.
- **Kern:** Fehlerflags gegen Handrechnung auf der Mini-Instanz und auf kleinen Folgen von Hand (LRU, FIFO, LFU, Belady); Randfälle (ein Platz, alles passt, Folgenformen).
- **Orakel** (`tests/test_oracle_paging.py`): Belady gegen die **vollständige Aufzählung aller Cache-Zustände** (200 Folgen); LRU gegen die Stapelabstands-Regel; FIFO und LFU gegen zweite Fassungen; Marking verdrängt nie eine in der laufenden Phase angefragte Seite.
- **Eigenschaften** (`tests/test_eigenschaften_paging.py`): kein Verfahren schlägt das Optimum; Online-Verfahren sehen die Zukunft nicht (Präfix-Eigenschaft); LRU und Optimum werden mit mehr Platz nie schlechter; Umbenennen der Seiten ändert nichts; LRU und Marking machen höchstens k·(OPT + 1) Fehler; LFU hat auf einer gebauten Folge keine solche Schranke.
- **Literatur:** kein Referenzwert-Test. Die Schranken 2·H_k und H_k stammen aus einem Auszug von Fiat u. a. (arXiv cs/0205038); Sleator und Tarjan (1985) und Belady (1966) wurden **nicht eingesehen** und sind in der App aus dem Gedächtnis zitiert (**offen**).
- **Verdikte** (`tests/test_verdicts.py`): jede Zahl und jede Verzweigung der Texte. **Claims** (`tests/test_claims.py`): jede Zahl dieser README.
- **Presets, Layout, Oberfläche:** vollständig, Werte in den Reglergrenzen; Schnellstart oben in der Seitenleiste, aktives Preset hervorgehoben, jede Regleränderung hebt die Markierung auf; AppTest-Rauchtest (jeder Button, jeder Regler an beiden Grenzen); Footer; Laufzeit-Importe.
- **Browser:** im Desktop-Browser durchgeklickt (alle sechs Presets, Seitenleiste, Expander, alle Diagramme). Nicht mit echtem Touch-Gerät getestet.

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App: Ergebnis, Kernfrage, vier Experimente, Grenzen, Formeln |
| `requirements-dev.txt` | Laufzeit plus pytest |
| `requirements.txt` | Laufzeit-Bibliotheken (ungepinnt) |
| `pag_algorithm.py` | Kern: LRU, FIFO, LFU, Marking mit Zufall, Belady |
| `pag_constants.py` | Regler-Grenzen, Folgenparameter, feste Experimente, Farben, Presets |
| `pag_evaluation.py` | Kennzahlen, Experimente, Ablauftabelle, Verdikte |
| `pag_layout.py` | Fester Kopf (Stylesheet) |
| `pag_presets.py` | Permalink (Begrenzen), Presets (Schnellstart in der Seitenleiste), Zufalls-Seed-Button |
| `pag_scenario.py` | Die sechs Anfragefolgen |
| `pag_visualization.py` | Plotly-Abbildungen (Achsen gesperrt) |
| `tests/` | Kern, Randfälle, Orakel, Eigenschaften, Verdikte, Claims, Presets, Layout, Smoke-Test, Footer, Laufzeit-Importe |

## Bewusst nicht umgesetzt

- **Seitengrößen und Gewichte** (unterschiedliche Nachschubkosten): ein anderes Problem.
- **Metrische Kosten** (Fahrzeuge im Netz statt gleicher Seiten) und **Vorhersagen** über kommende Anfragen: eigene Stücke der Reihe.
- **Mehrere Speicherstufen**, Vorabladen, Schreibzugriffe, echte Anfragedaten.
- **PDF-Export**: die Demo hat keine Ergebnisse, die man weitergibt; die Adresszeile (Permalink) reicht zum Teilen.

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Gebaut mit Streamlit, Plotly, NumPy und pandas.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html).
