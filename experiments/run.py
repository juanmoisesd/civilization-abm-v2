"""
run.py — Runner paralelo de experimentos para Civilization-ABM v2.

Usa multiprocessing para aprovechar todos los núcleos disponibles.
Lee la configuración de configs_v2.yaml y produce:
  - results/v2/all_conditions.csv   — datos agregados por condición
  - results/v2/timeseries/          — series temporales por condición
  - results/v2/figures/             — figuras de publicación

Uso:
    python -m experiments.run                    # todas las condiciones
    python -m experiments.run --condition baseline  # solo una condición
    python -m experiments.run --calibrate        # calibración WB primero
"""

import argparse
import multiprocessing as mp
import time
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from tqdm import tqdm

from model.model import CivilModelV2
from analysis.metrics import summary_statistics
from analysis.plots import (
    plot_baseline_panel,
    plot_strategy_evolution,
    plot_institutional_collapse,
    plot_results_heatmap,
    plot_comparison_panel,
)

# ------------------------------------------------------------------
# Constantes
# ------------------------------------------------------------------

CONFIGS_PATH = Path(__file__).parent / "configs_v2.yaml"
RESULTS_DIR = Path("results/v2")
FIGURES_DIR = RESULTS_DIR / "figures"
TIMESERIES_DIR = RESULTS_DIR / "timeseries"


# ------------------------------------------------------------------
# Worker — ejecuta una sola replicación
# ------------------------------------------------------------------

def _run_replication(task: dict) -> dict:
    """
    Ejecuta una sola replicación y devuelve métricas de resumen.

    Diseñado para ser llamado por multiprocessing.Pool.
    """
    condition = task["condition"]
    rep = task["rep"]
    seed = task["seed"]
    steps = task["steps"]
    params = task["params"]

    try:
        model = CivilModelV2(seed=seed, **params)
        for step in range(steps):
            model.step()
            # Parar si la población colapsa completamente
            if sum(1 for a in model.agents if a.alive) < 2:
                break

        model_df = model.datacollector.get_model_vars_dataframe()
        stats = summary_statistics(model_df)
        stats["condition"] = condition
        stats["rep"] = rep
        stats["seed"] = seed
        stats["actual_steps"] = model._step_count
        return stats

    except Exception as e:
        return {
            "condition": condition,
            "rep": rep,
            "seed": seed,
            "error": str(e),
        }


def _run_replication_with_timeseries(task: dict) -> tuple[dict, pd.DataFrame]:
    """
    Igual que _run_replication pero también devuelve la serie temporal.
    Usado para generar figuras de la condición baseline.
    """
    condition = task["condition"]
    rep = task["rep"]
    seed = task["seed"]
    steps = task["steps"]
    params = task["params"]

    model = CivilModelV2(seed=seed, **params)
    for _ in range(steps):
        model.step()
        if sum(1 for a in model.agents if a.alive) < 2:
            break

    model_df = model.datacollector.get_model_vars_dataframe()
    stats = summary_statistics(model_df)
    stats["condition"] = condition
    stats["rep"] = rep
    stats["seed"] = seed
    stats["actual_steps"] = model._step_count

    return stats, model_df, model


# ------------------------------------------------------------------
# Cargar configuración
# ------------------------------------------------------------------

