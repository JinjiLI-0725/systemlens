# SystemLens Atomic Operations v0.1

Atomic operations translate the conceptual lens taxonomy into small, inspectable reasoning tasks. The executable source of truth is `backend/reasoning/operations.py`; this document is its human-readable overview. The registry intentionally remains small for v0.1.

| Operation ID | Lens family | Intended output |
| --- | --- | --- |
| `define_system_boundary` | Systems Thinking | Scope, timeframe, and exclusions |
| `identify_actors` | Systems Thinking | Candidate actors and affected parties |
| `map_relationships` | Systems Thinking | Candidate relationship graph |
| `detect_feedback_loops` | Systems Thinking | Reinforcing or balancing loop hypotheses |
| `identify_leverage_points` | Systems Thinking | Candidate interventions or learning points |
| `identify_claim` | Critical Thinking | Explicit claim under examination |
| `identify_assumptions` | Critical Thinking | Unestablished premises |
| `detect_missing_evidence` | Critical Thinking | Material unknowns and evidence gaps |
| `generate_counterarguments` | Critical Thinking | Competing interpretations |
| `detect_confounders` | Causal Reasoning | Candidate common causes |
| `test_reverse_causation` | Causal Reasoning | Reversed-direction causal hypothesis |
| `build_causal_chain` | Causal Reasoning | Candidate mechanism chain |
| `compare_alternatives` | Decision Making | Options and trade-offs |
| `run_pre_mortem` | Decision Making | Failure modes and risks |
| `what_would_change_my_mind` | Metacognition & Bias | Belief-update triggers |

Every registry record also includes a display name, purpose, input requirements, and questions. The execution planner preserves selected-lens order and registry order, making plans reproducible. These operation contracts are executor-neutral: deterministic templates can later be replaced by validated LLM-backed handlers without changing operation IDs or the `/analyze` response contract.
