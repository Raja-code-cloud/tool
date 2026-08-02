import { AnimatePresence, motion } from "framer-motion";

import { StatusBadge } from "@/components/feedback";
import { Badge, Textarea } from "@/components/ui";
import { MOTION_DURATION, MOTION_EASING } from "@/lib/motion";

import { AiLoadingOverlay, TypingCursor } from "./ai-loading-states";
import { AiStudioEmptyState } from "./ai-studio-empty-states";
import { CharacterLimitBar } from "./character-limit-bar";
import { useWorkspaceMetrics } from "./use-workspace-metrics";
import type { WorkspaceActions, WorkspaceData } from "./workspace-contracts";

export function WorkspaceEditor({
  data,
  actions,
}: {
  data: WorkspaceData;
  actions: WorkspaceActions;
}): React.JSX.Element {
  const metrics = useWorkspaceMetrics(data.activePlatform, data.displayContent, data.current);
  const approvalVariant =
    data.current.approvalStatus === "approved"
      ? "success"
      : data.current.approvalStatus === "rejected"
        ? "danger"
        : data.current.approvalStatus === "changes"
          ? "warning"
          : "neutral";
  return (
    <div className="relative p-4">
      <AiLoadingOverlay phase={data.loadingPhase} />
      {!data.current.isGenerated && !data.isLoading ? (
        <AiStudioEmptyState variant="no-response" onGenerate={actions.onGenerate} />
      ) : (
        <AnimatePresence mode="wait">
          <motion.div
            key={data.activePlatform}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: MOTION_DURATION.page, ease: MOTION_EASING.enter }}
            className="grid gap-4"
          >
            <div className="flex flex-wrap items-center gap-2">
              <StatusBadge variant={approvalVariant}>
                {data.current.approvalStatus.replace("_", " ")}
              </StatusBadge>
              <Badge variant="neutral">{metrics.wordCount} words</Badge>
              <Badge variant="neutral">{metrics.charCount} characters</Badge>
              <Badge variant="info">SEO {metrics.seoScore}</Badge>
              <Badge variant="success">Readability {metrics.readabilityScore}</Badge>
              <Badge variant="warning">Engagement {metrics.engagementScore}</Badge>
            </div>
            <CharacterLimitBar platform={data.activePlatform} current={metrics.charCount} />
            <label className="grid gap-1.5">
              <span className="text-sm font-semibold">Generated content</span>
              <Textarea
                value={data.displayContent}
                onChange={(event) => actions.onContentChange(event.target.value)}
                rows={12}
                disabled={data.isLoading}
                aria-label={`${data.activePlatform} generated content`}
                className="font-mono text-sm"
              />
              {data.isLoading && <TypingCursor />}
            </label>
            {data.current.hashtags.length > 0 && (
              <div>
                <p className="text-sm font-semibold">Hashtags</p>
                <p className="text-muted-foreground mt-1 text-sm">
                  {data.current.hashtags.join(" ")}
                </p>
              </div>
            )}
            {data.current.cta && (
              <div>
                <p className="text-sm font-semibold">Suggested CTA</p>
                <p className="text-muted-foreground mt-1 text-sm">{data.current.cta}</p>
              </div>
            )}
            <div>
              <p className="text-sm font-semibold">Platform tips</p>
              <ul className="text-muted-foreground mt-2 list-disc space-y-1 pl-5 text-sm">
                {metrics.tips.map((tip) => (
                  <li key={tip}>{tip}</li>
                ))}
              </ul>
            </div>
          </motion.div>
        </AnimatePresence>
      )}
    </div>
  );
}
