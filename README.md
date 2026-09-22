# SystemLens — AI Decision Intelligence

[**Live Demo → lens.insightdock.com**](https://lens.insightdock.com)

SystemLens is a full-stack LLM application for structured decision analysis. Instead of returning only a fluent answer, it stress-tests a decision by surfacing assumptions, competing explanations, uncertainty, evidence gaps, and decision triggers.

## Why I built it

General-purpose LLMs are excellent at generating answers, but complex decisions often need a repeatable reasoning process. SystemLens turns open-ended analysis into a structured decision brief that makes the reasoning—and its limitations—visible.

## What this project demonstrates

- **LLM application engineering** — provider-backed structured generation with deterministic fallbacks
- **Reasoning orchestration** — problem classification, lens selection, operation planning, batching, and synthesis
- **Full-stack product development** — FastAPI backend + Next.js frontend
- **Reliability engineering** — schema validation, timeouts, partial fallbacks, execution traces, and confidence handling
- **Production deployment** — Linux, Nginx, systemd, HTTPS, and a live public deployment
- **AI product UX** — decision briefs, uncertainty display, next checks, and decision triggers

**Tech:** Python · FastAPI · Pydantic · Next.js · React · TypeScript · OpenRouter · Nginx · Linux

> API keys are never committed to the repository. Use `.env.example` to configure your own environment.

---

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
  → execution batches (grouped by operation family, at most two operations by default)
  → provider-neutral operation executor
      ├── deterministic local fallback
      └── LLMProvider interface
            ├── DeepSeek OpenAI-compatible adapter
            └── OpenRouter OpenAI-compatible adapter
  → Pydantic batch validation
      └── preserve valid findings and deterministically fill missing operations
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

Never put API keys in source control or logs. Supported `SYSTEMLENS_LLM_PROVIDER` values are `deepseek` and `openrouter`; `deepseek` remains the default. If `SYSTEMLENS_EXECUTION_MODE` is omitted or set to `deterministic`, no provider call is made. If `llm` is requested but the selected provider's API key is absent, SystemLens uses deterministic execution and records the reason in `execution_trace.fallback_events`. SystemLens does not make a second full model call to repair a batch: valid findings are preserved, extras and duplicates are discarded, and only missing findings are filled deterministically. Invalid JSON or a response with no usable requested findings falls back for that batch.

Latency and capacity limits can be tuned without changing the provider abstraction:

```bash
export SYSTEMLENS_LLM_TIMEOUT=20          # timeout for each provider call, in seconds
export SYSTEMLENS_MAX_OUTPUT_TOKENS=1200  # provider response token ceiling
export SYSTEMLENS_BATCH_SIZE=2            # operations in each family batch
export SYSTEMLENS_REQUEST_TIMEOUT=30      # overall concurrent execution budget, in seconds
```

Independent batches execute concurrently. Results are restored to planner order after
completion, and any batch still running when the overall request budget expires receives
the deterministic fallback.

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
    "batches": [["define_system_boundary", "identify_stocks_and_flows"], ["detect_feedback_loops", "identify_leverage_points"]],
    "fallback_events": [],
    "batch_timings": [
      {"batch_name": "systems_thinking", "elapsed_ms": 842, "fallback_used": false, "status": "llm", "missing_operation_ids": [], "validation_error_category": null},
      {"batch_name": "systems_thinking", "elapsed_ms": 901, "fallback_used": true, "status": "partial_fallback", "missing_operation_ids": ["identify_leverage_points"], "validation_error_category": "coverage_error"}
    ]
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

## Run the frontend locally

The frontend is a Next.js application in `frontend/` and requires Node.js 20 or newer. Start the FastAPI backend first, then run:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`. The Next.js server proxies browser requests from `/api/analyze` to `http://127.0.0.1:8000/analyze`, so provider credentials remain server-side. To use a backend at another address, set the server-only environment variable before starting Next.js:

```bash
SYSTEMLENS_BACKEND_URL=http://localhost:8000 npm run dev
```

Build and lint the frontend with `npm run build` and `npm run lint`.
