"use client";

import { SecondaryButton } from "@/components/buttons";
import { Dialog, DialogContent } from "@/components/dialogs";
import { PlatformChip } from "@/components/platform";
import { SUPPORTED_PLATFORMS } from "@/lib/config/social-accounts";

export type ConnectAccountDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onConnect: (platformName: string) => void;
};

export function ConnectAccountDialog({
  open,
  onOpenChange,
  onConnect,
}: ConnectAccountDialogProps): React.JSX.Element {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent
        title="Connect account"
        description="Choose a platform to connect. OAuth flow is simulated with mock data."
      >
        <ul className="grid gap-2">
          {SUPPORTED_PLATFORMS.map((platform) => (
            <li key={platform.id}>
              <button
                type="button"
                className="bg-card hover:bg-accent/40 flex w-full items-center justify-between rounded-lg border px-4 py-3 text-left transition-colors"
                onClick={() => onConnect(platform.label)}
              >
                <span className="flex items-center gap-3">
                  <PlatformChip platform={platform.id} />
                  <span className="text-sm font-semibold">{platform.label}</span>
                </span>
                <span className="text-muted-foreground text-xs">Connect</span>
              </button>
            </li>
          ))}
        </ul>
        <div className="mt-4 flex justify-end">
          <SecondaryButton type="button" onClick={() => onOpenChange(false)}>
            Cancel
          </SecondaryButton>
        </div>
      </DialogContent>
    </Dialog>
  );
}
