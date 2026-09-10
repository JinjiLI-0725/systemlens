# SystemLens

SystemLens is an API for structuring complex problems through explicit thinking lenses. Its definitions come from [`docs/lens-taxonomy.md`](docs/lens-taxonomy.md), supported by [`docs/thinking-canon.md`](docs/thinking-canon.md).

## Intelligence layer and optional LLM execution

The `/analyze` endpoint now follows the intended SystemLens architecture:

```text
problem
  → deterministic problem classification
  → relevant lens selection
  → ordered atomic-operation plan
  → logical operation batches
  → operation executor (deterministic or provider-backed)
  → Pydantic validation and synthesis
  → structured response with execution trace
```

Execution remains deterministic by default. Optionally, the same plan can be executed through an LLM provider; all inferred output is still labeled as a preliminary hypothesis rather than a fact. The public `/analyze` request and response fields are preserved.

### Execution architecture

```text
planner
  → execution batches (grouped by operation family, at most four operations)
  → provider-neutral operation executor
      ├── deterministic local fallback
      └── LLMProvider interface
            ├── DeepSeek OpenAI-compatible adapter
            └── OpenRouter OpenAI-compatible adapter
  → Pydantic batch validation
      └── one JSON repair attempt, then deterministic batch fallback
  → structured synthesis
  → AnalysisResponse
```

The **Canon** and **Active Registry** remain provider-independent. They define what an operation means; they never import DeepSeek or construct vendor requests. Prompts are built from registry metadata, and another provider can be added by implementing `LLMProvider.generate_structured` without changing the planner, registry, batching, or synthesis.

### Enable DeepSeek

DeepSeek is the first provider and uses its OpenAI-compatible chat-completions API. Secrets are read only from the environment:

```bash
export SYSTEMLENS_EXECUTION_MODE=llm
export SYSTEMLENS_LLM_PROVIDER=deepseek
export DEEPSEEK_API_KEY='your-key-here'
export DEEPSEEK_MODEL='deepseek-chat'  # optional; this is the default
uvicorn backend.main:app --reload
```

### Enable OpenRouter

OpenRouter uses its OpenAI-compatible `https://openrouter.ai/api/v1/chat/completions` endpoint. Select it independently from execution mode and configure its credentials and initial DeepSeek model:

```bash
export SYSTEMLENS_EXECUTION_MODE=llm
export SYSTEMLENS_LLM_PROVIDER=openrouter
export OPENROUTER_API_KEY='your-key-here'
export OPENROUTER_BASE_URL='https://openrouter.ai/api/v1'  # optional; this is the default
export OPENROUTER_MODEL='~deepseek/deepseek-v4-flash-latest'  # optional; this is the default
uvicorn backend.main:app --reload
```

Never put API keys in source control or logs. Supported `SYSTEMLENS_LLM_PROVIDER` values are `deepseek` and `openrouter`; `deepseek` remains the default. If `SYSTEMLENS_EXECUTION_MODE` is omitted or set to `deterministic`, no provider call is made. If `llm` is requested but the selected provider's API key is absent, SystemLens uses deterministic execution and records the reason in `execution_trace.fallback_events`. Invalid model JSON is retried once with a repair instruction; if repair also fails, only that batch falls back deterministically.

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
    "operations": ["define_system_boundary", "identify_stocks_and_flows", "detect_feedback_loops", "identify_leverage_points"],
    "execution_mode": "deterministic",
    "requested_execution_mode": "deterministic",
    "provider": null,
    "model": null,
    "batches": [["define_system_boundary", "identify_stocks_and_flows", "detect_feedback_loops", "identify_leverage_points"]],
    "fallback_events": []
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
├── llm/          # Provider interface, configuration, and adapters
├── reasoning/    # Atomic-operation registry
├── schemas/      # Pydantic API contracts
├── services/     # Classifier, selector, planner, and analysis orchestration
├── tests/        # Backend and pipeline tests
└── main.py       # Application setup
```
