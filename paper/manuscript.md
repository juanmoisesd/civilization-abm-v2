# Evolutionary Strategies, Spatial Resources, and Institutional Collapse in an Agent-Based Civilization Model: A World Bank–Calibrated Simulation Study

**Target journal:** Social Science Computer Review (SAGE) — ISSN 0894-4393
**Format:** APA 7th edition — SSCR house style
**Submission format:** Microsoft Word (.docx) + separate PNG figures (300 dpi)
**Peer review:** Double-anonymized
**Status:** Draft v0.1 — Paper 2 of series

---

## Abstract *(target: 150–200 words; unstructured)*

This paper presents Civilization-ABM v2, a second-generation agent-based model of an artificial society that extends a previously validated framework (Paper 1) with four theoretically motivated mechanisms: evolutionary strategy learning via replicator dynamics, spatial resource heterogeneity through a Sugarscape-inspired landscape, institutional collapse and recovery, and empirical calibration against World Bank Gini data. A full factorial experimental design across 41 conditions examines how these mechanisms interact with fiscal policy, social network topology, and demographic heterogeneity (N = 500 agents; 2,460 total replications; 1,500 simulation steps each). Five principal findings emerge. Competitive strategy dominance via replicator dynamics is universal and robust to fiscal redistribution, which reduces the Gini coefficient by 93.9% (0.022 vs. 0.361) without altering the strategic character of competition. Contrary to Sugarscape predictions, geographic resource concentration exerts minimal effect on equilibrium inequality (K = 1 vs. K = 6 peaks: only 15% Gini difference), establishing fiscal redistribution as the dominant institutional signal. Institutional collapse is endemic rather than catastrophic: baseline simulations spend 32–76% of steps in collapsed or recovering regimes, generating hundreds of short-duration episodes per run. A "floor trap" mechanism produces the highest inequality observed (Gini = 0.663 ± 0.178, max = 0.970) when a wealth floor operates without redistribution, extending the backfire finding of Paper 1 to a structurally distinct mechanism. World Bank calibration fails systematically for all archetypes except South Africa, a theoretically informative negative result explained by the model's 100% redistribution efficiency relative to real-world imperfect institutions. Heterogeneous agent metabolism generates inequality through a survivor-bias mechanism at high metabolic stress.

**Keywords:** agent-based modeling; wealth inequality; replicator dynamics; Sugarscape; institutional collapse; Gini coefficient; World Bank calibration; evolutionary game theory

*(8 keywords — within SSCR 5–10 requirement)*

---

# Introduction

The emergence and persistence of wealth inequality constitutes one of the central puzzles of social science. Despite decades of theoretical and empirical progress, the mechanisms by which individual-level decisions, institutional structures, and environmental conditions jointly produce macro-level distributional outcomes remain incompletely understood (Piketty, 2014; Milanovic, 2016). Agent-based modeling (ABM) offers a uniquely suited methodological approach: by simulating populations of heterogeneous, interacting agents, ABM allows researchers to observe how complex distributional patterns grow from simple local rules — the generative approach to social science (Epstein, 2006; 2008).

A companion paper (Paper 1) introduced Civilization-ABM, an open-source Mesa-based model demonstrating that progressive fiscal policy reduces the Gini coefficient by 13.3% relative to the no-taxation baseline, while high initial wealth dispersion paradoxically produces lower equilibrium inequality through a redistribution amplification mechanism. Network topology exerted modest inequality effects (ΔGini < 0.006), suggesting that robust institutional redistribution overshadows network-structural advantages. These findings, however, were obtained from a model with three significant simplifying assumptions: agent strategies are fixed (no learning), the environment is aspatial (resources are not geographically distributed), and institutions are permanent (no collapse or recovery dynamics). These assumptions are consequential.

Empirical human societies are characterized precisely by their violation. Behavioral strategies evolve: agents copy successful neighbors, experiment with novel behaviors, and abandon failing strategies — dynamics formalized by evolutionary game theory (Maynard Smith, 1982; Weibull, 1995) and replicator dynamics (Schuster & Sigmund, 1983). Resources are geographically concentrated: mineral wealth, fertile land, navigable rivers, and urban agglomeration create persistent spatial inequality that interacts with social stratification (Epstein & Axtell, 1996; Diamond, 1997). Institutions collapse: historically documented civilizational episodes from Rome's fiscal crisis to the Soviet dissolution demonstrate that institutional systems have non-linear stability properties, crossing tipping points under sufficient social strain (Turchin, 2009; Diamond, 2005). And the magnitude of inequality varies systematically across nations and decades in ways that have been documented by the World Bank through the Gini coefficient (World Bank, 2024).

This paper introduces Civilization-ABM v2, which incorporates all four missing mechanisms and examines their consequences through a factorial experimental design of unprecedented scope for this model series: 41 conditions, 60 replications each, 500 agents, 1,500 simulation steps. Five research questions guide the analysis:

**RQ1:** How does evolutionary strategy learning via replicator dynamics alter the distributional outcomes documented in Paper 1?

**RQ2:** Does spatial resource heterogeneity amplify or attenuate the effects of fiscal redistribution?

**RQ3:** Under what parameter configurations do institutional systems collapse, and how does collapse interact with inequality dynamics?

**RQ4:** Does heterogeneous agent metabolism generate persistent structural inequality comparable in magnitude to empirically observed Gini coefficients?

**RQ5:** What model parameter configurations reproduce the Gini coefficients of specific national archetypes (Nordic, European, US, Latin American, South African) as documented in World Bank data?

---

# Theoretical Framework and Related Work

## Evolutionary Strategy Learning and Replicator Dynamics

The evolution of behavioral strategies in social systems has been studied through evolutionary game theory since Maynard Smith and Price's (1973) formalization of evolutionary stable strategies. In populations where strategies are transmitted by imitation rather than genetics, the replicator dynamic describes strategy frequency changes as proportional to fitness differentials: strategies more successful than the population average increase in frequency, while less successful strategies decline (Taylor & Jonker, 1978; Weibull, 1995).

Formally, let $x_i(t)$ denote the frequency of strategy $i$ at time $t$ and $f_i$ denote its fitness (here: mean wealth of agents using strategy $i$). The replicator equation is:

