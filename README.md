# SystemLens

SystemLens is an API for structuring complex problems through explicit thinking lenses. Its definitions come from [`docs/lens-taxonomy.md`](docs/lens-taxonomy.md), supported by [`docs/thinking-canon.md`](docs/thinking-canon.md).

## Intelligence Layer v0.2

The `/analyze` endpoint now follows the intended SystemLens architecture:

```text
problem
  → deterministic problem classification
  → relevant lens selection
  → ordered atomic-operation plan
  → deterministic operation-informed analysis
  → structured response with execution trace
```

This is deliberately **deterministic v0.2**. It makes no LLM or external-service calls, and all inferred output is labeled as a preliminary hypothesis rather than a fact. Templates make the architecture inspectable and testable while leaving execution simple to replace later.

### Problem classifier

Transparent text signals route a problem to one of:

- `system_problem`
- `causal_problem`
- `decision_problem`
- `argument_problem`
- `forecasting_problem`
- `general_complex_problem`

For example, decision language such as “should” or alternatives such as “or wait” select `decision_problem`; explicit causal language selects `causal_problem`. Stable precedence resolves ties.

### Lens selector

Each problem class maps to a small relevant lens set rather than running every lens. A system problem selects systems thinking and critical thinking; a decision problem selects decision making, critical thinking, and metacognition & bias. If a caller supplies `selected_lenses`, that list is respected as an explicit override.

### Atomic operations and execution planner

The **Canon** is the broader research library: [`docs/thinking-canon.md`](docs/thinking-canon.md) records the sources and [`docs/atomic-operations.md`](docs/atomic-operations.md) defines all 30 Canon v0.2 operations. Documentation does not imply that an operation is executable.

The **Active Registry** is the curated production subset in `backend/reasoning/operations.py`. It activates exactly 18 operations, each with a stable ID, name, canonical family, purpose, inputs, critical questions, outputs, and source basis. The remaining 12 documented operations are explicitly marked inactive and cannot be scheduled. The planner expands selected lenses into a stable, deduplicated sequence containing active operations only.

### Execution trace

Responses retain the existing structured fields and add:

```json
{
  "execution_trace": {
    "problem_class": "system_problem",
    "selected_lenses": ["systems_thinking", "critical_thinking"],
    "operations": ["define_system_boundary", "identify_stocks_and_flows", "detect_feedback_loops", "identify_leverage_points"]
  }
}
```

Confidence remains explicit and is reduced when the prompt provides no evidence or when material unknowns remain. Its rationale states those limitations.

## Run the backend locally

SystemLens requires Python 3.10 or newer.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
uvicorn backend.main:app --reload
```

The API is available at `http://127.0.0.1:8000`, with interactive documentation at `http://127.0.0.1:8000/docs`.

```bash
curl -X POST http://127.0.0.1:8000/analyze \
  -H 'Content-Type: application/json' \
  -d '{"problem": "Why are young professionals leaving Hong Kong?"}'
```

Valid explicit lens identifiers correspond to all ten taxonomy lenses. Omit `selected_lenses` to let the classifier and selector choose lenses automatically.

## Run tests

```bash
pytest
```

## Backend layout

```text
backend/
├── api/          # FastAPI route definitions
├── reasoning/    # Atomic-operation registry
├── schemas/      # Pydantic API contracts
├── services/     # Classifier, selector, planner, and analysis orchestration
├── tests/        # Backend and pipeline tests
└── main.py       # Application setup
```

## Future LLM-backed execution

The public API need not change when an LLM is introduced. Classification and planning can continue to produce the same lens and operation IDs, while deterministic templates are replaced operation-by-operation with an executor that submits each registry operation's requirements and questions to an LLM. The executor's results can still be validated into the existing Pydantic response models, and `execution_trace` can continue to report exactly what ran.
