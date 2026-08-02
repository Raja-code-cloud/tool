import { cloneElement } from "react";
import type { HTMLAttributes, InputHTMLAttributes, ReactElement, ReactNode } from "react";
import { Search } from "lucide-react";

import { cn } from "../../lib/utils/cn";
import { Input, Label } from "../ui";

export type FormFieldProps = HTMLAttributes<HTMLDivElement> & {
  id: string;
  label: string;
  isRequired?: boolean;
  description?: string;
  error?: string;
  children: ReactElement<Record<string, unknown>>;
};
export function FormField({ id, label, isRequired = false, description, error, children, className, ...props }: FormFieldProps): React.JSX.Element {
  const descriptionId = description ? `${id}-description` : undefined;
  const errorId = error ? `${id}-error` : undefined;
  return <div className={cn("grid gap-1.5", className)} {...props}>
    <Label htmlFor={id}>{label}{isRequired && <span className="ml-1 text-muted-foreground">(required)</span>}</Label>
    {cloneElement(children, {
      id,
      "aria-describedby": [descriptionId, errorId].filter(Boolean).join(" ") || undefined,
      "aria-invalid": error ? true : undefined,
      "aria-required": isRequired || undefined,
    })}
    {description && <p id={descriptionId} className="text-xs text-muted-foreground">{description}</p>}
    {error && <p id={errorId} role="alert" className="text-xs text-destructive">{error}</p>}
  </div>;
}

export type SearchInputProps = InputHTMLAttributes<HTMLInputElement> & { label?: string };
export function SearchInput({ label = "Search", className, ...props }: SearchInputProps): React.JSX.Element {
  return <label className={cn("relative block", className)}><span className="sr-only">{label}</span><Search className="pointer-events-none absolute top-1/2 left-3 size-4 -translate-y-1/2 text-muted-foreground" aria-hidden="true" /><Input type="search" className="pl-9" {...props} /></label>;
}

export type CharacterCountProps = HTMLAttributes<HTMLOutputElement> & { current: number; maximum: number };
export function CharacterCount({ current, maximum, className, ...props }: CharacterCountProps): React.JSX.Element {
  const ratio = maximum > 0 ? current / maximum : 0;
  return <output className={cn("text-xs tabular-nums text-muted-foreground", ratio >= 1 && "font-semibold text-destructive", ratio >= 0.85 && ratio < 1 && "text-warning", className)} aria-live="polite" {...props}>{current}/{maximum}</output>;
}

export type FormError = { id: string; message: string };
export type FormErrorSummaryProps = HTMLAttributes<HTMLDivElement> & { title?: string; errors: readonly FormError[]; action?: ReactNode };
export function FormErrorSummary({ title = "Please fix the following", errors, action, className, ...props }: FormErrorSummaryProps): React.JSX.Element {
  if (errors.length === 0) return <></>;
  return <div role="alert" tabIndex={-1} className={cn("rounded-lg border border-destructive bg-destructive/10 p-4", className)} {...props}><h2 className="font-semibold">{title}</h2><ul className="mt-2 list-disc pl-5 text-sm">{errors.map((error) => <li key={error.id}><a className="underline" href={`#${error.id}`}>{error.message}</a></li>)}</ul>{action}</div>;
}