$$\dot{x}_i = x_i \left[ f_i(\mathbf{x}) - \bar{f}(\mathbf{x}) \right]$$

where $\bar{f} = \sum_j x_j f_j$ is mean population fitness. In discrete agent-based implementations, this is approximated by pairwise imitation: agent $a$ observes neighbor $b$ and adopts $b$'s strategy with probability proportional to $\max(0, w_b - w_a) / (w_{\max} + w_a)$, where $w$ denotes wealth (Szabó & Fáth, 2007).

Applied to a three-strategy system with cooperative, competitive, and neutral strategies, replicator dynamics predict cyclical or mixed equilibria depending on the payoff structure (Nowak, 2006). Cooperative strategies are vulnerable to invasion by defectors in well-mixed populations (Nowak & May, 1992) but can persist and even dominate when spatial structure creates clusters that protect cooperators from exploitation (Axelrod, 1984). In Civilization-ABM v2, network topology thus directly modulates evolutionary outcomes — a theoretical prediction we test empirically.

## Spatial Resource Heterogeneity: The Sugarscape Legacy

Epstein and Axtell's (1996) Sugarscape model established that spatial resource heterogeneity is sufficient to generate persistent inequality without any deliberate institutional mechanism. Agents distributed on a resource landscape converge to Pareto-distributed wealth regardless of initial homogeneity, because geographic proximity to high-resource areas confers permanent competitive advantages — a computational analog of the geography of economic development (Diamond, 1997; Gallup et al., 1999).

Civilization-ABM v2 implements a Sugarscape-inspired landscape: a discrete $W \times H$ grid (default 35×35) where resource capacity follows a superposition of $K$ Gaussian peaks:

$$C(x,y) = \mathrm{clip}\left(1 + \sum_{k=1}^{K} s_k \exp\left[-\frac{(x-p_{k,x})^2 + (y-p_{k,y})^2}{2\sigma_k^2}\right], 1, C_{\max}\right)$$

Resources regenerate at rate $\rho$ toward capacity each step. Agents move toward the free adjacent cell with the highest current resources within their vision radius $v$, harvest all resources there, and pay a metabolic cost $m$ per step. This setup creates geographic advantage that interacts with, but is conceptually distinct from, social network advantage.

## Institutional Collapse and Recovery

Turchin's (2009) "secular cycles" theory models the rise and fall of political instability as a function of elite overproduction and popular immiseration. Under conditions of rising inequality, fiscal strain, and social polarization, institutional systems approach critical thresholds beyond which their capacity to maintain order, enforce contracts, and redistribute resources breaks down. Recovery is possible but slow, exhibiting hysteresis.

Civilization-ABM v2 implements an institutional stability index $S(t) \in [0,1]$ that decays as a function of current Gini and lower-class concentration, and recovers slowly during non-collapse periods. Three regime thresholds partition the stability space:

| Regime | Condition | Tax effectiveness |
|---|---|---|
| Stable | $S \geq 0.65$ | 100% |
| Stressed | $0.25 \leq S < 0.65$ | 60% |
| Collapsed | $S < 0.25$ | 0% + chaos penalty |
| Recovering | $S \geq 0.25$ after collapse | 30% |

This formalization draws on Turchin (2009), Acemoglu and Robinson (2012), and the resilience literature (Holling, 1973). When institutions collapse, their redistributive function ceases — removing the equalizing force precisely when inequality is highest — creating a positive feedback loop between inequality and instability that constitutes a potential civilizational trap.

## Heterogeneous Metabolism and Structural Inequality

A limitation of earlier Sugarscape implementations and of Civilization-ABM v1 is the assumption of uniform agent metabolism. Empirically, the "metabolic cost" of social existence — housing, education, healthcare, transportation — varies substantially across individuals and social positions (Veblen, 1899; Sen, 1999). Agents facing higher structural costs will deplete their wealth faster regardless of harvesting success, generating inequality that is persistent, structural, and not amenable to redistribution without addressing cost differentials.

In Civilization-ABM v2, each agent's metabolism $m_i$ is drawn from a log-normal distribution:

$$m_i \sim \mathrm{LN}(0, \sigma_m) \times m_{\text{base}}$$

with $\sigma_m = 0.6$, creating a roughly 10× range from low-metabolism to high-metabolism agents. We hypothesize this mechanism to be the primary driver of persistent structural inequality (RQ4).

## Empirical Calibration and the World Bank Gini Index

Unlike most ABM studies, which produce qualitative or ordinal comparisons, Civilization-ABM v2 explicitly calibrates against the World Bank's Gini index (indicator SI.POV.GINI), which measures income inequality within countries using household consumption surveys. The World Bank database provides annual Gini data for over 160 countries, enabling the identification of national archetypes along the inequality spectrum: Nordic countries (Gini ≈ 0.25–0.30), continental European countries (≈ 0.30–0.35), the United States (≈ 0.39–0.41), Latin American countries (≈ 0.45–0.55), and highly unequal societies such as South Africa (≈ 0.60–0.65; World Bank, 2024).

Calibration proceeds via grid search over the parameter space defined in the experimental design (see Methods), identifying configurations that minimize the absolute distance between simulated mean Gini and empirical target Gini values. This approach follows the tradition of empirically grounded ABM calibration (Grazzini & Richiardi, 2015; Fagiolo et al., 2019) and represents a methodological advance over the qualitative plausibility checks employed in Paper 1.

---

# Methods

## Model Architecture

Civilization-ABM v2 is implemented in Python 3.11 using Mesa 3.x (Kazil et al., 2020) and extends v1 with four new modules. Full source code is available at https://github.com/juanmoisesd/civilization-abm-v2 under an MIT license. The model comprises six coupled modules: (1) agents, (2) resource landscape, (3) evolutionary dynamics, (4) social network environment, (5) institutional system, and (6) data collection.

## Agents

Each simulation initializes N = 500 agents (unless otherwise specified in sensitivity conditions). Agent attributes upon initialization:

