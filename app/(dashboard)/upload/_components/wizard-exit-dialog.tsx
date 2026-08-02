"use client";

import { Dialog, DialogContent } from "@/components/dialogs";
import { Button } from "@/components/ui";

export type WizardExitDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onConfirmExit: () => void;
  title?: string;
  description?: string;
};

export function WizardExitDialog({
  open,
  onOpenChange,
  onConfirmExit,
  title = "Leave upload wizard?",
  description = "You have unsaved changes. Your progress will be lost unless you save a draft first.",
}: WizardExitDialogProps): React.JSX.Element {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent title={title} description={description} className="max-w-md">
        <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
          <Button variant="secondary" onClick={() => onOpenChange(false)}>
            Keep editing
          </Button>
          <Button
            variant="destructive"
            onClick={() => {
              onConfirmExit();
              onOpenChange(false);
            }}
          >
            Exit wizard
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
