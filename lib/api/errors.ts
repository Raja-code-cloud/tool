export type ApiErrorCode =
  | "network_error"
  | "timeout"
  | "unauthorized"
  | "forbidden"
  | "not_found"
  | "validation_error"
  | "server_error"
  | "unknown";

export class ApiError extends Error {
  readonly code: ApiErrorCode;
  readonly status: number;
  readonly details?: unknown;

  constructor(message: string, code: ApiErrorCode, status: number, details?: unknown) {
    super(message);
    this.name = "ApiError";
    this.code = code;
    this.status = status;
    this.details = details;
  }
}

export function isApiError(error: unknown): error is ApiError {
  return error instanceof ApiError;
}
