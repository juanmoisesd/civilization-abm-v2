"""
metrics.py — Métricas de análisis para Civilization-ABM v2.

Amplía las métricas de v1 con:
  - Theil T y L (descomposición intra/inter clases)
  - Palma ratio
  - Movilidad social (correlación intergeneracional de riqueza)
  - Índice de volatilidad estratégica
  - Resumen de colapsos institucionales
"""

import numpy as np
import pandas as pd
from scipy import stats


# -----------------------------------------------------------------------
# Métricas de distribución de riqueza
# -----------------------------------------------------------------------

def gini(wealths: np.ndarray) -> float:
    """Coeficiente de Gini. Devuelve 0 si todas las riquezas son iguales."""
    w = np.asarray(wealths, dtype=float)
    w = w[w > 0]
    if len(w) == 0 or w.sum() == 0:
        return 0.0
    sorted_w = np.sort(w)
    n = len(sorted_w)
    idx = np.arange(1, n + 1)
    return float(((2 * idx - n - 1) * sorted_w).sum() / (n * sorted_w.sum()))


def theil_t(wealths: np.ndarray) -> float:
    """
    Índice de Theil T (sensible a desigualdad en la parte alta).
    T = (1/N) Σ (x_i / μ) ln(x_i / μ)
    """
    w = np.asarray(wealths, dtype=float)
    w = w[w > 0]
    if len(w) == 0:
        return 0.0
    mu = w.mean()
    if mu == 0:
        return 0.0
    ratios = w / mu
    return float(np.mean(ratios * np.log(ratios + 1e-12)))


def theil_l(wealths: np.ndarray) -> float:
    """
    Índice de Theil L / MLD (sensible a desigualdad en la parte baja).
    L = (1/N) Σ ln(μ / x_i)
    """
    w = np.asarray(wealths, dtype=float)
    w = w[w > 0]
    if len(w) == 0:
        return 0.0
    mu = w.mean()
    if mu == 0:
        return 0.0
    return float(np.mean(np.log(mu / (w + 1e-12))))


def palma_ratio(wealths: np.ndarray) -> float:
    """
    Ratio de Palma: riqueza del decil superior / riqueza de los cuatro deciles inferiores.
    Captura la desigualdad extrema mejor que el Gini.
    """
    w = np.sort(np.asarray(wealths, dtype=float))
    n = len(w)
    if n == 0:
        return 0.0
    top_10_pct = w[int(n * 0.9):]
    bot_40_pct = w[:int(n * 0.4)]
    if bot_40_pct.sum() == 0:
        return float("inf")
    return float(top_10_pct.sum() / bot_40_pct.sum())


