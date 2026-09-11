"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
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
const short = (value: string, max = 150) => value.length > max ? `${value.slice(0, max).trim()}…` : value;

function ConfidenceDisplay({ confidence }: { confidence: Confidence }) {
  const percent = Math.round(confidence.score * 100);
  return (
    <div className="confidence-card">
      <div className="confidence-ring" style={{ "--score": `${percent * 3.6}deg` } as React.CSSProperties}>
        <div><strong>{percent}</strong><span>/100</span></div>
      </div>
      <div>
        <p className="micro-label">Evidence strength</p>
        <h3>{confidence.level} confidence</h3>
        <p>{confidence.rationale}</p>
      </div>
    </div>
  );
}

function Results({ result, onNewAnalysis }: { result: AnalysisResponse; onNewAnalysis: () => void }) {
  const trace = result.execution_trace;
  const keyReason = result.key_drivers[0]?.explanation || result.synthesis;
  const mainRisk = result.competing_explanations[0]?.explanation || result.assumptions[0]?.statement || "The decision could change if a key constraint is missing.";
  const nextStep = result.leverage_points[0]?.description || result.next_checks[0]?.question || "Gather the missing decision inputs before committing.";
  const [copied, setCopied] = useState(false);

  const briefText = useMemo(() => [
    `Decision: ${result.problem}`,
    `Current view: ${result.diagnosis}`,
    `Key reason: ${keyReason}`,
    `Main risk: ${mainRisk}`,
    `Next step: ${nextStep}`,
  ].join("\n\n"), [result, keyReason, mainRisk, nextStep]);

  async function copyBrief() {
    await navigator.clipboard.writeText(briefText);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1600);
  }

  return (
    <section className="results" aria-live="polite">
      <div className="result-toolbar">
        <button className="ghost-button" type="button" onClick={onNewAnalysis}>← New analysis</button>
        <div className="toolbar-actions"><button className="ghost-button" type="button" onClick={copyBrief}>{copied ? "Copied" : "Copy brief"}</button></div>
      </div>

      <div className="result-title-row">
        <div>
          <p className="micro-label">Decision brief</p>
          <h2>{result.problem}</h2>
          <p className="result-meta">Analysis complete · {result.selected_lenses.length} lenses · {trace.operations.length} reasoning operations</p>
        </div>
      </div>

      <nav className="result-nav" aria-label="Result sections">
        <a href="#summary">Summary</a><a href="#variables">Key variables</a><a href="#checks">Checks</a><a href="#moves">Next moves</a><a href="#reasoning">Reasoning</a>
      </nav>

      <section className="summary-panel" id="summary">
        <div className="current-view-card">
          <div>
            <p className="micro-label green">Current view</p>
            <h3>{result.diagnosis}</h3>
            <p>{short(result.synthesis, 300)}</p>
          </div>
          <ConfidenceDisplay confidence={result.confidence} />
        </div>
        <div className="summary-cards">
          <article><span className="summary-icon">◎</span><p className="micro-label">Key reason</p><h4>{short(keyReason, 150)}</h4></article>
          <article><span className="summary-icon risk">△</span><p className="micro-label">Main risk</p><h4>{short(mainRisk, 150)}</h4></article>
          <article><span className="summary-icon next">→</span><p className="micro-label">Next step</p><h4>{short(nextStep, 150)}</h4></article>
        </div>
      </section>

      <section className="product-section" id="variables">
        <div className="section-title-row"><div><p className="micro-label">01</p><h3>Key decision variables</h3></div><span>{result.key_drivers.length} factors</span></div>
        {result.key_drivers.length > 0 ? (
          <div className="variable-grid">
            {result.key_drivers.slice(0, 6).map((driver, index) => (
              <article className="interactive-card" key={`${driver.title}-${index}`}>
                <span className="card-index">0{index + 1}</span><span className="card-arrow">↗</span>
                <h4>{short(driver.title, 88)}</h4><p>{short(driver.explanation, 170)}</p>
              </article>
            ))}
          </div>
        ) : <p className="empty-insight">Add more context to identify the variables most likely to change the decision.</p>}
      </section>

      {result.competing_explanations.length > 0 && (
        <section className="product-section">
          <div className="section-title-row"><div><p className="micro-label">02</p><h3>What could make this wrong</h3></div><span>Stress test</span></div>
          <div className="risk-list">
            {result.competing_explanations.slice(0, 4).map((item, index) => <article key={`${item.explanation}-${index}`}><span>{index + 1}</span><div><h4>{item.explanation}</h4><p>{item.why_it_matters}</p></div></article>)}
          </div>
        </section>
      )}

      <section className="product-section" id="checks">
        <div className="section-title-row"><div><p className="micro-label">03</p><h3>What to verify before deciding</h3></div><span>{result.next_checks.length} checks</span></div>
        <div className="check-list">
          {result.next_checks.slice(0, 5).map((item, index) => (
            <article key={`${item.question}-${index}`}><span className="check-mark">?</span><div><h4>{item.question}</h4><p><b>Look for</b>{item.signal}</p></div></article>
          ))}
        </div>
      </section>

      <section className="product-section" id="moves">
        <div className="section-title-row"><div><p className="micro-label">04</p><h3>Recommended next moves</h3><p className="section-subtitle">Prioritized actions to reduce uncertainty before committing.</p></div></div>
        <div className="moves-list">
          {result.leverage_points.slice(0, 5).map((point, index) => (
            <article key={`${point.title}-${index}`}><span className="move-number">{index + 1}</span><div><h4>{point.title}</h4><p>{point.description}</p></div><span className={`impact ${point.priority.toLowerCase()}`}>{point.priority}</span></article>
          ))}
        </div>
      </section>

      <section className="product-section compact-evidence"><ConfidenceDisplay confidence={result.confidence} /></section>

      <details className="reasoning-details" id="reasoning">
        <summary><span><strong>Inspect the reasoning</strong><small>Assumptions, claims and thinking lenses</small></span><span>{result.selected_lenses.length} lenses · {trace.operations.length} operations</span></summary>
        <div className="reasoning-inner">
          <div className="reasoning-columns">
            <section><p className="micro-label">Critical assumptions</p>{result.assumptions.slice(0, 5).map((item, index) => <article key={`${item.statement}-${index}`}><h4>{item.statement}</h4><p>{item.impact}</p></article>)}</section>
            <section><p className="micro-label">Claims examined</p>{result.claims.slice(0, 5).map((claim, index) => <article key={`${claim.statement}-${index}`}><h4>{claim.statement}</h4>{claim.evidence.length > 0 && <p>{claim.evidence.join(" · ")}</p>}</article>)}</section>
          </div>
          <div className="lens-grid">
            {result.selected_lenses.map((lens) => <article className="lens-card" key={lens.name}><h4>{label(lens.name)}</h4><p>{lens.purpose}</p><div className="tags">{lens.operations.map((operation) => <span key={operation}>{label(operation)}</span>)}</div></article>)}
          </div>
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
    setLoading(true); setError(null); setResult(null);
    try {
      const response = await fetch("/api/analyze", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ problem }) });
      const data = (await response.json()) as AnalysisResponse | ApiError;
      if (!response.ok || "error" in data) throw new Error("message" in data ? data.message : "Analysis failed.");
      setResult(data);
      window.setTimeout(() => document.querySelector(".results")?.scrollIntoView({ behavior: "smooth", block: "start" }), 80);
    } catch (caught) { setError(caught instanceof Error ? caught.message : "Something went wrong. Please try again."); }
    finally { setLoading(false); }
  }

  function startNewAnalysis() { setResult(null); setProblem(""); window.scrollTo({ top: 0, behavior: "smooth" }); }

  return (
    <main>
      <header className="site-header">
        <a className="wordmark" href="#top"><span className="mark">⌘</span><span>SystemLens</span></a>
        <nav><a href="#how">How it works</a><a href="#examples">Examples</a><a href="#about">About</a></nav>
        <a className="header-cta" href="#analyze">Try it now <span>→</span></a>
      </header>

      {!result && <>
        <section className="hero" id="top">
          <div className="hero-layout">
            <div className="hero-main">
              <p className="eyebrow">Better questions. Clearer decisions.</p>
              <h1>Turn uncertainty into <em>clarity.</em></h1>
              <p className="intro">SystemLens uses structured reasoning to stress-test decisions, diagnose complex problems, and surface what actually matters.</p>
              <div className="benefit-grid">
                <article><span>□</span><h3>Stress-test decisions</h3><p>See assumptions, risks and missing evidence before you commit.</p></article>
                <article><span>◎</span><h3>Diagnose blind spots</h3><p>Surface variables and failure conditions that change the answer.</p></article>
                <article><span>↗</span><h3>Know what to do next</h3><p>Turn uncertainty into clear checks and prioritized actions.</p></article>
              </div>
            </div>
            <aside className="hero-aside"><div className="orb"><span>SL</span></div><blockquote>“Think clearly before the cost of being wrong gets expensive.”</blockquote><p>Decision intelligence for founders, product teams and operators.</p></aside>
          </div>

          <form className="analyze-form" id="analyze" onSubmit={analyze}>
            <textarea value={problem} onChange={(event) => setProblem(event.target.value)} placeholder="Ask a decision, question or problem…" maxLength={10000} disabled={loading} />
            <div className="form-footer"><span>{problem.length.toLocaleString()} / 10,000</span><button type="submit" disabled={!problem.trim() || loading}>{loading ? "Analyzing" : "Analyze with SystemLens"}<i>→</i></button></div>
          </form>

          <div className="examples" id="examples"><p>Try an example</p><div>{examples.map((example) => <button type="button" key={example} onClick={() => setProblem(example)}>{example}</button>)}</div></div>
        </section>

        <section className="proof-strip"><p>Built for</p><span>Founders</span><span>Product teams</span><span>Operators</span><span>Consultants</span><span>Researchers</span></section>

        <section className="how-section" id="how"><div className="how-copy"><p className="eyebrow">How SystemLens works</p><h2>A structured path from uncertainty to action.</h2></div><div className="how-grid">{[["01","Understand","Classify the decision and identify the real question."],["02","Reason","Apply multiple lenses to assumptions, trade-offs and risks."],["03","Synthesize","Turn analysis into a concise decision brief."],["04","Act","Prioritize the next checks that reduce uncertainty."]].map(([n,t,d]) => <article key={n}><span>{n}</span><h3>{t}</h3><p>{d}</p></article>)}</div></section>
      </>}

      {loading && <section className="processing"><div><p>Stress-testing your decision</p><span>SystemLens is examining assumptions, alternatives, uncertainty, and failure conditions.</span></div><ol>{progressSteps.map((step, index) => <li key={step} className={index < progress ? "done" : index === progress ? "active" : ""}><i>{index < progress ? "✓" : index + 1}</i><span>{step}</span></li>)}</ol></section>}
      {error && <section className="error-message" role="alert"><span>Analysis interrupted</span><div><h2>We couldn’t complete this decision brief.</h2><p>{error}</p></div><button onClick={() => setError(null)}>Dismiss</button></section>}
      {result && <Results result={result} onNewAnalysis={startNewAnalysis} />}

      <footer id="about"><span>SystemLens</span><p>Decide with fewer blind spots.</p><small>Decision support, not decision replacement.</small></footer>
    </main>
  );
}
