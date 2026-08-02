"use client";

import * as AvatarPrimitive from "@radix-ui/react-avatar";
import * as CheckboxPrimitive from "@radix-ui/react-checkbox";
import * as LabelPrimitive from "@radix-ui/react-label";
import * as RadioGroupPrimitive from "@radix-ui/react-radio-group";
import * as SelectPrimitive from "@radix-ui/react-select";
import { Slot } from "@radix-ui/react-slot";
import * as SwitchPrimitive from "@radix-ui/react-switch";
import { cva, type VariantProps } from "class-variance-authority";
import { Check, ChevronDown } from "lucide-react";
import * as React from "react";

import { cn } from "../../lib/utils/cn";

export const buttonVariants = cva(
  "focus-visible:ring-ring focus-visible:ring-offset-background inline-flex min-h-9 items-center justify-center gap-2 rounded-md px-4 text-sm font-semibold transition-colors duration-150 focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:outline-none disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        primary: "bg-primary text-primary-foreground hover:brightness-110 active:brightness-95",
        secondary: "border-border bg-secondary text-secondary-foreground hover:bg-accent border",
        outline: "border-input text-foreground hover:bg-accent border bg-transparent",
        ghost: "text-foreground hover:bg-accent hover:text-accent-foreground bg-transparent",
        destructive: "bg-destructive text-destructive-foreground hover:brightness-110",
        icon: "text-foreground hover:bg-accent bg-transparent p-2",
      },
      size: { compact: "min-h-8 px-3", default: "min-h-9", prominent: "min-h-10 px-5" },
    },
    defaultVariants: { variant: "primary", size: "default" },
  },
);

export type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement> &
  VariantProps<typeof buttonVariants> & { asChild?: boolean; isLoading?: boolean };

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ asChild, className, isLoading = false, children, disabled, ...props }, ref) => {
    const Component = asChild ? Slot : "button";
    return (
      <Component
        ref={ref}
        className={cn(buttonVariants(props), className)}
        disabled={disabled || isLoading}
        aria-busy={isLoading || undefined}
        {...props}
      >
        {/* Slot accepts exactly one child, so the spinner is only injected when rendering a real button. */}
        {asChild ? (
          children
        ) : (
          <>
            {isLoading && (
              <span
                className="size-4 animate-spin rounded-full border-2 border-current border-r-transparent motion-reduce:animate-none"
                aria-hidden="true"
              />
            )}
            {children}
          </>
        )}
      </Component>
    );
  },
);
Button.displayName = "Button";

export type InputProps = React.InputHTMLAttributes<HTMLInputElement>;
export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, ...props }, ref) => (
    <input
      ref={ref}
      className={cn(
        "border-input bg-background text-foreground placeholder:text-muted-foreground focus-visible:ring-ring aria-invalid:border-destructive aria-invalid:ring-destructive min-h-9 w-full rounded-md border px-3 text-sm focus-visible:ring-2 focus-visible:outline-none disabled:cursor-not-allowed disabled:opacity-50",
        className,
      )}
      {...props}
    />
  ),
);
Input.displayName = "Input";

export type TextareaProps = React.TextareaHTMLAttributes<HTMLTextAreaElement>;
export const Textarea = React.forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className, ...props }, ref) => (
    <textarea
      ref={ref}
      className={cn(
        "border-input bg-background text-foreground placeholder:text-muted-foreground focus-visible:ring-ring aria-invalid:border-destructive min-h-24 w-full resize-y rounded-md border px-3 py-2 text-sm focus-visible:ring-2 focus-visible:outline-none disabled:opacity-50",
        className,
      )}
      {...props}
    />
  ),
);
Textarea.displayName = "Textarea";

export type LabelProps = React.ComponentPropsWithoutRef<typeof LabelPrimitive.Root>;
export const Label = React.forwardRef<React.ElementRef<typeof LabelPrimitive.Root>, LabelProps>(
  ({ className, ...props }, ref) => (
    <LabelPrimitive.Root
      ref={ref}
      className={cn("text-xs leading-4 font-semibold peer-disabled:opacity-50", className)}
      {...props}
    />
  ),
);
Label.displayName = "Label";

