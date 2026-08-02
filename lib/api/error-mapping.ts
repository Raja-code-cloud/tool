import type { ProblemDetailDto } from "@/lib/api/asset-types";
import { ApiError } from "@/lib/api/errors";

function extractProblemMessage(body: unknown): string | undefined {
  if (!body || typeof body !== "object") return undefined;
  const problem = body as ProblemDetailDto;
  return problem.error?.message ?? problem.detail ?? problem.title;
}

function extractProblemCode(body: unknown): string | undefined {
  if (!body || typeof body !== "object") return undefined;
  const problem = body as ProblemDetailDto;
  return problem.error?.code;
}

export function mapStatusToError(status: number, body: unknown): ApiError {
  const message = extractProblemMessage(body);
  const problemCode = extractProblemCode(body);

  if (status === 400) {
    return new ApiError(message ?? "Bad request", "bad_request", status, body, problemCode);
  }
  if (status === 401) {
    return new ApiError(message ?? "Unauthorized", "unauthorized", status, body);
  }
  if (status === 403) {
    return new ApiError(message ?? "Forbidden", "forbidden", status, body);
  }
  if (status === 404) {
    return new ApiError(message ?? "Not found", "not_found", status, body);
  }
  if (status === 409) {
    return new ApiError(message ?? "Conflict", "conflict", status, body);
  }
  if (status === 413) {
    return new ApiError(message ?? "Payload too large", "payload_too_large", status, body);
  }
  if (status === 415) {
    return new ApiError(message ?? "Unsupported media type", "unsupported_media", status, body);
  }
  if (status === 422) {
    if (problemCode === "unsupported_media_type" || problemCode === "unsupported_extension") {
      return new ApiError(message ?? "Unsupported media type", "unsupported_media", status, body);
    }
    return new ApiError(message ?? "Validation failed", "validation_error", status, body);
  }
  if (status === 429) {
    return new ApiError(message ?? "Rate limited", "rate_limited", status, body);
  }
  if (status === 408 || status === 504) {
    return new ApiError(message ?? "Request timed out", "timeout", status, body);
  }
  if (status >= 500) {
    return new ApiError(message ?? "Server error", "server_error", status, body);
  }
  return new ApiError(message ?? "Request failed", "unknown", status, body);
}

export function mapTransportError(error: unknown): ApiError {
  if (error instanceof ApiError) return error;
  if (error instanceof DOMException && error.name === "AbortError") {
    return new ApiError("Upload cancelled", "unknown", 0, error);
  }
  return new ApiError(
    error instanceof Error ? error.message : "Network request failed",
    "network_error",
    0,
    error,
  );
}
