# SystemLens Thinking Canon v0.2

SystemLens does not ingest books as prose.
It extracts reusable reasoning operations from foundational works and converts them into explicit, inspectable analytical procedures.

The canon is organized around one principle:

Source
→ Concept
→ Atomic reasoning operation
→ Lens family
→ Executable schema

## Selection criteria

A source belongs in the SystemLens canon if it contributes at least one of the following:

- a distinct reasoning operation
- a testable question
- a useful decomposition method
- a mechanism for challenging claims
- a method for reasoning under uncertainty
- a method for distinguishing explanation from evidence
- a method for improving judgment or decision quality

Books are not treated as authorities whose conclusions must be copied.
They are treated as sources of reasoning tools.

---

## Tier 1 — Core operational canon

| Source | Domain | Key concepts | Atomic operations to extract | Priority |
|---|---|---|---|---|
| Donella Meadows — Thinking in Systems | Systems Thinking | stocks, flows, reinforcing loops, balancing loops, delays, system structure, leverage points | define_system_boundary; identify_stocks_and_flows; detect_feedback_loops; identify_delays; identify_leverage_points | Core |
| Judea Pearl & Dana Mackenzie — The Book of Why | Causal Reasoning | causal models, intervention, counterfactuals, correlation vs causation | distinguish_correlation_from_causation; build_causal_graph; ask_intervention_question; generate_counterfactual | Core |
| Scott Cunningham — Causal Inference: The Mixtape | Causal Reasoning | DAGs, confounding, potential outcomes, identification | detect_confounders; test_backdoor_paths; define_treatment_and_outcome; assess_identification | Core |
| Julia Galef — The Scout Mindset | Critical Thinking / Metacognition | truth-seeking, motivated reasoning, belief updating, identity-protective cognition | detect_motivated_reasoning; generate_disconfirming_evidence; separate_identity_from_claim; update_confidence | Core |
| Philip Tetlock & Dan Gardner — Superforecasting | Forecasting / Probability | probabilistic judgment, decomposition, calibration, evidence aggregation, belief updating | define_forecast_target; decompose_forecast; assign_probability; identify_base_rate; update_forecast; define_resolution_condition | Core |
| Stephen Toulmin — The Uses of Argument | Argumentation | claim, grounds, warrant, backing, qualifier, rebuttal | decompose_argument; identify_warrant; identify_qualifier; identify_rebuttal | Core |
| Douglas Walton — Fundamentals of Critical Argumentation | Argumentation / Critical Thinking | argument schemes, burden of proof, critical questions, fallacies | identify_argument_scheme; assign_burden_of_proof; generate_critical_questions; test_argument_sufficiency | Core |
| Douglas Hubbard — How to Measure Anything | Measurement / Decision Making | measurement definition, uncertainty, risk, observable consequences, value of information | operationalize_variable; estimate_uncertainty; identify_decision_relevant_measurement; estimate_value_of_information | Core |
| Daniel Kahneman — Thinking, Fast and Slow | Judgment / Bias | fast vs deliberative judgment, anchoring, availability, framing, base-rate neglect, overconfidence | detect_anchoring; detect_availability_bias; detect_framing_effect; check_base_rate_neglect; test_overconfidence | Core |
| Daniel Kahneman, Olivier Sibony, Cass Sunstein — Noise | Judgment Quality | judgment variability, bias vs noise, decision hygiene | detect_judgment_noise; separate_bias_from_noise; standardize_judgment_process; compare_independent_estimates | Core |

---

## Tier 2 — Decision and problem-solving canon

| Source | Domain | Key concepts | Atomic operations to extract | Priority |
|---|---|---|---|---|
| Gary Klein — Sources of Power | Decision Making | recognition-primed decisions, mental simulation, leverage points, expert intuition | recognize_situation_pattern; mentally_simulate_action; test_first_workable_option; identify_expertise_limits | High |
| Brian Christian & Tom Griffiths — Algorithms to Live By | Decision Making / Search | explore-exploit, optimal stopping, sorting, scheduling, caching | test_explore_exploit_balance; evaluate_stopping_rule; prioritize_queue; reduce_search_cost | High |
| Karl Popper — The Logic of Scientific Discovery | Scientific Reasoning | falsifiability, testability, corroboration | define_falsification_condition; assess_testability; distinguish_confirmation_from_corrobation; design_risky_test | High |
| Carl Bergstrom & Jevin West — Calling Bullshit | Evidence / Data Reasoning | misleading statistics, selection bias, visualization, correlation vs causation, quantitative skepticism | challenge_quantitative_claim; inspect_denominator; test_like_with_like; detect_selection_bias; inspect_visualization_claim | High |
| Hans Rosling, Ola Rosling, Anna Rosling Rönnlund — Factfulness | Statistical / World-model Reasoning | gap instinct, negativity, size, generalization, single perspective | check_distribution_not_binary; normalize_by_denominator; test_trend_against_data; challenge_single_story | Medium |

