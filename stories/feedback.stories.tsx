import type { Meta, StoryObj } from "@storybook/react";
import { Search } from "lucide-react";

import {
  ConfirmationDialog,
  Dialog,
  DialogClose,
  DialogContent,
  DialogTrigger,
  DrawerContent,
  Modal,
  ModalContent,
  ModalTrigger,
} from "../components/dialogs";
import {
  Alert,
  EmptyState,
  ErrorState,
  LiveRegion,
  LoadingOverlay,
  NoContent,
  NoData,
  NoResults,
  Progress,
  Skeleton,
  SkeletonCard,
  SkeletonTable,
  SkeletonText,
  Spinner,
  StatusBadge,
} from "../components/feedback";
import { Button, Toast, ToastProvider } from "../components/ui";

const meta = {
  title: "Feedback/Status and Overlays",
  component: Alert,
  parameters: {
    docs: {
      description: {
        component:
          "Feedback patterns communicate status without relying on color alone. Live updates use appropriate status, alert, progress, dialog, and toast semantics.",
      },
    },
  },
  args: { title: "Information", children: "A concise message explains what happened." },
} satisfies Meta<typeof Alert>;

export default meta;
type Story = StoryObj<typeof meta>;

export const AlertsAndBadges: Story = {
  render: () => (
    <div className="grid gap-3">
      {(["info", "success", "warning", "danger"] as const).map((variant) => (
        <Alert key={variant} variant={variant} title={`${variant} alert`}>
          Message with an icon and text.
        </Alert>
      ))}
      <div className="flex gap-2">
        {(["neutral", "info", "success", "warning", "danger"] as const).map((variant) => (
          <StatusBadge key={variant} variant={variant} label={variant} />
        ))}
      </div>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story: "Alert variants and StatusBadge labels pair text/icon cues with color.",
      },
    },
  },
};

export const EmptyAndErrorStates: Story = {
  render: () => (
    <div className="tablet:grid-cols-2 grid gap-4">
      <EmptyState
        title="Nothing here"
        description="Create the first item."
        icon={<Search />}
        action={<Button>Create</Button>}
      />
      <NoResults title="No results" description="Try a broader search." />
      <NoData title="No data" description="Data will appear after processing." />
      <NoContent title="No content" description="Add content to continue." />
      <ErrorState
        title="Could not load"
        description="Try the request again."
        onRetry={() => undefined}
      />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story:
          "EmptyState, NoResults, NoData, NoContent, and ErrorState provide task-specific guidance and optional actions.",
      },
    },
  },
};

export const LoadingStates: Story = {
  render: () => (
    <div className="grid gap-5">
      <Spinner />
      <Progress label="Processing" value={62} />
      <Skeleton className="h-8 w-40" />
      <SkeletonText lines={4} />
      <SkeletonCard hasMedia />
      <SkeletonTable rows={3} columns={3} />
      <div className="relative h-24 border">
        <LoadingOverlay label="Loading preview" />
      </div>
      <LiveRegion>Background update complete.</LiveRegion>
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story:
          "Spinner, Progress, Skeleton, SkeletonText, SkeletonCard, SkeletonTable, LoadingOverlay, and LiveRegion cover determinate, indeterminate, and assistive-only updates.",
      },
    },
  },
};

export const DialogFamily: Story = {
  render: () => (
    <div className="flex flex-wrap gap-3">
      <Dialog>
        <DialogTrigger asChild>
          <Button>Open dialog</Button>
        </DialogTrigger>
        <DialogContent title="Edit campaign" description="Update campaign details.">
          <DialogClose asChild>
            <Button>Save</Button>
          </DialogClose>
        </DialogContent>
      </Dialog>
      <Modal>
        <ModalTrigger asChild>
          <Button variant="secondary">Open modal alias</Button>
        </ModalTrigger>
        <ModalContent title="Modal alias">Modal and Dialog share behavior.</ModalContent>
      </Modal>
      <Dialog>
        <DialogTrigger asChild>
          <Button variant="outline">Open drawer</Button>
        </DialogTrigger>
        <DrawerContent title="Filters" side="right">
          Drawer content
        </DrawerContent>
      </Dialog>
      <ConfirmationDialog
        trigger={<Button variant="destructive">Delete</Button>}
        title="Delete item?"
        description="This action cannot be undone."
        confirmLabel="Delete"
        isDestructive
        onConfirm={() => undefined}
      />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story:
          "Dialog, DialogTrigger, DialogContent, DialogClose, Modal aliases, DrawerContent, and ConfirmationDialog trap focus and restore it to the trigger.",
      },
    },
  },
};

export const ToastNotification: Story = {
  render: () => (
    <ToastProvider>
      <Toast
        open
        title="Upload complete"
        description="campaign.csv is ready."
        action={<Button size="compact">View</Button>}
      />
    </ToastProvider>
  ),
  parameters: {
    docs: {
      description: {
        story:
          "ToastProvider supplies the viewport; Toast exposes title, description, action, duration, and open-state controls.",
      },
    },
  },
};
