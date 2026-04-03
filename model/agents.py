"""
agents.py — Agente de Civilization-ABM v2.

Extiende el agente v1 con:
  - Posición espacial (x, y) en el ResourceLandscape.
  - Cosecha de recursos del paisaje.
  - Gancho de aprendizaje evolutivo (replicator dynamics).
  - Metabolismo: coste de subsistencia por paso.

Compatible con Mesa 3.x (sin unique_id explícito).
"""

import random

from mesa import Agent

from .evolution import replicator_step, STRATEGIES


class CivilAgentV2(Agent):
    """
    Agente de civilización con posición espacial y aprendizaje estratégico.

    Atributos
    ---------
    wealth : float
        Riqueza acumulada (recursos cosechados menos metabolismo).
    reputation : float
        Reputación social [0.0 – 2.0].
    strategy : str
        'cooperative' | 'competitive' | 'neutral'
    social_class : str
        'lower' | 'middle' | 'upper' — actualizado dinámicamente.
    memory : list[int]
        Historial de unique_ids de últimas interacciones (≤ 5).
    x, y : int
        Posición actual en el paisaje de recursos.
    metabolism : float
        Coste de subsistencia por paso (riqueza mínima requerida).
    alive : bool
        False si el agente muere por inanición.
    """

    def __init__(
        self,
        model,
        x: int = 0,
        y: int = 0,
        initial_wealth: float = None,
        strategy: str = None,
        metabolism: float = None,
        vision: int = None,
    ):
        super().__init__(model)

        self.x = x
        self.y = y
        self.alive = True

        # Metabolismo heterogéneo: lognormal(0, 0.6) * base_metabolism
        # Crea diversidad estructural persistente → Gini realista
        if metabolism is not None:
            self.metabolism = float(metabolism)
        else:
            base = getattr(model, "base_metabolism", 1.0)
            self.metabolism = max(0.1, random.lognormvariate(0.0, 0.6) * base)

        # Visión heterogénea: 1–3 celdas según capacidad del agente
        if vision is not None:
            self.vision = int(vision)
        else:
            self.vision = random.choices([1, 2, 3], weights=[0.5, 0.35, 0.15])[0]

        # Riqueza inicial
        if initial_wealth is not None:
            self.wealth = float(initial_wealth)
        else:
            self.wealth = max(1.0, random.lognormvariate(2.3, 0.8))

        self.reputation = 1.0
        self.strategy = strategy or random.choice(STRATEGIES)
        self.social_class = "middle"
        self.memory = []

    # ------------------------------------------------------------------
    # Movimiento y cosecha
    # ------------------------------------------------------------------

    def move_and_harvest(self):
        """
        1. Busca la celda libre con más recursos en el vecindario.
        2. Se mueve a esa celda (si la hay).
        3. Cosecha todos los recursos de la nueva celda.
        4. Deduce el metabolismo.
        5. Muere si la riqueza llega a 0.
        """
        landscape = self.model.landscape

        new_x, new_y = landscape.best_neighbor(self.x, self.y, radius=self.vision)

        # Mover si hay una celda mejor
        if (new_x, new_y) != (self.x, self.y):
            landscape.move_agent(self.unique_id, self.x, self.y, new_x, new_y)
            self.x, self.y = new_x, new_y

        # Cosechar
        harvested = landscape.harvest(self.x, self.y)
        self.wealth += harvested

        # Metabolismo
        self.wealth -= self.metabolism
        if self.wealth <= 0:
            self.wealth = 0.0
            self.alive = False

    # ------------------------------------------------------------------
    # Interacción social (igual que v1, mejorada)
    # ------------------------------------------------------------------

    def interact(self, other: "CivilAgentV2"):
        """Intercambio de riqueza según estrategias de ambos agentes."""
        if not self.alive or not other.alive:
            return
        if self.wealth <= 0:
            return

        transfer = min(1.0, self.wealth * 0.05)

        if self.strategy == "cooperative":
            if self.wealth > other.wealth:
                self._transfer_to(other, transfer)
        elif self.strategy == "competitive":
            if self.wealth < other.wealth:
                extracted = min(transfer, other.wealth)
                other.wealth -= extracted
                self.wealth += extracted
                other.reputation = max(0.0, other.reputation - 0.05)
        else:  # neutral
            if random.random() < 0.5 and self.wealth > other.wealth:
                self._transfer_to(other, transfer * 0.5)

        self._update_class()
        self.memory.append(other.unique_id)
        if len(self.memory) > 5:
            self.memory.pop(0)

    def _transfer_to(self, other: "CivilAgentV2", amount: float):
        amount = min(amount, self.wealth)
        self.wealth -= amount
        other.wealth += amount
        self.reputation = min(2.0, self.reputation + 0.02)

    def _update_class(self):
        mean_w = self.model.mean_wealth
        if self.wealth < mean_w * 0.5:
            self.social_class = "lower"
        elif self.wealth < mean_w * 1.5:
            self.social_class = "middle"
        else:
            self.social_class = "upper"

    # ------------------------------------------------------------------
    # Aprendizaje evolutivo
    # ------------------------------------------------------------------

    def evolve(self):
        """Aplica un paso de dinámica de replicador sobre la estrategia."""
        replicator_step(self, self.model, self.model.mutation_rate)

    # ------------------------------------------------------------------
    # Paso del scheduler (llamado por agents.shuffle_do en Mesa 3.x)
    # ------------------------------------------------------------------

    def step(self):
        if not self.alive:
            return

        # 1. Moverse y cosechar recursos del paisaje
        self.move_and_harvest()
        if not self.alive:
            return

        # 2. Interacción social con vecino de red
        if self.model.network is not None:
            neighbors_ids = list(self.model.network.neighbors(self.unique_id))
            agent_map = self.model._agent_map()
            alive_neighbors = [
                agent_map[nid]
                for nid in neighbors_ids
                if nid in agent_map and agent_map[nid].alive
            ]
            if alive_neighbors:
                other = random.choice(alive_neighbors)
                self.interact(other)
        else:
            others = [
                a for a in self.model.agents
                if a is not self and a.alive
            ]
            if others:
                self.interact(random.choice(others))

        # 3. Actualizar clase social
        self._update_class()

        # 4. Aprendizaje evolutivo (cada N pasos para eficiencia)
        if self.model._step_count % self.model.evolution_interval == 0:
            self.evolve()
