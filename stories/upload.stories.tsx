import type { Meta, StoryObj } from "@storybook/react";
import { FileText } from "lucide-react";

import {
  FileCard,
  UploadDropzone,
  UploadProgress,
  UploadQueueItem,
  UploadZone,
} from "../components/upload";

const meta = {
  title: "Upload/File Upload",
  component: UploadZone,
  parameters: {
    docs: {
      description: {
        component:
          "File upload patterns support drag/drop, keyboard file selection, validation callbacks, progress, failure recovery, and responsive wrapping.",
      },
    },
  },
  args: { onFiles: () => undefined, supportedTypes: "PNG, JPG, or PDF", maximumSize: 10_000_000 },
} satisfies Meta<typeof UploadZone>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Dropzones: Story = {
  render: (args) => (
    <div className="tablet:grid-cols-2 grid gap-4">
      <UploadZone {...args} />
      <UploadDropzone {...args} prompt="Upload campaign assets" />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story:
          "UploadZone and UploadDropzone are aliases. Both expose accept, maximumSize, maximumFiles, accepted files, and rejection callbacks.",
      },
    },
  },
};

export const QueueStates: Story = {
  render: () => (
    <ul className="grid max-w-xl gap-3">
      <UploadQueueItem
        name="brief.pdf"
        size={1_240_000}
        status="queued"
        preview={<FileText />}
        onRemove={() => undefined}
      />
      <UploadQueueItem name="video.mp4" size={8_400_000} status="uploading" progress={64} />
      <FileCard name="image.png" size={420_000} status="complete" />
      <FileCard
        name="invalid.exe"
        status="failed"
        error="Unsupported file type."
        onRetry={() => undefined}
        onRemove={() => undefined}
      />
    </ul>
  ),
  parameters: {
    docs: {
      description: {
        story:
          "UploadQueueItem and FileCard aliases demonstrate queued, uploading, complete, and failed states with named retry/remove controls.",
      },
    },
  },
};

export const ProgressIndicator: Story = {
  render: () => (
    <div className="max-w-lg">
      <UploadProgress value={72} label="Uploading media" />
    </div>
  ),
  parameters: {
    docs: {
      description: {
        story:
          "UploadProgress bounds values from 0–100 and pairs the native progress element with visible text.",
      },
    },
  },
};
