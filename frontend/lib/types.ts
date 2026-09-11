export type LensName =
  | "systems_thinking"
  | "critical_thinking"
  | "causal_reasoning"
  | "decision_making"
  | "probabilistic_thinking"
  | "forecasting"
  | "scientific_reasoning"
  | "problem_solving"
  | "argumentation"
  | "metacognition_and_bias";

export interface Confidence {
  score: number;
  level: string;
  rationale: string;
}

export interface SelectedLens {
  name: LensName;
  purpose: string;
  operations: string[];
}

export interface Claim {
  statement: string;
  evidence: string[];
  confidence: Confidence;
}

export interface Assumption {
  statement: string;
  impact: string;
  validation_question: string;
}

export interface Unknown {
  question: string;
  importance: string;
}

export interface LeveragePoint {
  title: string;
  description: string;
  related_lens: LensName;
  priority: string;
}

export interface GraphNode {
  id: string;
  label: string;
  category: string;
  description: string;
}

export interface GraphEdge {
  source: string;
  target: string;
  relationship: string;
  polarity: string;
}

export interface BatchTiming {
  batch_name: string;
  elapsed_ms: number;
  fallback_used: boolean;
  status: "llm" | "partial_fallback" | "deterministic_fallback";
  missing_operation_ids: string[];
  validation_error_category: string | null;
}

export interface ExecutionTrace {
  problem_class: string;
  selected_lenses: LensName[];
  operations: string[];
  execution_mode: string;
  requested_execution_mode: string;
  provider: string | null;
  model: string | null;
  batches: string[][];
  fallback_events: string[];
  batch_timings: BatchTiming[];
}

export interface AnalysisResponse {
  problem: string;
  summary: string;
  selected_lenses: SelectedLens[];
  claims: Claim[];
  assumptions: Assumption[];
  unknowns: Unknown[];
  leverage_points: LeveragePoint[];
  confidence: Confidence;
  graph_nodes: GraphNode[];
  graph_edges: GraphEdge[];
  execution_trace: ExecutionTrace;
}

export interface ApiError {
  error: "backend_unavailable" | "timeout" | "malformed_response" | "invalid_request" | "analysis_failed";
  message: string;
}