def lorenz_curve(wealths: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """
    Curva de Lorenz: (fracción acumulada de población, fracción acumulada de riqueza).
    """
    w = np.sort(np.asarray(wealths, dtype=float))
    n = len(w)
    cum_pop = np.linspace(0, 1, n + 1)
    cum_wealth = np.concatenate([[0], np.cumsum(w) / (w.sum() + 1e-12)])
    return cum_pop, cum_wealth


def top1_share(wealths: np.ndarray) -> float:
    """Fracción de la riqueza total en manos del 1% más rico."""
    w = np.sort(np.asarray(wealths, dtype=float))
    n = len(w)
    if n == 0 or w.sum() == 0:
        return 0.0
    top = w[max(0, int(n * 0.99)):]
    return float(top.sum() / w.sum())


def top10_share(wealths: np.ndarray) -> float:
    """Fracción de la riqueza total en manos del 10% más rico."""
    w = np.sort(np.asarray(wealths, dtype=float))
    n = len(w)
    if n == 0 or w.sum() == 0:
        return 0.0
    top = w[max(0, int(n * 0.90)):]
    return float(top.sum() / w.sum())


# -----------------------------------------------------------------------
# Métricas estratégicas y evolutivas
# -----------------------------------------------------------------------

def strategy_entropy(shares: dict) -> float:
    """Entropía de Shannon de la distribución estratégica."""
    h = 0.0
    for p in shares.values():
        if p > 0:
            h -= p * np.log2(p + 1e-12)
    return float(h)


def strategic_volatility(strategy_series: pd.Series) -> float:
    """
    Fracción de pasos en los que la estrategia dominante cambia.
    Mide la inestabilidad evolutiva del sistema.
    """
    if len(strategy_series) < 2:
        return 0.0
    changes = (strategy_series != strategy_series.shift(1)).sum()
    return float(changes / (len(strategy_series) - 1))


# -----------------------------------------------------------------------
# Métricas de colapso institucional
# -----------------------------------------------------------------------

def collapse_summary(regime_series: pd.Series) -> dict:
    """
    Analiza la serie de regímenes y extrae estadísticas de colapsos.

    Parámetros
    ----------
    regime_series : pd.Series
        Serie de strings 'stable'|'stressed'|'collapsed'|'recovering'

    Retorna
    -------
    dict con:
      n_collapses     — número de episodios de colapso
      total_collapse_steps — pasos totales en estado collapsed
      mean_collapse_duration — duración media de colapsos
      frac_collapsed  — fracción del tiempo en colapso
    """
    regimes = regime_series.values
    n = len(regimes)
    if n == 0:
        return {"n_collapses": 0, "total_collapse_steps": 0,
                "mean_collapse_duration": 0.0, "frac_collapsed": 0.0}

    collapsed = (regimes == "collapsed").astype(int)
    total_steps = int(collapsed.sum())

    # Contar episodios: transiciones 0→1
    n_collapses = int(np.sum(np.diff(np.concatenate([[0], collapsed, [0]])) == 1))

    mean_dur = total_steps / n_collapses if n_collapses > 0 else 0.0

    return {
        "n_collapses":           n_collapses,
        "total_collapse_steps":  total_steps,
        "mean_collapse_duration": float(mean_dur),
        "frac_collapsed":        float(total_steps / n),
    }


# -----------------------------------------------------------------------
# Resumen estadístico completo de una simulación
# -----------------------------------------------------------------------

def summary_statistics(model_df: pd.DataFrame) -> dict:
    """
    Genera estadísticas resumidas de una corrida a partir del DataFrame
    del DataCollector.

    Parámetros
    ----------
    model_df : pd.DataFrame
        model.datacollector.get_model_vars_dataframe()

    Retorna
    -------
    dict con métricas finales y de trayectoria.
    """
    if model_df.empty:
        return {}

    final = model_df.iloc[-1]
    gini_series = model_df["Gini"]

    result = {
        # Métricas finales
        "gini_final":       float(final.get("Gini", 0)),
        "mean_wealth_final": float(final.get("MeanWealth", 0)),
        "total_wealth_final": float(final.get("TotalWealth", 0)),
        "alive_final":      int(final.get("AliveAgents", 0)),
        "upper_frac_final": float(final.get("UpperClass", 0)),
        "lower_frac_final": float(final.get("LowerClass", 0)),
        "stability_final":  float(final.get("Stability", 1)),
        "regime_final":     str(final.get("Regime", "stable")),
        "coop_share_final": float(final.get("CoopShare", 0)),
        "comp_share_final": float(final.get("CompShare", 0)),
        "neutral_share_final": float(final.get("NeutralShare", 0)),
        "dominant_strategy_final": str(final.get("DominantStrategy", "neutral")),
        "strategy_entropy_final": float(final.get("StrategyEntropy", 0)),

        # Métricas de trayectoria
        "gini_mean":   float(gini_series.mean()),
        "gini_std":    float(gini_series.std()),
        "gini_max":    float(gini_series.max()),
        "gini_min":    float(gini_series.min()),
        "gini_trend":  float(stats.linregress(np.arange(len(gini_series)), gini_series).slope),
    }

    # Colapsos institucionales
    if "Regime" in model_df.columns:
        result.update(collapse_summary(model_df["Regime"]))

    # Volatilidad estratégica
    if "DominantStrategy" in model_df.columns:
        result["strategic_volatility"] = strategic_volatility(
            model_df["DominantStrategy"]
        )

    return result
