"use client";

import { Label, Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui";
import { cn } from "@/lib/utils/cn";

export type SelectOption = { readonly value: string; readonly label: string };

export type SelectFieldProps = {
  id: string;
  label: string;
  description?: string;
  value: string;
  options: readonly SelectOption[];
  onValueChange: (value: string) => void;
  /** Set when an enclosing row already renders a `<label for>` for this id. */
  hasExternalLabel?: boolean;
  className?: string;
};

/**
 * Labelled select. `FormField` attaches its id by cloning the child, which a
 * Radix Select root cannot receive, so the id must live on the trigger.
 */
export function SelectField({ id, label, description, value, options, onValueChange, hasExternalLabel = false, className }: SelectFieldProps): React.JSX.Element {
  const descriptionId = description ? `${id}-description` : undefined;

  return (
    <div className={cn("grid gap-1.5", className)}>
      {!hasExternalLabel && <Label htmlFor={id}>{label}</Label>}
      <Select value={value} onValueChange={onValueChange}>
        <SelectTrigger id={id} {...(descriptionId ? { "aria-describedby": descriptionId } : {})}>
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          {options.map((option) => <SelectItem key={option.value} value={option.value}>{option.label}</SelectItem>)}
        </SelectContent>
      </Select>
      {description && <p id={descriptionId} className="text-xs text-muted-foreground">{description}</p>}
    </div>
  );
}
