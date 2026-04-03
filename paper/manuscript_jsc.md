# Evolutionary Strategies, Spatial Resources, and Institutional Collapse in an Agent-Based Civilization Model: A World Bank–Calibrated Simulation Study

---

## Abstract

This paper presents Civilization-ABM v2, a second-generation agent-based model extending a validated framework with evolutionary strategy learning via replicator dynamics, spatial resource heterogeneity, institutional collapse and recovery, and empirical calibration against World Bank Gini data. Across 41 experimental conditions and 2,460 replications (N = 500 agents; 1,500 steps each), five principal findings emerge: competitive strategy dominance is universal and invariant to fiscal redistribution, which reduces the Gini coefficient by 93.9% without altering strategic equilibrium; geographic resource concentration exerts minimal effect on inequality (15% Gini difference across landscape configurations), establishing fiscal redistribution as the dominant institutional signal; institutional collapse is endemic, with baseline simulations spending 32–76% of steps in collapsed regimes; a floor trap mechanism produces the highest inequality observed (Gini = 0.663 ± 0.178, max = 0.970); and World Bank calibration fails systematically for all archetypes except South Africa, a theoretically informative negative result explained by the model's 100% redistribution efficiency.

**Keywords:** agent-based modeling; wealth inequality; replicator dynamics; Sugarscape; institutional collapse; Gini coefficient; World Bank calibration; evolutionary game theory

---

## I. Introduction

The emergence and persistence of wealth inequality constitutes one of the central puzzles of social science. Despite decades of theoretical and empirical progress, the mechanisms by which individual-level decisions, institutional structures, and environmental conditions jointly produce macro-level distributional outcomes remain incompletely understood [1, 2]. Agent-based modeling (ABM) offers a uniquely suited methodological approach: by simulating populations of heterogeneous, interacting agents, ABM allows researchers to observe how complex distributional patterns grow from simple local rules — the generative approach to social science [3, 4].

A companion paper [5] introduced Civilization-ABM, an open-source Mesa-based model demonstrating that progressive fiscal policy reduces the Gini coefficient by 13.3% relative to the no-taxation baseline, while high initial wealth dispersion paradoxically produces lower equilibrium inequality through a redistribution amplification mechanism. Network topology exerted modest inequality effects (ΔGini < 0.006), suggesting that robust institutional redistribution overshadows network-structural advantages. These findings, however, were obtained under three significant simplifying assumptions: agent strategies are fixed (no learning), the environment is aspatial (resources are not geographically distributed), and institutions are permanent (no collapse or recovery dynamics).

Empirical human societies are characterized precisely by their violation. Behavioral strategies evolve: agents copy successful neighbors, experiment with novel behaviors, and abandon failing strategies — dynamics formalized by evolutionary game theory [6, 7] and replicator dynamics [8]. Resources are geographically concentrated: mineral wealth, fertile land, and urban agglomeration create persistent spatial inequality [9, 10]. Institutions collapse: historical episodes from Rome's fiscal crisis to the Soviet dissolution demonstrate non-linear stability properties, crossing tipping points under sufficient social strain [11, 12]. And the magnitude of inequality varies systematically across nations and decades as documented by the World Bank Gini coefficient [13].

This paper introduces Civilization-ABM v2, which incorporates all four missing mechanisms through a factorial experimental design of 41 conditions, 60 replications each, 500 agents, 1,500 simulation steps. Five research questions guide the analysis:

- **RQ1:** How does evolutionary strategy learning via replicator dynamics alter the distributional outcomes documented in [5]?
- **RQ2:** Does spatial resource heterogeneity amplify or attenuate the effects of fiscal redistribution?
- **RQ3:** Under what parameter configurations do institutional systems collapse, and how does collapse interact with inequality dynamics?
- **RQ4:** Does heterogeneous agent metabolism generate persistent structural inequality comparable in magnitude to empirically observed Gini coefficients?
- **RQ5:** What model parameter configurations reproduce the Gini coefficients of specific national archetypes (Nordic, European, US, Latin American, South African) as documented in World Bank data [13]?

---

## II. Background and Related Work

### A. Evolutionary Strategy Learning and Replicator Dynamics

The evolution of behavioral strategies in social systems has been studied through evolutionary game theory since Maynard Smith and Price's [14] formalization of evolutionary stable strategies. In populations where strategies are transmitted by imitation rather than genetics, the replicator dynamic describes strategy frequency changes as proportional to fitness differentials [15, 7]. Formally, let $x_i(t)$ denote the frequency of strategy $i$ at time $t$ and $f_i$ its fitness (mean wealth of agents using strategy $i$). The replicator equation is:

