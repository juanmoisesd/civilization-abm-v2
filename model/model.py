"""
model.py — CivilModelV2: modelo principal de Civilization-ABM v2.

Integra:
  - ResourceLandscape: paisaje de recursos tipo Sugarscape.
  - CivilAgentV2: agentes con posición espacial y aprendizaje.
  - InstitutionalSystem: colapso y recuperación institucional.
  - Replicator dynamics: evolución estratégica.
  - DataCollector con métricas ampliadas.

Compatible con Mesa 3.x.
"""

import random as _random

import numpy as np
from mesa import Model
from mesa.datacollection import DataCollector

from .agents import CivilAgentV2
from .landscape import ResourceLandscape
from .rules import InstitutionalSystem
from .environment import build_small_world, build_scale_free, build_random, network_clustering
from .evolution import strategy_entropy, dominant_strategy, population_strategy_shares


# -----------------------------------------------------------------------
# Reporters del DataCollector
# -----------------------------------------------------------------------

def _gini(model) -> float:
    wealths = np.array([a.wealth for a in model.agents if a.alive])
    if len(wealths) == 0 or wealths.sum() == 0:
        return 0.0
    sorted_w = np.sort(wealths)
    n = len(sorted_w)
    idx = np.arange(1, n + 1)
    return float(((2 * idx - n - 1) * sorted_w).sum() / (n * sorted_w.sum()))


def _mean_wealth(model) -> float:
    vals = [a.wealth for a in model.agents if a.alive]
    return float(np.mean(vals)) if vals else 0.0


def _total_wealth(model) -> float:
    return float(sum(a.wealth for a in model.agents if a.alive))


def _upper_frac(model) -> float:
    alive = [a for a in model.agents if a.alive]
    return sum(1 for a in alive if a.social_class == "upper") / len(alive) if alive else 0.0


def _lower_frac(model) -> float:
    alive = [a for a in model.agents if a.alive]
    return sum(1 for a in alive if a.social_class == "lower") / len(alive) if alive else 0.0


def _alive_count(model) -> int:
    return sum(1 for a in model.agents if a.alive)


def _stability(model) -> float:
    return model.institutions.stability


def _regime(model) -> str:
    return model.institutions.regime


def _strategy_entropy_rep(model) -> float:
    return strategy_entropy(model)


def _dominant_strategy_rep(model) -> str:
    return dominant_strategy(model)


def _coop_share(model) -> float:
    return population_strategy_shares(model).get("cooperative", 0.0)


def _comp_share(model) -> float:
    return population_strategy_shares(model).get("competitive", 0.0)


def _neutral_share(model) -> float:
    return population_strategy_shares(model).get("neutral", 0.0)


def _landscape_gini(model) -> float:
    return model.landscape.gini_landscape()


def _total_resources(model) -> float:
    return model.landscape.total_resources()


def _clustering(model) -> float:
    if model.network is not None:
        return network_clustering(model.network)
    return 0.0


# -----------------------------------------------------------------------
# Modelo
# -----------------------------------------------------------------------

