"use client";

import { X } from "lucide-react";
import type { HTMLAttributes, ReactNode } from "react";

import { StatusBadge, type StatusBadgeProps } from "@/components/feedback";
import { SearchField, type SearchFieldProps } from "@/components/forms";
import {
  Button,
  Label,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui";
import { cn } from "@/lib/utils/cn";

export type FilterOption = {
  readonly value: string;
  readonly label: string;
  readonly disabled?: boolean;
};

export type FilterBarProps = HTMLAttributes<HTMLElement> & { label?: string };
export function FilterBar({
  label = "Filters",
  className,
  ...props
}: FilterBarProps): React.JSX.Element {
  return (
    <section
      aria-label={label}
      className={cn(
        "tablet:flex-row tablet:flex-wrap tablet:items-center flex flex-col gap-3",
        className,
      )}
      {...props}
    />
  );
}

export type FilterGroupProps = HTMLAttributes<HTMLDivElement> & { label?: string };
export function FilterGroup({ label, className, ...props }: FilterGroupProps): React.JSX.Element {
  return (
    <div
      role="group"
      aria-label={label}
      className={cn("flex flex-wrap items-center gap-2", className)}
      {...props}
    />
  );
}

export type FilterSelectProps = {
  id: string;
  label: string;
  value: string;
  options: readonly FilterOption[];
  onValueChange: (value: string) => void;
  placeholder?: string;
  className?: string;
  triggerClassName?: string;
};
export function FilterSelect({
  id,
  label,
  value,
  options,
  onValueChange,
  placeholder,
  className,
  triggerClassName,
}: FilterSelectProps): React.JSX.Element {
  return (
    <div className={cn("grid gap-1", className)}>
      <Label htmlFor={id} className="sr-only">
        {label}
      </Label>
      <Select value={value} onValueChange={onValueChange}>
        <SelectTrigger id={id} aria-label={label} className={triggerClassName}>
          <SelectValue placeholder={placeholder} />
        </SelectTrigger>
        <SelectContent>
          {options.map((option) => (
            <SelectItem
              key={option.value}
              value={option.value}
              {...(option.disabled !== undefined ? { disabled: option.disabled } : {})}
            >
              {option.label}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}

export type FilterSearchProps = SearchFieldProps;
export function FilterSearch(props: FilterSearchProps): React.JSX.Element {
  return <SearchField {...props} />;
}

export type FilterChipProps = Omit<StatusBadgeProps, "label"> & {
  label: ReactNode;
  onRemove?: () => void;
  removeLabel?: string;
};
export function FilterChip({
  label,
  onRemove,
  removeLabel = "Remove filter",
  children,
  ...props
}: FilterChipProps): React.JSX.Element {
  return (
    <StatusBadge {...props}>
      {children ?? label}
      {onRemove && (
        <Button
          type="button"
          variant="icon"
          className="-mr-1 size-5 min-h-0 p-0"
          aria-label={removeLabel}
          onClick={onRemove}
        >
          <X className="size-3" aria-hidden="true" />
        </Button>
      )}
    </StatusBadge>
  );
}