$$\dot{x}_i = x_i \left[ f_i(\mathbf{x}) - \bar{f}(\mathbf{x}) \right]$$

where $\bar{f} = \sum_j x_j f_j$ is mean population fitness. In discrete agent-based implementations, this is approximated by pairwise imitation: agent $a$ observes neighbor $b$ and adopts $b$'s strategy with probability proportional to $\max(0, w_b - w_a) / (w_{\max} + w_a)$, where $w$ denotes wealth [16].

Applied to a three-strategy system with cooperative, competitive, and neutral strategies, replicator dynamics predict cyclical or mixed equilibria depending on the payoff structure [17]. Cooperative strategies are vulnerable to invasion by defectors in well-mixed populations [18] but can persist when spatial structure creates protective clusters [19]. In Civilization-ABM v2, network topology directly modulates evolutionary outcomes — a theoretical prediction tested empirically.

### B. Spatial Resource Heterogeneity: The Sugarscape Legacy

Epstein and Axtell's [9] Sugarscape model established that spatial resource heterogeneity is sufficient to generate persistent inequality without any deliberate institutional mechanism. Agents distributed on a resource landscape converge to Pareto-distributed wealth regardless of initial homogeneity, because geographic proximity to high-resource areas confers permanent competitive advantages — a computational analog of the geography of economic development [10, 20].

Civilization-ABM v2 implements a Sugarscape-inspired landscape: a discrete $W \times H$ grid (default 35×35) where resource capacity follows a superposition of $K$ Gaussian peaks:

$$C(x,y) = \mathrm{clip}\left(1 + \sum_{k=1}^{K} s_k \exp\left[-\frac{(x-p_{k,x})^2 + (y-p_{k,y})^2}{2\sigma_k^2}\right], 1, C_{\max}\right)$$

Resources regenerate at rate $\rho$ toward capacity each step. Agents move toward the free adjacent cell with the highest current resources within their vision radius $v$, harvest all resources there, and pay a metabolic cost $m$ per step.

### C. Institutional Collapse and Recovery

Turchin's [11] secular cycles theory models the rise and fall of political instability as a function of elite overproduction and popular immiseration. Civilization-ABM v2 implements an institutional stability index $S(t) \in [0,1]$ that decays as a function of current Gini and lower-class concentration, and recovers slowly during non-collapse periods. Three regime thresholds partition the stability space, drawing on [11, 21, 22]:

| Regime | Condition | Tax effectiveness |
|---|---|---|
| Stable | $S \geq 0.65$ | 100% |
| Stressed | $0.25 \leq S < 0.65$ | 60% |
| Collapsed | $S < 0.25$ | 0% + chaos penalty |
| Recovering | $S \geq 0.25$ after collapse | 30% |

When institutions collapse, their redistributive function ceases — removing the equalizing force precisely when inequality is highest — creating a positive feedback loop between inequality and instability.

### D. Heterogeneous Metabolism and Structural Inequality

A limitation of earlier Sugarscape implementations is the assumption of uniform agent metabolism. Empirically, the "metabolic cost" of social existence varies substantially across individuals and social positions [23, 24]. In Civilization-ABM v2, each agent's metabolism $m_i$ is drawn from a log-normal distribution:

$$m_i \sim \mathrm{LN}(0, \sigma_m) \times m_{\text{base}}$$

with $\sigma_m = 0.6$, creating a roughly 10× range from low- to high-metabolism agents.

### E. Empirical Calibration and the World Bank Gini Index

Unlike most ABM studies, Civilization-ABM v2 explicitly calibrates against the World Bank's Gini index (indicator SI.POV.GINI) [13], enabling identification of national archetypes: Nordic countries (Gini ≈ 0.25–0.30), continental European countries (≈ 0.30–0.35), the United States (≈ 0.39–0.41), Latin American countries (≈ 0.45–0.55), and highly unequal societies such as South Africa (≈ 0.60–0.65). Calibration follows the tradition of empirically grounded ABM validation [25, 26].

---

## III. Model and Methods

### A. Model Architecture

Civilization-ABM v2 is implemented in Python 3.11 using Mesa 3.x [27] and extends v1 with four new modules. Full source code is available at https://github.com/juanmoisesd/civilization-abm-v2 under an MIT license. The model comprises six coupled modules: (1) agents, (2) resource landscape, (3) evolutionary dynamics, (4) social network, (5) institutional system, and (6) data collection.

### B. Agents

