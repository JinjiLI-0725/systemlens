# SystemLens Atomic Operations v0.2

Atomic operations are the smallest reusable reasoning procedures executed by SystemLens.

Each operation should be independently callable and should have:
- a stable ID
- one primary lens family
- a defined purpose
- explicit inputs
- critical questions
- structured outputs
- source basis
- confidence behavior

---

## 1. define_system_boundary

Family: systems_thinking

Purpose:
Specify what is inside and outside the system being analyzed.

Inputs:
- problem
- optional timeframe
- optional geography
- optional population

Questions:
- What system is actually being discussed?
- What timeframe matters?
- Which actors are inside the model?
- Which external forces should be treated as environment rather than internal structure?
- What exclusions could materially change the analysis?

Outputs:
- included_scope
- excluded_scope
- timeframe
- geography
- boundary_uncertainties

Source basis:
- Thinking in Systems

---

## 2. identify_stocks_and_flows

Family: systems_thinking

Purpose:
Identify accumulations and the rates that increase or decrease them.

Inputs:
- system boundary
- variables

Questions:
- What accumulates over time?
- What increases that stock?
- What decreases it?
- Which flows are slow, constrained, or delayed?

Outputs:
- stocks
- inflows
- outflows
- candidate_constraints

Source basis:
- Thinking in Systems

---

## 3. detect_feedback_loops

Family: systems_thinking

Purpose:
Identify circular causal structures that amplify or stabilize behavior.

Inputs:
- actors
- variables
- relationships

Questions:
- Which relationships form a loop?
- Does the loop reinforce change or counteract it?
- What observable behavior would this loop generate?
- Is a delay present?

Outputs:
- loop_name
- loop_type
- causal_chain
- expected_behavior
- uncertainty

Source basis:
- Thinking in Systems

---

## 4. identify_leverage_points

Family: systems_thinking

Purpose:
Locate interventions likely to change system behavior rather than symptoms.

Inputs:
- system map
- feedback loops
- constraints

Questions:
- Where is the system most sensitive?
- Is the proposed intervention changing a parameter, information flow, rule, goal, or structure?
- Could the system compensate for the intervention?
- What unintended feedback may appear?

Outputs:
- intervention
- leverage_level
- expected_effect
- compensating_response
- confidence

Source basis:
- Thinking in Systems
- Sources of Power

---

## 5. identify_claim

Family: critical_thinking

Purpose:
Convert vague prose into a precise claim that can be examined.

Inputs:
- problem or argument

Questions:
- What exactly is being asserted?
- Is the claim descriptive, causal, predictive, or normative?
- What would count as disagreement?

Outputs:
- claim
- claim_type
- scope
- ambiguity

Source basis:
- The Uses of Argument
- Fundamentals of Critical Argumentation

---

## 6. identify_assumptions

Family: critical_thinking

Purpose:
Surface unstated premises required for a claim or recommendation to hold.

Inputs:
- claim
- proposed explanation

Questions:
- What must be true for this conclusion to follow?
- Which premise is unstated?
- Which assumption is empirical?
- Which assumption is normative?
- Which assumption is most fragile?

Outputs:
- assumption
- assumption_type
- importance
- testability
- fragility

Source basis:
- The Scout Mindset
- The Uses of Argument

---

## 7. detect_missing_evidence

Family: critical_thinking

Purpose:
Identify evidence required to distinguish plausible explanations.

Inputs:
- claim
- evidence
- alternatives

Questions:
- What evidence currently supports the claim?
- What evidence is absent?
- Which missing observation would most change the analysis?
- Are we relying on assertion rather than measurement?

Outputs:
- missing_evidence
- importance
- collection_method
- expected_information_gain

Source basis:
- How to Measure Anything
- The Scout Mindset

---

## 8. generate_counterarguments

Family: critical_thinking

Purpose:
Construct strong alternative interpretations rather than weak objections.

Inputs:
- claim
- evidence
- assumptions

Questions:
- What is the strongest reasonable objection?
- What alternative interpretation explains the same evidence?
- Which premise would a skeptical expert attack?
- What evidence would strengthen the counterargument?

Outputs:
- counterargument
- targeted_premise
- supporting_evidence_needed
- strength

Source basis:
- Fundamentals of Critical Argumentation
- The Scout Mindset

---

## 9. detect_motivated_reasoning

Family: metacognition_bias

Purpose:
Identify whether preferences, identity, incentives, or desired conclusions may be distorting reasoning.

Inputs:
- claim
- reasoning
- stakeholder context

Questions:
- Would the reasoning change if the conclusion were undesirable?
- Is evidence being evaluated asymmetrically?
- Is identity attached to the claim?
- What evidence is being dismissed too quickly?

Outputs:
- possible_motivation
- asymmetry
- disconfirming_test
- confidence

