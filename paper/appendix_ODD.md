# Appendix A: ODD Protocol for Civilization-ABM v2

*ODD (Overview, Design concepts, Details) protocol following Grimm et al. (2020).*

---

## 1. Purpose and Patterns

**Purpose.** Civilization-ABM v2 is designed to investigate how four interacting mechanisms — evolutionary strategy learning, geographic resource heterogeneity, institutional collapse dynamics, and heterogeneous metabolic costs — jointly shape the emergence and persistence of wealth inequality in an artificial society. The model extends a validated first-generation framework (Paper 1) and is calibrated against empirical Gini data from the World Bank.

**Patterns used for calibration.** The model is calibrated to reproduce two empirical patterns:
(P1) The global range of Gini coefficients (0.25–0.65) documented by the World Bank across OECD and developing nations.
(P2) The qualitative ordering of inequality archetypes: Nordic < European < US < Latin American < Southern African.

---

## 2. Entities, State Variables, and Scales

**Entities.** The model contains two entity types: *agents* (individuals) and *landscape cells* (environment).

**Agent state variables:**

| Variable | Type | Range | Description |
|---|---|---|---|
| unique_id | int | [0, N) | Mesa-assigned unique identifier |
| wealth | float | [0, ∞) | Accumulated resources |
| strategy | str | {coop, comp, neutral} | Current behavioral strategy |
| metabolism | float | (0, ∞) | Per-step resource cost; lognormal heterogeneous |
| vision | int | {1, 2, 3} | Landscape navigation radius |
| reputation | float | [0.0, 2.0] | Social standing; affects institutional penalties |
| social_class | str | {lower, middle, upper} | Dynamically assigned by wealth quantile |
| x, y | int | [0, W)×[0, H) | Position on resource landscape |
| alive | bool | {True, False} | False when wealth ≤ 0 |

**Landscape cell state variables:**

| Variable | Type | Description |
|---|---|---|
| grid[x,y] | float | Current resource level |
| capacity[x,y] | int | Maximum resource capacity (Gaussian peaks) |
| occupant[x,y] | int/None | unique_id of occupying agent, or None |

**Scales.** Spatial extent: 35×35 discrete cells (default). Time: discrete steps; one step represents one interaction cycle. Population: N = 500 agents (default). Simulation horizon: 1,500 steps. All reported quantities represent means across 60 independent replications per experimental condition.

---

## 3. Process Overview and Scheduling

At each simulation step, processes execute in the following order:

1. **Data collection** (model level): DataCollector records all model-level and agent-level state variables.
2. **Resource growth** (landscape level): Each cell's resources grow by `growth_rate` toward its capacity ceiling.
3. **Institutional update** (model level): InstitutionalSystem computes stability index $S(t)$ based on current Gini and lower-class fraction; determines regime.
4. **Agent activation** (agent level, random order): Each agent sequentially executes:
   a. Move to best available neighboring cell within vision radius.
   b. Harvest resources from current cell.
   c. Deduct metabolism.
   d. If wealth ≤ 0: mark as dead.
   e. Otherwise: interact socially with one network neighbor.
   f. Update social class.
   g. If step % evolution_interval == 0: apply replicator dynamics step.
5. **Institution application** (model level): Apply fiscal redistribution (scaled by tax effectiveness multiplier), reputation penalty, optional wealth floor, and chaos cost if collapsed.
6. **Dead agent removal** (model level): Remove agents marked dead from landscape and Mesa agent set.

---

## 4. Design Concepts

**Basic principles.** The model draws on three theoretical traditions: (1) the generative social science approach (Epstein & Axtell, 1996), in which macro-level patterns emerge from micro-level rules without top-down design; (2) evolutionary game theory (Maynard Smith, 1982; Weibull, 1995), in which strategy frequencies evolve through pairwise imitation; and (3) resilience theory (Holling, 1973), in which systems exhibit threshold-dependent regime transitions.

**Emergence.** The following macro-level patterns emerge from agent interactions without being explicitly programmed: wealth inequality (Gini coefficient trajectory), social class distribution, dominant strategy, institutional regime, and population dynamics (mortality).

**Adaptation.** Agents adapt their strategy through replicator dynamics: they observe the wealthiest network neighbor and update their strategy proportionally to the observed wealth differential. This is a form of social learning (Bandura, 1977) or best-response updating (Fudenberg & Levine, 1998).

**Objectives.** Agents do not maximize an explicit utility function. They follow behavioral rules (move toward resources, interact according to strategy, imitate successful neighbors) that are proxies for wealth-maximizing behavior. This bounded rationality approach (Simon, 1955) is appropriate for a model of emergent social dynamics.

**Learning.** Agents update strategies via replicator dynamics (see Section 6). Learning is social (imitation-based) rather than individual (experience-based). Mutation introduces random exploration at rate μ = 0.02 per learning event.

