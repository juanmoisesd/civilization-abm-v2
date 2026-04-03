"""
main.py — Punto de entrada de Civilization-ABM v2.

Uso rápido:
    python main.py                        # run baseline, 200 steps, 1 rep
    python main.py --steps 300 --reps 5   # varias réplicas
    python main.py --experiments          # todos los experimentos del YAML
    python main.py --calibrate            # calibración con Banco Mundial

Para experimentos en paralelo completos (usa todos los CPUs):
    python -m experiments.run
"""

import argparse
import time
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")   # sin ventana gráfica para ejecución en background

from model.model import CivilModelV2
from analysis.metrics import summary_statistics, gini
from analysis.plots import (
    plot_baseline_panel,
    plot_strategy_evolution,
    plot_institutional_collapse,
    plot_landscape_snapshot,
)


def run_single(
    N: int = 100,
    steps: int = 200,
    tax_policy: str = "progressive",
    network_type: str = "small_world",
    initial_inequality: float = 0.8,
    enforce_floor: bool = False,
    landscape_peaks: int = 2,
    seed: int = 42,
    output_dir: str = "results/v2/quick",
    plot: bool = True,
    verbose: bool = True,
) -> dict:
    """Ejecuta una sola simulación y opcionalmente genera figuras."""
    if verbose:
        print(f"\nCivilization-ABM v2 — Simulación rápida")
        print(f"  N={N}, steps={steps}, tax={tax_policy}, net={network_type}")
        print(f"  inequality={initial_inequality}, floor={enforce_floor}")
        print(f"  peaks={landscape_peaks}, seed={seed}")

    t0 = time.time()
    model = CivilModelV2(
        N=N,
        tax_policy=tax_policy,
        network_type=network_type,
        initial_inequality=initial_inequality,
        enforce_floor=enforce_floor,
        landscape_peaks=landscape_peaks,
        seed=seed,
    )

    for step in range(steps):
        model.step()
        alive = sum(1 for a in model.agents if a.alive)
        if alive < 2:
            if verbose:
                print(f"  Población colapsó en paso {step}")
            break
        if verbose and step % 50 == 0:
            df_tmp = model.datacollector.get_model_vars_dataframe()
            g = df_tmp["Gini"].iloc[-1] if len(df_tmp) > 0 else 0
            print(f"  Step {step:4d} | Alive={alive:3d} | Gini={g:.3f} | "
                  f"Regime={model.institutions.regime}")

    elapsed = time.time() - t0
    model_df = model.datacollector.get_model_vars_dataframe()
    stats = summary_statistics(model_df)

    if verbose:
        print(f"\n  Completado en {elapsed:.1f}s")
        print(f"  Gini final:       {stats.get('gini_final', 0):.3f}")
        print(f"  Estabilidad:      {stats.get('stability_final', 0):.3f}")
        print(f"  Régimen final:    {stats.get('regime_final', 'N/A')}")
        print(f"  Estrategia dom.:  {stats.get('dominant_strategy_final', 'N/A')}")
        print(f"  Colapsos:         {stats.get('n_collapses', 0)}")
        print(f"  Agentes vivos:    {stats.get('alive_final', 0)}/{N}")

    if plot:
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)

        plot_baseline_panel(model_df, output_path=str(out / "baseline_panel.png"))
        plot_strategy_evolution(model_df, output_path=str(out / "strategy_evolution.png"))
        plot_institutional_collapse(model_df, output_path=str(out / "institutional_collapse.png"))
        plot_landscape_snapshot(model, output_path=str(out / "landscape_snapshot.png"))

        if verbose:
            print(f"  Figuras en: {out}")

    return stats


def run_replications(
    n_reps: int = 10,
    steps: int = 200,
    seed_base: int = 42,
    **model_kwargs,
) -> pd.DataFrame:
    """Ejecuta múltiples réplicas y devuelve DataFrame con estadísticas."""
    results = []
    for rep in range(n_reps):
        seed = seed_base + rep * 137
        stats = run_single(
            steps=steps, seed=seed, plot=False, verbose=False,
            **model_kwargs
        )
        stats["rep"] = rep
        stats["seed"] = seed
        results.append(stats)
        print(f"  Réplica {rep+1}/{n_reps} | Gini={stats.get('gini_final', 0):.3f} | "
              f"Colapsos={stats.get('n_collapses', 0)}")

    return pd.DataFrame(results)


def main():
    parser = argparse.ArgumentParser(description="Civilization-ABM v2")
    parser.add_argument("--steps", type=int, default=200)
    parser.add_argument("--agents", type=int, default=100)
    parser.add_argument("--reps", type=int, default=1)
    parser.add_argument("--tax", type=str, default="progressive",
                        choices=["flat", "progressive", "none"])
    parser.add_argument("--network", type=str, default="small_world",
                        choices=["small_world", "scale_free", "random", "none"])
    parser.add_argument("--inequality", type=float, default=0.8)
    parser.add_argument("--floor", action="store_true")
    parser.add_argument("--peaks", type=int, default=2)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=str, default="results/v2/quick")
    parser.add_argument("--experiments", action="store_true",
                        help="Run full experiment suite from YAML config")
    parser.add_argument("--calibrate", action="store_true",
                        help="Run World Bank calibration")
    parser.add_argument("--no-plot", action="store_true")
    args = parser.parse_args()

    tax = None if args.tax == "none" else args.tax
    network = None if args.network == "none" else args.network

    if args.experiments:
        import subprocess
        import sys
        cmd = [sys.executable, "-m", "experiments.run"]
        if args.calibrate:
            cmd.append("--calibrate")
        subprocess.run(cmd, cwd=Path(__file__).parent)
        return

    if args.calibrate:
        from calibration.fitting import grid_search_calibration, CalibrationConfig
        print("Iniciando calibración con datos del Banco Mundial...")
        cal_df = grid_search_calibration(
            CalibrationConfig(steps=150, replications=5),
            use_worldbank=True,
            verbose=True,
        )
        Path(args.output).mkdir(parents=True, exist_ok=True)
        cal_df.to_csv(Path(args.output) / "calibration.csv", index=False)
        print(cal_df.head(5).to_string())
        return

    if args.reps == 1:
        run_single(
            N=args.agents,
            steps=args.steps,
            tax_policy=tax,
            network_type=network,
            initial_inequality=args.inequality,
            enforce_floor=args.floor,
            landscape_peaks=args.peaks,
            seed=args.seed,
            output_dir=args.output,
            plot=not args.no_plot,
        )
    else:
        print(f"\nEjecutando {args.reps} réplicas...")
        df = run_replications(
            n_reps=args.reps,
            steps=args.steps,
            seed_base=args.seed,
            N=args.agents,
            tax_policy=tax,
            network_type=network,
            initial_inequality=args.inequality,
            enforce_floor=args.floor,
            landscape_peaks=args.peaks,
        )
        out = Path(args.output)
        out.mkdir(parents=True, exist_ok=True)
        df.to_csv(out / "replications.csv", index=False)
        print(f"\nResumen ({args.reps} réplicas):")
        print(f"  Gini final:  {df['gini_final'].mean():.3f} ± {df['gini_final'].std():.3f}")
        print(f"  Colapsos:    {df['n_collapses'].mean():.1f} ± {df['n_collapses'].std():.1f}")
        print(f"  Resultados:  {out / 'replications.csv'}")


if __name__ == "__main__":
    main()