Source basis:
- The Scout Mindset

---

## 10. distinguish_correlation_from_causation

Family: causal_reasoning

Purpose:
Determine whether a causal interpretation is justified.

Inputs:
- proposed cause
- proposed effect
- observed association

Questions:
- Could both variables share a common cause?
- Could the direction of causation be reversed?
- Could selection produce the association?
- What intervention would distinguish causation from correlation?

Outputs:
- causal_claim
- alternative_explanations
- evidence_required
- causal_confidence

Source basis:
- The Book of Why
- Causal Inference: The Mixtape

---

## 11. detect_confounders

Family: causal_reasoning

Purpose:
Identify variables that may influence both proposed cause and effect.

Inputs:
- treatment/cause
- outcome/effect
- context

Questions:
- What could cause both X and Y?
- Was that variable measured?
- Would conditioning on it clarify or distort the relationship?
- Are there plausible unobserved confounders?

Outputs:
- confounder
- pathway
- observed_or_unobserved
- severity

Source basis:
- Causal Inference: The Mixtape
- The Book of Why

---

## 12. test_reverse_causation

Family: causal_reasoning

Purpose:
Check whether the stated effect may actually influence the proposed cause.

Inputs:
- proposed cause
- proposed effect

Questions:
- Could Y plausibly cause X?
- What temporal ordering is observed?
- What evidence would distinguish X→Y from Y→X?

Outputs:
- reverse_path
- plausibility
- evidence_needed

Source basis:
- The Book of Why

---

## 13. generate_counterfactual

Family: causal_reasoning

Purpose:
Ask what would likely happen under a meaningful alternative condition.

Inputs:
- factual scenario
- intervention
- outcome

Questions:
- What would happen if the intervention did not occur?
- What comparable case approximates that alternative?
- Which assumptions are required to estimate the counterfactual?

Outputs:
- factual_state
- counterfactual_state
- identifying_assumptions
- confidence

Source basis:
- The Book of Why
- Causal Inference: The Mixtape

---

## 14. define_decision

Family: decision_making

Purpose:
Convert an ambiguous situation into an explicit decision problem.

Inputs:
- problem

Questions:
- What decision actually needs to be made?
- Who is the decision maker?
- What are the alternatives?
- What is the decision deadline?
- Which constraints are binding?

Outputs:
- decision
- decision_maker
- alternatives
- deadline
- constraints

Source basis:
- How to Measure Anything

---

## 15. compare_alternatives

Family: decision_making

Purpose:
Compare options across explicit criteria rather than intuition alone.

Inputs:
- alternatives
- objectives
- constraints

Questions:
- What does each option optimize?
- What does each option sacrifice?
- Which outcomes are reversible?
- Which risks are asymmetric?

Outputs:
- alternative
- upside
- downside
- reversibility
- opportunity_cost
- uncertainty

Source basis:
- How to Measure Anything
- Algorithms to Live By

---

## 16. run_pre_mortem

Family: decision_making

Purpose:
Expose failure modes before committing to an option.

Inputs:
- proposed decision

Questions:
- Imagine the decision failed. Why?
- Which assumption was wrong?
- Which early warning signal was ignored?
- Which failure mode is preventable?

Outputs:
- failure_mode
- trigger
- early_warning_signal
- mitigation

Source basis:
- decision science / prospective hindsight
- compatible with Sources of Power mental simulation

---

## 17. mentally_simulate_action

Family: decision_making

Purpose:
Test whether a candidate action plausibly works in context before executing it.

Inputs:
- candidate action
- situation model

Questions:
- If we take this action, what happens next?
- Where does the scenario break?
- What cue would indicate the option is failing?
- Is another option needed before execution?

Outputs:
- simulated_sequence
- failure_point
- cues
- viability

Source basis:
- Sources of Power

---

## 18. estimate_value_of_information

Family: decision_making

Purpose:
Determine whether collecting more information is worth the time or cost.

Inputs:
- decision
- uncertainty
- possible measurement

Questions:
- Could this information change the decision?
- How uncertain are we now?
- What is the cost of being wrong?
- What is the cost of obtaining the information?

Outputs:
- information
- decision_sensitivity
- value
- collection_priority

Source basis:
- How to Measure Anything

---

## 19. identify_base_rate

Family: probabilistic_thinking

Purpose:
Anchor reasoning in the frequency of similar cases.

Inputs:
- target event
- reference class

Questions:
- What is the relevant reference class?
- How often does this outcome occur in similar cases?
- Is the current case genuinely exceptional?

Outputs:
- reference_class
- base_rate
- relevance
- adjustment_factors

Source basis:
- Superforecasting
- Thinking, Fast and Slow

---

## 20. assign_probability

Family: probabilistic_thinking

