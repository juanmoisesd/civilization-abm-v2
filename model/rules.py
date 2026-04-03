"""
rules.py — Reglas institucionales y sistema de colapso institucional.

v2 añade:
  - InstitutionalSystem: índice de estabilidad, umbrales de colapso/recuperación.
  - Régimen dinámico: 'stable' | 'stressed' | 'collapsed' | 'recovering'
  - Las reglas fiscales se atenúan o suspenden durante el colapso.

Compatible con Mesa 3.x: usa model.agents (AgentSet).
"""

import numpy as np


# -----------------------------------------------------------------------
# Reglas fiscales (idénticas a v1, funcionan sobre model.agents)
# -----------------------------------------------------------------------

def flat_tax(model, rate: float = 0.01) -> float:
    """Impuesto proporcional; ingresos redistribuidos de forma igualitaria."""
    agents = list(model.agents)
    collected = []
    for agent in agents:
        if not agent.alive:
            continue
        tax = agent.wealth * rate
        agent.wealth -= tax
        collected.append(tax)

    total = sum(collected)
    active = [a for a in agents if a.alive]
    share = total / len(active) if active else 0.0
    for agent in active:
        agent.wealth += share

    return total


def progressive_tax(model, brackets=None) -> float:
    """
    Impuesto progresivo por tramos de riqueza.

    brackets : list of (threshold, rate)
        Defecto: [(20, 0.05), (50, 0.10), (inf, 0.20)]
    """
    if brackets is None:
        # Tasas por step: 0.5% / 1% / 2%
        # (aplicadas cada paso; equivalen a ~10%/20%/40% anual si un año = 20 pasos)
        brackets = [(20, 0.005), (50, 0.010), (float("inf"), 0.020)]

    agents = list(model.agents)
    collected = []
    for agent in agents:
        if not agent.alive:
            continue
        for threshold, rate in brackets:
            if agent.wealth <= threshold:
                tax = agent.wealth * rate
                break
        else:
            tax = agent.wealth * brackets[-1][1]
        agent.wealth = max(0.0, agent.wealth - tax)
        collected.append(tax)

    total = sum(collected)
    active = [a for a in agents if a.alive]
    share = total / len(active) if active else 0.0
    for agent in active:
        agent.wealth += share

    return total


def reputation_penalty(model, threshold: float = 0.3, penalty: float = 0.1):
    """Sanción económica a agentes con reputación por debajo del umbral."""
    for agent in model.agents:
        if agent.alive and agent.reputation < threshold:
            agent.wealth = max(0.0, agent.wealth - penalty)


def enforce_minimum_wealth(model, minimum: float = 1.0):
    """
    Piso social: transfiere riqueza de los más ricos a quienes
    están por debajo del mínimo.
    """
    agents = [a for a in model.agents if a.alive]
    deficit = sum(max(0.0, minimum - a.wealth) for a in agents)
    if deficit == 0:
        return

    rich = [a for a in agents if a.wealth > minimum * 2]
    if not rich:
        return

    contrib_per = deficit / len(rich)
    for agent in rich:
        agent.wealth = max(minimum, agent.wealth - contrib_per)

    for agent in agents:
        if agent.wealth < minimum:
            agent.wealth = minimum


# -----------------------------------------------------------------------
# Sistema institucional con colapso y recuperación
# -----------------------------------------------------------------------