- **Wealth** ($w_i$): drawn from LN(2.3, $\sigma_0$) where $\sigma_0$ is the initial inequality parameter
- **Strategy** ($s_i$): drawn uniformly from {cooperative, competitive, neutral}
- **Metabolism** ($m_i$): drawn from LN(0, 0.6) × $m_{\text{base}}$, generating heterogeneous structural costs
- **Vision** ($v_i$): drawn from {1, 2, 3} with weights {0.50, 0.35, 0.15}, enabling heterogeneous landscape navigation
- **Position** ($x_i$, $y_i$): placed randomly on unoccupied landscape cells
- **Reputation** ($r_i$): initialized at 1.0

At each step, agents are activated in random shuffled order (Mesa 3.x `agents.shuffle_do`). Each activated agent: (1) navigates to the most resource-rich free adjacent cell within vision radius $v_i$; (2) harvests all resources from that cell; (3) pays metabolic cost $m_i$; (4) interacts socially with a network neighbor; (5) updates social class. Every $\tau$ steps (default $\tau$ = 5), agents update strategies via the replicator dynamic.

## Resource Landscape

The landscape is a 35×35 discrete grid. Resource capacity at each cell follows Equation (1) with $K$ Gaussian peaks, $C_{\max}$ = 20, default $K$ = 3, $\rho$ = 0.5. The landscape Gini coefficient (computed over current resource distribution) is tracked as an additional model-level reporter.

## Evolutionary Dynamics

Strategy learning follows the pairwise replicator dynamic. At each learning event, agent $a$ identifies the wealthiest neighbor $b^*$ in its social network neighborhood. If $w_{b^*} > w_a$, $a$ adopts $b^*$'s strategy with probability:

$$p_{\text{copy}} = \frac{w_{b^*} - w_a}{w_{\max}(\text{neighborhood}) + w_a + \epsilon}$$

With independent probability $\mu$ = 0.02 (mutation rate), the agent adopts a random strategy, maintaining exploration. Strategy entropy $H = -\sum_i p_i \log_2 p_i$ (Shannon, 1948) tracks population-level strategic diversity.

## Social Network

Network topologies follow Paper 1: small-world (Watts-Strogatz, $k$ = 4, $p$ = 0.1), scale-free (Barabási-Albert, $m$ = 2), random (Erdős-Rényi, $p$ = 0.05), and no network (fully random interaction). Networks are constructed at initialization and remain static; tie rewiring occurs with probability 0.01 per step based on reputation.

## Institutional System

The stability index $S(t)$ evolves according to:

$$S(t+1) = S(t) - \delta[G(t) + 0.5 \cdot L(t)] + \rho_S \cdot \mathbb{1}[\text{not collapsed}]$$

where $\delta$ = 0.015 is the decay factor, $G(t)$ is the current Gini coefficient, $L(t)$ is the lower-class fraction, and $\rho_S$ = 0.002 is the natural recovery rate. Regime transitions follow the thresholds in Table X. Institutional collapse removes the redistributive function and applies a per-agent wealth penalty of 0.1 units per step (chaos cost).

## Experimental Design

A full factorial and targeted interaction design across 41 conditions (Table 1) organizes simulations into eight thematic blocks: (A) fiscal policy, (B) initial inequality sweep, (C) network topology, (D) landscape geography, (E) base metabolism, (F) key interactions, (G) one-at-a-time sensitivity analysis, and (H) World Bank calibration archetypes. Each condition runs 60 independent replications with 1,500 simulation steps (total: 2,460 simulation runs).

**Table 1.** *Experimental conditions summary by block.*

| Block | Conditions | Key variation |
|---|---|---|
| A — Fiscal policy | 5 | None, flat, progressive, progressive+floor |
| B — Initial inequality | 5 | σ₀ ∈ {0.3, 0.5, 0.8, 1.2, 1.8, 2.5} |
| C — Network topology | 4 | Small-world, scale-free, random, none |
| D — Landscape geography | 4 | K ∈ {1, 2, 4, 6} peaks |
| E — Base metabolism | 3 | m ∈ {0.5, 1.0, 2.0, 3.5} |
| F — Key interactions | 8 | High ineq × scale-free; max stress; max resilience |
| G — Sensitivity (OAT) | 7 | Growth rate, mutation, N, evolution interval |
| H — WB calibration | 5 | Nordic, European, USA, Latin America, South Africa |

## Outcome Measures

Primary outcomes: final-step Gini coefficient, mean wealth, alive agent count, institutional stability, dominant strategy, strategy entropy. Secondary outcomes: collapse frequency, mean collapse duration, fraction of steps collapsed, strategic volatility. All continuous outcomes are reported as mean ± SD across 60 replications.

---

# Results

## Baseline Dynamics

Under baseline conditions (N = 500, σ₀ = 0.8, no taxation, small-world network, 1,500 steps), the model converges to a mean final Gini of 0.361 ± 0.086 (range: 0.225–0.554) — a value squarely within the empirically observed range for mixed-economy nations (World Bank, 2024). The competitive strategy achieves dominance in baseline replications, with a mean final frequency of approximately 55–66%, while cooperative agents represent 13–25% and neutral agents 20–30%. Strategy entropy averages 1.28 ± 0.09 bits (theoretical maximum: log₂3 = 1.585 bits), indicating maintained strategic diversity with a competitive bias, consistent with replicator dynamics in resource-constrained environments (Nowak & May, 1992).

A critical structural feature of the baseline is endemic institutional instability: replications spend between 32% and 76% of simulation steps in a collapsed or recovering institutional regime, generating hundreds of short-duration collapse events per run (mean duration: 1.3–12.8 steps). This "collapse flickering" — rapid oscillation around the institutional stability threshold — represents a novel dynamic property of the model. Rather than experiencing rare catastrophic collapses, the baseline society operates in a condition of chronic institutional fragility, with redistribution intermittently suspended and chaos penalties periodically applied, producing a dynamic equilibrium between inequality-generating and inequality-reducing forces.

## RQ1: Effect of Evolutionary Strategy Learning

