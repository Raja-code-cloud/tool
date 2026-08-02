import {
  Expand,
  Minimize2,
  Redo2,
  RefreshCw,
  Sparkles,
  Square,
  ThumbsDown,
  ThumbsUp,
  Undo2,
  Wand2,
} from "lucide-react";

import { CopyButton, OutlineButton, PrimaryButton, SecondaryButton } from "@/components/buttons";
import { Toolbar } from "@/components/common";

import type { WorkspaceActions, WorkspaceData, WorkspacePanelState } from "./workspace-contracts";

export function WorkspaceActionToolbars({
  data,
  panelState,
  actions,
}: {
  data: WorkspaceData;
  panelState: WorkspacePanelState;
  actions: WorkspaceActions;
}): React.JSX.Element {
  return (
    <div className="space-y-3 border-t p-4">
      <Toolbar label="AI actions">
        <PrimaryButton type="button" onClick={actions.onGenerate} disabled={data.isLoading}>
          <Sparkles className="size-4" aria-hidden="true" /> Generate
        </PrimaryButton>
        <SecondaryButton
          type="button"
          onClick={actions.onRegenerate}
          disabled={data.isLoading || !data.current.isGenerated}
        >
          <RefreshCw className="size-4" aria-hidden="true" /> Regenerate
        </SecondaryButton>
        {data.isLoading && (
          <OutlineButton type="button" onClick={actions.onCancelGeneration}>
            <Square className="size-4" aria-hidden="true" /> Cancel
          </OutlineButton>
        )}
        <SecondaryButton
          type="button"
          onClick={() => actions.onTransform("improve")}
          disabled={data.isLoading || !data.current.isGenerated}
        >
          <Wand2 className="size-4" aria-hidden="true" /> Improve
        </SecondaryButton>
        <SecondaryButton
          type="button"
          onClick={() => actions.onTransform("expand")}
          disabled={data.isLoading || !data.current.isGenerated}
        >
          <Expand className="size-4" aria-hidden="true" /> Expand
        </SecondaryButton>
        <SecondaryButton
          type="button"
          onClick={() => actions.onTransform("shorten")}
          disabled={data.isLoading || !data.current.isGenerated}
        >
          <Minimize2 className="size-4" aria-hidden="true" /> Shorten
        </SecondaryButton>
      </Toolbar>
      <Toolbar label="Tone transforms">
        {(["professional", "friendly", "technical", "executive"] as const).map((tone) => (
          <OutlineButton
            key={tone}
            type="button"
            size="compact"
            onClick={() => actions.onTransform(tone)}
            disabled={data.isLoading || !data.current.isGenerated}
          >
            {tone.charAt(0).toUpperCase() + tone.slice(1)}
          </OutlineButton>
        ))}
      </Toolbar>
      <Toolbar label="Content actions">
        <CopyButton value={data.displayContent} />
        <SecondaryButton type="button" onClick={actions.onSaveDraft} disabled={data.isLoading}>
          Save draft
        </SecondaryButton>
        <SecondaryButton
          type="button"
          onClick={actions.onApprove}
          disabled={!data.current.isGenerated}
        >
          <ThumbsUp className="size-4" aria-hidden="true" /> Approve
        </SecondaryButton>
        <SecondaryButton
          type="button"
          onClick={actions.onReject}
          disabled={!data.current.isGenerated}
        >
          <ThumbsDown className="size-4" aria-hidden="true" /> Reject
        </SecondaryButton>
        <SecondaryButton type="button" onClick={actions.onUndo} disabled={!panelState.canUndo}>
          <Undo2 className="size-4" aria-hidden="true" /> Undo
        </SecondaryButton>
        <SecondaryButton type="button" onClick={actions.onRedo} disabled={!panelState.canRedo}>
          <Redo2 className="size-4" aria-hidden="true" /> Redo
        </SecondaryButton>
      </Toolbar>
    </div>
  );
}
