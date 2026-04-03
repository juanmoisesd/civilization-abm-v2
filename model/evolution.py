"""
evolution.py — Aprendizaje estratégico por dinámica de replicador.

Los agentes observan a sus vecinos en la red social y copian
la estrategia del vecino más exitoso con probabilidad proporcional
a la diferencia de riqueza (replicator dynamics).

Referencia:
    Schuster & Sigmund (1983). Replicator dynamics.
    Journal of Theoretical Biology, 100(3), 533-538.
"""

import random
import numpy as np


# Estrategias disponibles en el modelo
STRATEGIES = ("cooperative", "competitive", "neutral")

# Probabilidad base de mutación espontánea
DEFAULT_MUTATION_RATE = 0.02


def replicator_step(agent, model, mutation_rate: float = DEFAULT_MUTATION_RATE):
    """
    Actualiza la estrategia del agente mediante dinámica de replicador.

    Algoritmo:
    1. Obtener vecinos en la red social.
    2. Seleccionar el vecino con mayor riqueza (el más "exitoso").
    3. Si ese vecino es más rico, copiar su estrategia con probabilidad
       proporcional a la diferencia de riqueza normalizada.
    4. Con probabilidad `mutation_rate`, adoptar una estrategia aleatoria.

    Parámetros
    ----------
    agent : CivilAgentV2
        El agente que aprende.
    model : CivilModelV2
        Referencia al modelo (para acceder a red y otros agentes).
    mutation_rate : float
        Probabilidad de mutación espontánea.
    """
    # Mutación primero (rara pero prioritaria para exploración)
    if random.random() < mutation_rate:
        agent.strategy = random.choice(STRATEGIES)
        return

    # Obtener vecinos de la red social
    if model.network is None:
        return

    neighbors_ids = list(model.network.neighbors(agent.unique_id))
    if not neighbors_ids:
        return

    # Mapa id → agente
    agent_map = model._agent_map()

    # Filtrar vecinos que siguen vivos
    neighbors = [agent_map[nid] for nid in neighbors_ids if nid in agent_map]
    if not neighbors:
        return

    # Elegir el vecino más rico como "modelo de referencia"
    best_neighbor = max(neighbors, key=lambda a: a.wealth)

    if best_neighbor.wealth <= agent.wealth:
        return  # El agente ya es el más exitoso; no copia

    # Probabilidad de imitar proporcional a la diferencia de riqueza
    # Normalizada por la riqueza máxima en el vecindario para mantenerse en [0,1]
    max_w = max(a.wealth for a in neighbors)
    if max_w == 0:
        return

    p_copy = (best_neighbor.wealth - agent.wealth) / (max_w + agent.wealth + 1e-9)
    p_copy = min(p_copy, 1.0)

    if random.random() < p_copy:
        agent.strategy = best_neighbor.strategy


def population_strategy_shares(model) -> dict:
    """
    Devuelve la fracción de agentes usando cada estrategia.

    Útil como reporter del DataCollector.
    """
    counts = {s: 0 for s in STRATEGIES}
    total = 0
    for agent in model.agents:
        counts[agent.strategy] = counts.get(agent.strategy, 0) + 1
        total += 1
    if total == 0:
        return {s: 0.0 for s in STRATEGIES}
    return {s: counts[s] / total for s in STRATEGIES}


def strategy_entropy(model) -> float:
    """
    Entropía de Shannon de la distribución estratégica.

    H = 0  → toda la población usa la misma estrategia (convergencia).
    H = log2(3) ≈ 1.585 → distribución uniforme (máxima diversidad).
    """
    shares = population_strategy_shares(model)
    h = 0.0
    for p in shares.values():
        if p > 0:
            h -= p * np.log2(p)
    return float(h)


def dominant_strategy(model) -> str:
    """Retorna la estrategia más frecuente en la población."""
    shares = population_strategy_shares(model)
    return max(shares, key=shares.get)