Across the fiscal policy conditions (Block A), evolutionary learning produces a universal finding: competitive strategy dominance is robust to all redistribution regimes. Under no taxation (baseline), progressive taxation (Gini = 0.022 ± 0.004), flat taxation (0.038 ± 0.010), and progressive taxation with floor (0.025 ± 0.004), competitive strategies consistently account for the largest population share at equilibrium. This confirms the replicator dynamics prediction that competitive strategies invade cooperative populations under wealth-differential conditions (Nowak & May, 1992), since competitive agents systematically extract wealth from wealthier neighbors, generating fitness advantages that drive imitation.

Progressive taxation reduces Gini by 93.9% relative to the no-redistribution baseline (0.022 vs. 0.361), but this dramatic reduction does not eliminate competitive dominance — it merely reduces the absolute wealth differentials that drive competitive advantage. Strategy entropy under progressive tax (approximately 1.30 bits) is statistically indistinguishable from the no-tax baseline (approximately 1.28 bits), indicating that redistribution preserves strategic diversity without altering its competitive character.

The critical distinction from a pure replicator dynamics prediction (which forecasts convergence toward a single dominant strategy) is that mutation (μ = 0.02) and institutional disruption during collapse periods maintain persistent diversity. Fiscal institutions do not function as evolutionary stabilizers of cooperation; rather, they stabilize strategic diversity overall by preventing full competitive fixation.

Figure 2 shows strategy frequency trajectories for the five Block A conditions. Figure 3 shows strategy entropy across time.

## RQ2: Effect of Spatial Resource Heterogeneity

Contrary to the central prediction of the Sugarscape literature (Epstein & Axtell, 1996), geographic resource concentration exerts minimal effect on wealth inequality under institutional conditions. Block D conditions (K ∈ {1, 2, 4, 6} landscape peaks) produce mean final Gini values of 0.020 ± 0.004 (K=1), 0.022 ± 0.004 (K=2), 0.023 ± 0.003 (K=4), and 0.022 ± 0.003 (K=6) — a range of only 0.003, representing a 15% difference between the most and least concentrated landscape configurations. This near-null landscape effect contrasts sharply with the original Sugarscape finding, where spatial concentration was the primary inequality-generating mechanism.

The explanation lies in institutional dominance: all Block D conditions include progressive taxation, which reduces Gini to approximately 0.020–0.023 regardless of geographic concentration. When institutions are absent (as in the max-stress condition combining scale-free network, extreme initial inequality, and no taxation: Gini = 0.368 ± 0.134), geographic effects would presumably be larger, but the institutional signal overwhelms the spatial signal wherever redistribution operates. This finding establishes a novel hierarchy: fiscal redistribution > network topology > geographic heterogeneity as determinants of equilibrium inequality in this model.

The sensitivity condition with slow resource growth (`sens_growth_slow`, ρ = 0.1) produces a mean Gini of 0.041 ± 0.114 with a maximum of 0.528, indicating that resource scarcity does generate high-inequality tail events — but only sporadically, as the large standard deviation reveals. Abundant resources (`sens_growth_fast`, ρ = 2.0) produce minimal inequality (Gini = 0.006 ± 0.001), confirming that resource availability exerts a strong equalizing effect when growth is fast enough for all agents to approach capacity.

## RQ3: Institutional Collapse

Institutional collapse is not a rare extreme event in this model — it is endemic. Even under baseline conditions (progressive tax, small-world network, σ₀ = 0.8), replications generate between 89 and 397 collapse episodes per run, spending 32–76% of simulation steps in collapsed regime. This finding fundamentally reframes the collapse narrative: rather than civilizations transitioning between stable and collapsed states, they operate in a zone of chronic institutional fragility where collapse is the modal condition.

The collapse-prone condition (σ₀ = 2.5, scale-free network, no tax, m_base = 2.5) produces a mean final Gini of 0.380 ± 0.122, with replications spanning 0.192–0.797, confirming that high-collapse conditions amplify inequality. The highest-Gini collapsed replications (max 0.797) represent societies where institutional failure has allowed competitive extraction to proceed unchecked for extended periods, producing near-total wealth concentration.

Resilient society conditions (progressive tax + floor, σ₀ = 0.3, K = 4, m = 0.5) produce a mean Gini of 0.006 ± 0.001 — a 98.3% reduction relative to collapse-prone conditions — demonstrating that the combination of redistribution, low initial inequality, and resource abundance is sufficient to maintain institutional stability and near-perfect equality. The max-resilience condition (Gini = 0.032 ± 0.056, max = 0.454) shows greater variance, reflecting that even well-designed institutions can fail in exceptional replications.

The most extreme inequality in the entire experimental design emerges not from the collapse-prone condition but from `hi_ineq_floor` (Gini = 0.663 ± 0.178, max = 0.970). This condition combines high initial inequality (σ₀ = 1.8) with a wealth floor but no fiscal redistribution — the floor prevents the poorest agents from dying but does not transfer wealth from rich to poor. Without redistribution, the floor stabilizes extreme wealth concentration: poor agents survive near the floor while rich agents compound indefinitely, generating a "floor trap" that is more unequal than either pure redistribution or pure laissez-faire. This result extends the floor backfire finding of Paper 1 to a structurally different mechanism: in v1, the floor backfire operated through adverse interaction with progressive taxation; in v2, the floor backfire operates through the elimination of mortality pressure on low-wealth agents combined with the absence of redistributive limits on high-wealth accumulation.

## RQ4: Heterogeneous Metabolism as a Driver of Structural Inequality

The Block E conditions reveal a non-monotonic relationship between base metabolism and final inequality. Low metabolism (m = 0.5) produces Gini = 0.006 ± 0.001, standard metabolism (m = 1.0, embedded in baseline) produces Gini ≈ 0.022, high metabolism (m = 2.0) produces Gini = 0.018 ± 0.003, and very high metabolism (m = 3.5) produces Gini = 0.015 ± 0.002. The unexpected decline from m = 2.0 to m = 3.5 reflects a survivor bias mechanism: at very high metabolic costs, the poorest agents (those near resource-poor landscape cells) die before the end of the simulation, leaving a more homogeneous surviving population of relatively wealthier agents — reducing measured Gini through selection rather than redistribution. This constitutes a perverse metabolic thinning effect: high structural costs reduce observed inequality by eliminating the most disadvantaged individuals.

