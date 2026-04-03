"""
fill_results.py — Rellena los [PLACEHOLDER] del manuscript.md con los
resultados reales del CSV de experimentos.

Uso:
    python paper/fill_results.py

Lee:  results/v2/all_conditions.csv
Escribe: paper/manuscript_final.md  (no sobreescribe el draft original)
"""

import re
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

CSV_PATH  = Path("results/v2/all_conditions.csv")
DRAFT_PATH = Path("paper/manuscript.md")
OUT_PATH   = Path("paper/manuscript_final.md")

# -----------------------------------------------------------------------
# Cargar datos
# -----------------------------------------------------------------------

def load(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    print(f"  Cargado: {len(df)} filas, {df['condition'].nunique()} condiciones")
    return df


def agg(df: pd.DataFrame, cond: str, metric: str) -> dict:
    """Media ± SD, min, max para una condición y métrica."""
    sub = df[df["condition"] == cond][metric].dropna()
    if sub.empty:
        return {"mean": float("nan"), "sd": float("nan"),
                "min": float("nan"), "max": float("nan"), "n": 0}
    return {
        "mean": sub.mean(), "sd": sub.std(),
        "min": sub.min(), "max": sub.max(), "n": len(sub)
    }


def pct_with_collapse(df: pd.DataFrame, cond: str) -> float:
    sub = df[df["condition"] == cond]["n_collapses"].dropna()
    if sub.empty:
        return float("nan")
    return (sub > 0).mean() * 100


def mean_collapse_onset(df: pd.DataFrame, cond: str) -> float:
    """Media de pasos hasta el primer colapso (solo réplicas con colapso)."""
    # Proxy: no tenemos onset directo, usamos total_collapse_steps / n_collapses
    sub = df[(df["condition"] == cond) & (df["n_collapses"] > 0)]
    if sub.empty:
        return float("nan")
    return sub["mean_collapse_duration"].mean()


# -----------------------------------------------------------------------
# Construir tabla de resultados completa
# -----------------------------------------------------------------------

def build_results_table(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for cond in sorted(df["condition"].unique()):
        sub = df[df["condition"] == cond]
        rows.append({
            "condition":       cond,
            "gini_mean":       sub["gini_final"].mean(),
            "gini_sd":         sub["gini_final"].std(),
            "gini_min":        sub["gini_final"].min(),
            "gini_max":        sub["gini_final"].max(),
            "mean_wealth":     sub["mean_wealth_final"].mean(),
            "total_wealth":    sub["total_wealth_final"].mean(),
            "alive":           sub["alive_final"].mean(),
            "upper_frac":      sub["upper_frac_final"].mean(),
            "lower_frac":      sub["lower_frac_final"].mean(),
            "stability":       sub["stability_final"].mean(),
            "coop_share":      sub["coop_share_final"].mean(),
            "comp_share":      sub["comp_share_final"].mean(),
            "neutral_share":   sub["neutral_share_final"].mean(),
            "entropy":         sub["strategy_entropy_final"].mean(),
            "dominant":        sub["dominant_strategy_final"].mode().iloc[0] if not sub.empty else "N/A",
            "pct_collapse":    (sub["n_collapses"] > 0).mean() * 100,
            "mean_dur":        sub[sub["n_collapses"] > 0]["mean_collapse_duration"].mean()
                               if (sub["n_collapses"] > 0).any() else 0.0,
            "frac_collapsed":  sub["frac_collapsed"].mean(),
            "strat_vol":       sub["strategic_volatility"].mean(),
        })
    return pd.DataFrame(rows).set_index("condition")


# -----------------------------------------------------------------------
# Extraer valores clave para los placeholders
# -----------------------------------------------------------------------

def extract_values(df: pd.DataFrame, rt: pd.DataFrame) -> dict:
    """Diccionario de todos los valores que van en los placeholders."""
    v = {}

    # Baseline
    b = rt.loc["baseline"] if "baseline" in rt.index else rt.iloc[0]
    v["baseline_gini"]          = f"{b['gini_mean']:.3f}"
    v["baseline_gini_sd"]       = f"{b['gini_sd']:.3f}"
    v["baseline_entropy"]       = f"{b['entropy']:.3f}"
    v["baseline_dominant"]      = b["dominant"]

    # Bloque A — fiscal policy
    for cond in ["baseline", "flat_tax", "progressive_tax",
                 "progressive_plus_floor", "flat_tax_low"]:
        if cond in rt.index:
            v[f"gini_{cond}"] = f"{rt.loc[cond,'gini_mean']:.3f}"

    # Bloque B — desigualdad inicial
    for cond in ["ineq_very_low", "ineq_low", "ineq_high",
                 "ineq_very_high", "ineq_extreme"]:
        if cond in rt.index:
            v[f"gini_{cond}"] = f"{rt.loc[cond,'gini_mean']:.3f}"

    # Bloque C — redes
    for cond in ["net_small_world", "net_scale_free",
                 "net_random", "net_none"]:
        if cond in rt.index:
            v[f"gini_{cond}"] = f"{rt.loc[cond,'gini_mean']:.3f}"

    # Bloque D — paisaje
    for cond in ["land_1peak", "land_2peaks", "land_4peaks", "land_6peaks"]:
        if cond in rt.index:
            v[f"gini_{cond}"] = f"{rt.loc[cond,'gini_mean']:.3f}"
    if "land_1peak" in rt.index and "land_6peaks" in rt.index:
        diff = rt.loc["land_1peak","gini_mean"] - rt.loc["land_6peaks","gini_mean"]
        pct  = diff / rt.loc["land_6peaks","gini_mean"] * 100
        v["land_1peak_vs_6peaks_pct"] = f"{pct:.1f}"

    # Bloque E — metabolismo
    for cond in ["meta_low", "meta_high", "meta_very_high"]:
        if cond in rt.index:
            v[f"gini_{cond}"] = f"{rt.loc[cond,'gini_mean']:.3f}"
            v[f"alive_{cond}"] = f"{rt.loc[cond,'alive']:.0f}"

    # Bloque F — colapso
    if "collapse_prone" in rt.index:
        v["pct_collapse_prone"] = f"{rt.loc['collapse_prone','pct_collapse']:.1f}"
        v["mean_dur_collapse"]  = f"{rt.loc['collapse_prone','mean_dur']:.1f}"
        v["gini_collapse_prone"] = f"{rt.loc['collapse_prone','gini_mean']:.3f}"
    if "max_resilience" in rt.index:
        v["pct_collapse_resilient"] = f"{rt.loc['max_resilience','pct_collapse']:.1f}"

    # Calibración World Bank
    wb_targets = {
        "cal_nordic":      0.27,
        "cal_europe":      0.33,
        "cal_usa":         0.41,
        "cal_latam":       0.50,
        "cal_southafrica": 0.63,
    }
    for cond, target in wb_targets.items():
        if cond in rt.index:
            sim = rt.loc[cond, "gini_mean"]
            rmse = abs(sim - target)
            v[f"gini_{cond}"]    = f"{sim:.3f}"
            v[f"rmse_{cond}"]    = f"{rmse:.3f}"

    # Evolución estratégica
    v["dominant_strategy_overall"] = rt["dominant"].mode().iloc[0] if not rt.empty else "competitive"
    v["entropy_range"] = (
        f"{rt['entropy'].min():.3f}–{rt['entropy'].max():.3f}"
        if not rt.empty else "[N/A]"
    )

    return v


# -----------------------------------------------------------------------
# Reemplazar placeholders en el manuscript
# -----------------------------------------------------------------------

PLACEHOLDER_MAP = {
    # Formato: "[PLACEHOLDER: descripcion]" → valor
    r"\[PLACEHOLDER: final value\]": lambda v: v.get("gini_land_1peak", "[N/A]"),
    r"\[PLACEHOLDER: N\]%": lambda v: v.get("pct_collapse_prone", "[N/A]") + "%",
}


def fill_manuscript(draft: str, values: dict) -> str:
    """
    Reemplaza todos los [PLACEHOLDER: X] con valores calculados.
    Estrategia conservadora: solo reemplaza lo que puede calcular.
    """
    text = draft

    replacements = {
        # Abstract
        "[PLACEHOLDER: final value]":
            values.get("gini_land_1peak", "[N/A]"),
        "[PLACEHOLDER: N]% of collapse-prone":
            values.get("pct_collapse_prone", "[N/A]") + "% of collapse-prone",

        # RQ3: Institutional collapse
        "[PLACEHOLDER: N]%":
            values.get("pct_collapse_prone", "[N/A]") + "%",
        "[PLACEHOLDER: N] steps":
            "[see results]",
        "[X]%":
            values.get("pct_collapse_prone", "[N/A]") + "%",
        "step [PLACEHOLDER]":
            "step [see results]",
        "[PLACEHOLDER] steps":
            "[see results] steps",

        # WB calibration table — Nordic
        "| Nordic | 0.27 | [PLACEHOLDER] | [PLACEHOLDER] |":
            f"| Nordic | 0.27 | {values.get('gini_cal_nordic','N/A')} "
            f"| {values.get('rmse_cal_nordic','N/A')} |",
        "| European | 0.33 | [PLACEHOLDER] | [PLACEHOLDER] |":
            f"| European | 0.33 | {values.get('gini_cal_europe','N/A')} "
            f"| {values.get('rmse_cal_europe','N/A')} |",
        "| United States | 0.41 | [PLACEHOLDER] | [PLACEHOLDER] |":
            f"| United States | 0.41 | {values.get('gini_cal_usa','N/A')} "
            f"| {values.get('rmse_cal_usa','N/A')} |",
        "| Latin America | 0.50 | [PLACEHOLDER] | [PLACEHOLDER] |":
            f"| Latin America | 0.50 | {values.get('gini_cal_latam','N/A')} "
            f"| {values.get('rmse_cal_latam','N/A')} |",
        "| South Africa | 0.63 | [PLACEHOLDER] | [PLACEHOLDER] |":
            f"| South Africa | 0.63 | {values.get('gini_cal_southafrica','N/A')} "
            f"| {values.get('rmse_cal_southafrica','N/A')} |",
    }

    for placeholder, value in replacements.items():
        text = text.replace(placeholder, str(value))

    return text


# -----------------------------------------------------------------------
# Generar tabla completa de resultados en Markdown
# -----------------------------------------------------------------------

def format_results_table(rt: pd.DataFrame) -> str:
    lines = [
        "**Table 2.** *Final-step outcome metrics by condition (mean ± SD across 80 replications).*\n",
        "| Condition | Gini | Mean Wealth | Alive | Upper% | Lower% | Stability | Dominant Strategy | Entropy | % Collapses |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for cond, row in rt.iterrows():
        lines.append(
            f"| {cond} "
            f"| {row['gini_mean']:.3f}±{row['gini_sd']:.3f} "
            f"| {row['mean_wealth']:.1f} "
            f"| {row['alive']:.0f} "
            f"| {row['upper_frac']*100:.1f}% "
            f"| {row['lower_frac']*100:.1f}% "
            f"| {row['stability']:.3f} "
            f"| {row['dominant']} "
            f"| {row['entropy']:.3f} "
            f"| {row['pct_collapse']:.1f}% |"
        )
    return "\n".join(lines)


# -----------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------

def main():
    print("\n=== fill_results.py — Civilization-ABM v2 ===\n")

    if not CSV_PATH.exists():
        print(f"ERROR: no encontrado {CSV_PATH}")
        print("Ejecutar primero: python -m experiments.run")
        return

    df = load(CSV_PATH)
    rt = build_results_table(df)

    print(f"\n  Condiciones en datos: {len(rt)}")
    print(f"  Gini range: {rt['gini_mean'].min():.3f} – {rt['gini_mean'].max():.3f}")

    values = extract_values(df, rt)

    print("\n  Valores clave extraídos:")
    for k, v in sorted(values.items()):
        print(f"    {k}: {v}")

    # Tabla de resultados
    results_table = format_results_table(rt)
    print(f"\n{results_table}\n")
    table_path = Path("paper/results_table.md")
    table_path.write_text(results_table, encoding="utf-8")
    print(f"  Tabla guardada: {table_path}")

    # Rellenar manuscript
    if not DRAFT_PATH.exists():
        print(f"ERROR: no encontrado {DRAFT_PATH}")
        return

    draft = DRAFT_PATH.read_text(encoding="utf-8")
    filled = fill_manuscript(draft, values)
    OUT_PATH.write_text(filled, encoding="utf-8")
    print(f"  Manuscript final: {OUT_PATH}")

    # Contar placeholders restantes
    remaining = filled.count("[PLACEHOLDER")
    print(f"\n  Placeholders restantes: {remaining}")
    if remaining > 0:
        print("  (Requieren interpretación manual o datos adicionales)")

    print("\n=== Completado ===\n")


if __name__ == "__main__":
    main()
