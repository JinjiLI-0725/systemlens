import { NextRequest, NextResponse } from "next/server";
import type { AnalysisResponse, ApiError } from "@/lib/types";

export const runtime = "nodejs";

const BACKEND_URL = process.env.SYSTEMLENS_BACKEND_URL ?? "http://127.0.0.1:8000";
const TIMEOUT_MS = 60_000;

function errorResponse(error: ApiError["error"], message: string, status: number) {
  return NextResponse.json({ error, message } satisfies ApiError, { status });
}

function looksLikeAnalysis(value: unknown): value is AnalysisResponse {
  if (!value || typeof value !== "object") return false;
  const result = value as Partial<AnalysisResponse>;
  return (
    typeof result.problem === "string" &&
    typeof result.summary === "string" &&
    Array.isArray(result.selected_lenses) &&
    Array.isArray(result.claims) &&
    Array.isArray(result.assumptions) &&
    Array.isArray(result.unknowns) &&
    Array.isArray(result.leverage_points) &&
    typeof result.confidence?.score === "number" &&
    typeof result.execution_trace?.execution_mode === "string" &&
    Array.isArray(result.execution_trace?.batch_timings)
  );
}

export async function POST(request: NextRequest) {
  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return errorResponse("invalid_request", "Enter a problem before starting an analysis.", 400);
  }

  const problem = (body as { problem?: unknown })?.problem;
  if (typeof problem !== "string" || !problem.trim() || problem.length > 10_000) {
    return errorResponse("invalid_request", "The problem must be between 1 and 10,000 characters.", 400);
  }

  try {
    const response = await fetch(`${BACKEND_URL.replace(/\/$/, "")}/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ problem: problem.trim() }),
      cache: "no-store",
      signal: AbortSignal.timeout(TIMEOUT_MS),
    });

    let data: unknown;
    try {
      data = await response.json();
    } catch {
      return errorResponse("malformed_response", "The analysis service returned an unreadable response.", 502);
    }

    if (!response.ok) {
      const detail = (data as { detail?: unknown })?.detail;
      const message = typeof detail === "string" ? detail : "The analysis service could not process this problem.";
      return errorResponse("analysis_failed", message, response.status >= 500 ? 502 : response.status);
    }

    if (!looksLikeAnalysis(data)) {
      return errorResponse("malformed_response", "The analysis was incomplete. Please try again.", 502);
    }

    return NextResponse.json(data);
  } catch (error) {
    if (error instanceof Error && (error.name === "TimeoutError" || error.name === "AbortError")) {
      return errorResponse("timeout", "The analysis took longer than expected. Please try again.", 504);
    }
    return errorResponse("backend_unavailable", "SystemLens cannot reach the analysis service right now.", 503);
  }
}