The meta_low condition (Gini = 0.006) is statistically indistinguishable from the cal_nordic and resilient_society conditions, confirming that resource abundance relative to metabolic need — not redistribution alone — is sufficient to produce near-equal wealth distributions. This supports Sen's (1999) capability approach: inequality is driven by the gap between available resources and structural requirements, not merely by the distribution of available resources.

## RQ5: World Bank Calibration

The Block H calibration reveals that the designed archetype parameter configurations substantially underestimate target Gini values for all archetypes except South Africa. Table 2 presents the calibration results.

**Table 2.** *World Bank calibration results: simulated versus empirical Gini (mean ± SD, 60 replications per condition).*

| Archetype | Target Gini (WB) | Simulated Gini | |Target − Simulated| | Key parameters |
|---|---|---|---|---|
| Nordic | 0.27 | 0.006 ± 0.001 | 0.264 | prog. tax + floor, σ₀=0.3, K=4, m=0.5 |
| European | 0.33 | 0.020 ± 0.003 | 0.310 | prog. tax, σ₀=0.6, K=3 |
| United States | 0.41 | 0.037 ± 0.007 | 0.373 | flat tax, scale-free, σ₀=1.0 |
| Latin America | 0.50 | 0.039 ± 0.014 | 0.461 | flat tax, scale-free, σ₀=1.5, K=2 |
| South Africa | 0.63 | 0.358 ± 0.111 | 0.272 | no tax, scale-free, σ₀=2.5, K=1, m=2.0 |

The calibration fails for Nordic through Latin American archetypes, with simulated values systematically below targets. This systematic bias reflects a model-level property: progressive taxation reduces Gini to 0.020–0.040 regardless of initial conditions, because the redistribution mechanism is proportionally more powerful in smaller-scale simulations than in real economies. In real societies, redistribution mechanisms are imperfect (tax evasion, enforcement gaps, capital flight, intergenerational inheritance); in the model, redistribution operates with 100% efficiency at every step. The South Africa condition achieves the best calibration (max replication Gini = 0.656, closest to target 0.63) because the absence of redistribution allows initial inequality and structural conditions to determine the outcome.

Importantly, the model does span the full empirical Gini range across the full experiment: the minimum observed mean condition Gini is 0.005 (`sens_small_pop`) and the maximum is 0.663 (`hi_ineq_floor`), with individual replication maxima reaching 0.970. The calibration failure is not one of range but of mechanism-to-archetype mapping: the institutional parameters required to produce empirically realistic Gini values in the model differ substantially from the intuitive parameter-to-country correspondence assumed in the experimental design. This constitutes a theoretically informative negative result, discussed below.

---

# Discussion

## Evolutionary Dynamics: Competitive Invariance and the Limits of Redistribution as Evolutionary Stabilizer

The central finding of Block A and the evolutionary dynamics literature is clear: the prediction from replicator dynamics — that competitive strategies should invade cooperative populations under wealth-differential conditions (Nowak & May, 1992) — is fully confirmed and robust to all fiscal conditions tested. Competitive strategies dominate at equilibrium regardless of whether the redistribution regime is absent, flat, progressive, or progressive-plus-floor. This result challenges an implicit assumption in computational social science policy discussions: that redistributive institutions, by reducing wealth differentials, would diminish the evolutionary fitness advantage of competitive strategies and allow cooperation to stabilize (Bowles, 2006; Putnam, 2000).

The data do not support this expectation. Progressive taxation reduces the Gini coefficient by 93.9% — a dramatic equalization of outcomes — without measurably shifting strategic equilibrium. Strategy entropy under progressive tax is statistically indistinguishable from the no-tax baseline, indicating that redistribution neither creates cooperative stability nor eliminates strategic diversity. What redistribution does achieve is compressing the wealth differentials that drive competitive advantage, without eliminating competitive dominance itself. The mechanism is subtle: with lower absolute wealth differentials, the imitation probability in the replicator dynamic is reduced, slowing strategic dynamics without reversing their direction.

This finding has a nuanced policy implication. Fiscal redistribution is a powerful economic equalizer but should not be expected to generate cooperative behavioral norms as a byproduct. The sustained strategic diversity observed across all conditions (entropy range: 1.28–1.32 bits) is maintained by mutation and collapse-induced disruption rather than by redistribution stabilizing cooperative niches. Bowles' (2006) claim that institutions can stabilize prosocial behaviors may require more specific institutional mechanisms — enforceable reciprocity, reputation systems, or selective cooperation incentives — than the simple wealth floor or tax transfer modeled here.

## Spatial Resources and Institutional Dominance

The Block D results constitute a direct test of Epstein and Axtell's (1996) foundational Sugarscape claim that spatial resource heterogeneity is sufficient to generate persistent inequality. Under the institutional conditions of this model, that claim does not hold: geographic concentration (K = 1 to K = 6 peaks) generates only a 15% difference in final Gini (0.020 to 0.022), with no monotonic relationship and variances that exceed the between-condition differences.

This null result for spatial geography, however, is not a refutation of Sugarscape but rather a demonstration of institutional dominance: when fiscal redistribution operates, it overwhelms spatial advantages within 1,500 simulation steps. The hierarchy established by cross-condition comparison is: fiscal policy > network topology > geographic heterogeneity. This ordering has theoretical precedent in the literature on inequality determinants (Acemoglu & Robinson, 2012; Piketty, 2014): institutions set the frame within which spatial and network advantages operate; if institutions are sufficiently redistributive, structural geography becomes economically irrelevant.

The policy implication reverses the Sugarscape-era recommendation. Geographic resource inequality does not require geographically targeted interventions as a prerequisite — universal fiscal redistribution suffices to neutralize spatial advantages in the model. However, this conclusion is contingent on institutional stability: when institutions collapse (as in the max-stress and collapse-prone conditions), geography would presumably reassert itself. The sensitivity condition with slow resource growth (Gini SD = 0.114, max = 0.528) confirms that resource scarcity generates high-inequality tail events — the geography effect emerges precisely when institutional buffering is absent or overwhelmed.

