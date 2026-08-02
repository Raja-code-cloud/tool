"use client";

import * as React from "react";

import { PageContainer } from "@/components/layout";
import { ErrorState } from "@/components/feedback";

export default function DashboardError({ error, reset }: { error: Error & { digest?: string }; reset: () => void }): React.JSX.Element {
  React.useEffect(() => {
    // Replaced by the observability client in a later milestone.
    console.error(error);
  }, [error]);

  return (
    <PageContainer>
      <ErrorState
        title="Something went wrong"
        description={error.digest ? `This page failed to render. Reference: ${error.digest}` : "This page failed to render. Retrying usually resolves it."}
        onRetry={reset}
      />
    </PageContainer>
  );
}
