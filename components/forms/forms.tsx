import { cloneElement, forwardRef } from "react";
import type { HTMLAttributes, ReactElement, ReactNode } from "react";

import { cn } from "../../lib/utils/cn";
import { Label } from "../ui";

export type FormFieldProps = HTMLAttributes<HTMLDivElement> & {
  id: string;
  label: string;
  isRequired?: boolean;
  description?: string;
  error?: string;
  children: ReactElement<Record<string, unknown>>;
};
export function FormField({
  id,
  label,
  isRequired = false,
  description,
  error,
  children,
  className,
  ...props
}: FormFieldProps): React.JSX.Element {
  const descriptionId = description ? `${id}-description` : undefined;
  const errorId = error ? `${id}-error` : undefined;
  return (
    <div className={cn("grid gap-1.5", className)} {...props}>
      <Label htmlFor={id}>
        {label}
        {isRequired && <span className="text-muted-foreground ml-1">(required)</span>}
      </Label>
      {cloneElement(children, {
        id,
        "aria-describedby": [descriptionId, errorId].filter(Boolean).join(" ") || undefined,
        "aria-invalid": error ? true : undefined,
        "aria-required": isRequired || undefined,
      })}
      {description && (
        <p id={descriptionId} className="text-muted-foreground text-xs">
          {description}
        </p>
      )}
      {error && (
        <p id={errorId} role="alert" className="text-destructive text-xs">
          {error}
        </p>
      )}
    </div>
  );
}

export type CharacterCountProps = HTMLAttributes<HTMLOutputElement> & {
  current: number;
  maximum: number;
};
export function CharacterCount({
  current,
  maximum,
  className,
  ...props
}: CharacterCountProps): React.JSX.Element {
  const ratio = maximum > 0 ? current / maximum : 0;
  return (
    <output
      className={cn(
        "text-muted-foreground text-xs tabular-nums",
        ratio >= 1 && "text-destructive font-semibold",
        ratio >= 0.85 && ratio < 1 && "text-warning",
        className,
      )}
      aria-live="polite"
      {...props}
    >
      {current}/{maximum}
    </output>
  );
}

export type FormError = { id: string; message: string };
export type FormErrorSummaryProps = HTMLAttributes<HTMLDivElement> & {
  title?: string;
  errors: readonly FormError[];
  action?: ReactNode;
};
export const FormErrorSummary = forwardRef<HTMLDivElement, FormErrorSummaryProps>(
  function FormErrorSummary(
    { title = "Please fix the following", errors, action, className, ...props },
    ref,
  ) {
    if (errors.length === 0) return <></>;
    return (
      <div
        ref={ref}
        role="alert"
        tabIndex={-1}
        className={cn("border-destructive bg-destructive/10 rounded-lg border p-4", className)}
        {...props}
      >
        <h2 className="font-semibold">{title}</h2>
        <ul className="mt-2 list-disc pl-5 text-sm">
          {errors.map((error) => (
            <li key={error.id}>
              <a className="underline" href={`#${error.id}`}>
                {error.message}
              </a>
            </li>
          ))}
        </ul>
        {action}
      </div>
    );
  },
);
