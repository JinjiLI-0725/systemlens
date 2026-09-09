"""Machine-readable atomic operations derived from the lens taxonomy."""

from dataclasses import asdict, dataclass

from backend.schemas.analysis import LensName


@dataclass(frozen=True)
class AtomicOperation:
    """A small reasoning task that can later be implemented by any executor."""

    id: str
    name: str
    lens_family: LensName
    purpose: str
    input_requirements: tuple[str, ...]
    questions: tuple[str, ...]
    output_type: str

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-compatible representation of the operation."""
        value = asdict(self)
        value["lens_family"] = self.lens_family.value
        return value


OPERATIONS: tuple[AtomicOperation, ...] = (
    AtomicOperation(
        "define_system_boundary",
        "Define system boundary",
        LensName.SYSTEMS_THINKING,
        "Set the scope, timeframe, and exclusions.",
        ("problem statement",),
        ("What is inside the system?", "What timeframe matters?"),
        "system_boundary",
    ),
    AtomicOperation(
        "identify_actors",
        "Identify actors",
        LensName.SYSTEMS_THINKING,
        "Surface parties that influence or experience the problem.",
        ("problem statement", "system boundary"),
        ("Who acts?", "Who is affected?"),
        "actor_list",
    ),
    AtomicOperation(
        "map_relationships",
        "Map relationships",
        LensName.SYSTEMS_THINKING,
        "Describe candidate links among actors, drivers, and outcomes.",
        ("actors", "candidate variables"),
        ("What may influence what?", "In which direction?"),
        "relationship_graph",
    ),
    AtomicOperation(
        "detect_feedback_loops",
        "Detect feedback loops",
        LensName.SYSTEMS_THINKING,
        "Find candidate reinforcing or balancing cycles.",
        ("relationship graph",),
        ("Which effects feed back into their causes?",),
        "feedback_loop_list",
    ),
    AtomicOperation(
        "identify_leverage_points",
        "Identify leverage points",
        LensName.SYSTEMS_THINKING,
        "Propose places to learn or intervene with disproportionate effect.",
        ("system boundary", "relationship graph"),
        ("Where could a small change alter behavior?",),
        "leverage_point_list",
    ),
    AtomicOperation(
        "identify_claim",
        "Identify main claim",
        LensName.CRITICAL_THINKING,
        "Make the proposition under examination explicit.",
        ("problem statement",),
        ("What is being claimed or presupposed?",),
        "claim",
    ),
    AtomicOperation(
        "identify_assumptions",
        "Identify assumptions",
        LensName.CRITICAL_THINKING,
        "Expose premises that have not been established.",
        ("problem statement", "claim"),
        ("What must be true for this framing to hold?",),
        "assumption_list",
    ),
    AtomicOperation(
        "detect_missing_evidence",
        "Detect missing evidence",
        LensName.CRITICAL_THINKING,
        "Identify information needed to assess the claim.",
        ("claim",),
        ("What evidence is supplied?", "What evidence is absent?"),
        "unknown_list",
    ),
    AtomicOperation(
        "generate_counterarguments",
        "Generate counterarguments",
        LensName.CRITICAL_THINKING,
        "Challenge the initial framing with plausible alternatives.",
        ("claim", "assumptions"),
        ("What is the strongest competing interpretation?",),
        "counterargument_list",
    ),
    AtomicOperation(
        "detect_confounders",
        "Detect confounders",
        LensName.CAUSAL_REASONING,
        "Surface variables that may affect both proposed cause and effect.",
        ("proposed cause", "proposed effect"),
        ("What third factor could produce both?",),
        "confounder_list",
    ),
    AtomicOperation(
        "test_reverse_causation",
        "Test reverse causation",
        LensName.CAUSAL_REASONING,
        "Check whether the proposed effect may influence the proposed cause.",
        ("proposed cause", "proposed effect"),
        ("Could the direction run the other way?",),
        "causal_hypothesis",
    ),
    AtomicOperation(
        "build_causal_chain",
        "Build causal chain",
        LensName.CAUSAL_REASONING,
        "Express an inspectable candidate path from cause to effect.",
        ("proposed cause", "proposed effect"),
        ("Through which mechanisms could the effect occur?",),
        "causal_chain",
    ),
    AtomicOperation(
        "compare_alternatives",
        "Compare alternatives",
        LensName.DECISION_MAKING,
        "Compare options against constraints, uncertainty, and trade-offs.",
        ("decision", "alternatives"),
        ("What are the options?", "What is gained or given up?"),
        "alternative_comparison",
    ),
    AtomicOperation(
        "run_pre_mortem",
        "Run pre-mortem",
        LensName.DECISION_MAKING,
        "Imagine failure to reveal risks before committing.",
        ("decision", "candidate option"),
        ("If this failed, what likely caused it?",),
        "risk_list",
    ),
    AtomicOperation(
        "what_would_change_my_mind",
        "Ask what would change my mind",
        LensName.METACOGNITION_AND_BIAS,
        "Define evidence that would update the current view and limit confirmation bias.",
        ("current claim", "confidence"),
        ("Which observation would materially change the conclusion?",),
        "update_trigger_list",
    ),
)

OPERATION_REGISTRY = {operation.id: operation for operation in OPERATIONS}

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
    """Return registry operations for a lens in canonical execution order."""
    return tuple(operation for operation in OPERATIONS if operation.lens_family == lens)