Purpose:
Express uncertainty numerically rather than with vague certainty language.

Inputs:
- proposition
- evidence
- base rate

Questions:
- What probability best reflects current belief?
- What evidence pushes it above or below the base rate?
- What uncertainty remains?

Outputs:
- probability
- confidence_interval_or_range
- rationale

Source basis:
- Superforecasting
- How to Measure Anything

---

## 21. update_belief

Family: probabilistic_thinking

Purpose:
Revise confidence when new evidence arrives.

Inputs:
- prior belief
- new evidence

Questions:
- How diagnostic is the evidence?
- Was this evidence expected under competing hypotheses?
- How much should confidence move?

Outputs:
- prior_probability
- evidence_direction
- updated_probability
- update_rationale

Source basis:
- Superforecasting
- The Scout Mindset
- How to Measure Anything

---

## 22. define_forecast_target

Family: forecasting

Purpose:
Turn a vague prediction into a resolvable forecasting question.

Inputs:
- forecast question

Questions:
- What exactly will be measured?
- By what date?
- What outcome counts as yes/no or success/failure?
- Which source will resolve the question?

Outputs:
- target
- resolution_date
- resolution_criteria
- source

Source basis:
- Superforecasting

---

## 23. decompose_forecast

Family: forecasting

Purpose:
Break a difficult forecast into smaller drivers.

Inputs:
- forecast target

Questions:
- Which independent or semi-independent drivers determine the outcome?
- Which drivers are measurable?
- Which driver dominates uncertainty?

Outputs:
- drivers
- subquestions
- driver_weights
- key_uncertainty

Source basis:
- Superforecasting

---

## 24. define_falsification_condition

Family: scientific_reasoning

Purpose:
Specify what observation would count against a hypothesis.

Inputs:
- hypothesis

Questions:
- What observation should not occur if the hypothesis is true?
- Is the hypothesis testable?
- Could every possible result be explained away?

Outputs:
- falsifying_observation
- testability
- escape_clauses
- strength

Source basis:
- The Logic of Scientific Discovery

---

## 25. design_risky_test

Family: scientific_reasoning

Purpose:
Prefer tests that strongly discriminate among competing explanations.

Inputs:
- hypothesis
- alternatives

Questions:
- Which observation would strongly support one explanation over another?
- What result would surprise the hypothesis?
- Is the test independent of the evidence used to generate the hypothesis?

Outputs:
- test
- predicted_result
- alternative_predictions
- discrimination_power

Source basis:
- The Logic of Scientific Discovery

---

## 26. decompose_argument

Family: argumentation

Purpose:
Represent an argument in structured form.

Inputs:
- argument text

Questions:
- What is the claim?
- What grounds support it?
- What warrant connects grounds to claim?
- What backing supports the warrant?
- What qualifier limits the claim?
- What rebuttal is acknowledged?

Outputs:
- claim
- grounds
- warrant
- backing
- qualifier
- rebuttal

Source basis:
- The Uses of Argument

---

## 27. assign_burden_of_proof

Family: argumentation

Purpose:
Identify which party must provide evidence for a contested claim.

Inputs:
- competing claims

Questions:
- Who is making the positive or exceptional assertion?
- What standard of evidence is appropriate?
- Has the burden been met?

Outputs:
- claimant
- burden
- evidence_standard
- burden_status

Source basis:
- Fundamentals of Critical Argumentation

---

## 28. challenge_quantitative_claim

Family: critical_thinking

Purpose:
Test whether a numerical claim is being presented fairly.

Inputs:
- quantitative claim
- data context

Questions:
- What is the denominator?
- What is the comparison group?
- Are like cases being compared?
- Is the time period cherry-picked?
- Is correlation being presented as causation?

Outputs:
- issue
- severity
- corrected_question
- evidence_needed

Source basis:
- Calling Bullshit
- Factfulness

---

## 29. detect_judgment_noise

Family: metacognition_bias

Purpose:
Identify unwanted variability in judgments that should be similar.

Inputs:
- multiple judgments
- decision context

Questions:
- Would independent reviewers reach materially different conclusions?
- Does timing, framing, or reviewer identity change the answer?
- Is disagreement caused by information or process noise?

Outputs:
- noise_source
- expected_variability
- process_fix

Source basis:
- Noise

---

## 30. ask_what_would_change_my_mind

Family: metacognition_bias

Purpose:
Force the reasoning process to specify disconfirming evidence in advance.

Inputs:
- current conclusion
- confidence

Questions:
- What evidence would lower confidence materially?
- What evidence would reverse the conclusion?
- What observation would support the strongest alternative?

Outputs:
- disconfirming_evidence
- update_threshold
- alternative_supported
- expected_confidence_change

Source basis:
- The Scout Mindset
- Superforecasting