export type CheckboxProps = React.ComponentPropsWithoutRef<typeof CheckboxPrimitive.Root>;
export const Checkbox = React.forwardRef<
  React.ElementRef<typeof CheckboxPrimitive.Root>,
  CheckboxProps
>(({ className, ...props }, ref) => (
  <CheckboxPrimitive.Root
    ref={ref}
    className={cn(
      "peer border-input bg-background focus-visible:ring-ring data-[state=checked]:bg-primary data-[state=checked]:text-primary-foreground size-5 shrink-0 rounded border focus-visible:ring-2 focus-visible:outline-none disabled:opacity-50",
      className,
    )}
    {...props}
  >
    <CheckboxPrimitive.Indicator className="grid place-items-center">
      <Check className="size-4" aria-hidden="true" />
    </CheckboxPrimitive.Indicator>
  </CheckboxPrimitive.Root>
));
Checkbox.displayName = "Checkbox";

export type SwitchProps = React.ComponentPropsWithoutRef<typeof SwitchPrimitive.Root>;
export const Switch = React.forwardRef<React.ElementRef<typeof SwitchPrimitive.Root>, SwitchProps>(
  ({ className, ...props }, ref) => (
    <SwitchPrimitive.Root
      ref={ref}
      className={cn(
        "bg-input focus-visible:ring-ring data-[state=checked]:bg-primary h-6 w-11 rounded-full p-0.5 transition-colors focus-visible:ring-2 focus-visible:outline-none",
        className,
      )}
      {...props}
    >
      <SwitchPrimitive.Thumb className="bg-background block size-5 rounded-full shadow transition-transform data-[state=checked]:translate-x-5" />
    </SwitchPrimitive.Root>
  ),
);
Switch.displayName = "Switch";

export type RadioGroupProps = React.ComponentPropsWithoutRef<typeof RadioGroupPrimitive.Root>;
export const RadioGroup = RadioGroupPrimitive.Root;
export type RadioGroupItemProps = React.ComponentPropsWithoutRef<typeof RadioGroupPrimitive.Item>;
export const RadioGroupItem = React.forwardRef<
  React.ElementRef<typeof RadioGroupPrimitive.Item>,
  RadioGroupItemProps
>(({ className, ...props }, ref) => (
  <RadioGroupPrimitive.Item
    ref={ref}
    className={cn(
      "border-input focus-visible:ring-ring grid size-5 place-items-center rounded-full border focus-visible:ring-2 focus-visible:outline-none disabled:opacity-50",
      className,
    )}
    {...props}
  >
    <RadioGroupPrimitive.Indicator className="bg-primary size-2.5 rounded-full" />
  </RadioGroupPrimitive.Item>
));
RadioGroupItem.displayName = "RadioGroupItem";

export type SelectProps = React.ComponentPropsWithoutRef<typeof SelectPrimitive.Root>;
export const Select = SelectPrimitive.Root;
export const SelectValue = SelectPrimitive.Value;
export type SelectTriggerProps = React.ComponentPropsWithoutRef<typeof SelectPrimitive.Trigger>;
export const SelectTrigger = React.forwardRef<
  React.ElementRef<typeof SelectPrimitive.Trigger>,
  SelectTriggerProps
>(({ className, children, ...props }, ref) => (
  <SelectPrimitive.Trigger
    ref={ref}
    className={cn(
      "border-input bg-background focus-visible:ring-ring flex min-h-9 w-full items-center justify-between rounded-md border px-3 text-sm focus-visible:ring-2 focus-visible:outline-none disabled:opacity-50",
      className,
    )}
    {...props}
  >
    {children}
    <SelectPrimitive.Icon>
      <ChevronDown className="size-4" aria-hidden="true" />
    </SelectPrimitive.Icon>
  </SelectPrimitive.Trigger>
));
SelectTrigger.displayName = "SelectTrigger";
export type SelectContentProps = React.ComponentPropsWithoutRef<typeof SelectPrimitive.Content>;
export const SelectContent = React.forwardRef<
  React.ElementRef<typeof SelectPrimitive.Content>,
  SelectContentProps