**Prediction.** Agents do not predict future states. They respond to current local information only (neighboring cells, network neighbors' current wealth and strategy).

**Sensing.** Agents observe: (1) resource levels of all cells within vision radius; (2) the strategy and wealth of all network neighbors; (3) no global information (no knowledge of population-wide means, distant landscape, or others' reputations).

**Interaction.** Agents interact bilaterally through strategy-contingent wealth transfers. Interaction partners are selected from the agent's social network neighbors; if no network is present, a random agent is selected from the population.

**Stochasticity.** Stochastic elements include: (1) initial wealth drawn from a log-normal distribution; (2) initial strategy assignment (uniform random); (3) initial position assignment (random unoccupied cells); (4) metabolism drawn from a log-normal distribution; (5) vision drawn from a categorical distribution; (6) activation order (random shuffle at each step); (7) interaction partner selection (random network neighbor); (8) replicator dynamic copy probability; (9) mutation (Bernoulli with rate μ).

**Collectives.** The social network constitutes a formal collective structure. Social class (lower/middle/upper) constitutes an emergent collective categorization computed at each step.

**Observation.** Data are collected at every step via Mesa's DataCollector. Model-level reporters record 16 aggregate metrics (Gini, mean wealth, alive count, stability, strategy frequencies, etc.). Agent-level reporters record 9 individual attributes (wealth, strategy, metabolism, vision, position, alive status, etc.).

---

## 5. Initialization

Simulations are initialized with:
- N agents placed at randomly selected unoccupied landscape cells.
- Agent wealth drawn independently from LN(2.3, σ₀) where σ₀ is the experimental condition's initial inequality parameter.
- Agent strategy drawn uniformly from {cooperative, competitive, neutral}.
- Agent metabolism drawn from LN(0, 0.6) × m_base; vision drawn from {1,2,3} with weights {0.50, 0.35, 0.15}.
- Landscape capacity generated from superposition of K Gaussian peaks (Equation 1 in main text); grid initialized equal to capacity.
- Social network constructed with topology specified by condition (Watts-Strogatz, Barabási-Albert, Erdős-Rényi, or null).
- InstitutionalSystem initialized with stability = 1.0, regime = 'stable'.

All stochastic elements are seeded by the condition-specific seed for full reproducibility. Seeds are computed as: `seed = seed_base × 1000 + hash(condition_name) % 10000 + replication_index`.

---

## 6. Input Data

The model does not use empirical time-series as dynamic input. World Bank Gini data (indicator SI.POV.GINI; World Bank, 2024) are used as *calibration targets* to evaluate model output against, not as model inputs.

---

## 7. Submodels

### 7.1 Resource Landscape Generation

Landscape capacity is initialized as:

$$C(x,y) = \mathrm{clip}\!\left(1 + \sum_{k=1}^{K} s_k \exp\!\left[-\frac{(x-p_{k,x})^2+(y-p_{k,y})^2}{2\sigma_k^2}\right],\; 1,\; C_{\max}\right)$$

where $K$ is the number of peaks, $(p_{k,x}, p_{k,y})$ are peak locations drawn uniformly at random, $s_k \sim U(0.5, 1.0) \times C_{\max}$ is peak strength, $\sigma_k = \min(W,H)/4$ is the spatial spread, and $C_{\max} = 20$. Landscape is generated once at initialization and remains fixed throughout the simulation.

### 7.2 Resource Growth

At each step, resources regenerate according to:

$$\text{grid}[x,y] \leftarrow \min(\text{grid}[x,y] + \rho,\; C[x,y])$$

where $\rho$ = 0.5 is the default growth rate.

### 7.3 Agent Navigation and Harvest

Agent $a$ identifies the free cell (unoccupied by another agent) with maximum current resources within its vision radius $v_a$:

$$(\hat{x}, \hat{y}) = \arg\max_{(x',y') : \text{free},\; d\leq v_a} \text{grid}[x',y']$$

If $(\hat{x},\hat{y}) \neq (x_a, y_a)$, agent moves there. Agent then harvests all resources:

$$w_a \leftarrow w_a + \text{grid}[\hat{x},\hat{y}];\quad \text{grid}[\hat{x},\hat{y}] \leftarrow 0$$

### 7.4 Metabolic Cost and Mortality

After harvesting, metabolic cost is deducted:

$$w_a \leftarrow w_a - m_a$$

If $w_a \leq 0$: agent is marked `alive = False` and removed at end of step.

### 7.5 Social Interaction

Agent $a$ selects a random network neighbor $b$. Wealth transfer depends on strategy combination:

| $a$'s strategy | Condition | Transfer |
|---|---|---|
| cooperative | $w_a > w_b$ | $a$ transfers $\min(0.05 w_a,\, w_a)$ to $b$; $r_a +0.02$ |
| competitive | $w_a < w_b$ | $a$ extracts $\min(0.05 w_a,\, w_b)$ from $b$; $r_b -0.05$ |
| neutral | $w_a > w_b$, p=0.5 | $a$ transfers $\min(0.025 w_a,\, w_a)$ to $b$ |

### 7.6 Social Class Assignment

$$c_a = \begin{cases} \text{lower} & \text{if } w_a < 0.5\bar{w} \\ \text{upper} & \text{if } w_a \geq 1.5\bar{w} \\ \text{middle} & \text{otherwise} \end{cases}$$

where $\bar{w}$ is the current population mean wealth of living agents.

### 7.7 Replicator Dynamics

Every $\tau$ = 5 steps, each agent applies:
1. With probability $\mu$ = 0.02: adopt a random strategy (mutation).
2. Else: identify richest network neighbor $b^*$. If $w_{b^*} > w_a$:
   $$p_{\text{copy}} = \frac{w_{b^*} - w_a}{w_{\max}(\mathcal{N}_a) + w_a + \varepsilon}$$
   With probability $p_{\text{copy}}$: $s_a \leftarrow s_{b^*}$.

### 7.8 Institutional Stability Dynamics

$$S(t+1) = \begin{cases} \max(0,\; S(t) - \delta[G(t) + 0.5 L(t)] + 0.5\rho_S) & \text{if collapsed} \\ \min(1,\; S(t) - \delta[G(t) + 0.5 L(t)] + 0.1\rho_S) & \text{otherwise} \end{cases}$$

where $G(t)$ is the Gini coefficient, $L(t)$ is the lower-class fraction, $\delta = 0.015$ is the decay factor, and $\rho_S = 0.02$ is the recovery rate. Regime transitions:

- Collapsed → Recovering: when $S$ rises above $\theta_c = 0.25$
- Any → Collapsed: when $S$ falls below $\theta_c = 0.25$
- Recovering/Stressed → Stable: when $S$ rises above $\theta_s = 0.65$

### 7.9 Fiscal Redistribution

Redistribution is applied at the end of each step, scaled by the institutional tax multiplier $\phi \in \{0.0, 0.3, 0.6, 1.0\}$ according to current regime.

**Flat tax:** $\tau_a = \phi \cdot 0.01 \cdot w_a$. Revenue $R = \sum_a \tau_a$ redistributed equally: $w_a \leftarrow w_a - \tau_a + R/N_{\text{alive}}$.

**Progressive tax:** $\tau_a = \phi \cdot r(w_a) \cdot w_a$ where marginal rate $r(w)$ is:

$$r(w) = \begin{cases} 0.005 & w \leq 20 \\ 0.010 & 20 < w \leq 50 \\ 0.020 & w > 50 \end{cases}$$

Revenue redistributed equally across living agents.

### 7.10 Institutional Chaos Cost

During collapsed regime, each living agent incurs a wealth penalty per step:

$$w_a \leftarrow \max(0,\; w_a - c_{\text{chaos}})$$

with $c_{\text{chaos}} = 0.5$ units.

### 7.11 Gini Coefficient Computation

$$G = \frac{\sum_{i=1}^{n}(2i - n - 1) \cdot w_{(i)}}{n \sum_{i=1}^{n} w_{(i)}}$$

where $w_{(1)} \leq w_{(2)} \leq \ldots \leq w_{(n)}$ is the ordered wealth vector of living agents.

---

## References for ODD

Bandura, A. (1977). *Social learning theory*. Prentice Hall.

Epstein, J. M., & Axtell, R. (1996). *Growing artificial societies: Social science from the bottom up*. MIT Press.

Fudenberg, D., & Levine, D. K. (1998). *The theory of learning in games*. MIT Press.

Grimm, V., Railsback, S. F., Vincenot, C. E., Berger, U., Gallagher, C., DeAngelis, D. L., … & Müller, B. (2020). The ODD protocol for describing agent-based and other simulation models: A second update to improve clarity, replication, and structural realism. *Journal of Artificial Societies and Social Simulation*, *23*(2), 7. https://doi.org/10.18564/jasss.4259

Holling, C. S. (1973). Resilience and stability of ecological systems. *Annual Review of Ecology and Systematics*, *4*(1), 1–23.

Maynard Smith, J. (1982). *Evolution and the theory of games*. Cambridge University Press.

Simon, H. A. (1955). A behavioral model of rational choice. *Quarterly Journal of Economics*, *69*(1), 99–118. https://doi.org/10.2307/1884852

Weibull, J. W. (1995). *Evolutionary game theory*. MIT Press.

World Bank. (2024). *Gini index (World Bank estimate)*. https://data.worldbank.org/indicator/SI.POV.GINI
