"""
landscape.py — Paisaje de recursos tipo Sugarscape.

Implementa una cuadrícula NxN con recursos heterogéneos
que crecen de forma autónoma y son cosechados por los agentes.

Inspirado en: Epstein & Axtell (1996) Growing Artificial Societies.
"""

import numpy as np


class ResourceLandscape:
    """
    Cuadrícula 2D de recursos renovables.

    La capacidad máxima de cada celda varía espacialmente,
    creando montañas de riqueza y valles de escasez.
    Este gradiente geográfico es la fuente primaria de
    desigualdad estructural en Civilization-ABM v2.

    Parámetros
    ----------
    width, height : int
        Dimensiones de la cuadrícula.
    max_capacity : int
        Capacidad máxima global de una celda.
    growth_rate : int
        Unidades de recurso que crecen por paso por celda.
    n_peaks : int
        Número de picos de riqueza en el paisaje.
    seed : int | None
        Semilla para reproducibilidad.
    """

    def __init__(
        self,
        width: int = 25,
        height: int = 25,
        max_capacity: int = 10,
        growth_rate: int = 1,
        n_peaks: int = 2,
        seed: int = None,
    ):
        self.width = width
        self.height = height
        self.max_capacity = max_capacity
        self.growth_rate = growth_rate
        self.n_peaks = n_peaks

        rng = np.random.default_rng(seed)
        self._rng = rng

        # Capacidad de cada celda (heterogeneidad geográfica)
        self.capacity = self._generate_landscape(rng)

        # Estado actual de recursos (empieza lleno)
        self.grid = self.capacity.copy().astype(float)

        # Mapa de qué agente ocupa cada celda (None = vacía)
        self.occupant = np.full((width, height), None, dtype=object)

    # ------------------------------------------------------------------
    # Generación del paisaje
    # ------------------------------------------------------------------

    def _generate_landscape(self, rng) -> np.ndarray:
        """
        Crea un paisaje con N picos gaussianos de alta capacidad
        y fondo de baja capacidad.
        """
        cap = np.ones((self.width, self.height), dtype=float)

        # Picos de recursos (montañas de riqueza)
        peak_x = rng.integers(3, self.width - 3, size=self.n_peaks)
        peak_y = rng.integers(3, self.height - 3, size=self.n_peaks)
        peak_strength = rng.integers(6, self.max_capacity + 1, size=self.n_peaks)
        sigma = self.width / (self.n_peaks * 2.5)

        for px, py, ps in zip(peak_x, peak_y, peak_strength):
            for x in range(self.width):
                for y in range(self.height):
                    dist2 = (x - px) ** 2 + (y - py) ** 2
                    cap[x, y] += ps * np.exp(-dist2 / (2 * sigma ** 2))

        # Normalizar al rango [1, max_capacity]
        cap = np.clip(cap, 1, self.max_capacity).astype(int)
        return cap

    # ------------------------------------------------------------------
    # Dinámica de recursos
    # ------------------------------------------------------------------

    def grow(self):
        """Crece los recursos en cada celda hasta su capacidad máxima."""
        self.grid = np.minimum(self.grid + self.growth_rate, self.capacity)

    def harvest(self, x: int, y: int) -> float:
        """
        El agente cosecha todos los recursos de la celda (x, y).
        Devuelve la cantidad cosechada.
        """
        amount = float(self.grid[x, y])
        self.grid[x, y] = 0.0
        return amount

    def resource_at(self, x: int, y: int) -> float:
        return float(self.grid[x, y])

    # ------------------------------------------------------------------
    # Navegación
    # ------------------------------------------------------------------

    def best_neighbor(self, x: int, y: int, radius: int = 1) -> tuple[int, int]:
        """
        Devuelve la celda libre con más recursos en el vecindario de Von Neumann.
        Si todas están ocupadas, devuelve la posición actual.
        """
        best_val = -1.0
        best_pos = (x, y)

        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                if dx == 0 and dy == 0:
                    continue
                nx_, ny_ = (x + dx) % self.width, (y + dy) % self.height
                if self.occupant[nx_, ny_] is None:
                    val = self.grid[nx_, ny_]
                    if val > best_val:
                        best_val = val
                        best_pos = (nx_, ny_)

        return best_pos

    def move_agent(self, agent_id, old_x: int, old_y: int, new_x: int, new_y: int):
        """Actualiza el mapa de ocupación al mover un agente."""
        self.occupant[old_x, old_y] = None
        self.occupant[new_x, new_y] = agent_id

    def place_agent(self, agent_id, x: int, y: int):
        self.occupant[x, y] = agent_id

    def remove_agent(self, agent_id, x: int, y: int):
        if self.occupant[x, y] == agent_id:
            self.occupant[x, y] = None

    # ------------------------------------------------------------------
    # Métricas del paisaje
    # ------------------------------------------------------------------

    def total_resources(self) -> float:
        return float(self.grid.sum())

    def gini_landscape(self) -> float:
        """Gini de los recursos actuales (desigualdad geográfica)."""
        flat = self.grid.flatten()
        if flat.sum() == 0:
            return 0.0
        flat = np.sort(flat)
        n = len(flat)
        idx = np.arange(1, n + 1)
        return float(((2 * idx - n - 1) * flat).sum() / (n * flat.sum()))

    def mean_resource(self) -> float:
        return float(self.grid.mean())
