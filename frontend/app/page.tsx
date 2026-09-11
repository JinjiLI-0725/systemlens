"use client";

import { FormEvent, useEffect, useState } from "react";
import type { AnalysisResponse, ApiError, Confidence } from "@/lib/types";

const examples = [
  "Why do software projects keep missing their deadlines?",
  "Does remote work cause lower productivity?",
  "Should a startup hire now or wait six months?",
];

const progressSteps = [
  "Classifying problem",
  "Selecting reasoning lenses",
  "Running analytical operations",
  "Synthesizing findings",
];

const label = (value: string) => value.replaceAll("_", " ");

function ConfidenceDisplay({ confidence }: { confidence: Confidence }) {
  const percent = Math.round(confidence.score * 100);
  return (
    <div className="confidence-block">
      <div className="confidence-score">
        <span>{percent}</span>
        <small>/ 100</small>
      </div>
      <div className="confidence-copy">
        <div className="confidence-heading">
          <strong>{confidence.level} confidence</strong>
          <span className="confidence-line" aria-hidden="true"><i style={{ width: `${percent}%` }} /></span>
        </div>
        <p>{confidence.rationale}</p>
      </div>
    </div>
  );
}

function Results({ result }: { result: AnalysisResponse }) {
  const trace = result.execution_trace;
  const totalElapsed = trace.batch_timings.reduce((total, batch) => total + batch.elapsed_ms, 0);
  const fallbackUsed = trace.fallback_events.length > 0 || trace.batch_timings.some((batch) => batch.fallback_used);

  return (
    <section className="results" aria-live="polite">
      <div className="results-kicker"><span>Analysis complete</span><span>{label(trace.problem_class)}</span></div>
      <div className="summary-grid">
        <h2>Summary</h2>
        <p>{result.summary}</p>
      </div>

      <section className="section-block lenses-section">
        <div className="section-heading"><p>01</p><h2>Reasoning lenses</h2><span>{result.selected_lenses.length} selected</span></div>
        <div className="lens-grid">
          {result.selected_lenses.map((lens) => (
            <article className="lens-card" key={lens.name}>
              <h3>{label(lens.name)}</h3>
              <p>{lens.purpose}</p>
              <div className="tags">{lens.operations.map((operation) => <span key={operation}>{label(operation)}</span>)}</div>
            </article>
          ))}
        </div>
      </section>

      <section className="section-block">
        <div className="section-heading"><p>02</p><h2>Claims</h2><span>{result.claims.length} identified</span></div>
        <div className="stack-list">
          {result.claims.map((claim, index) => (
            <article className="claim" key={`${claim.statement}-${index}`}>
              <div className="item-number">{String(index + 1).padStart(2, "0")}</div>
              <div><h3>{claim.statement}</h3>{claim.evidence.length > 0 && <p><b>Evidence:</b> {claim.evidence.join(" · ")}</p>}</div>
              <span className="score">{Math.round(claim.confidence.score * 100)}%</span>
            </article>
          ))}
        </div>
      </section>

      <div className="split-sections">
        <section className="section-block compact-section">
          <div className="section-heading"><p>03</p><h2>Assumptions</h2></div>
          {result.assumptions.map((item, index) => (
            <article className="detail-item" key={`${item.statement}-${index}`}>
              <h3>{item.statement}</h3>
              <p><b>Why it matters</b>{item.impact}</p>
              <p><b>Test</b>{item.validation_question}</p>
            </article>
          ))}
        </section>
        <section className="section-block compact-section">
          <div className="section-heading"><p>04</p><h2>Unknowns</h2></div>
          {result.unknowns.map((item, index) => (
            <article className="detail-item unknown" key={`${item.question}-${index}`}>
              <h3>{item.question}</h3>
              <p><b>Importance</b>{item.importance}</p>
            </article>
          ))}
        </section>
      </div>

      <section className="section-block leverage-section">
        <div className="section-heading"><p>05</p><h2>Leverage points</h2><span>Places to intervene</span></div>
        <div className="leverage-grid">
          {result.leverage_points.map((point, index) => (
            <article key={`${point.title}-${index}`}>
              <span className="priority">{point.priority}</span>
              <h3>{point.title}</h3>
              <p>{point.description}</p>
              <small>{label(point.related_lens)}</small>
            </article>
          ))}
        </div>
      </section>

      <section className="section-block confidence-section">
        <div className="section-heading"><p>06</p><h2>Confidence</h2></div>
        <ConfidenceDisplay confidence={result.confidence} />
      </section>

      <details className="execution">
        <summary><span>Execution details</span><small>Inspectable metadata</small></summary>
        <div className="metadata-grid">
          <dl><dt>Mode</dt><dd>{label(trace.execution_mode)}</dd></dl>
          <dl><dt>Provider</dt><dd>{trace.provider ?? "Local"}</dd></dl>
          <dl><dt>Model</dt><dd>{trace.model ?? "—"}</dd></dl>
          <dl><dt>Elapsed</dt><dd>{(totalElapsed / 1000).toFixed(2)}s</dd></dl>
          <dl><dt>Fallback</dt><dd className={fallbackUsed ? "fallback-yes" : "fallback-no"}>{fallbackUsed ? "Used" : "Not used"}</dd></dl>
        </div>
        <div className="batch-list">
          {trace.batch_timings.map((batch, index) => (
            <div key={`${batch.batch_name}-${index}`}>
              <span>{batch.batch_name}</span><span>{label(batch.status)}</span><span>{batch.elapsed_ms}ms</span>
            </div>
          ))}
        </div>
        {trace.fallback_events.length > 0 && <p className="fallback-note">{trace.fallback_events.join(" · ")}</p>}
      </details>
    </section>
  );
}