class InstitutionalSystem:
    """
    Gestiona la estabilidad institucional de la civilización.

    La estabilidad es un índice continuo en [0, 1]:
      - 1.0 = instituciones plenamente funcionales
      - 0.0 = colapso total

    Régimen:
      'stable'     → estabilidad ≥ stable_threshold
      'stressed'   → collapse_threshold ≤ estabilidad < stable_threshold
      'collapsed'  → estabilidad < collapse_threshold
      'recovering' → estabilidad ≥ collapse_threshold tras colapso

    Efectos del régimen sobre las reglas fiscales:
      - stable:     impuestos al 100 %
      - stressed:   impuestos al 60 %
      - collapsed:  impuestos suspendidos; coste de caos
      - recovering: impuestos al 30 %

    Parámetros
    ----------
    collapse_threshold : float
        Estabilidad mínima para evitar colapso (defecto 0.25).
    stable_threshold : float
        Estabilidad mínima para régimen estable (defecto 0.65).
    recovery_rate : float
        Incremento de estabilidad por paso durante recuperación.
    decay_factor : float
        Factor multiplicativo de deterioro por alta desigualdad.
    chaos_cost : float
        Pérdida de riqueza por agente por paso en estado 'collapsed'.
    """

    def __init__(
        self,
        collapse_threshold: float = 0.25,
        stable_threshold: float = 0.65,
        recovery_rate: float = 0.02,
        decay_factor: float = 0.015,
        chaos_cost: float = 0.5,
    ):
        self.collapse_threshold = collapse_threshold
        self.stable_threshold = stable_threshold
        self.recovery_rate = recovery_rate
        self.decay_factor = decay_factor
        self.chaos_cost = chaos_cost

        self.stability = 1.0
        self.regime = "stable"
        self._in_collapse = False

        # Historial para análisis
        self.stability_history = []
        self.regime_history = []
        self.collapse_events = []   # pasos en que ocurrió colapso
        self.recovery_events = []   # pasos en que comenzó recuperación

    # ------------------------------------------------------------------

    def update(self, model):
        """
        Actualiza el índice de estabilidad y el régimen.

        La estabilidad decae cuando la desigualdad (Gini) es alta y
        crece orgánicamente cuando la sociedad está en fase de recuperación.

        Llamar una vez por paso del modelo, ANTES de aplicar reglas fiscales.
        """
        step = model._step_count

        # Calcular Gini actual
        wealths = np.array([a.wealth for a in model.agents if a.alive])
        if len(wealths) == 0 or wealths.sum() == 0:
            gini = 0.0
        else:
            sorted_w = np.sort(wealths)
            n = len(sorted_w)
            idx = np.arange(1, n + 1)
            gini = float(((2 * idx - n - 1) * sorted_w).sum() / (n * sorted_w.sum()))

        # Fracción de población en clase baja (presión social)
        alive = [a for a in model.agents if a.alive]
        lower_frac = (
            sum(1 for a in alive if a.social_class == "lower") / len(alive)
            if alive else 0.0
        )

        # Deterioro proporcional a desigualdad y concentración de pobreza
        deterioration = self.decay_factor * (gini + lower_frac * 0.5)
        self.stability = max(0.0, self.stability - deterioration)

        # Recuperación orgánica si no está en colapso
        if self._in_collapse:
            # Durante colapso: recuperación lenta
            self.stability = min(1.0, self.stability + self.recovery_rate * 0.5)
            if self.stability >= self.collapse_threshold:
                self._in_collapse = False
                self.regime = "recovering"
                self.recovery_events.append(step)
        else:
            # Pequeña recuperación natural en régimen no colapsado
            self.stability = min(1.0, self.stability + self.recovery_rate * 0.1)

        # Determinar régimen
        if self.stability < self.collapse_threshold:
            if not self._in_collapse:
                self._in_collapse = True
                self.collapse_events.append(step)
            self.regime = "collapsed"
        elif self.stability < self.stable_threshold:
            if self._in_collapse:
                self.regime = "recovering"
            else:
                self.regime = "stressed"
        else:
            self._in_collapse = False
            self.regime = "stable"

        self.stability_history.append(self.stability)
        self.regime_history.append(self.regime)

    def tax_multiplier(self) -> float:
        """Factor de efectividad fiscal según el régimen."""
        return {
            "stable":    1.0,
            "stressed":  0.6,
            "recovering": 0.3,
            "collapsed": 0.0,
        }.get(self.regime, 1.0)

    def apply_chaos(self, model):
        """
        En estado 'collapsed', cada agente sufre pérdida de riqueza
        (pillaje, destrucción de capital, coste del caos).
        """
        if self.regime != "collapsed":
            return
        for agent in model.agents:
            if agent.alive:
                agent.wealth = max(0.0, agent.wealth - self.chaos_cost)

    # ------------------------------------------------------------------

    def apply_institutions(self, model):
        """
        Aplica todas las reglas institucionales al modelo,
        moduladas por el régimen actual.

        Llamar en CivilModelV2.step() después de agents.shuffle_do.
        """
        mult = self.tax_multiplier()

        if mult > 0:
            if model.tax_policy == "flat":
                flat_tax(model, rate=0.01 * mult)
            elif model.tax_policy == "progressive":
                if mult < 1.0:
                    reduced_brackets = [
                        (thr, rate * mult)
                        for thr, rate in [(20, 0.005), (50, 0.010), (float("inf"), 0.020)]
                    ]
                    progressive_tax(model, brackets=reduced_brackets)
                else:
                    progressive_tax(model)

        reputation_penalty(model)

        if model.enforce_floor:
            enforce_minimum_wealth(model, minimum=1.0)

        self.apply_chaos(model)
