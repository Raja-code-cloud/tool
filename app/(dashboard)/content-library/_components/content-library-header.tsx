"use client";

import { Download, MoreHorizontal, Upload } from "lucide-react";
import Link from "next/link";

import { PrimaryButton, SecondaryButton } from "@/components/buttons";
import { PageHeader } from "@/components/layout";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui";
import { ROUTES } from "@/constants/navigation";

export function ContentLibraryHeader(): React.JSX.Element {
  return (
    <PageHeader
      title="Content Library"
      description="Manage all your content assets from one place."
      actions={
        <div className="flex flex-wrap items-center gap-2">
          <SecondaryButton size="compact">Import</SecondaryButton>
          <SecondaryButton size="compact">
            <Download className="size-4" aria-hidden="true" />
            Export
          </SecondaryButton>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <SecondaryButton size="compact">
                <MoreHorizontal className="size-4" aria-hidden="true" />
                Bulk actions
              </SecondaryButton>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem>Tag selected</DropdownMenuItem>
              <DropdownMenuItem>Move to archive</DropdownMenuItem>
              <DropdownMenuItem>Schedule selected</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
          <PrimaryButton asChild size="compact">
            <Link href={ROUTES.upload}>
              <Upload className="size-4" aria-hidden="true" />
              Upload content
            </Link>
          </PrimaryButton>
        </div>
      }
    />
  );
}