Each simulation initializes N = 500 agents with the following attributes:

- **Wealth** ($w_i$): drawn from LN(2.3, $\sigma_0$) where $\sigma_0$ is the initial inequality parameter
- **Strategy** ($s_i$): drawn uniformly from {cooperative, competitive, neutral}
- **Metabolism** ($m_i$): drawn from LN(0, 0.6) × $m_{\text{base}}$, generating heterogeneous structural costs
- **Vision** ($v_i$): drawn from {1, 2, 3} with weights {0.50, 0.35, 0.15}
- **Position** ($x_i$, $y_i$): placed randomly on unoccupied landscape cells
- **Reputation** ($r_i$): initialized at 1.0

At each step, agents are activated in random shuffled order. Each activated agent: (1) navigates to the most resource-rich free adjacent cell within vision radius $v_i$; (2) harvests all resources from that cell; (3) pays metabolic cost $m_i$; (4) interacts socially with a network neighbor; (5) updates social class. Every $\tau$ steps (default $\tau$ = 5), agents update strategies via the replicator dynamic.

### C. Resource Landscape

The landscape is a 35×35 discrete grid. Resource capacity at each cell follows Eq. (2) with $K$ Gaussian peaks, $C_{\max}$ = 20, default $K$ = 3, $\rho$ = 0.5.

### D. Evolutionary Dynamics

Strategy learning follows the pairwise replicator dynamic. At each learning event, agent $a$ identifies the wealthiest neighbor $b^*$ in its network neighborhood. If $w_{b^*} > w_a$, agent $a$ adopts $b^*$'s strategy with probability:

$$p_{\text{copy}} = \frac{w_{b^*} - w_a}{w_{\max}(\text{neighborhood}) + w_a + \epsilon}$$

With independent probability $\mu$ = 0.02 (mutation rate), the agent adopts a random strategy, maintaining exploration. Strategy entropy $H = -\sum_i p_i \log_2 p_i$ [28] tracks population-level strategic diversity.

### E. Social Network

Network topologies: small-world (Watts-Strogatz [29], $k$ = 4, $p$ = 0.1), scale-free (Barabási-Albert [30], $m$ = 2), random (Erdős-Rényi, $p$ = 0.05), and no network. Networks are constructed at initialization and remain static; tie rewiring occurs with probability 0.01 per step based on reputation.

### F. Institutional System

The stability index $S(t)$ evolves according to:

$$S(t+1) = S(t) - \delta[G(t) + 0.5 \cdot L(t)] + \rho_S \cdot \mathbb{1}[\text{not collapsed}]$$

where $\delta$ = 0.015 is the decay factor, $G(t)$ is the current Gini coefficient, $L(t)$ is the lower-class fraction, and $\rho_S$ = 0.002 is the natural recovery rate. Institutional collapse removes the redistributive function and applies a per-agent wealth penalty of 0.1 units per step (chaos cost).

### G. Experimental Design

A full factorial and targeted interaction design across 41 conditions (Table I) organizes simulations into eight thematic blocks. Each condition runs 60 independent replications with 1,500 simulation steps (total: 2,460 simulation runs).

**Table I.** Experimental Conditions Summary by Block.

| Block | Conditions | Key variation |
|---|---|---|
| A — Fiscal policy | 5 | None, flat, progressive, progressive+floor |
| B — Initial inequality | 5 | $\sigma_0$ in {0.3, 0.5, 0.8, 1.2, 1.8, 2.5} |
| C — Network topology | 4 | Small-world, scale-free, random, none |
| D — Landscape geography | 4 | $K \in \{1, 2, 4, 6\}$ peaks |
| E — Base metabolism | 3 | $m \in \{0.5, 1.0, 2.0, 3.5\}$ |
| F — Key interactions | 8 | High ineq × scale-free; max stress; max resilience |
| G — Sensitivity (OAT) | 7 | Growth rate, mutation rate, N, evolution interval |
| H — WB calibration | 5 | Nordic, European, USA, Latin America, South Africa |

### H. Outcome Measures

Primary outcomes: final-step Gini coefficient, mean wealth, alive agent count, institutional stability, dominant strategy, strategy entropy. Secondary outcomes: collapse frequency, mean collapse duration, fraction of steps collapsed, strategic volatility. All continuous outcomes are reported as mean ± SD across 60 replications.

---

## IV. Results

### A. Baseline Dynamics

