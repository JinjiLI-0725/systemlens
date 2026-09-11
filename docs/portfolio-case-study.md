# SystemLens — Portfolio Case Study

## Product

SystemLens is a decision stress-testing application for ambiguous, high-uncertainty choices. A user enters a decision such as “Should we hire another engineer now or wait six months?” and receives a structured decision brief rather than a generic chat response.

The user-facing brief focuses on:

- the strongest current view supported by the prompt;
- the reasoning behind that view;
- key decision variables;
- conditions that could make the conclusion wrong;
- evidence to verify before committing;
- recommended next moves;
- evidence strength and inspectable reasoning details.

## Why it exists

General-purpose chatbots often produce advice without making the reasoning structure visible. SystemLens separates the decision itself from assumptions, competing explanations, missing evidence, uncertainty, and next checks so the user can see what would actually change the decision.

## End-to-end architecture

```text
Browser / Next.js
      ↓
POST /api/analyze
      ↓
Next.js server proxy
      ↓
FastAPI /analyze
      ↓
Problem classifier
      ↓
Reasoning-lens selector
      ↓
Atomic-operation planner
      ↓
Provider-neutral executor
      ↓
OpenRouter / DeepSeek-compatible LLM
      ↓
Pydantic validation + safe fallback
      ↓
Structured synthesis
      ↓
Decision brief + execution trace
```

## Engineering highlights

- Next.js + TypeScript frontend with an opinionated decision-brief interface.
- FastAPI backend with Pydantic request/response contracts.
- Transparent problem classification and lens selection.
- Research-derived atomic reasoning operations grouped into an executable registry.
- Provider abstraction supporting OpenRouter and DeepSeek-compatible endpoints.
- Structured-output validation, deterministic fallback, and execution tracing.
- Automated Python test suite isolated from local API credentials.
- Production deployment using Linux, systemd, Nginx, and HTTPS.

## Tech stack

**Frontend:** Next.js, React, TypeScript, CSS  
**Backend:** Python, FastAPI, Pydantic  
**LLM:** OpenRouter / DeepSeek-compatible structured generation  
**Infrastructure:** Ubuntu, systemd, Nginx, Let’s Encrypt  
**Testing:** pytest

## CV version

**SystemLens — AI Decision Intelligence Application**  
Built and deployed a full-stack AI decision stress-testing application that converts ambiguous decisions into structured briefs covering key variables, assumptions, failure conditions, uncertainty, evidence gaps, and next actions. Implemented a FastAPI reasoning pipeline, provider-neutral LLM execution through OpenRouter, Pydantic validation and fallback handling, a Next.js/TypeScript frontend, automated tests, and Linux/Nginx production deployment.

## Demo prompt

> Should a startup hire another engineer now or wait six months?

A good demo should show the decision brief first. Reasoning lenses, assumptions, claims, model/provider details, and execution metadata are intentionally secondary and inspectable rather than dominating the main user experience.
