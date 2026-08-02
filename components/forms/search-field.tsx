import { Search } from "lucide-react";
import type { InputHTMLAttributes } from "react";

import { Input } from "@/components/ui";
import { cn } from "@/lib/utils/cn";

export type SearchFieldProps = InputHTMLAttributes<HTMLInputElement> & {
  label?: string;
  inputClassName?: string;
};

export function SearchField({
  label = "Search",
  className,
  inputClassName,
  ...props
}: SearchFieldProps): React.JSX.Element {
  return (
    <label className={cn("relative block", className)}>
      <span className="sr-only">{label}</span>
      <Search
        className="text-muted-foreground pointer-events-none absolute top-1/2 left-3 size-4 -translate-y-1/2"
        aria-hidden="true"
      />
      <Input type="search" className={cn("pl-9", inputClassName)} {...props} />
    </label>
  );
}

export const SearchInput = SearchField;
export const SearchBar = SearchField;
export type SearchInputProps = SearchFieldProps;
export type SearchBarProps = SearchFieldProps;