export default function Home() {
  const [problem, setProblem] = useState("");
  const [result, setResult] = useState<AnalysisResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    if (!loading) return;
    setProgress(0);
    const interval = window.setInterval(() => setProgress((current) => Math.min(current + 1, progressSteps.length - 1)), 1800);
    return () => window.clearInterval(interval);
  }, [loading]);

  async function analyze(event: FormEvent) {
    event.preventDefault();
    if (!problem.trim() || loading) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const response = await fetch("/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ problem }),
      });
      const data = (await response.json()) as AnalysisResponse | ApiError;
      if (!response.ok || "error" in data) throw new Error("message" in data ? data.message : "Analysis failed.");
      setResult(data);
      window.setTimeout(() => document.querySelector(".results")?.scrollIntoView({ behavior: "smooth", block: "start" }), 50);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main>
      <header className="site-header">
        <a className="wordmark" href="#top" aria-label="SystemLens home"><span>System</span>Lens</a>
        <p>AI for thinking in systems</p>
        <span className="edition">Research preview · 01</span>
      </header>

      <section className="hero" id="top">
        <div className="hero-copy">
          <p className="eyebrow"><span /> Structured analysis</p>
          <h1>See the structure behind <em>complex problems.</em></h1>
          <p className="intro">SystemLens decomposes difficult questions using explicit reasoning lenses—surfacing claims, assumptions, unknowns, and the points where change matters most.</p>
        </div>

        <form className="analyze-form" onSubmit={analyze}>
          <label htmlFor="problem">What are you trying to understand?</label>
          <textarea
            id="problem"
            value={problem}
            onChange={(event) => setProblem(event.target.value)}
            placeholder="Describe a complex problem, decision, or system…"
            maxLength={10000}
            disabled={loading}
          />
          <div className="form-footer">
            <span>{problem.length.toLocaleString()} / 10,000</span>
            <button type="submit" disabled={!problem.trim() || loading}>
              {loading ? "Analyzing" : "Analyze problem"}<i aria-hidden="true">↗</i>
            </button>
          </div>
        </form>

        <div className="examples">
          <p>Try an example</p>
          <div>{examples.map((example, index) => <button type="button" key={example} onClick={() => setProblem(example)}><span>0{index + 1}</span>{example}</button>)}</div>
        </div>
      </section>

      {loading && (
        <section className="processing" aria-live="polite">
          <div><p>Processing your question</p><span>These stages indicate activity, not exact backend progress.</span></div>
          <ol>{progressSteps.map((step, index) => <li key={step} className={index < progress ? "done" : index === progress ? "active" : ""}><i>{index < progress ? "✓" : index + 1}</i><span>{step}</span></li>)}</ol>
        </section>
      )}

      {error && <section className="error-message" role="alert"><span>Analysis interrupted</span><div><h2>We couldn’t complete this analysis.</h2><p>{error}</p></div><button type="button" onClick={() => setError(null)}>Dismiss</button></section>}
      {result && <Results result={result} />}

      <footer><span>SystemLens</span><p>Clearer structures. Better questions.</p><small>Built for inquiry, not certainty.</small></footer>
    </main>
  );
}