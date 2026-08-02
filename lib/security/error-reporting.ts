import { isProd } from "@/lib/config/env";

type ClientErrorContext = {
  readonly digest?: string;
  readonly boundary?: string;
};

/** Redacts client-side errors before logging. Full details belong in server observability. */
export function reportClientError(error: unknown, context: ClientErrorContext = {}): void {
  if (!isProd) {
    console.error("[client-error]", error, context);
    return;
  }

  const payload: Record<string, string> = {
    boundary: context.boundary ?? "unknown",
  };
  if (context.digest) payload.digest = context.digest;

  console.error("[client-error]", payload);
}