def load_config(path: Path = CONFIGS_PATH) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def build_tasks(config: dict, condition_filter: str = None) -> list[dict]:
    """Construye la lista de tareas a ejecutar."""
    global_cfg = config["global"]
    steps = global_cfg["steps"]
    replications = global_cfg["replications"]
    seed_base = global_cfg.get("seed_base", 42)

    # Parámetros del modelo que se extraen del global
    global_model_params = {
        "N":                global_cfg.get("N", 150),
        "landscape_width":  global_cfg.get("landscape_width", 25),
        "landscape_height": global_cfg.get("landscape_height", 25),
        "growth_rate":      global_cfg.get("growth_rate", 1),
        "vision":           global_cfg.get("vision", 1),
        "metabolism":       global_cfg.get("metabolism", 1.0),
        "mutation_rate":    global_cfg.get("mutation_rate", 0.02),
        "evolution_interval": global_cfg.get("evolution_interval", 5),
    }

    tasks = []
    for cond in config["conditions"]:
        name = cond["name"]
        if condition_filter and name != condition_filter:
            continue

        # Parámetros de la condición sobreescriben los globales
        params = {**global_model_params}
        overridable = [
            "initial_inequality", "tax_policy", "network_type",
            "enforce_floor", "landscape_peaks", "metabolism",
            "growth_rate", "mutation_rate", "evolution_interval", "N",
        ]
        for key in overridable:
            if key in cond:
                params[key] = cond[key]

        for rep in range(replications):
            seed = seed_base * 1000 + hash(name) % 10000 + rep
            tasks.append({
                "condition": name,
                "rep": rep,
                "seed": int(seed) % (2**31),
                "steps": steps,
                "params": params,
            })

    return tasks


def _build_condition_params_df(config: dict) -> pd.DataFrame:
    """
    Construye un DataFrame con los parámetros de cada condición del YAML.
    Se usa para enriquecer results_df antes de los heatmaps.
    """
    rows = []
    for c in config["conditions"]:
        rows.append({
            "condition":          c["name"],
            "tax_policy":         str(c.get("tax_policy", "none")),
            "initial_inequality": float(c.get("initial_inequality", 0.8)),
            "network_type":       str(c.get("network_type", "none")),
            "enforce_floor":      bool(c.get("enforce_floor", False)),
            "landscape_peaks":    int(c.get("landscape_peaks", 2)),
        })
    return pd.DataFrame(rows)


# ------------------------------------------------------------------
# Runner principal
# ------------------------------------------------------------------

def run_all_conditions(
    config: dict,
    condition_filter: str = None,
    n_jobs: int = None,
    verbose: bool = True,
) -> pd.DataFrame:
    """
    Ejecuta todas las condiciones en paralelo.

    Retorna
    -------
    pd.DataFrame con una fila por replicación.
    """
    tasks = build_tasks(config, condition_filter)
    if not tasks:
        print(f"No se encontró condición: {condition_filter}")
        return pd.DataFrame()

    n_jobs = n_jobs or config["global"].get("n_jobs", mp.cpu_count())
    n_jobs = min(n_jobs, mp.cpu_count())

    if verbose:
        n_conds = len(set(t["condition"] for t in tasks))
        print(f"\nCivilization-ABM v2 — Experimentos")
        print(f"  Condiciones: {n_conds}")
        print(f"  Tareas totales: {len(tasks)}")
        print(f"  CPUs: {n_jobs}")
        print(f"  Inicio: {time.strftime('%H:%M:%S')}\n")

    t0 = time.time()

    with mp.Pool(processes=n_jobs) as pool:
        iterator = pool.imap_unordered(_run_replication, tasks, chunksize=2)
        if verbose:
            iterator = tqdm(iterator, total=len(tasks), desc="Simulando")
        results = list(iterator)

    elapsed = time.time() - t0
    if verbose:
        print(f"\n  Completado en {elapsed:.1f}s ({elapsed/len(tasks):.2f}s/tarea)")

    df = pd.DataFrame(results)
    return df


# ------------------------------------------------------------------
# Generación de figuras
# ------------------------------------------------------------------

