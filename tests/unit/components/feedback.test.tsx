import { describe, expect, it, vi } from "vitest";

import {
  Alert,
  EmptyState,
  ErrorState,
  LiveRegion,
  LoadingOverlay,
  NoResults,
  Progress,
  SkeletonTable,
  Spinner,
  StatusBadge,
} from "@/components/feedback/feedback";
import { renderWithProviders, screen } from "@/tests/utils";

describe("feedback components", () => {
  it("renders status badges and alert variants with appropriate roles", () => {
    renderWithProviders(
      <>
        <StatusBadge label="Healthy">Connected</StatusBadge>
        <Alert title="Heads up">Publishing queue is paused.</Alert>
        <Alert variant="success" title="Published">
          Content is live.
        </Alert>
        <Alert variant="warning" title="Warning">
          Token expiring soon.
        </Alert>
        <Alert variant="danger" title="Failed">
          Upload failed.
        </Alert>
      </>,
    );

    expect(screen.getByText("Connected")).toBeInTheDocument();
    expect(screen.getByText("Heads up").closest("[role='status']")).toBeTruthy();
    expect(screen.getByText("Failed").closest("[role='alert']")).toBeTruthy();
  });

  it("renders empty and error states with actions", async () => {
    const onRetry = vi.fn();
    const { user } = renderWithProviders(
      <>
        <NoResults title="No matches" description="Try another query." />
        <ErrorState title="Unable to load" description="Try again." onRetry={onRetry} />
      </>,
    );

    expect(screen.getByText("No matches")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: /Try again/i }));
    expect(onRetry).toHaveBeenCalledOnce();
  });

  it("renders progress, loading, and live region helpers", () => {
    renderWithProviders(
      <>
        <Progress value={65} label="Upload progress" />
        <Spinner label="Saving draft" />
        <LiveRegion politeness="assertive">Updated</LiveRegion>
        <LoadingOverlay label="Syncing" />
        <SkeletonTable rows={2} columns={3} />
      </>,
    );

    expect(screen.getByText("Upload progress")).toBeInTheDocument();
    expect(screen.getAllByRole("status").length).toBeGreaterThan(0);
    expect(screen.getByText("Updated").closest("[aria-live='assertive']")).toBeTruthy();
    expect(screen.getByLabelText("Syncing")).toBeInTheDocument();
  });

  it("supports custom empty-state content", () => {
    renderWithProviders(
      <EmptyState
        title="No drafts"
        description="Upload content to get started."
        action={<button type="button">Upload</button>}
      />,
    );

    expect(screen.getByRole("button", { name: "Upload" })).toBeInTheDocument();
  });
});
