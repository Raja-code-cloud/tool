import { Check, Copy } from "lucide-react";
import * as React from "react";
import type { ReactNode } from "react";

import { cn } from "../../lib/utils/cn";
import { Button, type ButtonProps } from "../ui";

export type ActionButtonProps = ButtonProps & { leadingIcon?: ReactNode; trailingIcon?: ReactNode };
export function ActionButton({
  leadingIcon,
  trailingIcon,
  children,
  className,
  ...props
}: ActionButtonProps): React.JSX.Element {
  return (
    <Button className={cn("whitespace-nowrap", className)} {...props}>
      {leadingIcon && <span aria-hidden="true">{leadingIcon}</span>}
      {children}
      {trailingIcon && <span aria-hidden="true">{trailingIcon}</span>}
    </Button>
  );
}

export type IconButtonProps = Omit<ButtonProps, "children" | "variant"> & {
  label: string;
  icon: ReactNode;
};
export function IconButton({
  label,
  icon,
  className,
  ...props
}: IconButtonProps): React.JSX.Element {
  return (
    <Button
      variant="icon"
      className={cn("size-11 p-0 sm:size-9", className)}
      aria-label={label}
      title={label}
      {...props}
    >
      {icon}
    </Button>
  );
}

export type PrimaryButtonProps = ButtonProps;
export function PrimaryButton(props: PrimaryButtonProps): React.JSX.Element {
  return <Button variant="primary" {...props} />;
}
export type SecondaryButtonProps = ButtonProps;
export function SecondaryButton(props: SecondaryButtonProps): React.JSX.Element {
  return <Button variant="secondary" {...props} />;
}
export type OutlineButtonProps = ButtonProps;
export function OutlineButton(props: OutlineButtonProps): React.JSX.Element {
  return <Button variant="outline" {...props} />;
}
export type DestructiveButtonProps = ButtonProps;
export function DestructiveButton(props: DestructiveButtonProps): React.JSX.Element {
  return <Button variant="destructive" {...props} />;
}

export type CopyButtonProps = Omit<IconButtonProps, "icon" | "label" | "onClick"> & {
  value: string;
  label?: string;
  onCopied?: () => void;
};
export function CopyButton({
  value,
  label = "Copy to clipboard",
  onCopied,
  ...props
}: CopyButtonProps): React.JSX.Element {
  const [isCopied, setIsCopied] = React.useState(false);
  const handleCopy = async (): Promise<void> => {
    await navigator.clipboard.writeText(value);
    setIsCopied(true);
    onCopied?.();
    window.setTimeout(() => setIsCopied(false), 1500);
  };
  return (
    <IconButton
      label={isCopied ? "Copied" : label}
      icon={isCopied ? <Check aria-hidden="true" /> : <Copy aria-hidden="true" />}
      onClick={() => void handleCopy()}
      {...props}
    />
  );
}