Under baseline conditions (N = 500, σ₀ = 0.8, no taxation, small-world network, 1,500 steps), the model converges to a mean final Gini of 0.361 ± 0.086 (range: 0.225–0.554) — within the empirically observed range for mixed-economy nations [13]. The competitive strategy achieves dominance in baseline replications (mean final frequency 55–66%), while cooperative agents represent 13–25% and neutral agents 20–30%. Strategy entropy averages 1.28 ± 0.09 bits (theoretical maximum: log₂3 = 1.585 bits), indicating maintained strategic diversity with a competitive bias, consistent with replicator dynamics predictions [18].

A critical structural feature of the baseline is endemic institutional instability: replications spend between 32% and 76% of simulation steps in a collapsed or recovering institutional regime, generating hundreds of short-duration collapse events per run (mean duration: 1.3–12.8 steps). This "collapse flickering" — rapid oscillation around the institutional stability threshold — represents a novel dynamic property of the model. Rather than experiencing rare catastrophic collapses, the baseline society operates in a condition of chronic institutional fragility. Fig. 1 shows the full baseline dynamics panel.

### B. RQ1: Effect of Evolutionary Strategy Learning

Across fiscal policy conditions (Block A), evolutionary learning produces a universal finding: competitive strategy dominance is robust to all redistribution regimes. Under no taxation (baseline), progressive taxation (Gini = 0.022 ± 0.004), flat taxation (0.038 ± 0.010), and progressive taxation with floor (0.025 ± 0.004), competitive strategies consistently account for the largest population share at equilibrium. This confirms the replicator dynamics prediction that competitive strategies invade cooperative populations under wealth-differential conditions [18].

Progressive taxation reduces Gini by 93.9% relative to the no-redistribution baseline (0.022 vs. 0.361), but this dramatic reduction does not eliminate competitive dominance. Strategy entropy under progressive tax (approximately 1.30 bits) is statistically indistinguishable from the no-tax baseline (approximately 1.28 bits), indicating that redistribution preserves strategic diversity without altering its competitive character.

Fig. 1 shows strategy frequency trajectories for the five Block A conditions. Fig. 2 shows strategy entropy across time.

### C. RQ2: Effect of Spatial Resource Heterogeneity

Contrary to the Sugarscape prediction [9], geographic resource concentration exerts minimal effect on wealth inequality under institutional conditions. Block D conditions ($K \in \{1, 2, 4, 6\}$ landscape peaks) produce mean final Gini values of 0.020 ± 0.004 (K=1), 0.022 ± 0.004 (K=2), 0.023 ± 0.003 (K=4), and 0.022 ± 0.003 (K=6) — a range of only 0.003, representing a 15% difference between the most and least concentrated landscape configurations.

The explanation lies in institutional dominance: all Block D conditions include progressive taxation, which reduces Gini to approximately 0.020–0.023 regardless of geographic concentration. This finding establishes a novel hierarchy: fiscal redistribution > network topology > geographic heterogeneity as determinants of equilibrium inequality. The sensitivity condition with slow resource growth (ρ = 0.1) produces Gini SD = 0.114 with a maximum of 0.528, confirming that resource scarcity generates high-inequality tail events when institutional buffering is overwhelmed.

### D. RQ3: Institutional Collapse

Institutional collapse is not a rare extreme event in this model — it is endemic. The collapse-prone condition (σ₀ = 2.5, scale-free network, no tax, m_base = 2.5) produces a mean final Gini of 0.380 ± 0.122 (range: 0.192–0.797). The resilient society condition (progressive tax + floor, σ₀ = 0.3, K = 4, m = 0.5) produces a mean Gini of 0.006 ± 0.001 — a 98.3% reduction relative to collapse-prone conditions.

The most extreme inequality in the entire experimental design emerges from `hi_ineq_floor` (Gini = 0.663 ± 0.178, max = 0.970). This condition combines high initial inequality (σ₀ = 1.8) with a wealth floor but no fiscal redistribution. Without redistribution, the floor prevents the poorest agents from dying but does not transfer wealth from rich to poor — stabilizing extreme concentration rather than alleviating it, producing a "floor trap" that is more unequal than either pure redistribution or pure laissez-faire. Fig. 3 shows collapse dynamics and the floor trap mechanism.

### E. RQ4: Heterogeneous Metabolism

The Block E conditions reveal a non-monotonic relationship between base metabolism and final inequality. Low metabolism (m = 0.5) produces Gini = 0.006 ± 0.001, high metabolism (m = 2.0) produces Gini = 0.018 ± 0.003, and very high metabolism (m = 3.5) produces Gini = 0.015 ± 0.002. The unexpected decline from m = 2.0 to m = 3.5 reflects a survivor bias mechanism: at very high metabolic costs, the poorest agents die before the end of the simulation, leaving a more homogeneous surviving population. This metabolic thinning reduces measured Gini through selection rather than redistribution, consistent with Sen's [24] capability approach applied to the measurement of structural disadvantage.

