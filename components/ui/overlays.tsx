"use client";

import * as DropdownMenuPrimitive from "@radix-ui/react-dropdown-menu";
import * as ToastPrimitive from "@radix-ui/react-toast";
import { Check, X } from "lucide-react";
import * as React from "react";

import { cn } from "../../lib/utils/cn";
import { Button } from "./primitives";

export const DropdownMenu = DropdownMenuPrimitive.Root;
export const DropdownMenuTrigger = DropdownMenuPrimitive.Trigger;
export type DropdownMenuContentProps = React.ComponentPropsWithoutRef<
  typeof DropdownMenuPrimitive.Content
>;
export const DropdownMenuContent = React.forwardRef<
  React.ElementRef<typeof DropdownMenuPrimitive.Content>,
  DropdownMenuContentProps
>(({ className, sideOffset = 6, ...props }, ref) => (
  <DropdownMenuPrimitive.Portal>
    <DropdownMenuPrimitive.Content
      ref={ref}
      sideOffset={sideOffset}
      className={cn(
        "bg-popover text-popover-foreground shadow-popover data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=closed]:zoom-out-95 data-[state=open]:animate-in data-[state=open]:fade-in-0 data-[state=open]:zoom-in-95 z-50 max-h-90 min-w-45 overflow-auto rounded-lg border p-1 focus:outline-none motion-reduce:animate-none",
        className,
      )}
      {...props}
    />
  </DropdownMenuPrimitive.Portal>
));
DropdownMenuContent.displayName = "DropdownMenuContent";
export type DropdownMenuItemProps = React.ComponentPropsWithoutRef<
  typeof DropdownMenuPrimitive.Item
> & { isDestructive?: boolean };
export const DropdownMenuItem = React.forwardRef<
  React.ElementRef<typeof DropdownMenuPrimitive.Item>,
  DropdownMenuItemProps
>(({ className, isDestructive = false, ...props }, ref) => (
  <DropdownMenuPrimitive.Item
    ref={ref}
    className={cn(
      "focus:bg-accent flex min-h-9 cursor-default items-center gap-2 rounded-md px-3 text-sm outline-none select-none data-[disabled]:opacity-50",
      isDestructive && "text-destructive focus:bg-destructive/10",
      className,
    )}
    {...props}
  />
));
DropdownMenuItem.displayName = "DropdownMenuItem";
export type DropdownMenuCheckboxItemProps = React.ComponentPropsWithoutRef<
  typeof DropdownMenuPrimitive.CheckboxItem
>;
export const DropdownMenuCheckboxItem = React.forwardRef<
  React.ElementRef<typeof DropdownMenuPrimitive.CheckboxItem>,
  DropdownMenuCheckboxItemProps
>(({ className, children, ...props }, ref) => (
  <DropdownMenuPrimitive.CheckboxItem
    ref={ref}
    className={cn(
      "focus:bg-accent relative flex min-h-9 cursor-default items-center rounded-md py-2 pr-3 pl-9 text-sm outline-none select-none",
      className,
    )}
    {...props}
  >
    <DropdownMenuPrimitive.ItemIndicator className="absolute left-3">
      <Check className="size-4" />
    </DropdownMenuPrimitive.ItemIndicator>
    {children}
  </DropdownMenuPrimitive.CheckboxItem>
));
DropdownMenuCheckboxItem.displayName = "DropdownMenuCheckboxItem";
export const DropdownMenuSeparator = DropdownMenuPrimitive.Separator;
export const DropdownMenuLabel = DropdownMenuPrimitive.Label;

export type ToastProviderProps = React.ComponentPropsWithoutRef<typeof ToastPrimitive.Provider>;
export function ToastProvider({ children, ...props }: ToastProviderProps): React.JSX.Element {
  return (
    <ToastPrimitive.Provider {...props}>
      {children}
      <ToastPrimitive.Viewport className="fixed right-0 bottom-0 z-100 flex max-h-dvh w-full max-w-sm flex-col gap-2 p-4" />
    </ToastPrimitive.Provider>
  );
}
export type ToastProps = React.ComponentPropsWithoutRef<typeof ToastPrimitive.Root> & {
  title: string;
  description?: string;
  action?: React.ReactNode;
};
export const Toast = React.forwardRef<React.ElementRef<typeof ToastPrimitive.Root>, ToastProps>(
  ({ title, description, action, className, ...props }, ref) => (
    <ToastPrimitive.Root
      ref={ref}
      className={cn(
        "bg-popover text-popover-foreground relative rounded-lg border p-4 pr-12 shadow-xl",
        className,
      )}
      {...props}
    >
      <ToastPrimitive.Title className="font-semibold">{title}</ToastPrimitive.Title>
      {description && (
        <ToastPrimitive.Description className="text-muted-foreground mt-1 text-sm">
          {description}
        </ToastPrimitive.Description>
      )}
      {action}
      <ToastPrimitive.Close asChild>
        <Button variant="icon" className="absolute top-2 right-2" aria-label="Dismiss notification">
          <X className="size-4" />
        </Button>
      </ToastPrimitive.Close>
    </ToastPrimitive.Root>
  ),
);
Toast.displayName = "Toast";
