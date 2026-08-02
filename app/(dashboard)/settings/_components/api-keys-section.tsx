"use client";

import { Plus } from "lucide-react";
import * as React from "react";

import { CopyButton } from "@/components/buttons";
import { ConfirmationDialog } from "@/components/dialogs";
import { DataTable, type DataTableColumn } from "@/components/tables";
import { Badge, Button } from "@/components/ui";
import { useToast } from "@/hooks/use-toast";
import type { ApiKeyRecord, ApiKeyScope } from "@/lib/domain/settings";
import { settingsService } from "@/lib/services";
import { formatDate } from "@/lib/utils/formatting";

import { SettingsSection } from "./settings-section";

const SCOPE_VARIANT: Record<ApiKeyScope, "neutral" | "info" | "warning"> = {
  read: "neutral",
  write: "info",
  admin: "warning",
};

export function ApiKeysSection(): React.JSX.Element {
  const { toast } = useToast();
  const [keys, setKeys] = React.useState<readonly ApiKeyRecord[]>(() =>
    settingsService.listApiKeys(),
  );

  const revoke = React.useCallback(
    (id: string, label: string): void => {
      setKeys((current) => current.filter((key) => key.id !== id));
      toast({ title: "API key revoked", description: `“${label}” can no longer be used.` });
    },
    [toast],
  );

  const columns = React.useMemo<readonly DataTableColumn<ApiKeyRecord>[]>(
    () => [
      {
        id: "label",
        header: "Name",
        isPrimary: true,
        cell: (row) => (
          <div className="min-w-0">
            <p className="font-medium">{row.label}</p>
            <p className="text-muted-foreground text-xs">Created {formatDate(row.createdAt)}</p>
          </div>
        ),
      },
      {
        id: "key",
        header: "Key",
        cell: (row) => (
          <span className="flex items-center gap-2">
            <code className="text-data">{row.maskedKey}</code>
            <CopyButton value={row.maskedKey} label={`Copy ${row.label} key`} />
          </span>
        ),
      },
      {
        id: "scope",
        header: "Scope",
        cell: (row) => <Badge variant={SCOPE_VARIANT[row.scope]}>{row.scope}</Badge>,
      },
      {
        id: "lastUsed",
        header: "Last used",
        cell: (row) =>
          row.lastUsedAt ? (
            formatDate(row.lastUsedAt)
          ) : (
            <span className="text-muted-foreground">Never</span>
          ),
      },
      {
        id: "actions",
        header: <span className="sr-only">Actions</span>,
        align: "right",
        cell: (row) => (
          <ConfirmationDialog
            trigger={
              <Button variant="ghost" size="compact">
                Revoke
              </Button>
            }
            title={`Revoke “${row.label}”?`}
            description="Any integration using this key will start failing immediately. This cannot be undone."
            confirmLabel="Revoke key"
            isDestructive
            onConfirm={() => revoke(row.id, row.label)}
          />
        ),
      },
    ],
    [revoke],
  );

  return (
    <SettingsSection
      id="api-keys"
      title="API Keys"
      description="Keys authenticate server-to-server requests to the Cloud Content Hub API."
      action={
        <Button variant="secondary" size="compact">
          <Plus className="size-4" aria-hidden="true" />
          Create key
        </Button>
      }
    >
      <DataTable
        caption="API keys for this workspace"
        columns={columns}
        rows={keys}
        getRowId={(row) => row.id}
        density="compact"
        empty="No API keys yet. Create one to start using the API."
      />
      <p className="text-muted-foreground mt-3 text-xs">
        Secret values are shown once at creation time and cannot be retrieved later.
      </p>
    </SettingsSection>
  );
}