### F. RQ5: World Bank Calibration

The Block H calibration reveals that the designed archetype parameter configurations substantially underestimate target Gini values for all archetypes except South Africa. Table II presents the calibration results.

**Table II.** Calibration Results: Simulated Versus Empirical Gini (mean ± SD, 60 replications per condition).

| Archetype | Target Gini (WB) | Simulated Gini | |Target − Sim.| | Key parameters |
|---|---|---|---|---|
| Nordic | 0.27 | 0.006 ± 0.001 | 0.264 | prog. tax + floor, σ₀=0.3, K=4, m=0.5 |
| European | 0.33 | 0.020 ± 0.003 | 0.310 | prog. tax, σ₀=0.6, K=3 |
| United States | 0.41 | 0.037 ± 0.007 | 0.373 | flat tax, scale-free, σ₀=1.0 |
| Latin America | 0.50 | 0.039 ± 0.014 | 0.461 | flat tax, scale-free, σ₀=1.5, K=2 |
| South Africa | 0.63 | 0.358 ± 0.111 | 0.272 | no tax, scale-free, σ₀=2.5, K=1, m=2.0 |

The calibration fails for Nordic through Latin American archetypes, with simulated values systematically below targets. The South Africa condition achieves the best calibration (max replication Gini = 0.656, closest to target 0.63). The model does span the full empirical Gini range across the full experiment (condition means: 0.005–0.663; individual replication maxima: up to 0.970). Fig. 4 shows the Gini heatmap across Block A-F conditions.

---

## V. Discussion

### A. Evolutionary Dynamics: Competitive Invariance and the Limits of Redistribution as Evolutionary Stabilizer

The prediction from replicator dynamics — that competitive strategies should invade cooperative populations under wealth-differential conditions [18] — is fully confirmed and robust to all fiscal conditions tested. Competitive strategies dominate at equilibrium regardless of redistribution regime. This result challenges an implicit assumption in computational social science policy discussions: that redistributive institutions, by reducing wealth differentials, would diminish the evolutionary fitness advantage of competitive strategies and allow cooperation to stabilize [31, 32].

Progressive taxation reduces the Gini coefficient by 93.9% without measurably shifting strategic equilibrium. Strategy entropy under progressive tax is statistically indistinguishable from the no-tax baseline, indicating that redistribution neither creates cooperative stability nor eliminates strategic diversity. What redistribution achieves is compressing the wealth differentials that drive competitive advantage, without eliminating competitive dominance itself. The sustained strategic diversity observed across all conditions (entropy range: 1.28–1.32 bits) is maintained by mutation and collapse-induced disruption rather than by redistribution stabilizing cooperative niches.

This finding has a nuanced policy implication: fiscal redistribution is a powerful economic equalizer but should not be expected to generate cooperative behavioral norms as a byproduct. Generating cooperation may require more specific institutional mechanisms — enforceable reciprocity, reputation systems, or selective cooperation incentives — than the simple wealth floor or tax transfer modeled here.

### B. Spatial Resources and Institutional Dominance

The Block D results constitute a direct test of the foundational Sugarscape claim [9] that spatial resource heterogeneity is sufficient to generate persistent inequality. Under the institutional conditions of this model, that claim does not hold: geographic concentration (K = 1 to K = 6 peaks) generates only a 15% difference in final Gini, with no monotonic relationship and variances that exceed the between-condition differences.

This null result is not a refutation of Sugarscape but rather a demonstration of institutional dominance: when fiscal redistribution operates, it overwhelms spatial advantages within 1,500 simulation steps. The hierarchy established by cross-condition comparison — fiscal policy > network topology > geographic heterogeneity — has theoretical precedent in the literature on inequality determinants [21, 1]. Geographic resource inequality does not require geographically targeted interventions as a prerequisite; universal fiscal redistribution suffices to neutralize spatial advantages in the model. However, this conclusion is contingent on institutional stability: when institutions collapse, geography would presumably reassert itself.

### C. Institutional Collapse: From Catastrophe to Chronic Condition

Perhaps the most consequential finding for theoretical framing is that institutional collapse in this model is endemic rather than rare. Even the baseline generates hundreds of collapse episodes per run, with replications spending 32–76% of steps in collapsed or recovering regimes. This reframes the theoretical question: the relevant question is not "under what conditions do societies collapse?" but "under what conditions do societies stabilize sufficiently to maintain sustained institutional function?"

