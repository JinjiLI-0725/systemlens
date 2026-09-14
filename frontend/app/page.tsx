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
const short = (value: string, max = 150) =>
  value.length > max ? `${value.slice(0, max).trim()}…` : value;

function ConfidenceDisplay({ confidence }: { confidence: Confidence }) {
  const percent = Math.round(confidence.score * 100);

  return (
    <div className="confidence-card">
      <div
        className="confidence-arc"
        style={
          {
            "--score": `${Math.max(8, percent) * 1.8}deg`,
          } as React.CSSProperties
        }
      >
        <div>
          <strong>{percent}</strong>
          <span>/100</span>
        </div>
      </div>

      <div className="confidence-copy">
        <p className="micro-label">Evidence strength</p>
        <h3>{confidence.level} confidence</h3>
        <p>{confidence.rationale}</p>
      </div>
    </div>
  );
}

function Results({
  result,
  onNewAnalysis,
}: {
  result: AnalysisResponse;
  onNewAnalysis: () => void;
}) {
  const trace = result.execution_trace;

  const keyReason =
    result.key_drivers[0]?.explanation || result.synthesis;

  const mainRisk =
    result.competing_explanations[0]?.explanation ||
    result.assumptions[0]?.statement ||
    "A missing constraint could change the recommendation.";

  const nextStep =
    result.leverage_points[0]?.description ||
    result.next_checks[0]?.question ||
    "Gather the missing decision inputs before committing.";

  const [copied, setCopied] = useState(false);

  const briefText = useMemo(
    () =>
      [
        `Decision: ${result.problem}`,
        `Current view: ${result.diagnosis}`,
        `Key reason: ${keyReason}`,
        `Main risk: ${mainRisk}`,
        `Next step: ${nextStep}`,
      ].join("\n\n"),
    [result, keyReason, mainRisk, nextStep]
  );

  async function copyBrief() {
    await navigator.clipboard.writeText(briefText);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1600);
  }

  return (
    <section className="results" aria-live="polite">
      <div className="result-toolbar">
        <button
          className="text-button"
          type="button"
          onClick={onNewAnalysis}
        >
          ← Back
        </button>

        <button
          className="soft-button"
          type="button"
          onClick={copyBrief}
        >
          {copied ? "Copied" : "Copy brief"}
        </button>
      </div>

      <header className="result-header">
        <p className="micro-label">Decision brief</p>
        <h2>{result.problem}</h2>
        <p>
          Analysis complete · {result.selected_lenses.length} lenses ·{" "}
          {trace.operations.length} key insights
        </p>
      </header>

      <nav className="result-nav" aria-label="Result sections">
        <a href="#summary">Summary</a>
        <a href="#variables">Key variables</a>
        <a href="#checks">Checks</a>
        <a href="#moves">Next moves</a>
        <a href="#reasoning">Reasoning</a>
      </nav>

      <section className="summary-panel" id="summary">
        <div className="current-view-card">
          <div className="current-view-copy">
            <p className="micro-label green">Current view</p>
            <h3>{result.diagnosis}</h3>
            <p>{short(result.synthesis, 300)}</p>
          </div>

          <ConfidenceDisplay confidence={result.confidence} />
        </div>

        <div className="summary-cards">
          <article>
            <span className="summary-icon amber">✦</span>
            <p className="micro-label">Key reason</p>
            <h4>{short(keyReason, 145)}</h4>
          </article>

          <article>
            <span className="summary-icon coral">△</span>
            <p className="micro-label">Main risk</p>
            <h4>{short(mainRisk, 145)}</h4>
          </article>

          <article>
            <span className="summary-icon green-icon">→</span>
            <p className="micro-label">Next step</p>
            <h4>{short(nextStep, 145)}</h4>
          </article>
        </div>
      </section>

      <section className="product-section" id="variables">
        <div className="section-title-row">
          <div>
            <h3>Key decision variables</h3>
            <p>What is most likely to change the answer.</p>
          </div>

          <span>{result.key_drivers.length} factors</span>
        </div>

        {result.key_drivers.length > 0 ? (
          <div className="variable-grid">
            {result.key_drivers.slice(0, 6).map((driver, index) => (
              <article
                className="variable-card"
                key={`${driver.title}-${index}`}
              >
                <div className="variable-top">
                  <span className="variable-icon">
                    {["◉", "⌁", "◷", "♙", "◇", "⬡"][index] ?? "•"}
                  </span>
                  <span>›</span>
                </div>

                <h4>{short(driver.title, 82)}</h4>
                <p>{short(driver.explanation, 150)}</p>
              </article>
            ))}
          </div>
        ) : (
          <p className="empty-insight">
            Add more context to identify the variables most likely to change
            the decision.
          </p>
        )}
      </section>

      <section className="product-section" id="moves">
        <div className="section-title-row">
          <div>
            <h3>Recommended next moves</h3>
            <p>Prioritized actions to reduce uncertainty.</p>
          </div>
        </div>

        <div className="moves-list">
          {result.leverage_points.slice(0, 5).map((point, index) => (
            <article key={`${point.title}-${index}`}>
              <span className="move-number">{index + 1}</span>

              <div>
                <h4>{point.title}</h4>
                <p>{point.description}</p>
              </div>

              <span className={`impact ${point.priority.toLowerCase()}`}>
                {point.priority} impact
              </span>
            </article>
          ))}
        </div>
      </section>

      <section className="product-section" id="checks">
        <div className="section-title-row">
          <div>
            <h3>What to verify before deciding</h3>
            <p>Evidence that would make the recommendation more reliable.</p>
          </div>

          <span>{result.next_checks.length} checks</span>
        </div>

        <div className="check-grid">
          {result.next_checks.slice(0, 4).map((item, index) => (
            <article key={`${item.question}-${index}`}>
              <span>0{index + 1}</span>
              <h4>{item.question}</h4>
              <p>{item.signal}</p>
            </article>
          ))}
        </div>
      </section>

      <details className="reasoning-details" id="reasoning" open>
        <summary>
          <span>
            <strong>Inspect the reasoning</strong>
            <small>Assumptions, claims and thinking lenses</small>
          </span>

          <span>
            {result.selected_lenses.length} lenses ·{" "}
            {trace.operations.length} operations
          </span>
        </summary>

        <div className="reasoning-inner">
          <div className="reasoning-columns">
            <section>
              <p className="micro-label">Critical assumptions</p>

              {result.assumptions.slice(0, 4).map((item, index) => (
                <article key={`${item.statement}-${index}`}>
                  <h4>{item.statement}</h4>
                  <p>{item.impact}</p>
                </article>
              ))}
            </section>

            <section>
              <p className="micro-label">Claims examined</p>

              {result.claims.slice(0, 4).map((claim, index) => (
                <article key={`${claim.statement}-${index}`}>
                  <h4>{claim.statement}</h4>

                  {claim.evidence.length > 0 && (
                    <p>{claim.evidence.join(" · ")}</p>
                  )}
                </article>
              ))}
            </section>
          </div>

          <div className="lens-grid">
            {result.selected_lenses.map((lens) => (
              <article key={lens.name}>
                <h4>{label(lens.name)}</h4>
                <p>{lens.purpose}</p>

                <div className="tags">
                  {lens.operations.map((operation) => (
                    <span key={operation}>{label(operation)}</span>
                  ))}
                </div>
              </article>
            ))}
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

    const interval = window.setInterval(
      () =>
        setProgress((current) =>
          Math.min(current + 1, progressSteps.length - 1)
        ),
      1800
    );

    return () => window.clearInterval(interval);
  }, [loading]);

  async function runAnalysis(input: string) {
    const cleanProblem = input.trim();

    if (!cleanProblem || loading) return;

    setProblem(cleanProblem);
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch("/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ problem: cleanProblem }),
      });

      const data = (await response.json()) as AnalysisResponse | ApiError;

      if (!response.ok || "error" in data) {
        throw new Error(
          "message" in data ? data.message : "Analysis failed."
        );
      }

      setResult(data);

      window.setTimeout(
        () =>
          document
            .querySelector(".results")
            ?.scrollIntoView({
              behavior: "smooth",
              block: "start",
            }),
        80
      );
    } catch (caught) {
      setError(
        caught instanceof Error
          ? caught.message
          : "Something went wrong. Please try again."
      );
    } finally {
      setLoading(false);
    }
  }

  async function analyze(event: FormEvent) {
    event.preventDefault();
    await runAnalysis(problem);
  }

  function startNewAnalysis() {
    setResult(null);
    setProblem("");
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  return (
    <main>
      <header className="site-header">
        <a className="wordmark" href="#top">
          <span className="mark">⌘</span>
          <span>SystemLens</span>
        </a>

        <nav>
          <a href="#top">Home</a>
          <a href="#how">How it works</a>
          <a href="#examples">Use cases</a>
          <a href="#about">About</a>
        </nav>

        {!result && !loading && (
          <button
            className="header-cta header-cta-button"
            type="button"
            onClick={() =>
              document
                .querySelector("#analyze")
                ?.scrollIntoView({ behavior: "smooth", block: "center" })
            }
          >
            Try it now
          </button>
        )}

        {loading && (
          <button
            className="header-cta header-cta-button is-disabled"
            type="button"
            disabled
          >
            Analyzing…
          </button>
        )}

        {result && (
          <button
            className="header-cta header-cta-button"
            type="button"
            onClick={startNewAnalysis}
          >
            New analysis
          </button>
        )}
      </header>

      {!result && (
        <>
          <section className={`sl-hero ${loading ? "is-loading" : ""}`} id="top">
            <div className="sl-hero-grid">
              <div className="sl-hero-left">
                <p className="sl-eyebrow">
                  Better questions. Clearer decisions.
                </p>

                <h1 className="sl-hero-title">
                  Decision intelligence
                  <br />
                  for <em>complex choices.</em>
                </h1>

                <p className="sl-hero-copy">
                  Stress-test your decisions, uncover hidden assumptions, and
                  surface what really matters — before you commit.
                </p>

                <form
                  className="sl-analysis-box"
                  id="analyze"
                  onSubmit={analyze}
                >
                  <textarea
                    value={problem}
                    onChange={(event) => setProblem(event.target.value)}
                    placeholder="Ask a decision, question or problem..."
                    maxLength={10000}
                    disabled={loading}
                  />

                  <div className="sl-analysis-footer">
                    <span>
                      {problem.length.toLocaleString()} / 10,000
                    </span>

                    <button
                      type="submit"
                      disabled={!problem.trim() || loading}
                    >
                      {loading ? "Analyzing" : "Analyze with SystemLens"}
                      <i>→</i>
                    </button>
                  </div>
                </form>

                <div className="sl-example-row">
                  <span className="sl-example-label">Try an example</span>

                  <div className="sl-example-pills">
                    {examples.map((example) => (
                      <button
                        type="button"
                        key={example}
                        onClick={() => setProblem(example)}
                      >
                        {example}
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              {!loading && <aside className="sl-preview-card">
                <div className="sl-preview-head">
                  <span>Example analysis result</span>

                  <button
                    type="button"
                    onClick={() => runAnalysis(examples[0])}
                  >
                    View full report <b>→</b>
                  </button>
                </div>

                <h2>
                  Should we hire another engineer
                  <br />
                  now or wait six months?
                </h2>

                <div className="sl-current-view">
                  <div className="sl-current-copy">
                    <span className="sl-preview-kicker">Current view</span>

                    <h3>Wait 3–6 months</h3>

                    <p>
                      Unless pipeline conversion improves
                      <br />
                      in the next two quarters.
                    </p>
                  </div>

                  <div className="sl-demo-confidence">
                    <div className="sl-demo-ring">
                      <div>
                        <strong>72</strong>
                        <span>/ 100</span>
                      </div>
                    </div>

                    <small>Confidence</small>
                  </div>
                </div>

                <div className="sl-preview-insights">
                  <article>
                    <div className="sl-insight-heading">
                      <span className="sl-insight-icon">⌁</span>
                      <strong>Key variable</strong>
                    </div>

                    <h4>Revenue visibility</h4>
                    <p>Biggest driver of the decision</p>
                  </article>

                  <article>
                    <div className="sl-insight-heading">
                      <span className="sl-insight-icon sl-risk-icon">
                        △
                      </span>
                      <strong>Main risk</strong>
                    </div>

                    <h4>Hiring too early</h4>
                    <p>Fixed cost before demand is validated</p>
                  </article>

                  <article>
                    <div className="sl-insight-heading">
                      <span className="sl-insight-icon">→</span>
                      <strong>Next move</strong>
                    </div>

                    <h4>Validate pipeline</h4>
                    <p>Get clearer revenue signals in 4–8 weeks</p>
                  </article>
                </div>

                <button
                  className="sl-preview-bottom"
                  type="button"
                  onClick={() => runAnalysis(examples[0])}
                >
                  <span className="sl-report-icon">▧</span>
                  <strong>See the full analysis</strong>
                  <span>→</span>
                </button>
              </aside>}

              {loading && (
                <section className="sl-processing-inline">
                  <div className="sl-processing-copy">
                    <p className="micro-label">Analysis in progress</p>
                    <h2>Stress-testing your decision</h2>
                    <p>
                      SystemLens is examining assumptions, alternatives,
                      uncertainty, and failure conditions.
                    </p>
                  </div>

                  <ol>
                    {progressSteps.map((step, index) => (
                      <li
                        key={step}
                        className={
                          index < progress
                            ? "done"
                            : index === progress
                            ? "active"
                            : ""
                        }
                      >
                        <i>{index < progress ? "✓" : index + 1}</i>
                        <span>{step}</span>
                      </li>
                    ))}
                  </ol>
                </section>
              )}
            </div>

            <div className="sl-capabilities">
              <article>
                <span className="sl-capability-icon">⌕</span>

                <div>
                  <h3>Decision stress testing</h3>
                  <p>
                    Explore multiple perspectives and identify where the
                    decision breaks.
                  </p>
                </div>
              </article>

              <article>
                <span className="sl-capability-icon">⌘</span>

                <div>
                  <h3>Root-cause reasoning</h3>
                  <p>
                    Separate symptoms from real drivers using structured
                    analysis.
                  </p>
                </div>
              </article>

              <article>
                <span className="sl-capability-icon">▥</span>

                <div>
                  <h3>Evidence planning</h3>
                  <p>
                    Identify what information is worth gathering next.
                  </p>
                </div>
              </article>
            </div>
          </section>

          <section className="example-section" id="examples">
            <div className="example-heading">
              <h2>Explore real examples</h2>
              <span>View all →</span>
            </div>

            <div className="example-grid">
              {[
                [
                  "Hiring Decision",
                  "Should a startup hire another engineer now or wait six months?",
                ],
                [
                  "Product Launch",
                  "Should we launch this product now or delay for another quarter?",
                ],
                [
                  "Make or Buy",
                  "Should we build this feature in-house or buy an external solution?",
                ],
              ].map(([title, copy], index) => (
                <button
                  type="button"
                  key={title}
                  onClick={() => {
                    setProblem(copy);
                    document
                      .querySelector("#analyze")
                      ?.scrollIntoView({ behavior: "smooth" });
                  }}
                >
                  <div className={`example-thumb thumb-${index + 1}`} />
                  <span className="micro-label">Decision</span>
                  <h3>{title}</h3>
                  <p>{copy}</p>
                  <i>→</i>
                </button>
              ))}
            </div>
          </section>

          <section className="how-section" id="how">
            <div className="how-editorial-head">
              <div>
                <p className="eyebrow">Why SystemLens</p>
                <h2>
                  More than an answer.
                  <br />
                  A stress test for your reasoning.
                </h2>
              </div>

              <p className="how-editorial-intro">
                General-purpose AI responds to the prompt. SystemLens
                interrogates the decision itself — surfacing hidden assumptions,
                competing explanations, uncertainty, and the evidence that could
                change the conclusion.
              </p>
            </div>

            <div className="how-editorial-grid">
              <article>
                <span className="how-number">01</span>
                <p className="how-kicker">Decompose</p>
                <h3>Find the real decision.</h3>
                <p>
                  Identify the alternatives, constraints, hidden assumptions,
                  and variables that actually drive the outcome.
                </p>
              </article>

              <article>
                <span className="how-number">02</span>
                <p className="how-kicker">Challenge</p>
                <h3>Search for what could make the answer wrong.</h3>
                <p>
                  Test counterarguments, competing explanations, and failure
                  modes instead of accepting the first plausible response.
                </p>
              </article>

              <article>
                <span className="how-number">03</span>
                <p className="how-kicker">Calibrate</p>
                <h3>Make uncertainty visible.</h3>
                <p>
                  Separate evidence from inference, expose confidence, and show
                  which information is still missing.
                </p>
              </article>

              <article>
                <span className="how-number">04</span>
                <p className="how-kicker">Trigger</p>
                <h3>Define what should change the decision.</h3>
                <p>
                  Identify the next checks, high-value information, and
                  conditions that should trigger a different action.
                </p>
              </article>
            </div>

            <div className="how-editorial-compare">
              <div className="compare-label">
                <span>Typical AI chat</span>
                <strong>Answer → explanation</strong>
              </div>

              <div className="compare-flow">
                <span>SystemLens</span>
                <strong>
                  Decision → assumptions → competing views → uncertainty →
                  evidence gaps → decision triggers
                </strong>
              </div>
            </div>
          </section>
        </>
      )}



      {error && (
        <section className="error-message" role="alert">
          <span>Analysis interrupted</span>

          <div>
            <h2>We couldn’t complete this decision brief.</h2>
            <p>{error}</p>
          </div>

          <button onClick={() => setError(null)}>Dismiss</button>
        </section>
      )}

      {result && (
        <Results result={result} onNewAnalysis={startNewAnalysis} />
      )}

      <footer id="about">
        <span>SystemLens</span>
        <p>Decide with fewer blind spots.</p>
        <small>Decision support, not decision replacement.</small>
      </footer>
    </main>
  );
}