class CivilModelV2(Model):
    """
    Civilización artificial v2 con recursos espaciales, evolución
    estratégica y colapso institucional.

    Parámetros
    ----------
    N : int
        Número de agentes.
    initial_inequality : float
        Sigma del lognormal para la riqueza inicial.
    tax_policy : str | None
        'flat' | 'progressive' | None
    network_type : str | None
        'small_world' | 'scale_free' | 'random' | None
    enforce_floor : bool
        Activar piso de riqueza mínima.
    landscape_width, landscape_height : int
        Dimensiones del paisaje.
    landscape_peaks : int
        Picos de recursos en el paisaje.
    growth_rate : int
        Tasa de regeneración de recursos por celda.
    vision : int
        Radio de visión de los agentes para moverse.
    metabolism : float
        Coste de subsistencia por paso por agente.
    mutation_rate : float
        Tasa de mutación estratégica (replicator dynamics).
    evolution_interval : int
        Cada cuántos pasos ocurre el aprendizaje evolutivo.
    seed : int | None
        Semilla para reproducibilidad.
    """

    def __init__(
        self,
        N: int = 100,
        initial_inequality: float = 0.8,
        tax_policy: str = "progressive",
        network_type: str = "small_world",
        enforce_floor: bool = False,
        landscape_width: int = 35,
        landscape_height: int = 35,
        landscape_peaks: int = 3,
        growth_rate: float = 0.5,
        vision: int = 1,
        metabolism: float = 1.0,
        mutation_rate: float = 0.02,
        evolution_interval: int = 5,
        seed: int = None,
    ):
        super().__init__(rng=seed)

        self.num_agents = N
        self.tax_policy = tax_policy
        self.enforce_floor = enforce_floor
        self.vision = vision
        self.mutation_rate = mutation_rate
        self.evolution_interval = evolution_interval
        self._step_count = 0

        if seed is not None:
            _random.seed(seed)
            np.random.seed(seed)

        # Metabolismo base (los agentes generan el suyo propio con dispersión lognormal)
        self.base_metabolism = metabolism

        # Paisaje de recursos — max_capacity=20 para mayor heterogeneidad espacial
        self.landscape = ResourceLandscape(
            width=landscape_width,
            height=landscape_height,
            max_capacity=20,
            growth_rate=growth_rate,
            n_peaks=landscape_peaks,
            seed=seed,
        )

        # Sistema institucional
        self.institutions = InstitutionalSystem()

        # Colocar agentes en celdas libres aleatorias del paisaje
        rng = np.random.default_rng(seed)
        all_cells = [
            (x, y)
            for x in range(landscape_width)
            for y in range(landscape_height)
        ]
        rng.shuffle(all_cells)
        cells = all_cells[:N]

        for i in range(N):
            x, y = cells[i]
            wealth = max(1.0, _random.lognormvariate(2.3, initial_inequality))
            # metabolism=None → el agente genera el suyo desde lognormal(0, 0.6)*base
            agent = CivilAgentV2(
                self,
                x=x,
                y=y,
                initial_wealth=wealth,
                metabolism=None,
            )
            self.landscape.place_agent(agent.unique_id, x, y)

        # Red social
        self.network = None
        agent_list = list(self.agents)
        if network_type == "small_world":
            self.network = build_small_world(agent_list)
        elif network_type == "scale_free":
            self.network = build_scale_free(agent_list)
        elif network_type == "random":
            self.network = build_random(agent_list)

        # DataCollector
        self.datacollector = DataCollector(
            model_reporters={
                "Gini":              _gini,
                "MeanWealth":        _mean_wealth,
                "TotalWealth":       _total_wealth,
                "AliveAgents":       _alive_count,
                "UpperClass":        _upper_frac,
                "LowerClass":        _lower_frac,
                "Stability":         _stability,
                "Regime":            _regime,
                "StrategyEntropy":   _strategy_entropy_rep,
                "DominantStrategy":  _dominant_strategy_rep,
                "CoopShare":         _coop_share,
                "CompShare":         _comp_share,
                "NeutralShare":      _neutral_share,
                "LandscapeGini":     _landscape_gini,
                "TotalResources":    _total_resources,
                "NetworkClustering": _clustering,
            },
            agent_reporters={
                "Wealth":      "wealth",
                "Reputation":  "reputation",
                "Strategy":    "strategy",
                "SocialClass": "social_class",
                "Metabolism":  "metabolism",
                "Vision":      "vision",
                "X":           "x",
                "Y":           "y",
                "Alive":       "alive",
            },
        )

    # ------------------------------------------------------------------
    # Propiedad de riqueza media
    # ------------------------------------------------------------------

    @property
    def mean_wealth(self) -> float:
        vals = [a.wealth for a in self.agents if a.alive]
        return sum(vals) / len(vals) if vals else 0.0

    # ------------------------------------------------------------------
    # Mapa id → agente (usado por evolution y agents)
    # ------------------------------------------------------------------

    def _agent_map(self) -> dict:
        return {a.unique_id: a for a in self.agents}

    # ------------------------------------------------------------------
    # Paso del modelo
    # ------------------------------------------------------------------

    def step(self):
        # 1. Recolectar datos al inicio del paso
        self.datacollector.collect(self)

        # 2. Paisaje: crecer recursos
        self.landscape.grow()

        # 3. Actualizar sistema institucional (antes de aplicar reglas)
        self.institutions.update(self)

        # 4. Paso de cada agente (movimiento, cosecha, interacción)
        self.agents.shuffle_do("step")

        # 5. Aplicar instituciones (impuestos, piso, caos)
        self.institutions.apply_institutions(self)

        # 6. Eliminar agentes muertos del paisaje
        self._remove_dead_agents()

        self._step_count += 1

    def _remove_dead_agents(self):
        """Libera celdas ocupadas por agentes que murieron este paso."""
        for agent in list(self.agents):
            if not agent.alive:
                self.landscape.remove_agent(agent.unique_id, agent.x, agent.y)
                agent.remove()