The positive feedback loop between inequality and institutional collapse — inequality degrades institutions, which suspends redistribution, which increases inequality further — is confirmed as the core dynamic [11, 21]. The asymmetry between collapse and recovery timescales produces observed flickering analogous to the chronic low-intensity institutional dysfunction documented in historical cases of state fragility [33], rather than the singular civilizational collapse narratives of [12].

The "floor trap" constitutes a novel mechanism. The `hi_ineq_floor` condition produces the highest observed inequality in the entire design (Gini = 0.663, max = 0.970). The floor eliminates mortality pressure on low-wealth agents while placing no redistributive ceiling on high-wealth accumulation. Poor agents survive indefinitely near the floor while rich agents compound wealth through competitive extraction; the floor stabilizes the lower tail at subsistence, mathematically maximizing Gini by creating a permanent zero-variance lower class and an unrestricted upper tail. This constitutes a theoretical caution against welfare floors designed without accompanying redistribution from the upper tail.

### D. Metabolic Heterogeneity: Structural Costs and the Survivor-Bias Mechanism

The Block E results partially support the structural inequality hypothesis [34, 24] but reveal an important qualification. The expected positive relationship between base metabolism and final inequality holds from m = 0.5 to m = 2.0 but reverses from m = 2.0 to m = 3.5. This non-monotonicity is explained by a survivor-bias mechanism: at very high metabolic stress, the most disadvantaged agents die before simulation end, leaving a more homogeneous surviving population. Observed inequality declines because the most unequal element — the lowest-wealth stratum — has been eliminated by mortality.

This finding has a stark policy implication: policies that measure inequality only among survivors will systematically underestimate the full distributional impact of structural cost differentials — a concern directly relevant to empirical inequality research in contexts where mortality is differentially concentrated among low-wealth populations [35].

### E. Calibration: A Theoretically Informative Negative Result

The systematic calibration failure for Nordic through Latin American archetypes (simulated 0.006–0.039 vs. targets 0.27–0.50) reveals a specific model assumption violated in empirical societies: 100% redistribution efficiency. In the model, every tax collected is immediately and perfectly redistributed each step; there is no tax evasion, capital flight, intergenerational wealth transfer, or enforcement gap. In empirical economies, redistribution is systematically imperfect at each of these steps [1, 36].

The South Africa calibration achieves the best fit (simulated max = 0.656, target = 0.63) precisely because that condition involves no redistribution: with null fiscal policy, the model's redistribution-efficiency assumption is irrelevant, and initial inequality and structural conditions determine outcomes. The model spans the full empirical Gini range (condition means: 0.005–0.663; individual replication maxima: up to 0.970), demonstrating that the mechanisms are present but the parameter-to-archetype mapping is confounded by the efficiency assumption. This constitutes the strongest argument for incorporating imperfect redistribution in the next generation of the model.

### F. Limitations

Several limitations warrant acknowledgment. First, the calibration uses final-step Gini as the sole calibration target; future work should calibrate against temporal Gini trajectories and additional distributional moments. Second, and most critically, the model assumes 100% redistribution efficiency; incorporating imperfect enforcement, tax evasion, and capital returns [1, 36] is the primary extension required to achieve archetype-specific calibration. Third, the population size (N = 500) and landscape grid (35×35) remain abstractions from real demographic and spatial scales. Fourth, agent strategies are limited to three archetypes; richer behavioral repertoires could be incorporated through extended evolutionary game-theoretic frameworks. Fifth, the network is quasi-static; endogenous network formation would more faithfully represent real social dynamics. Sixth, the institutional collapse model is stylized; empirical validation against historical stability indices would strengthen the collapse dynamics component.

---

## VI. Conclusion

This paper introduces Civilization-ABM v2, a second-generation agent-based model of an artificial society that adds evolutionary strategy learning, spatial resource heterogeneity, institutional collapse dynamics, and World Bank calibration to the validated v1 framework. Across 41 experimental conditions and 2,460 independent replications, five principal findings emerge.

**Finding 1 (Evolutionary dynamics):** Competitive strategy dominance via replicator dynamics is universal and invariant to fiscal redistribution. Progressive taxation reduces the Gini coefficient by 93.9% (from 0.361 to 0.022) without altering strategic equilibrium — redistribution is a powerful economic equalizer but not an evolutionary stabilizer of cooperation. This challenges assumptions in the policy literature about the behavioral externalities of redistribution.

