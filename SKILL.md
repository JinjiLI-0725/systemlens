---
name: systemlens-decision-analysis
description: Stress-test complex decisions by decomposing the decision, surfacing hidden assumptions, comparing competing explanations, exposing uncertainty and evidence gaps, and defining decision triggers and next checks. Use when a user asks whether to choose, launch, hire, build, buy, delay, prioritize, invest, or otherwise make a consequential decision under uncertainty.
---

# SystemLens Decision Analysis

Use this skill to turn an ambiguous decision into a structured decision brief rather than a single fluent answer.

## Core principle

Do not optimize for sounding certain. Optimize for making the decision structure visible.

A useful analysis should show:
- what decision is actually being made,
- which variables drive the outcome,
- which assumptions are carrying the conclusion,
- what could make the current view wrong,
- what evidence is missing,
- what should be checked next,
- and what conditions should change the decision.

## Workflow

### 1. Frame the decision

Rewrite the user's question as a concrete decision.

Identify:
- the decision maker,
- the available alternatives,
- the time horizon,
- important constraints,
- and the consequence of delaying or choosing incorrectly.

If the prompt is underspecified, do not invent precise facts. State the missing information explicitly.

### 2. Decompose the decision

Identify the 3-7 variables that most affect the outcome.

Typical categories include:
- cost and runway,
- expected upside,
- timing,
- team or execution capacity,
- reversibility,
- dependency risk,
- opportunity cost,
- strategic fit,
- evidence quality.

Do not create a long generic checklist. Keep only variables that materially affect this decision.

### 3. Surface assumptions

Separate facts supplied by the user from assumptions and inferences.

For each important assumption, ask:
- What must be true for this conclusion to hold?
- Is that claim supported by evidence or merely plausible?
- How sensitive is the decision to this assumption?

### 4. Stress-test the current view

Actively search for:
- counterarguments,
- competing explanations,
- failure modes,
- hidden constraints,
- second-order effects,
- and reasons the preferred option could be wrong.

Do not manufacture false balance. Give more weight to better-supported explanations.

### 5. Expose uncertainty

State what is known, inferred, and unknown.

Use qualitative confidence unless the user provides enough evidence for a defensible quantitative estimate.

Never treat model fluency as evidence.

### 6. Identify high-value checks

Prioritize checks by decision value: what information would most reduce uncertainty or change the choice?

For each check, state:
- what to verify,
- why it matters,
- and what result would favor one option over another.

### 7. Define decision triggers

Translate uncertainty into action conditions.

Use trigger language such as:
- "Choose A if..."
- "Delay if..."
- "Reconsider if..."
- "Escalate if..."

Triggers should be observable and specific enough to guide action.

## Output format

Produce a concise decision brief with these sections:

### Decision
One sentence stating the actual decision.

### Current view
A short synthesis of the best-supported position. Avoid pretending certainty when evidence is thin.

### Key variables
3-7 variables that drive the decision.

### Assumptions
The assumptions carrying the current view.

### What could make this wrong
Counterarguments, failure modes, or competing explanations.

### Evidence gaps
What is still unknown or weakly supported.

### Next checks
The highest-value information to verify next.

### Decision triggers
Observable conditions that should change the action.

### Confidence
State High, Medium, or Low and explain why in one sentence.

## Style

- Prefer decision-relevant information over exhaustive explanation.
- Distinguish evidence from inference.
- Do not hide uncertainty.
- Do not repeat the user's question as filler.
- Keep the brief executive-readable.
- When evidence is insufficient, say so and recommend what to verify instead of fabricating precision.

## Example

User:
"Should we hire another engineer now or wait six months?"

A strong SystemLens analysis would focus on variables such as runway, bottleneck severity, expected milestone acceleration, onboarding cost, reversibility, and the cost of waiting. It would identify assumptions about workload and revenue timing, test the risk of premature hiring, and define observable triggers such as runway thresholds or milestone slippage.

## Related project

SystemLens is also available as a full-stack interactive application:

- Live demo: https://lens.insightdock.com
- Source: https://github.com/JinjiLI-0725/systemlens
