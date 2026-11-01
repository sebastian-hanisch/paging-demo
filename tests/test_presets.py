"""Presets: Vollständigkeit, gültige Werte, Standard-Preset = Standardeinstellungen; Permalink; feste Experimente."""

import pag_constants as C
import pag_evaluation as ev
import pag_presets as P


def test_every_preset_has_help_and_all_keys():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, preset in C.PRESETS.items():
        assert set(preset) == set(P.PRESET_KEYS), name
        assert C.PRESET_HELP[name]


def test_preset_values_are_inside_the_control_ranges():
    for preset in C.PRESETS.values():
        assert C.K_MIN <= preset["k"] <= C.K_MAX and C.N_MIN <= preset["n"] <= C.N_MAX and 0 <= preset["seed"] <= C.SEED_MAX
        assert preset["folge"] in C.FOLGEN and preset["laenge"] in C.LENGTHS and preset["verfahren"] in C.VERFAHREN


def test_default_preset_equals_the_default_settings():
    assert ev.Settings(**next(iter(C.PRESETS.values()))) == ev.Settings()


def test_setting_specs_cover_every_preset_key():
    assert set(P.PRESET_KEYS.values()) == set(P.SETTING_SPECS)


def test_every_choice_has_a_help_text():
    assert set(C.FOLGEN_HILFE) == set(C.FOLGEN) and set(C.VERFAHREN_HILFE) == set(C.VERFAHREN)
    assert C.DEFAULT_FOLGE in C.FOLGEN and C.DEFAULT_VERFAHREN in C.VERFAHREN and C.DEFAULT_LENGTH in C.LENGTHS


def test_experiment_grids_are_sorted_and_inside_the_slider():
    assert list(C.ADV_KS) == sorted(C.ADV_KS) and max(C.ADV_KS) <= C.K_MAX
    assert list(C.PLATZ_KS) == sorted(C.PLATZ_KS) and C.LENGTHS == tuple(sorted(C.LENGTHS))


def test_experiment_rows_have_the_documented_shape():
    rows = ev.adversary_rows(ks=(2, 3), cycles=20, runs=2)
    assert [r["k"] for r in rows] == [2, 3] and all(r["LRU"] >= 1 for r in rows)
    rows = ev.typisch_rows(4, 6, length=300, seeds=(1, 2))
    assert [r["Folge"] for r in rows] == list(C.FOLGEN)
    assert all(r[v] >= 1.0 - 1e-9 for r in rows for v in C.VERFAHREN)
    rows = ev.platz_formel_rows(ks=(4,), cycles=20)
    assert [(r["k"], r["h"]) for r in rows] == [(4, 4), (4, 3), (4, 2), (4, 1)]
    rows = ev.platz_quote_rows(ev.Settings(4, 6, "Zipf", 500, "LRU", 1), ks=(2, 4))
    assert [r["k"] for r in rows] == [2, 4]