>(({ className, children, position = "popper", ...props }, ref) => (
  <SelectPrimitive.Portal>
    <SelectPrimitive.Content
      ref={ref}
      position={position}
      className={cn(
        "bg-popover text-popover-foreground shadow-popover data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:animate-in data-[state=open]:fade-in-0 data-[state=open]:zoom-in-95 z-50 max-h-90 min-w-45 overflow-auto rounded-lg border p-1 motion-reduce:animate-none",
        className,
      )}
      {...props}
    >
      <SelectPrimitive.Viewport>{children}</SelectPrimitive.Viewport>
    </SelectPrimitive.Content>
  </SelectPrimitive.Portal>
));
SelectContent.displayName = "SelectContent";
export type SelectItemProps = React.ComponentPropsWithoutRef<typeof SelectPrimitive.Item>;
export const SelectItem = React.forwardRef<
  React.ElementRef<typeof SelectPrimitive.Item>,
  SelectItemProps
>(({ className, children, ...props }, ref) => (
  <SelectPrimitive.Item
    ref={ref}
    className={cn(
      "focus:bg-accent relative flex min-h-9 cursor-default items-center rounded-md py-2 pr-8 pl-3 text-sm outline-none select-none data-[disabled]:opacity-50",
      className,
    )}
    {...props}
  >
    <SelectPrimitive.ItemText>{children}</SelectPrimitive.ItemText>
    <SelectPrimitive.ItemIndicator className="absolute right-2">
      <Check className="size-4" />
    </SelectPrimitive.ItemIndicator>
  </SelectPrimitive.Item>
));
SelectItem.displayName = "SelectItem";

export const badgeVariants = cva(
  "inline-flex items-center gap-1 rounded px-2 py-0.5 text-xs font-semibold",
  {
    variants: {
      variant: {
        neutral: "bg-muted text-muted-foreground",
        info: "bg-info/15 text-info",
        success: "bg-success/15 text-success",
        warning: "bg-warning/15 text-warning",
        danger: "bg-destructive/15 text-destructive",
      },
    },
    defaultVariants: { variant: "neutral" },
  },
);
export type BadgeProps = React.HTMLAttributes<HTMLSpanElement> & VariantProps<typeof badgeVariants>;
export function Badge({ className, variant, ...props }: BadgeProps): React.JSX.Element {
  return <span className={cn(badgeVariants({ variant }), className)} {...props} />;
}

export type AvatarProps = React.ComponentPropsWithoutRef<typeof AvatarPrimitive.Root> & {
  src?: string;
  alt: string;
  fallback?: string;
  size?: "sm" | "md" | "lg";
};
export function Avatar({
  src,
  alt,
  fallback,
  size = "md",
  className,
  ...props
}: AvatarProps): React.JSX.Element {
  return (
    <AvatarPrimitive.Root
      className={cn(
        "bg-muted inline-flex shrink-0 overflow-hidden rounded-full",
        size === "sm" && "size-6",
        size === "md" && "size-8",
        size === "lg" && "size-10",
        className,
      )}
      {...props}
    >
      <AvatarPrimitive.Image src={src} alt={alt} className="size-full object-cover" />
      <AvatarPrimitive.Fallback
        className="grid size-full place-items-center text-xs font-semibold"
        aria-label={alt}
      >
        {fallback ?? alt.slice(0, 2).toUpperCase()}
      </AvatarPrimitive.Fallback>
    </AvatarPrimitive.Root>
  );
}

export type SeparatorProps = React.HTMLAttributes<HTMLHRElement> & {
  orientation?: "horizontal" | "vertical";
};
export function Separator({
  orientation = "horizontal",
  className,
  ...props
}: SeparatorProps): React.JSX.Element {
  return (
    <hr
      aria-orientation={orientation}
      className={cn(
        "bg-border shrink-0 border-0",
        orientation === "horizontal" ? "h-px w-full" : "h-full w-px",
        className,
      )}
      {...props}
    />
  );
}
