"use client";

import * as React from "react";
import * as DialogPrimitive from "@radix-ui/react-dialog";
import { X } from "lucide-react";

import { cn } from "../../lib/utils/cn";
import { Button } from "../ui";

export type DialogProps = React.ComponentPropsWithoutRef<typeof DialogPrimitive.Root>;
export const Dialog = DialogPrimitive.Root;
export const Modal = DialogPrimitive.Root;
export const DialogTrigger = DialogPrimitive.Trigger;
export const ModalTrigger = DialogPrimitive.Trigger;
export const DialogClose = DialogPrimitive.Close;

export type DialogContentProps = React.ComponentPropsWithoutRef<typeof DialogPrimitive.Content> & { title: string; description?: string };
export const DialogContent = React.forwardRef<React.ElementRef<typeof DialogPrimitive.Content>, DialogContentProps>(({ title, description, children, className, ...props }, ref) => (
  <DialogPrimitive.Portal>
    <DialogPrimitive.Overlay className="fixed inset-0 z-50 bg-background/75 backdrop-blur-sm data-[state=closed]:animate-out data-[state=open]:animate-in motion-reduce:animate-none" />
    <DialogPrimitive.Content ref={ref} className={cn("fixed top-1/2 left-1/2 z-50 max-h-[90dvh] w-[calc(100%-2rem)] max-w-xl -translate-x-1/2 -translate-y-1/2 overflow-auto rounded-xl border bg-card p-6 shadow-dialog focus:outline-none data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=closed]:zoom-out-95 data-[state=open]:animate-in data-[state=open]:fade-in-0 data-[state=open]:zoom-in-95 motion-reduce:animate-none motion-reduce:transition-none", className)} {...props}>
      <DialogPrimitive.Title className="pr-10 text-xl font-semibold">{title}</DialogPrimitive.Title>
      {description && <DialogPrimitive.Description className="mt-1 text-sm text-muted-foreground">{description}</DialogPrimitive.Description>}
      <div className="mt-5">{children}</div>
      <DialogPrimitive.Close asChild><Button variant="icon" className="absolute top-3 right-3" aria-label="Close dialog"><X className="size-5" /></Button></DialogPrimitive.Close>
    </DialogPrimitive.Content>
  </DialogPrimitive.Portal>
));
DialogContent.displayName = "DialogContent";
export const ModalContent = DialogContent;

export type ConfirmationDialogProps = DialogProps & { trigger: React.ReactNode; title: string; description: string; confirmLabel: string; onConfirm: () => void; isDestructive?: boolean };
export function ConfirmationDialog({ trigger, title, description, confirmLabel, onConfirm, isDestructive = false, ...props }: ConfirmationDialogProps): React.JSX.Element {
  return <Dialog {...props}><DialogTrigger asChild>{trigger}</DialogTrigger><DialogContent className="max-w-md" title={title} description={description}><div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end"><DialogClose asChild><Button variant="secondary">Cancel</Button></DialogClose><DialogClose asChild><Button variant={isDestructive ? "destructive" : "primary"} onClick={onConfirm}>{confirmLabel}</Button></DialogClose></div></DialogContent></Dialog>;
}

export type DrawerContentProps = DialogContentProps & { side?: "left" | "right" };
export const DrawerContent = React.forwardRef<React.ElementRef<typeof DialogPrimitive.Content>, DrawerContentProps>(({ side = "right", className, ...props }, ref) => (
  <DialogContent ref={ref} className={cn("top-0 h-dvh max-h-dvh w-full max-w-md translate-y-0 rounded-none", side === "right" ? "right-0 left-auto translate-x-0" : "left-0 translate-x-0", className)} {...props} />
));
DrawerContent.displayName = "DrawerContent";
