"use client";

import { Card, CardHeader } from "@/components/cards";
import { Alert } from "@/components/feedback";
import { CharacterCount, FormField } from "@/components/forms";
import { Tabs } from "@/components/navigation";
import { Badge, Textarea } from "@/components/ui";
import { UploadQueueItem, UploadZone } from "@/components/upload";
import { ARTICLE_ACCEPT, ARTICLE_MAX_BYTES } from "@/constants/upload-wizard";
import { INPUT_LIMITS } from "@/lib/security";

import { countWords, estimateReadingMinutes, type WizardFormState } from "../wizard-types";

export type StepMasterArticleProps = {
  form: WizardFormState;
  errors: Readonly<Record<string, string>>;
  onChange: (patch: Partial<WizardFormState>) => void;
  onUpload: (file: File) => void;
  onRemoveFile: () => void;
};

export function StepMasterArticle({
  form,
  errors,
  onChange,
  onUpload,
  onRemoveFile,
}: StepMasterArticleProps): React.JSX.Element {
  const wordCount = countWords(form.articleContent);
  const readingMinutes = estimateReadingMinutes(wordCount);
  const charCount = form.articleContent.length;

  return (
    <Card>
      <CardHeader
        title="Master article"
        description="Upload a Markdown, DOCX, or TXT file — or paste content directly."
      />
      <Tabs
        items={[
          { id: "paste", label: "Paste content" },
          { id: "upload", label: "Upload file" },
        ]}
        value={form.articleMode}
        onValueChange={(value) =>
          onChange({ articleMode: value as WizardFormState["articleMode"] })
        }
        label="Article input mode"
      />
      <div
        role="tabpanel"
        id="panel-paste"
        aria-labelledby="tab-paste"
        hidden={form.articleMode !== "paste"}
        className="mt-4"
      >
        <FormField
          id="article-content"
          label="Article content"
          isRequired
          {...(errors.articleContent ? { error: errors.articleContent } : {})}
        >
          <Textarea
            value={form.articleContent}
            rows={14}
            maxLength={INPUT_LIMITS.articleContent}
            placeholder="# Your article title&#10;&#10;Write or paste your master article in Markdown..."
            onChange={(event) => onChange({ articleContent: event.target.value })}
          />
        </FormField>
        <div className="mt-3 flex flex-wrap items-center gap-2">
          <Badge variant="neutral">{wordCount} words</Badge>
          <Badge variant="neutral">{charCount} characters</Badge>
          <Badge variant="neutral">~{readingMinutes} min read</Badge>
          <CharacterCount
            current={charCount}
            maximum={INPUT_LIMITS.articleContent}
            className="ml-auto"
          />
        </div>
        {form.articleContent.trim().length > 0 && (
          <div className="mt-5">
            <p className="mb-2 text-sm font-semibold">Markdown preview</p>
            <div className="bg-muted/40 max-h-64 overflow-auto rounded-lg border p-4 text-sm whitespace-pre-wrap">
              {form.articleContent}
            </div>
          </div>
        )}
        {errors.articleContent && (
          <Alert variant="danger" title="Article content required" className="mt-4">
            {errors.articleContent}
          </Alert>
        )}
      </div>
      <div
        role="tabpanel"
        id="panel-upload"
        aria-labelledby="tab-upload"
        hidden={form.articleMode !== "upload"}
        className="mt-4"
      >
        {!form.articleFile && (
          <UploadZone
            accept={ARTICLE_ACCEPT}
            maximumSize={ARTICLE_MAX_BYTES}
            supportedTypes="Markdown (.md), DOCX, TXT"
            prompt="Drop your master article here"
            onFiles={(files) => {
              const file = files[0];
              if (file) onUpload(file);
            }}
          />
        )}
        {form.articleFile && (
          <ul className="grid gap-2">
            <UploadQueueItem
              name={form.articleFile.name}
              size={form.articleFile.size}
              status={
                form.articleFile.status === "complete"
                  ? "complete"
                  : form.articleFile.status === "failed"
                    ? "failed"
                    : "uploading"
              }
              progress={form.articleFile.progress}
              onRemove={onRemoveFile}
            />
          </ul>
        )}
        {errors.articleFile && (
          <Alert variant="danger" title="Article file required" className="mt-4">
            {errors.articleFile}
          </Alert>
        )}
      </div>
    </Card>
  );
}