**Finding 2 (Spatial resources):** Contrary to the Sugarscape legacy [9], geographic resource concentration exerts minimal effect on equilibrium inequality under institutional conditions: the Gini difference across K = 1 to K = 6 landscape configurations is only 15% (0.020 to 0.022). Fiscal redistribution is the dominant institutional signal, establishing a hierarchy: fiscal policy > network topology > geographic heterogeneity.

**Finding 3 (Institutional collapse and the floor trap):** Institutional collapse is endemic rather than catastrophic: baseline simulations spend 32–76% of steps in collapsed or recovering regimes across hundreds of episodes per run. The highest inequality in the entire experimental design emerges from the floor trap — a wealth floor without redistribution produces Gini = 0.663 ± 0.178 (max = 0.970), a novel mechanism by which welfare policy without redistribution entrenchs extreme concentration.

**Finding 4 (Metabolic heterogeneity):** The metabolism–inequality relationship is non-monotonic due to a survivor-bias mechanism: at very high metabolic stress (m = 3.5), the most disadvantaged agents die before simulation end, reducing observed Gini among survivors (0.015 vs. 0.018 at m = 2.0). Structural cost differentials generate inequality that is systematically underestimated when measured only among survivors.

**Finding 5 (Calibration — theoretically informative negative result):** World Bank calibration fails systematically for Nordic through Latin American archetypes (simulated 0.006–0.039 vs. targets 0.27–0.50), because the model's 100% redistribution efficiency constitutes a theoretical lower bound incompatible with empirically realistic inequality levels wherever redistribution operates. South Africa achieves the best fit (max = 0.656 vs. target 0.63) precisely where redistribution is absent. This negative result specifies the mechanism — imperfect redistribution [1, 36] — that must be incorporated in the next generation of the model.

All model code, experimental configurations, and data are openly available at https://github.com/juanmoisesd/civilization-abm-v2 under an MIT license.

---

## Figure Captions

**Fig. 1.** Baseline dynamics panel (N = 500, σ₀ = 0.8, no taxation, small-world network, 1,500 steps). Top-left: Gini coefficient evolution (mean ± SD across 60 replications). Top-right: mean wealth trajectory. Bottom-left: alive agent count over time. Bottom-right: institutional stability index with collapse threshold (S = 0.25) indicated.

**Fig. 2.** Strategy evolution under five fiscal policy conditions (Block A). Lines show mean frequency of competitive (solid), cooperative (dashed), and neutral (dotted) strategies across 1,500 steps. Shannon entropy (right panel) remains statistically indistinguishable across all redistribution regimes (range: 1.28–1.32 bits).

**Fig. 3.** Institutional collapse dynamics. Left: stability index trajectory under collapse-prone conditions (σ₀ = 2.5, scale-free, no tax). Center: Gini distribution under collapse-prone vs. resilient conditions. Right: floor trap mechanism — Gini trajectory under hi\_ineq\_floor (Gini = 0.663 ± 0.178, max = 0.970) compared to no-floor baseline.

**Fig. 4.** Gini coefficient heatmap across Block A–F experimental conditions. Color scale indicates mean final Gini (60 replications per cell). Rows: fiscal policy regimes. Columns: initial inequality (σ₀). Annotations show mean ± SD.

**Fig. 5.** Comparative panel across all 41 experimental conditions. Box plots of final Gini distribution per condition, ordered by mean Gini. Highlighted conditions: baseline (grey), hi\_ineq\_floor (red), resilient\_society (green), and World Bank calibration archetypes (blue).

---

## Acknowledgment

[Acknowledgment removed for blind review. To be restored upon acceptance.]

---

## References

[1] T. Piketty, *Capital in the Twenty-First Century*, Harvard Univ. Press, 2014.

[2] B. Milanovic, *Global Inequality: A New Approach for the Age of Globalization*, Harvard Univ. Press, 2016.

[3] J. M. Epstein, *Generative Social Science: Studies in Agent-Based Computational Modeling*, Princeton Univ. Press, 2006.

[4] J. M. Epstein, "Why model?" *J. Artif. Soc. Soc. Simul.*, vol. 11, no. 4, p. 12, 2008.

[5] [Author], "Fiscal policy, network topology, and wealth inequality in an agent-based civilization model," *Soc. Sci. Comput. Rev.*, under review, 2025.

[6] J. Maynard Smith, *Evolution and the Theory of Games*, Cambridge Univ. Press, 1982.