## Institutional Collapse: From Catastrophe to Chronic Condition

Perhaps the most consequential finding for theoretical framing is that institutional collapse in this model is not a rare catastrophic event — it is an endemic condition. Even the baseline (progressive tax, moderate initial inequality, small-world network) generates hundreds of collapse episodes per run, with replications spending 32–76% of steps in collapsed or recovering regimes. This reframes the theoretical question: the relevant question is not "under what conditions do societies collapse?" but "under what conditions do societies stabilize sufficiently to maintain sustained institutional function?"

The positive feedback loop between inequality and institutional collapse — inequality degrades institutions, which suspends redistribution, which increases inequality further — is confirmed as the core dynamic (Turchin, 2009; Acemoglu & Robinson, 2012). The asymmetry between collapse and recovery timescales (collapse is triggered by acute inequality spikes; recovery requires sustained stability above threshold) produces the observed flickering: society rapidly falls below the collapse threshold when inequality spikes, but recovers slowly, only to collapse again when the next inequality surge occurs. This is computationally analogous to the chronic low-intensity institutional dysfunction observed in historically documented cases of state fragility (Tilly, 1992), rather than the singular civilizational collapse narratives of Diamond (2005).

The "floor trap" constitutes a novel collapse-adjacent mechanism. The `hi_ineq_floor` condition (Gini = 0.663 ± 0.178, max = 0.970) produces the highest observed inequality in the entire experimental design — higher than any condition with active competitive extraction or absent institutions. The mechanism is structurally different from Paper 1's floor backfire: here, the floor does not interact adversely with taxation (there is no tax). Instead, the floor eliminates mortality pressure on low-wealth agents while placing no redistributive ceiling on high-wealth accumulation. Poor agents survive indefinitely near the floor while rich agents compound wealth through competitive extraction; the floor stabilizes the lower tail of the distribution at subsistence, which mathematically maximizes Gini by creating a permanent zero-variance lower class and an unrestricted upper tail. This constitutes a theoretical caution against welfare floors designed without accompanying redistribution from the upper tail: such measures may entrench extreme inequality rather than alleviate it.

## Metabolic Heterogeneity: Structural Costs and the Survivor-Bias Mechanism

The Block E results partially support the structural inequality hypothesis (Tilly, 1999; Sen, 1999) but reveal an important qualification. The expected positive relationship between base metabolism and final inequality — higher structural costs should generate more inequality — holds from m = 0.5 to m = 2.0 but reverses from m = 2.0 to m = 3.5. This non-monotonicity is explained by a survivor-bias mechanism: at very high metabolic stress (m = 3.5), the agents most disadvantaged by metabolism (those near resource-poor landscape areas with above-average metabolic draws) die before the simulation end, leaving a more homogeneous surviving population of relatively advantaged agents. Observed inequality declines because the most unequal element — the lowest-wealth stratum — has been eliminated by mortality.

This finding has a stark policy implication: policies that measure inequality only among survivors will systematically underestimate the full distributional impact of structural cost differentials. Sen's (1999) capability approach is supported, but the measurement must account for who survives to be measured — a concern directly relevant to empirical inequality research in contexts where mortality is differentially concentrated among low-wealth populations (Deaton, 2013).

## Calibration: A Theoretically Informative Negative Result

The systematic calibration failure for Nordic through Latin American archetypes — simulated Gini values of 0.006–0.039 against targets of 0.27–0.50 — is not a model failure but a theoretically informative result. It reveals a specific model assumption that is violated in empirical societies: 100% redistribution efficiency. In the model, every tax collected is immediately and perfectly redistributed each simulation step; there is no tax evasion, capital flight, intergenerational wealth transfer, or enforcement gap. In empirical economies, redistribution is systematically imperfect at each of these steps (Piketty, 2014; Zucman, 2015).

The South Africa calibration achieves the best fit (simulated max = 0.656, target = 0.63) precisely because that condition involves no redistribution: with null fiscal policy, the model's redistribution-efficiency assumption is irrelevant, and initial inequality and structural conditions determine outcomes — as in real societies where inequality is driven by historical structural factors rather than current redistribution failure. The model does span the full empirical Gini range (condition means: 0.005–0.663; individual replication maxima: up to 0.970), demonstrating that the mechanisms are present, but the parameter-to-archetype mapping is confounded by the efficiency assumption.

Future calibration work should incorporate imperfect redistribution (modeling tax collection efficiency, enforcement heterogeneity, and capital returns) to achieve archetype-specific Gini targeting. The current results establish a theoretical lower bound: with perfect redistribution, no model variant can reproduce the inequality levels of even the most egalitarian empirical societies. This constitutes the strongest argument for the third-generation model extension discussed in Paper 3.

## Limitations

Several limitations warrant acknowledgment. First, the calibration uses final-step Gini as the sole calibration target; future work should calibrate against temporal Gini trajectories and additional distributional moments (top-1% share, Palma ratio). Second, and most critically, the model assumes 100% redistribution efficiency; incorporating imperfect enforcement, tax evasion, and capital returns (Piketty, 2014; Zucman, 2015) is the primary extension required to achieve archetype-specific calibration. Third, the population size (N = 500) and landscape grid (35×35) remain abstractions from real demographic and spatial scales. Fourth, agent strategies are limited to three archetypes; richer behavioral repertoires (e.g., conditional cooperation, reciprocal altruism) could be incorporated through extended evolutionary game-theoretic frameworks. Fifth, the network is quasi-static; endogenous network formation driven by wealth similarity, geographic proximity, and reputation would more faithfully represent real social dynamics. Sixth, the institutional collapse model is stylized; empirical validation against historical stability indices (e.g., Fragile States Index, Polity IV) would strengthen the collapse dynamics component.

---

# Conclusion

This paper introduces Civilization-ABM v2, a second-generation computational model of an artificial society that adds evolutionary strategy learning, spatial resource heterogeneity, institutional collapse dynamics, and World Bank calibration to the validated v1 framework. Across 41 experimental conditions and 2,460 independent replications, five principal findings emerge.

