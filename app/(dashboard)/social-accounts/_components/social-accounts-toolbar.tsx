"use client";

import { Link2, RefreshCw, Unplug } from "lucide-react";

import { PrimaryButton, SecondaryButton } from "@/components/buttons";
import { Toolbar } from "@/components/common";
import { NoContent } from "@/components/feedback";
import { FilterGroup, FilterSearch, FilterSelect } from "@/components/filters";
import { SOCIAL_ACCOUNT_FILTERS } from "@/lib/config/social-accounts";
import type { SocialAccountFilter } from "@/lib/domain/social-account";

export type SocialAccountsToolbarProps = {
  search: string;
  onSearchChange: (value: string) => void;
  filter: SocialAccountFilter;
  onFilterChange: (filter: SocialAccountFilter) => void;
  onConnect: () => void;
  onRefresh: () => void;
  isRefreshing: boolean;
};

export function SocialAccountsToolbar({
  search,
  onSearchChange,
  filter,
  onFilterChange,
  onConnect,
  onRefresh,
  isRefreshing,
}: SocialAccountsToolbarProps): React.JSX.Element {
  return (
    <div className="bg-card rounded-xl border p-4">
      <Toolbar
        label="Social accounts controls"
        className="flex-col gap-3 sm:flex-row sm:items-center sm:justify-between"
      >
        <div className="flex flex-wrap gap-2">
          <PrimaryButton type="button" onClick={onConnect}>
            <Link2 className="size-4" aria-hidden="true" /> Connect account
          </PrimaryButton>
          <SecondaryButton type="button" onClick={onRefresh} disabled={isRefreshing}>
            <RefreshCw
              className={`size-4 ${isRefreshing ? "animate-spin" : ""}`}
              aria-hidden="true"
            />{" "}
            Refresh connections
          </SecondaryButton>
        </div>
      </Toolbar>
      <FilterGroup label="Social account filter values" className="mt-3 grid gap-3 sm:grid-cols-2">
        <FilterSearch
          placeholder="Search platforms or accounts…"
          value={search}
          onChange={(event) => onSearchChange(event.target.value)}
          aria-label="Search social accounts"
        />
        <FilterSelect
          id="social-account-filter"
          label="Filter accounts"
          value={filter}
          options={SOCIAL_ACCOUNT_FILTERS}
          onValueChange={(value) => onFilterChange(value as SocialAccountFilter)}
        />
      </FilterGroup>
    </div>
  );
}

export function SocialAccountsEmptyState({
  onConnect,
}: {
  onConnect: () => void;
}): React.JSX.Element {
  return (
    <NoContent
      icon={<Unplug aria-hidden="true" />}
      title="No accounts connected"
      description="Connect your first platform to start publishing content across channels."
      action={
        <PrimaryButton type="button" onClick={onConnect}>
          <Link2 className="size-4" aria-hidden="true" /> Connect your first platform
        </PrimaryButton>
      }
    />
  );
}
