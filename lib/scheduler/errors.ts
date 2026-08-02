import { ApiError, isApiError, type ApiErrorCode } from "@/lib/api/errors";
import type { ProblemDetail } from "@/lib/api/scheduler-types";

export type SchedulerErrorCode =
  | ApiErrorCode
  | "conflict"
  | "rate_limited"
  | "schedule_time_ambiguous"
  | "schedule_time_nonexistent"
  | "invalid_state_transition"
  | "version_conflict"
  | "idempotency_conflict";

export class SchedulerError extends Error {
  readonly code: SchedulerErrorCode;
  readonly status: number;
  readonly details?: unknown;

  constructor(message: string, code: SchedulerErrorCode, status: number, details?: unknown) {
    super(message);
    this.name = "SchedulerError";
    this.code = code;
    this.status = status;
    this.details = details;
  }
}

function extractProblemCode(body: unknown): string | null {
  if (!body || typeof body !== "object") return null;
  const problem = body as ProblemDetail;
  return problem.error?.code ?? null;
}

function extractProblemMessage(body: unknown, fallback: string): string {
  if (!body || typeof body !== "object") return fallback;
  const problem = body as ProblemDetail;
  return problem.error?.message ?? problem.detail ?? problem.title ?? fallback;
}

export function mapSchedulerError(error: unknown): SchedulerError {
  if (error instanceof SchedulerError) return error;

  if (isApiError(error)) {
    const problemCode = extractProblemCode(error.details);
    const message = extractProblemMessage(error.details, error.message);

    if (error.status === 409) {
      if (problemCode === "schedule_time_ambiguous") {
        return new SchedulerError(message, "schedule_time_ambiguous", 409, error.details);
      }
      if (problemCode === "version_conflict") {
        return new SchedulerError(message, "version_conflict", 409, error.details);
      }
      if (problemCode === "idempotency_conflict") {
        return new SchedulerError(message, "idempotency_conflict", 409, error.details);
      }
      if (problemCode === "invalid_state_transition") {
        return new SchedulerError(message, "invalid_state_transition", 409, error.details);
      }
      return new SchedulerError(message, "conflict", 409, error.details);
    }

    if (error.status === 429) {
      return new SchedulerError(message, "rate_limited", 429, error.details);
    }

    if (error.status === 422 && problemCode === "schedule_time_nonexistent") {
      return new SchedulerError(message, "schedule_time_nonexistent", 422, error.details);
    }

    return new SchedulerError(message, error.code, error.status, error.details);
  }

  if (error instanceof Error) {
    return new SchedulerError(error.message, "unknown", 0, error);
  }

  return new SchedulerError("An unexpected scheduler error occurred.", "unknown", 0, error);
}

export function isSchedulerError(error: unknown): error is SchedulerError {
  return error instanceof SchedulerError;
}

export function schedulerErrorMessage(error: unknown): string {
  return mapSchedulerError(error).message;
}

export function wrapApiError(error: ApiError): never {
  throw mapSchedulerError(error);
}