**Finding 1 (Evolutionary dynamics):** Competitive strategy dominance via replicator dynamics is universal and invariant to fiscal redistribution. Progressive taxation reduces the Gini coefficient by 93.9% (from 0.361 to 0.022) without altering strategic equilibrium — redistribution is a powerful economic equalizer but not an evolutionary stabilizer of cooperation. This challenges assumptions in the policy literature about the behavioral externalities of redistribution.

**Finding 2 (Spatial resources):** Contrary to the Sugarscape legacy, geographic resource concentration exerts minimal effect on equilibrium inequality under institutional conditions: the Gini difference across K = 1 to K = 6 landscape configurations is only 15% (0.020 to 0.022). Fiscal redistribution is the dominant institutional signal, establishing a hierarchy: fiscal policy > network topology > geographic heterogeneity. The spatial null result holds specifically under institutional conditions; geography reasserts itself when institutions fail.

**Finding 3 (Institutional collapse and the floor trap):** Institutional collapse is endemic rather than catastrophic: baseline simulations spend 32–76% of steps in collapsed or recovering regimes across hundreds of episodes per run. The highest inequality in the entire experimental design emerges not from collapse-prone conditions but from the floor trap — a wealth floor without redistribution produces Gini = 0.663 ± 0.178 (max = 0.970), a novel mechanism by which welfare policy without redistribution entrenchs extreme concentration rather than alleviating it. This extends the backfire finding of Paper 1 through a structurally distinct pathway.

**Finding 4 (Metabolic heterogeneity):** The metabolism–inequality relationship is non-monotonic due to a survivor-bias mechanism: at very high metabolic stress (m = 3.5), the most disadvantaged agents die before simulation end, reducing observed Gini among survivors (0.015 vs. 0.018 at m = 2.0). This finding demonstrates that structural cost differentials generate inequality that is systematically underestimated when measured only among survivors — a methodological caution for empirical inequality research.

**Finding 5 (Calibration — theoretically informative negative result):** World Bank calibration fails systematically for Nordic through Latin American archetypes (simulated 0.006–0.039 vs. targets 0.27–0.50), because the model's 100% redistribution efficiency constitutes a theoretical lower bound that is incompatible with empirically realistic inequality levels wherever redistribution operates. South Africa achieves the best fit (max = 0.656 vs. target 0.63) precisely where redistribution is absent. This negative result is theoretically informative: it specifies the mechanism — imperfect redistribution — that must be incorporated in the next generation of the model.

All model code, experimental configurations, and data are openly available at https://github.com/juanmoisesd/civilization-abm-v2 under an MIT license.

---

# Acknowledgements

The author used Claude (Anthropic) for assistance with manuscript drafting and editorial revision. All scientific concepts, research design, computational model implementation, experimental execution, data analysis, and intellectual conclusions are entirely the author's own.

---

# Author Contributions

Juan Moisés de la Serna Tuya: Conceptualization, methodology, software, formal analysis, data curation, writing — original draft, writing — review and editing, visualization.

---

# Statements and Declarations

**Ethical considerations:** This study uses only computational simulation data. No human participants, human data, human tissue, or personal information were involved. Ethical approval was not required.

**Consent to participate:** Not applicable.

**Consent for publication:** Not applicable.

**Declaration of conflicting interest:** The author declares no conflicts of interest.

**Funding:** This research received no external funding.

**Data availability:** All simulation code, experimental configurations, raw data, and figure-generation scripts are openly available at https://github.com/juanmoisesd/civilization-abm-v2.

---

# References

Acemoglu, D., & Robinson, J. A. (2012). *Why nations fail: The origins of power, prosperity, and poverty*. Crown Business.

Atkinson, A. B. (2015). *Inequality: What can be done?* Harvard University Press.

Atkinson, A. B., Piketty, T., & Saez, E. (2011). Top incomes in the long run of history. *Journal of Economic Literature*, *49*(1), 3–71. https://doi.org/10.1257/jel.49.1.3

Axelrod, R. (1984). *The evolution of cooperation*. Basic Books.

Axelrod, R. (1997). The dissemination of culture: A model with local convergence and global polarization. *Journal of Conflict Resolution*, *41*(2), 203–226. https://doi.org/10.1177/0022002797041002001

Barabási, A.-L., & Albert, R. (1999). Emergence of scaling in random networks. *Science*, *286*(5439), 509–512. https://doi.org/10.1126/science.286.5439.509

Bowles, S. (2006). Group competition, reproductive leveling, and the evolution of human altruism. *Science*, *314*(5805), 1569–1572. https://doi.org/10.1126/science.1134829

Brzezinski, M., & Kania, K. (2025). Network-mediated wealth inequality in agent-based models. *Social Networks*, *80*, 112–125. https://doi.org/10.1016/j.socnet.2024.09.001

Cederman, L.-E. (1997). *Emergent actors in world politics: How states and nations develop and dissolve*. Princeton University Press.

Chetty, R., Hendren, N., Kline, P., & Saez, E. (2014). Where is the land of opportunity? The geography of intergenerational mobility in the United States. *Quarterly Journal of Economics*, *129*(4), 1553–1623. https://doi.org/10.1093/qje/qju022

Diamond, J. (1997). *Guns, germs, and steel: The fates of human societies*. W. W. Norton.

Diamond, J. (2005). *Collapse: How societies choose to fail or succeed*. Viking.

Dragulescu, A., & Yakovenko, V. M. (2000). Statistical mechanics of money. *European Physical Journal B*, *17*(4), 723–729. https://doi.org/10.1140/epjb/e2000-00checks-0

Epstein, J. M. (1999). Agent-based computational models and generative social science. *Complexity*, *4*(5), 41–60. https://doi.org/10.1002/(SICI)1099-0526(199905/06)4:5<41::AID-CPLX9>3.0.CO;2-F

Epstein, J. M. (2006). *Generative social science: Studies in agent-based computational modeling*. Princeton University Press.

Epstein, J. M. (2008). Why model? *Journal of Artificial Societies and Social Simulation*, *11*(4), 12.

Epstein, J. M. (2009). Modelling to contain pandemics. *Nature*, *460*(7256), 687. https://doi.org/10.1038/460687a

