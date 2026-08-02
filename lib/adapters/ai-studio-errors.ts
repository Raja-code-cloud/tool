import type { ProblemDetailsDto } from "@/lib/api/ai-studio-types";
import { ApiError, type ApiErrorCode } from "@/lib/api/errors";

function readBackendCode(body: unknown): string | undefined {
  if (!body || typeof body !== "object") return undefined;
  const problem = body as ProblemDetailsDto;
  return problem.error?.code;
}

function readBackendMessage(body: unknown, fallback: string): string {
  if (!body || typeof body !== "object") return fallback;
  const problem = body as ProblemDetailsDto;
  return problem.error?.message ?? problem.detail ?? fallback;
}

export function mapStatusToApiError(status: number, body: unknown): ApiError {
  const backendCode = readBackendCode(body);
  const message = readBackendMessage(body, "Request failed");

  const mappings: ReadonlyArray<[number | "range", ApiErrorCode, string]> = [
    [400, "bad_request", message],
    [401, "unauthorized", "Unauthorized"],
    [403, "forbidden", "Forbidden"],
    [404, "not_found", "Not found"],
    [408, "timeout", "Request timed out"],
    [409, "conflict", message],
    [422, "validation_error", message],
    [429, backendCode === "quota_exceeded" ? "quota_exceeded" : "rate_limited", message],
    [503, "service_unavailable", message],
    [504, "timeout", "Upstream service timed out"],
  ];

  for (const [statusCode, code, defaultMessage] of mappings) {
    if (statusCode === "range") continue;
    if (status === statusCode) {
      return new ApiError(defaultMessage, code, status, body, backendCode);
    }
  }

  if (status >= 500) {
    return new ApiError("Server error", "server_error", status, body, backendCode);
  }

  return new ApiError(message, "unknown", status, body, backendCode);
}

export function mapAiStudioError(error: unknown): {
  readonly title: string;
  readonly description: string;
  readonly recoverable: boolean;
} {
  if (error instanceof ApiError) {
    switch (error.code) {
      case "validation_error":
        return {
          title: "Invalid prompt",
          description: error.message,
          recoverable: true,
        };
      case "rate_limited":
        return {
          title: "Rate limited",
          description: "Too many generation requests. Wait a moment and try again.",
          recoverable: true,
        };
      case "quota_exceeded":
        return {
          title: "Quota exceeded",
          description: "Your AI usage quota has been reached for this billing period.",
          recoverable: false,
        };
      case "timeout":
        return {
          title: "Generation timed out",
          description: "The AI provider did not respond in time. You can retry generation.",
          recoverable: true,
        };
      case "service_unavailable":
        return {
          title: "Provider unavailable",
          description: error.message || "The AI provider is temporarily unavailable.",
          recoverable: true,
        };
      case "forbidden":
        return {
          title: "Permission denied",
          description: "You do not have permission to generate content.",
          recoverable: false,
        };
      case "conflict":
        return {
          title: "Conflict",
          description: error.message,
          recoverable: true,
        };
      case "not_found":
        return {
          title: "Content not found",
          description: "The source content or model could not be found.",
          recoverable: false,
        };
      case "unauthorized":
        return {
          title: "Session expired",
          description: "Sign in again to continue generating content.",
          recoverable: false,
        };
      case "network_error":
        return {
          title: "Network error",
          description: error.message,
          recoverable: true,
        };
      default:
        return {
          title: "Generation failed",
          description: error.message,
          recoverable: true,
        };
    }
  }

  if (error instanceof DOMException && error.name === "AbortError") {
    return {
      title: "Generation cancelled",
      description: "The in-flight generation request was cancelled.",
      recoverable: true,
    };
  }

  return {
    title: "Unexpected error",
    description: error instanceof Error ? error.message : "Something went wrong.",
    recoverable: true,
  };
}
