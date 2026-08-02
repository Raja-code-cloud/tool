"use client";

import * as React from "react";

import { ErrorState } from "@/components/feedback";
import { PageContainer } from "@/components/layout";
import { reportClientError } from "@/lib/security";

export default function DashboardError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}): React.JSX.Element {
  React.useEffect(() => {
    reportClientError(error, {
      boundary: "dashboard",
      ...(error.digest ? { digest: error.digest } : {}),
    });
  }, [error]);

  return (
    <PageContainer>
      <ErrorState
        title="Something went wrong"
        description={
          error.digest
            ? `This page failed to render. Reference: ${error.digest}`
            : "This page failed to render. Retrying usually resolves it."
        }
        onRetry={reset}
      />
    </PageContainer>
  );
}
