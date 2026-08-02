"use client";

import { CheckCircle2, XCircle } from "lucide-react";
import Image from "next/image";

import { Card, CardHeader } from "@/components/cards";
import { Alert } from "@/components/feedback";
import { Badge } from "@/components/ui";
import {
  AI_LENGTHS,
  AI_PLATFORMS,
  AI_TONES,
  CONTENT_SERIES,
  PROJECT_CATEGORIES,
} from "@/constants/upload-wizard";
import { formatBytes } from "@/lib/utils/upload-wizard";

import {
  countWords,
  estimateReadingMinutes,
  validateStep,
  type WizardFormState,
} from "../wizard-types";

export type StepReviewProps = {
  form: WizardFormState;
};

function ValidationRow({ label, valid }: { label: string; valid: boolean }): React.JSX.Element {
  const Icon = valid ? CheckCircle2 : XCircle;
  return (
    <li className="flex items-center gap-2 text-sm">
      <Icon
        className={valid ? "text-success size-4" : "text-destructive size-4"}
        aria-hidden="true"
      />
      <span>{label}</span>
      <span className="sr-only">{valid ? "Complete" : "Incomplete"}</span>
    </li>
  );
}

export function StepReview({ form }: StepReviewProps): React.JSX.Element {
  const categoryLabel =
    PROJECT_CATEGORIES.find((item) => item.value === form.category)?.label ?? form.category;
  const seriesLabel =
    CONTENT_SERIES.find((item) => item.value === form.contentSeries)?.label ?? form.contentSeries;
  const toneLabel = AI_TONES.find((item) => item.value === form.tone)?.label ?? form.tone;
  const lengthLabel = AI_LENGTHS.find((item) => item.value === form.length)?.label ?? form.length;
  const wordCount = countWords(form.articleContent);
  const validations = [1, 2, 3, 4, 5, 6].map((step) => validateStep(step, form));

  return (
    <div className="grid gap-5">
      <Card>
        <CardHeader title="Project information" />
        <dl className="grid gap-3 text-sm sm:grid-cols-2">
          <div>
            <dt className="text-muted-foreground">Project name</dt>
            <dd className="font-medium">{form.projectName || "—"}</dd>
          </div>
          <div>
            <dt className="text-muted-foreground">Category</dt>
            <dd className="font-medium">{categoryLabel || "—"}</dd>
          </div>
          <div className="sm:col-span-2">
            <dt className="text-muted-foreground">Description</dt>
            <dd className="font-medium">{form.description || "—"}</dd>
          </div>
          <div>
            <dt className="text-muted-foreground">Tags</dt>
            <dd className="font-medium">{form.tags || "—"}</dd>
          </div>
          <div>
            <dt className="text-muted-foreground">Content series</dt>
            <dd className="font-medium">{seriesLabel}</dd>
          </div>
          <div>
            <dt className="text-muted-foreground">Estimated publish date</dt>
            <dd className="font-medium">{form.publishDate || "—"}</dd>
          </div>
        </dl>
      </Card>

      <div className="grid gap-5 lg:grid-cols-2">
        <Card>
          <CardHeader title="Poster preview" />
          {form.poster?.previewUrl ? (
            <Image
              src={form.poster.previewUrl}
              alt={`Poster preview for ${form.projectName || "project"}`}
              width={480}
              height={270}
              unoptimized
              className="rounded-lg border object-contain"
            />
          ) : (
            <p className="text-muted-foreground text-sm">No poster uploaded.</p>
          )}
        </Card>
        <Card>
          <CardHeader title="Thumbnail" />
          {form.thumbnailSkipped ? (
            <p className="text-muted-foreground text-sm">Skipped</p>
          ) : form.thumbnail?.previewUrl ? (
            <Image
              src={form.thumbnail.previewUrl}
              alt={`Thumbnail preview for ${form.projectName || "project"}`}
              width={480}
              height={270}
              unoptimized
              className="rounded-lg border object-contain"
            />
          ) : (
            <p className="text-muted-foreground text-sm">No thumbnail uploaded.</p>
          )}
        </Card>
      </div>

      <Card>
        <CardHeader title="Article summary" />
        <dl className="grid gap-2 text-sm sm:grid-cols-3">
          <div>
            <dt className="text-muted-foreground">Mode</dt>
            <dd className="font-medium capitalize">{form.articleMode}</dd>
          </div>
          <div>
            <dt className="text-muted-foreground">Word count</dt>
            <dd className="font-medium">{wordCount || (form.articleFile ? "File uploaded" : 0)}</dd>
          </div>
          <div>
            <dt className="text-muted-foreground">Reading time</dt>
            <dd className="font-medium">~{estimateReadingMinutes(wordCount)} min</dd>
          </div>
        </dl>
        {form.articleMode === "paste" && form.articleContent && (
          <p className="text-muted-foreground mt-3 line-clamp-4 text-sm">{form.articleContent}</p>
        )}
        {form.articleFile && <p className="mt-3 text-sm font-medium">{form.articleFile.name}</p>}
      </Card>

      <Card>
        <CardHeader title="Video summary" />
        {form.videoSkipped ? (
          <p className="text-muted-foreground text-sm">Skipped</p>
        ) : form.video ? (
          <dl className="grid gap-2 text-sm sm:grid-cols-3">
            <div>
              <dt className="text-muted-foreground">File</dt>
              <dd className="font-medium">{form.video.name}</dd>
            </div>
            <div>
              <dt className="text-muted-foreground">Size</dt>
              <dd className="font-medium">{formatBytes(form.video.size)}</dd>
            </div>
            <div>
              <dt className="text-muted-foreground">Duration</dt>
              <dd className="font-medium">{form.videoDuration || "—"}</dd>
            </div>
          </dl>
        ) : (
          <p className="text-muted-foreground text-sm">No video uploaded.</p>
        )}
      </Card>

      <Card>
        <CardHeader title="AI settings" />
        <div className="flex flex-wrap gap-2">
          {form.platforms.map((id) => {
            const label = AI_PLATFORMS.find((p) => p.id === id)?.label ?? id;
            return (
              <Badge key={id} variant="neutral">
                {label}
              </Badge>
            );
          })}
        </div>
        <dl className="mt-4 grid gap-2 text-sm sm:grid-cols-3">
          <div>
            <dt className="text-muted-foreground">Tone</dt>
            <dd className="font-medium">{toneLabel}</dd>
          </div>
          <div>
            <dt className="text-muted-foreground">Length</dt>
            <dd className="font-medium">{lengthLabel}</dd>
          </div>
          <div>
            <dt className="text-muted-foreground">Options</dt>
            <dd className="font-medium">
              {[
                form.generateHashtags && "Hashtags",
                form.generateCta && "CTA",
                form.generateSeo && "SEO",
              ]
                .filter(Boolean)
                .join(", ") || "None"}
            </dd>
          </div>
        </dl>
      </Card>

      <Card>
        <CardHeader title="Validation status" />
        <ul className="grid gap-2">
          <ValidationRow label="Project information" valid={validations[0]?.valid ?? false} />
          <ValidationRow label="Poster upload" valid={validations[1]?.valid ?? false} />
          <ValidationRow label="Master article" valid={validations[2]?.valid ?? false} />
          <ValidationRow label="Video upload" valid={validations[3]?.valid ?? false} />
          <ValidationRow label="Thumbnail upload" valid={validations[4]?.valid ?? false} />
          <ValidationRow label="AI generation settings" valid={validations[5]?.valid ?? false} />
        </ul>
        {validations.every((item) => item.valid) ? (
          <Alert variant="success" title="Ready to create" className="mt-4">
            All required steps are complete. Click Create project to finish.
          </Alert>
        ) : (
          <Alert variant="warning" title="Some steps need attention" className="mt-4">
            Go back and complete any incomplete steps before creating your project.
          </Alert>
        )}
      </Card>
    </div>
  );
}
