"""Canon v0.2 metadata for the curated executable reasoning registry."""

from dataclasses import asdict, dataclass

from backend.schemas.analysis import LensName


@dataclass(frozen=True)
class AtomicOperation:
    """Stable metadata for one executable atomic reasoning operation."""

    id: str
    name: str
    family: str
    purpose: str
    inputs: tuple[str, ...]
    questions: tuple[str, ...]
    outputs: tuple[str, ...]
    source_basis: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-compatible representation of the operation."""
        return asdict(self)


def _operation(
    id: str,
    name: str,
    family: str,
    purpose: str,
    inputs: tuple[str, ...],
    questions: tuple[str, ...],
    outputs: tuple[str, ...],
    source_basis: tuple[str, ...],
) -> AtomicOperation:
    return AtomicOperation(
        id, name, family, purpose, inputs, questions, outputs, source_basis
    )


# This tuple is deliberately smaller than the documented 30-operation canon.
ACTIVE_OPERATIONS: tuple[AtomicOperation, ...] = (
    _operation(
        "define_system_boundary",
        "Define system boundary",
        "systems_thinking",
        "Specify what is inside and outside the system being analyzed.",
        ("problem", "optional timeframe", "optional geography", "optional population"),
        (
            "What system is actually being discussed?",
            "What timeframe matters?",
            "Which actors are inside the model?",
            "Which external forces should be treated as environment rather than internal structure?",
            "What exclusions could materially change the analysis?",
        ),
        (
            "included_scope",
            "excluded_scope",
            "timeframe",
            "geography",
            "boundary_uncertainties",
        ),
        ("Thinking in Systems",),
    ),
    _operation(
        "identify_stocks_and_flows",
        "Identify stocks and flows",
        "systems_thinking",
        "Identify accumulations and the rates that increase or decrease them.",
        ("system boundary", "variables"),
        (
            "What accumulates over time?",
            "What increases that stock?",
            "What decreases it?",
            "Which flows are slow, constrained, or delayed?",
        ),
        ("stocks", "inflows", "outflows", "candidate_constraints"),
        ("Thinking in Systems",),
    ),
    _operation(
        "detect_feedback_loops",
        "Detect feedback loops",
        "systems_thinking",
        "Identify circular causal structures that amplify or stabilize behavior.",
        ("actors", "variables", "relationships"),
        (
            "Which relationships form a loop?",
            "Does the loop reinforce change or counteract it?",
            "What observable behavior would this loop generate?",
            "Is a delay present?",
        ),
        ("loop_name", "loop_type", "causal_chain", "expected_behavior", "uncertainty"),
        ("Thinking in Systems",),
    ),
    _operation(
        "identify_leverage_points",
        "Identify leverage points",
        "systems_thinking",
        "Locate interventions likely to change system behavior rather than symptoms.",
        ("system map", "feedback loops", "constraints"),
        (
            "Where is the system most sensitive?",
            "Is the proposed intervention changing a parameter, information flow, rule, goal, or structure?",
            "Could the system compensate for the intervention?",
            "What unintended feedback may appear?",
        ),
        (
            "intervention",
            "leverage_level",
            "expected_effect",
            "compensating_response",
            "confidence",
        ),
        ("Thinking in Systems", "Sources of Power"),
    ),
    _operation(
        "identify_claim",
        "Identify claim",
        "critical_thinking",
        "Convert vague prose into a precise claim that can be examined.",
        ("problem or argument",),
        (
            "What exactly is being asserted?",
            "Is the claim descriptive, causal, predictive, or normative?",
            "What would count as disagreement?",
        ),
        ("claim", "claim_type", "scope", "ambiguity"),
        ("The Uses of Argument", "Fundamentals of Critical Argumentation"),
    ),
    _operation(
        "identify_assumptions",
        "Identify assumptions",
        "critical_thinking",
        "Surface unstated premises required for a claim or recommendation to hold.",
        ("claim", "proposed explanation"),
        (
            "What must be true for this conclusion to follow?",
            "Which premise is unstated?",
            "Which assumption is empirical?",
            "Which assumption is normative?",
            "Which assumption is most fragile?",
        ),
        ("assumption", "assumption_type", "importance", "testability", "fragility"),
        ("The Scout Mindset", "The Uses of Argument"),
    ),
    _operation(
        "detect_missing_evidence",
        "Detect missing evidence",
        "critical_thinking",
        "Identify evidence required to distinguish plausible explanations.",
        ("claim", "evidence", "alternatives"),
        (
            "What evidence currently supports the claim?",
            "What evidence is absent?",
            "Which missing observation would most change the analysis?",
            "Are we relying on assertion rather than measurement?",
        ),
        (
            "missing_evidence",
            "importance",
            "collection_method",
            "expected_information_gain",
        ),
        ("How to Measure Anything", "The Scout Mindset"),
    ),
    _operation(
        "generate_counterarguments",
        "Generate counterarguments",
        "critical_thinking",
        "Construct strong alternative interpretations rather than weak objections.",
        ("claim", "evidence", "assumptions"),
        (
            "What is the strongest reasonable objection?",
            "What alternative interpretation explains the same evidence?",
            "Which premise would a skeptical expert attack?",
            "What evidence would strengthen the counterargument?",
        ),
        (
            "counterargument",
            "targeted_premise",
            "supporting_evidence_needed",
            "strength",
        ),
        ("Fundamentals of Critical Argumentation", "The Scout Mindset"),
    ),
    _operation(
        "distinguish_correlation_from_causation",
        "Distinguish correlation from causation",
        "causal_reasoning",
        "Determine whether a causal interpretation is justified.",
        ("proposed cause", "proposed effect", "observed association"),
        (
            "Could both variables share a common cause?",
            "Could the direction of causation be reversed?",
            "Could selection produce the association?",
            "What intervention would distinguish causation from correlation?",
        ),
        (
            "causal_claim",
            "alternative_explanations",
            "evidence_required",
            "causal_confidence",
        ),
        ("The Book of Why", "Causal Inference: The Mixtape"),
    ),
    _operation(
        "detect_confounders",
        "Detect confounders",
        "causal_reasoning",
        "Identify variables that may influence both proposed cause and effect.",
        ("treatment/cause", "outcome/effect", "context"),
        (
            "What could cause both X and Y?",
            "Was that variable measured?",
            "Would conditioning on it clarify or distort the relationship?",
            "Are there plausible unobserved confounders?",
        ),
        ("confounder", "pathway", "observed_or_unobserved", "severity"),
        ("Causal Inference: The Mixtape", "The Book of Why"),
    ),
    _operation(
        "test_reverse_causation",
        "Test reverse causation",
        "causal_reasoning",
        "Check whether the stated effect may actually influence the proposed cause.",
        ("proposed cause", "proposed effect"),
        (
            "Could Y plausibly cause X?",
            "What temporal ordering is observed?",
            "What evidence would distinguish X→Y from Y→X?",
        ),
        ("reverse_path", "plausibility", "evidence_needed"),
        ("The Book of Why",),
    ),
    _operation(
        "generate_counterfactual",
        "Generate counterfactual",
        "causal_reasoning",
        "Ask what would likely happen under a meaningful alternative condition.",
        ("factual scenario", "intervention", "outcome"),
        (
            "What would happen if the intervention did not occur?",
            "What comparable case approximates that alternative?",
            "Which assumptions are required to estimate the counterfactual?",
        ),
        (
            "factual_state",
            "counterfactual_state",
            "identifying_assumptions",
            "confidence",
        ),
        ("The Book of Why", "Causal Inference: The Mixtape"),
    ),
    _operation(
        "define_decision",
        "Define decision",
        "decision_making",
        "Convert an ambiguous situation into an explicit decision problem.",
        ("problem",),
        (
            "What decision actually needs to be made?",
            "Who is the decision maker?",
            "What are the alternatives?",
            "What is the decision deadline?",
            "Which constraints are binding?",
        ),
        ("decision", "decision_maker", "alternatives", "deadline", "constraints"),
        ("How to Measure Anything",),
    ),
    _operation(
        "compare_alternatives",
        "Compare alternatives",
        "decision_making",
        "Compare options across explicit criteria rather than intuition alone.",
        ("alternatives", "objectives", "constraints"),
        (
            "What does each option optimize?",
            "What does each option sacrifice?",
            "Which outcomes are reversible?",
            "Which risks are asymmetric?",
        ),
        (
            "alternative",
            "upside",
            "downside",
            "reversibility",
            "opportunity_cost",
            "uncertainty",
        ),
        ("How to Measure Anything", "Algorithms to Live By"),
    ),
    _operation(
        "run_pre_mortem",
        "Run pre-mortem",
        "decision_making",
        "Expose failure modes before committing to an option.",
        ("proposed decision",),
        (
            "Imagine the decision failed. Why?",
            "Which assumption was wrong?",
            "Which early warning signal was ignored?",
            "Which failure mode is preventable?",
        ),
        ("failure_mode", "trigger", "early_warning_signal", "mitigation"),
        (
            "decision science / prospective hindsight",
            "compatible with Sources of Power mental simulation",
        ),
    ),
    _operation(
        "estimate_value_of_information",
        "Estimate value of information",
        "decision_making",
        "Determine whether collecting more information is worth the time or cost.",
        ("decision", "uncertainty", "possible measurement"),
        (
            "Could this information change the decision?",
            "How uncertain are we now?",
            "What is the cost of being wrong?",
            "What is the cost of obtaining the information?",
        ),
        ("information", "decision_sensitivity", "value", "collection_priority"),
        ("How to Measure Anything",),
    ),
    _operation(
        "identify_base_rate",
        "Identify base rate",
        "probabilistic_thinking",
        "Anchor reasoning in the frequency of similar cases.",
        ("target event", "reference class"),
        (
            "What is the relevant reference class?",
            "How often does this outcome occur in similar cases?",
            "Is the current case genuinely exceptional?",
        ),
        ("reference_class", "base_rate", "relevance", "adjustment_factors"),
        ("Superforecasting", "Thinking, Fast and Slow"),
    ),
    _operation(
        "ask_what_would_change_my_mind",
        "Ask what would change my mind",
        "metacognition_bias",
        "Force the reasoning process to specify disconfirming evidence in advance.",
        ("current conclusion", "confidence"),
        (
            "What evidence would lower confidence materially?",
            "What evidence would reverse the conclusion?",
            "What observation would support the strongest alternative?",
        ),
        (
            "disconfirming_evidence",
            "update_threshold",
            "alternative_supported",
            "expected_confidence_change",
        ),
        ("The Scout Mindset", "Superforecasting"),
    ),
)

# Documented Canon v0.2 operations intentionally unavailable to the runtime.
INACTIVE_OPERATIONS: tuple[str, ...] = (
    "detect_motivated_reasoning",
    "mentally_simulate_action",
    "assign_probability",
    "update_belief",
    "define_forecast_target",
    "decompose_forecast",
    "define_falsification_condition",
    "design_risky_test",
    "decompose_argument",
    "assign_burden_of_proof",
    "challenge_quantitative_claim",
    "detect_judgment_noise",
)
INACTIVE_OPERATION_IDS = frozenset(INACTIVE_OPERATIONS)

CANON_OPERATION_IDS = (
    frozenset(operation.id for operation in ACTIVE_OPERATIONS) | INACTIVE_OPERATION_IDS
)

# Compatibility name: OPERATIONS continues to mean executable operations.
OPERATIONS = ACTIVE_OPERATIONS
OPERATION_REGISTRY = {operation.id: operation for operation in ACTIVE_OPERATIONS}

LENS_OPERATION_IDS: dict[LensName, tuple[str, ...]] = {
    LensName.SYSTEMS_THINKING: tuple(
        op.id for op in ACTIVE_OPERATIONS if op.family == "systems_thinking"
    ),
    LensName.CRITICAL_THINKING: tuple(
        op.id for op in ACTIVE_OPERATIONS if op.family == "critical_thinking"
    ),
    LensName.CAUSAL_REASONING: tuple(
        op.id for op in ACTIVE_OPERATIONS if op.family == "causal_reasoning"
    ),
    LensName.DECISION_MAKING: tuple(
        op.id for op in ACTIVE_OPERATIONS if op.family == "decision_making"
    ),
    LensName.PROBABILISTIC_THINKING: tuple(
        op.id for op in ACTIVE_OPERATIONS if op.family == "probabilistic_thinking"
    ),
    LensName.FORECASTING: (),
    LensName.SCIENTIFIC_REASONING: (),
    LensName.PROBLEM_SOLVING: (),
    LensName.ARGUMENTATION: (),
    LensName.METACOGNITION_AND_BIAS: tuple(
        op.id for op in ACTIVE_OPERATIONS if op.family == "metacognition_bias"
    ),
}

LENS_PURPOSES: dict[LensName, str] = {
    LensName.SYSTEMS_THINKING: "Understand structure, interactions, feedback, boundaries and leverage points.",
    LensName.CRITICAL_THINKING: "Evaluate whether claims and conclusions are well supported.",
    LensName.CAUSAL_REASONING: "Distinguish correlation from causation and test causal explanations.",
    LensName.DECISION_MAKING: "Compare alternatives under uncertainty and trade-offs.",
    LensName.PROBABILISTIC_THINKING: "Reason explicitly about uncertainty.",
    LensName.FORECASTING: "Reason about possible future states.",
    LensName.SCIENTIFIC_REASONING: "Test explanations against evidence.",
    LensName.PROBLEM_SOLVING: "Turn an ambiguous problem into actionable structure.",
    LensName.ARGUMENTATION: "Analyze structured disagreement.",
    LensName.METACOGNITION_AND_BIAS: "Challenge the quality of the reasoning process itself.",
}


def operations_for_lens(lens: LensName) -> tuple[AtomicOperation, ...]:
    """Return active operations for a public lens in stable execution order."""
    return tuple(OPERATION_REGISTRY[id] for id in LENS_OPERATION_IDS[lens])


assert len(ACTIVE_OPERATIONS) == 18
assert len(CANON_OPERATION_IDS) == 30
assert not (set(OPERATION_REGISTRY) & INACTIVE_OPERATION_IDS)
