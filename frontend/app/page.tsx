"use client";

import { FormEvent, useEffect, useState } from "react";
import type { AnalysisResponse, ApiError, Confidence } from "@/lib/types";

const examples = [
  "Should a startup hire another engineer now or wait six months?",
  "Should we launch this product now or delay for another quarter?",
  "Should we build this feature in-house or buy an external solution?",
];

const progressSteps = [
  "Classifying the decision",
  "Testing assumptions",
  "Comparing risks and alternatives",
  "Building the decision brief",
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
          <strong>{confidence.level} evidence strength</strong>
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
      <div className="results-kicker"><span>Decision brief</span><span>{label(trace.problem_class)}</span></div>

      <div className="diagnosis-grid">
        <div>
          <p className="result-label">Current view</p>
          <span className="result-note">The strongest conclusion supported by the information provided</span>
        </div>
        <p>{result.diagnosis}</p>
      </div>

      <section className="section-block synthesis-section">
        <div className="section-heading"><p>01</p><h2>Why this is the current view</h2><span>Integrated reasoning</span></div>
        <p className="synthesis-copy">{result.synthesis}</p>
      </section>

      <section className="section-block drivers-section">
        <div className="section-heading"><p>02</p><h2>Key decision variables</h2><span>{result.key_drivers.length} surfaced</span></div>
        {result.key_drivers.length > 0 ? (
          <div className="driver-grid">
            {result.key_drivers.map((driver, index) => (
              <article key={`${driver.title}-${index}`}>
                <span>{String(index + 1).padStart(2, "0")}</span>
                <h3>{driver.title}</h3>
                {driver.explanation !== driver.title && <p>{driver.explanation}</p>}
              </article>
            ))}
          </div>
        ) : (
          <p className="empty-insight">The input does not yet contain enough evidence to rank the decision variables. Use the checks below to identify what matters most.</p>
        )}
      </section>

      {result.competing_explanations.length > 0 && (
        <section className="section-block alternatives-section">
          <div className="section-heading"><p>03</p><h2>What could make this wrong</h2><span>Stress-test the current view</span></div>
          <div className="alternative-list">
            {result.competing_explanations.map((item, index) => (
              <article key={`${item.explanation}-${index}`}>
                <span>{String(index + 1).padStart(2, "0")}</span>
                <div><h3>{item.explanation}</h3><p>{item.why_it_matters}</p></div>
              </article>
            ))}
          </div>
        </section>
      )}

      <section className="section-block compact-section">
        <div className="section-heading"><p>04</p><h2>What to verify before deciding</h2><span>{result.next_checks.length} checks</span></div>
        {result.next_checks.map((item, index) => (
          <article className="detail-item unknown" key={`${item.question}-${index}`}>
            <h3>{item.question}</h3>
            <p><b>Look for</b>{item.signal}</p>
          </article>
        ))}
      </section>

      <section className="section-block leverage-section">
        <div className="section-heading"><p>05</p><h2>Recommended next moves</h2><span>Reduce uncertainty before committing</span></div>
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
        <div className="section-heading"><p>06</p><h2>Evidence strength</h2><span>How much weight to place on this brief</span></div>
        <ConfidenceDisplay confidence={result.confidence} />
      </section>

      <details className="reasoning-details">
        <summary><span>Inspect the reasoning</span><small>{result.selected_lenses.length} lenses · {trace.operations.length} operations</small></summary>
        <div className="reasoning-inner">
          <div className="split-sections">
            <section className="section-block compact-section">
              <div className="section-heading"><p>A</p><h2>Critical assumptions</h2></div>
              {result.assumptions.map((item, index) => (
                <article className="detail-item" key={`${item.statement}-${index}`}>
                  <h3>{item.statement}</h3>
                  <p><b>Why it matters</b>{item.impact}</p>
                  <p><b>Test</b>{item.validation_question}</p>
                </article>
              ))}
            </section>
            <section className="section-block compact-section">
              <div className="section-heading"><p>B</p><h2>Claims examined</h2></div>
              {result.claims.map((claim, index) => (
                <article className="detail-item" key={`${claim.statement}-${index}`}>
                  <h3>{claim.statement}</h3>
                  {claim.evidence.length > 0 && <p><b>Evidence</b>{claim.evidence.join(" · ")}</p>}
                </article>
              ))}
            </section>
          </div>

          <div className="lens-grid">
            {result.selected_lenses.map((lens) => (
              <article className="lens-card" key={lens.name}>
                <h3>{label(lens.name)}</h3>
                <p>{lens.purpose}</p>
                <div className="tags">{lens.operations.map((operation) => <span key={operation}>{label(operation)}</span>)}</div>
              </article>
            ))}
          </div>

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
        </div>
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
        <p>Decision stress test</p>
        <span className="edition">Portfolio build · 01</span>
      </header>

      <section className="hero" id="top">
        <div className="hero-copy">
          <p className="eyebrow"><span /> Decision intelligence</p>
          <h1>Stress-test a decision <em>before you commit.</em></h1>
          <p className="intro">SystemLens turns an uncertain decision into a structured brief: the current view, key variables, failure conditions, missing evidence, and the next moves that reduce uncertainty.</p>
        </div>

        <form className="analyze-form" onSubmit={analyze}>
          <label htmlFor="problem">What decision are you trying to make?</label>
          <textarea
            id="problem"
            value={problem}
            onChange={(event) => setProblem(event.target.value)}
            placeholder="Example: Should we hire another engineer now or wait six months? Include any context you already know."
            maxLength={10000}
            disabled={loading}
          />
          <div className="form-footer">
            <span>{problem.length.toLocaleString()} / 10,000</span>
            <button type="submit" disabled={!problem.trim() || loading}>
              {loading ? "Stress-testing" : "Stress-test decision"}<i aria-hidden="true">↗</i>
            </button>
          </div>
        </form>

        <div className="examples">
          <p>Try a decision</p>
          <div>{examples.map((example, index) => <button type="button" key={example} onClick={() => setProblem(example)}><span>0{index + 1}</span>{example}</button>)}</div>
        </div>
      </section>

      {loading && (
        <section className="processing" aria-live="polite">
          <div><p>Stress-testing your decision</p><span>SystemLens is examining assumptions, alternatives, uncertainty, and failure conditions.</span></div>
          <ol>{progressSteps.map((step, index) => <li key={step} className={index < progress ? "done" : index === progress ? "active" : ""}><i>{index < progress ? "✓" : index + 1}</i><span>{step}</span></li>)}</ol>
        </section>
      )}

      {error && <section className="error-message" role="alert"><span>Analysis interrupted</span><div><h2>We couldn’t complete this decision brief.</h2><p>{error}</p></div><button type="button" onClick={() => setError(null)}>Dismiss</button></section>}
      {result && <Results result={result} />}

      <footer><span>SystemLens</span><p>Decide with fewer blind spots.</p><small>Decision support, not decision replacement.</small></footer>
    </main>
  );
}