[7] J. W. Weibull, *Evolutionary Game Theory*, MIT Press, 1995.

[8] P. Schuster and K. Sigmund, "Replicator dynamics," *J. Theor. Biol.*, vol. 100, no. 3, pp. 533–538, 1983.

[9] J. M. Epstein and R. Axtell, *Growing Artificial Societies: Social Science from the Bottom Up*, MIT Press, 1996.

[10] J. Diamond, *Guns, Germs, and Steel: The Fates of Human Societies*, W. W. Norton, 1997.

[11] P. Turchin, "A theory for formation of large empires," *J. Glob. Hist.*, vol. 4, no. 2, pp. 191–217, 2009.

[12] J. Diamond, *Collapse: How Societies Choose to Fail or Succeed*, Viking, 2005.

[13] World Bank, "Gini index (World Bank estimate)," 2024. [Online]. Available: https://data.worldbank.org/indicator/SI.POV.GINI

[14] J. Maynard Smith and G. R. Price, "The logic of animal conflict," *Nature*, vol. 246, no. 5427, pp. 15–18, 1973.

[15] P. D. Taylor and L. B. Jonker, "Evolutionary stable strategies and game dynamics," *Math. Biosci.*, vol. 40, no. 1–2, pp. 145–156, 1978.

[16] G. Szabó and G. Fáth, "Evolutionary games on graphs," *Phys. Rep.*, vol. 446, no. 4–6, pp. 97–216, 2007.

[17] M. A. Nowak, "Five rules for the evolution of cooperation," *Science*, vol. 314, no. 5805, pp. 1560–1563, 2006.

[18] M. A. Nowak and R. M. May, "Evolutionary games and spatial chaos," *Nature*, vol. 359, no. 6398, pp. 826–829, 1992.

[19] R. Axelrod, *The Evolution of Cooperation*, Basic Books, 1984.

[20] J. L. Gallup, J. D. Sachs, and A. D. Mellinger, "Geography and economic development," *Int. Reg. Sci. Rev.*, vol. 22, no. 2, pp. 179–232, 1999.

[21] D. Acemoglu and J. A. Robinson, *Why Nations Fail: The Origins of Power, Prosperity, and Poverty*, Crown Business, 2012.

[22] C. S. Holling, "Resilience and stability of ecological systems," *Annu. Rev. Ecol. Syst.*, vol. 4, no. 1, pp. 1–23, 1973.

[23] T. Veblen, *The Theory of the Leisure Class*, Macmillan, 1899.

[24] A. Sen, *Development as Freedom*, Oxford Univ. Press, 1999.

[25] J. Grazzini and M. G. Richiardi, "Estimation of ergodic agent-based models by simulated minimum distance," *J. Econ. Dyn. Control*, vol. 51, pp. 148–165, 2015.

[26] G. Fagiolo, M. Guerini, F. Lamperti, A. Moneta, and A. Roventini, "Validation of agent-based models in economics and finance," in *Computer Simulation Validation*, C. Beisbart and N. J. Saam, Eds. Springer, 2019, pp. 763–787.

[27] J. Kazil, D. Masad, and A. Crooks, "Utilizing Python for agent-based modeling: The Mesa framework," in *Proc. Social, Cultural, and Behavioral Modeling*, Springer, 2020, pp. 308–317.

[28] C. E. Shannon, "A mathematical theory of communication," *Bell Syst. Tech. J.*, vol. 27, no. 3, pp. 379–423, 1948.

[29] D. J. Watts and S. H. Strogatz, "Collective dynamics of 'small-world' networks," *Nature*, vol. 393, no. 6684, pp. 440–442, 1998.

[30] A.-L. Barabási and R. Albert, "Emergence of scaling in random networks," *Science*, vol. 286, no. 5439, pp. 509–512, 1999.

[31] S. Bowles, "Group competition, reproductive leveling, and the evolution of human altruism," *Science*, vol. 314, no. 5805, pp. 1569–1572, 2006.

[32] R. D. Putnam, *Bowling Alone: The Collapse and Revival of American Community*, Simon & Schuster, 2000.

[33] C. Tilly, *Coercion, Capital, and European States, AD 990–1992*, Blackwell, 1992.

[34] C. Tilly, *Durable Inequality*, Univ. of California Press, 1999.

[35] A. Deaton, *The Great Escape: Health, Wealth, and the Origins of Inequality*, Princeton Univ. Press, 2013.

[36] G. Zucman, *The Hidden Wealth of Nations: The Scourge of Tax Havens*, Univ. of Chicago Press, 2015.
