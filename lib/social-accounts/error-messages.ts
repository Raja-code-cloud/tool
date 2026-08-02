import { isApiError } from "@/lib/api/errors";

export function resolveSocialAccountErrorMessage(error: unknown): string {
  if (isApiError(error)) {
    switch (error.code) {
      case "unauthorized":
        return "Your session expired. Sign in again to manage social accounts.";
      case "forbidden":
        return "You do not have permission to manage social accounts in this workspace.";
      case "not_found":
        return "The social account or platform could not be found.";
      case "conflict":
        if (error.backendCode === "social_account_unhealthy") {
          return "This account is disconnected or needs reauthorization before publishing.";
        }
        return error.message || "The account state changed. Refresh and try again.";
      case "validation_error":
        return error.message || "The request was invalid. Check your input and try again.";
      case "rate_limited":
        return "Too many requests. Wait a moment and try again.";
      case "network_error":
        return "Network error. Check your connection and try again.";
      case "server_error":
        return "The server encountered an error. Try again shortly.";
      default:
        return error.message || "Something went wrong. Try again.";
    }
  }

  if (error instanceof Error) {
    return error.message;
  }

  return "Something went wrong. Try again.";
}