def generate_figures(config: dict, results_df: pd.DataFrame, verbose: bool = True):
    """
    Genera las figuras de publicación a partir de los resultados.
    Ejecuta una replicación representativa del baseline para las series temporales.
    """
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    if verbose:
        print("\nGenerando figuras...")

    # Replicación baseline para plots de series temporales
    baseline_candidates = ["baseline", config["conditions"][0]["name"]]
    existing_conditions = set(results_df["condition"].unique()) if "condition" in results_df.columns else set()
    baseline_name = next(
        (c for c in baseline_candidates if c in existing_conditions),
        config["conditions"][0]["name"]
    )

    tasks = build_tasks(config, condition_filter=baseline_name)
    if tasks:
        _, model_df, model = _run_replication_with_timeseries(tasks[0])

        plot_baseline_panel(
            model_df,
            output_path=str(FIGURES_DIR / "Figure_1_baseline_panel.png")
        )
        plot_strategy_evolution(
            model_df,
            output_path=str(FIGURES_DIR / "Figure_2_strategy_evolution.png")
        )
        plot_institutional_collapse(
            model_df,
            output_path=str(FIGURES_DIR / "Figure_3_institutional_collapse.png")
        )

    # Heatmap: enriquecer results_df con parámetros del YAML antes del pivot
    if len(results_df) > 0 and "gini_final" in results_df.columns:
        params_df = _build_condition_params_df(config)
        enriched = results_df.merge(params_df, on="condition", how="left")

        # Solo generar heatmap si hay variación real en ambas dimensiones
        if (enriched["tax_policy"].nunique() > 1
                and enriched["initial_inequality"].nunique() > 1):
            plot_results_heatmap(
                enriched,
                metric="gini_final",
                row_var="tax_policy",
                col_var="initial_inequality",
                output_path=str(FIGURES_DIR / "Figure_4_gini_heatmap.png")
            )
        elif verbose:
            print("  (Figura 4 omitida: insuficiente variación de parámetros)")

        plot_comparison_panel(
            results_df,
            output_path=str(FIGURES_DIR / "Figure_5_comparison_panel.png")
        )

    if verbose:
        print(f"  Figuras guardadas en: {FIGURES_DIR}")


# ------------------------------------------------------------------
# Punto de entrada
# ------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Civilization-ABM v2 experiments")
    parser.add_argument("--condition", type=str, default=None,
                        help="Run only this condition (by name)")
    parser.add_argument("--calibrate", action="store_true",
                        help="Run World Bank calibration before experiments")
    parser.add_argument("--jobs", type=int, default=None,
                        help="Number of parallel workers (default: all CPUs)")
    parser.add_argument("--no-figures", action="store_true",
                        help="Skip figure generation")
    args = parser.parse_args()

    config = load_config()
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    TIMESERIES_DIR.mkdir(parents=True, exist_ok=True)

    # Calibración opcional
    if args.calibrate:
        print("Calibración con datos del Banco Mundial...")
        from calibration.fitting import grid_search_calibration, CalibrationConfig
        cal_config = CalibrationConfig(
            steps=150,
            replications=5,
            n_jobs=args.jobs or config["global"].get("n_jobs", 4),
        )
        cal_df = grid_search_calibration(cal_config, use_worldbank=True, verbose=True)
        cal_path = RESULTS_DIR / "calibration_results.csv"
        cal_df.to_csv(cal_path, index=False)
        print(f"Calibración guardada en: {cal_path}")
        print(f"\nTop 5 configuraciones calibradas:")
        print(cal_df.head())

    # Ejecutar experimentos
    results = run_all_conditions(
        config,
        condition_filter=args.condition,
        n_jobs=args.jobs,
        verbose=True,
    )

    if results.empty:
        print("Sin resultados. Verificar configuración.")
        return

    # Guardar resultados
    out_path = RESULTS_DIR / "all_conditions.csv"
    results.to_csv(out_path, index=False)
    print(f"\nResultados guardados: {out_path}")
    print(f"  {len(results)} filas, {len(results.columns)} columnas")

    # Resumen por condición
    if "condition" in results.columns and "gini_final" in results.columns:
        summary = results.groupby("condition")["gini_final"].agg(
            ["mean", "std", "min", "max"]
        ).round(3)
        print(f"\nGini final por condición:")
        print(summary.to_string())

    # Generar figuras
    if not args.no_figures:
        generate_figures(config, results, verbose=True)

    print(f"\nExperimentos completados. {time.strftime('%H:%M:%S')}")


if __name__ == "__main__":
    main()
