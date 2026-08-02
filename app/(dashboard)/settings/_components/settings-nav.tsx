"use client";

import * as React from "react";

import { SETTINGS_SECTIONS } from "@/constants/settings";
import { cn } from "@/lib/utils/cn";

const FIRST_SECTION_ID = SETTINGS_SECTIONS[0].id;

/**
 * In-page section jump list. Anchors keep it deep-linkable and functional
 * without JavaScript; an IntersectionObserver adds active highlighting on top.
 */
export function SettingsNav(): React.JSX.Element {
  const [activeId, setActiveId] = React.useState<string>(FIRST_SECTION_ID);

  React.useEffect(() => {
    const sections = SETTINGS_SECTIONS.map(({ id }) => document.getElementById(id)).filter(
      (element): element is HTMLElement => element !== null,
    );
    if (sections.length === 0) return;

    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((entry) => entry.isIntersecting)
          .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top);
        if (visible[0]) setActiveId(visible[0].target.id);
      },
      // Bias the viewport towards the top so the heading nearest the sticky
      // header wins rather than whichever section is largest.
      { rootMargin: "-25% 0px -65% 0px", threshold: 0 },
    );

    sections.forEach((section) => observer.observe(section));
    return () => observer.disconnect();
  }, []);

  return (
    <nav aria-label="Settings sections" className="desktop:sticky desktop:top-20">
      <ul className="desktop:grid desktop:overflow-visible desktop:pb-0 flex scrollbar-thin gap-1 overflow-x-auto pb-2">
        {SETTINGS_SECTIONS.map((section) => {
          const isActive = section.id === activeId;
          return (
            <li key={section.id}>
              <a
                href={`#${section.id}`}
                aria-current={isActive ? "true" : undefined}
                className={cn(
                  "hover:bg-accent hover:text-foreground focus-visible:ring-ring block min-h-9 shrink-0 rounded-md px-3 py-2 text-sm font-medium whitespace-nowrap transition-colors duration-(--duration-fast) focus-visible:ring-2 focus-visible:outline-none",
                  isActive ? "bg-accent text-foreground font-semibold" : "text-muted-foreground",
                )}
              >
                {section.label}
              </a>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