---

## Tier 3 — Supporting canon

These sources are useful but should not define the first implementation.

| Source | Domain | Role in SystemLens |
|---|---|---|
| Donella Meadows — Leverage Points: Places to Intervene in a System | Systems Thinking | refine intervention ranking |
| Gary Klein — Seeing What Others Don't | Insight / Sensemaking | anomaly detection and insight formation |
| Nate Silver — The Signal and the Noise | Forecasting | signal/noise distinction and prediction discipline |
| Annie Duke — Thinking in Bets | Decision Making | separate decision quality from outcome quality |
| Richard Nisbett — Mindware | Statistical Reasoning | statistical and scientific reasoning habits |
| David Spiegelhalter — The Art of Statistics | Evidence / Statistics | uncertainty communication and evidence interpretation |

---

# Lens family mapping

## Systems Thinking
Primary sources:
- Thinking in Systems
- Sources of Power
- Leverage Points

Primary operations:
- define_system_boundary
- identify_stocks_and_flows
- map_relationships
- detect_feedback_loops
- identify_delays
- identify_leverage_points

## Critical Thinking
Primary sources:
- The Scout Mindset
- Fundamentals of Critical Argumentation
- Calling Bullshit
- Thinking, Fast and Slow

Primary operations:
- identify_claim
- identify_assumptions
- detect_missing_evidence
- generate_counterarguments
- detect_motivated_reasoning
- challenge_quantitative_claim

## Causal Reasoning
Primary sources:
- The Book of Why
- Causal Inference: The Mixtape

Primary operations:
- distinguish_correlation_from_causation
- build_causal_graph
- detect_confounders
- test_reverse_causation
- generate_counterfactual
- assess_identification

## Decision Making
Primary sources:
- How to Measure Anything
- Sources of Power
- Algorithms to Live By
- Thinking, Fast and Slow

Primary operations:
- define_decision
- compare_alternatives
- identify_opportunity_cost
- mentally_simulate_action
- run_pre_mortem
- estimate_value_of_information
- test_explore_exploit_balance

## Forecasting & Probability
Primary sources:
- Superforecasting
- How to Measure Anything

Primary operations:
- define_forecast_target
- identify_base_rate
- assign_probability
- decompose_forecast
- update_forecast
- calibrate_confidence
- define_resolution_condition

## Scientific Reasoning
Primary sources:
- The Logic of Scientific Discovery
- Calling Bullshit
- Causal Inference: The Mixtape

Primary operations:
- form_hypothesis
- define_falsification_condition
- assess_testability
- design_risky_test
- separate_observation_from_interpretation

## Argumentation
Primary sources:
- The Uses of Argument
- Fundamentals of Critical Argumentation

Primary operations:
- decompose_argument
- identify_warrant
- identify_rebuttal
- assign_burden_of_proof
- generate_critical_questions

## Metacognition & Judgment Quality
Primary sources:
- The Scout Mindset
- Thinking, Fast and Slow
- Noise
- Superforecasting

Primary operations:
- detect_motivated_reasoning
- detect_confirmation_bias
- detect_anchoring
- detect_judgment_noise
- ask_what_would_change_my_mind
- calibrate_confidence

---

# Canon rules for implementation

1. An atomic operation should correspond to a reasoning action, not a book chapter.
2. Two sources may support the same operation.
3. An operation should be reusable across domains.
4. Outputs should be inspectable.
5. The model must separate:
   - observation
   - inference
   - assumption
   - hypothesis
   - uncertainty
6. Operations should explicitly state what evidence would change their conclusion.
7. A lens should activate only operations relevant to the problem.
8. More lenses do not automatically mean better reasoning.
9. The system must not treat framework-derived hypotheses as facts.
10. Confidence must remain separate from eloquence.

---

# v0.2 implementation target

SystemLens v0.2 should support approximately 25–30 high-quality atomic operations.

The first production-quality set should prioritize:

- systems structure
- assumptions
- evidence quality
- causality
- alternatives
- counterfactuals
- uncertainty
- measurement
- decision trade-offs
- falsification
- forecasting
- judgment hygiene

The target is not maximum framework coverage.

The target is a small set of reasoning operations that materially improve analysis.