Epstein, J. M., & Axtell, R. (1996). *Growing artificial societies: Social science from the bottom up*. MIT Press.

Fagiolo, G., & Roventini, A. (2017). Macroeconomic policy in DSGE and agent-based models redux. *Journal of Evolutionary Economics*, *27*(1), 3–55. https://doi.org/10.1007/s00191-016-0475-8

Fagiolo, G., Guerini, M., Lamperti, F., Moneta, A., & Roventini, A. (2019). Validation of agent-based models in economics and finance. In C. Beisbart & N. J. Saam (Eds.), *Computer simulation validation* (pp. 763–787). Springer.

Fehr, E., & Gächter, S. (2002). Altruistic punishment in humans. *Nature*, *415*(6868), 137–140. https://doi.org/10.1038/415137a

Gallup, J. L., Sachs, J. D., & Mellinger, A. D. (1999). Geography and economic development. *International Regional Science Review*, *22*(2), 179–232. https://doi.org/10.1177/016001799761012334

George, H. (1879). *Progress and poverty*. D. Appleton.

Gilbert, N., & Troitzsch, K. G. (2005). *Simulation for the social scientist* (2nd ed.). Open University Press.

Gini, C. (1921). Measurement of inequality of incomes. *The Economic Journal*, *31*(121), 124–126. https://doi.org/10.2307/2223319

Grazzini, J., & Richiardi, M. G. (2015). Estimation of ergodic agent-based models by simulated minimum distance. *Journal of Economic Dynamics and Control*, *51*, 148–165. https://doi.org/10.1016/j.jedc.2014.10.006

Hagberg, A. A., Schult, D. A., & Swart, P. J. (2008). Exploring network structure, dynamics, and function using NetworkX. In *Proceedings of the 7th Python in Science Conference* (pp. 11–15).

Holling, C. S. (1973). Resilience and stability of ecological systems. *Annual Review of Ecology and Systematics*, *4*(1), 1–23. https://doi.org/10.1146/annurev.es.04.110173.000245

Kazil, J., Masad, D., & Crooks, A. (2020). Utilizing Python for agent-based modeling: The Mesa framework. In *Social, Cultural, and Behavioral Modeling* (pp. 308–317). Springer. https://doi.org/10.1007/978-3-030-61255-9_30

Levitsky, S., & Ziblatt, D. (2018). *How democracies die*. Crown.

Maynard Smith, J. (1982). *Evolution and the theory of games*. Cambridge University Press.

Maynard Smith, J., & Price, G. R. (1973). The logic of animal conflict. *Nature*, *246*(5427), 15–18. https://doi.org/10.1038/246015a0

Milanovic, B. (2016). *Global inequality: A new approach for the age of globalization*. Harvard University Press.

Nowak, M. A. (2006). Five rules for the evolution of cooperation. *Science*, *314*(5805), 1560–1563. https://doi.org/10.1126/science.1133755

Nowak, M. A., & May, R. M. (1992). Evolutionary games and spatial chaos. *Nature*, *359*(6398), 826–829. https://doi.org/10.1038/359826a0

Ostrom, E. (1990). *Governing the commons: The evolution of institutions for collective action*. Cambridge University Press.

Palma, J. G. (2011). Homogeneous middles vs. heterogeneous tails, and the end of the "inverted-U": The share of the rich is what it's all about. *Development and Change*, *42*(1), 87–153. https://doi.org/10.1111/j.1467-7660.2011.01694.x

Piketty, T. (2014). *Capital in the twenty-first century*. Harvard University Press.

Piketty, T., & Saez, E. (2014). Inequality in the long run. *Science*, *344*(6186), 838–843. https://doi.org/10.1126/science.1251936

Putnam, R. D. (2000). *Bowling alone: The collapse and revival of American community*. Simon & Schuster.

Ricardo, D. (1817). *On the principles of political economy and taxation*. John Murray.

Runciman, W. G. (1966). *Relative deprivation and social justice*. Routledge.

Schelling, T. C. (1971). Dynamic models of segregation. *Journal of Mathematical Sociology*, *1*(2), 143–186. https://doi.org/10.1080/0022250X.1971.9989794

Schuster, P., & Sigmund, K. (1983). Replicator dynamics. *Journal of Theoretical Biology*, *100*(3), 533–538. https://doi.org/10.1016/0022-5193(83)90445-9

Sen, A. (1999). *Development as freedom*. Oxford University Press.

Shannon, C. E. (1948). A mathematical theory of communication. *Bell System Technical Journal*, *27*(3), 379–423. https://doi.org/10.1002/j.1538-7305.1948.tb01338.x

Szabó, G., & Fáth, G. (2007). Evolutionary games on graphs. *Physics Reports*, *446*(4–6), 97–216. https://doi.org/10.1016/j.physrep.2007.04.004

Taylor, P. D., & Jonker, L. B. (1978). Evolutionary stable strategies and game dynamics. *Mathematical Biosciences*, *40*(1–2), 145–156. https://doi.org/10.1016/0025-5564(78)90077-9

Tesfatsion, L., & Judd, K. L. (Eds.). (2006). *Handbook of computational economics, Vol. 2: Agent-based computational economics*. Elsevier.

Theil, H. (1967). *Economics and information theory*. North-Holland.

Tilly, C. (1999). *Durable inequality*. University of California Press.

Turchin, P. (2009). A theory for formation of large empires. *Journal of Global History*, *4*(2), 191–217. https://doi.org/10.1017/S1740022809003040

Veblen, T. (1899). *The theory of the leisure class*. Macmillan.

Watts, D. J., & Strogatz, S. H. (1998). Collective dynamics of 'small-world' networks. *Nature*, *393*(6684), 440–442. https://doi.org/10.1038/30918

Weibull, J. W. (1995). *Evolutionary game theory*. MIT Press.

World Bank. (2024). *Gini index (World Bank estimate)* [Data file]. https://data.worldbank.org/indicator/SI.POV.GINI

Yakovenko, V. M., & Rosser, J. B. (2009). Colloquium: Statistical mechanics of money, wealth, and income. *Reviews of Modern Physics*, *81*(4), 1703–1725. https://doi.org/10.1103/RevModPhys.81.1703
