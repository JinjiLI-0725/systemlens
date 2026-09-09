# SystemLens

SystemLens is an API for structuring a problem through explicit thinking lenses. The current backend follows the lens definitions in [`docs/lens-taxonomy.md`](docs/lens-taxonomy.md) and the sources in [`docs/thinking-canon.md`](docs/thinking-canon.md).

The initial `/analyze` implementation is deliberately deterministic mock logic. It makes no LLM or external service calls.

## Run the backend locally

SystemLens requires Python 3.10 or newer.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
uvicorn backend.main:app --reload
```

The API is available at `http://127.0.0.1:8000`, with interactive documentation at `http://127.0.0.1:8000/docs`.

Check its health:

```bash
curl http://127.0.0.1:8000/health
```

Request an analysis:

```bash
curl -X POST http://127.0.0.1:8000/analyze \
  -H 'Content-Type: application/json' \
  -d '{
    "problem": "Customer wait times are increasing",
    "selected_lenses": ["systems_thinking", "causal_reasoning"]
  }'
```

If `selected_lenses` is omitted, the API defaults to systems thinking, critical thinking, and causal reasoning. Valid lens identifiers correspond to all ten lenses in the taxonomy and are visible in the generated API documentation.

## Run tests

From the repository root with the virtual environment active:

```bash
pytest
```

## Backend layout

```text
backend/
├── api/          # FastAPI route definitions
├── schemas/      # Pydantic API contracts
├── services/     # Analysis logic
├── tests/        # Backend API tests
└── main.py       # Application setup
```
