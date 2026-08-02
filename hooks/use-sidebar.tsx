"use client";

import * as React from "react";

export type SidebarContextValue = {
  isOpen: boolean;
  isCollapsed: boolean;
  open: () => void;
  close: () => void;
  toggle: () => void;
  toggleCollapsed: () => void;
};
export type SidebarProviderProps = { children: React.ReactNode; defaultCollapsed?: boolean };

const SidebarContext = React.createContext<SidebarContextValue | null>(null);

export function SidebarProvider({ children, defaultCollapsed = false }: SidebarProviderProps): React.JSX.Element {
  const [isOpen, setIsOpen] = React.useState(false);
  const [isCollapsed, setIsCollapsed] = React.useState(defaultCollapsed);
  const value: SidebarContextValue = {
    isOpen,
    isCollapsed,
    open: () => setIsOpen(true),
    close: () => setIsOpen(false),
    toggle: () => setIsOpen((current) => !current),
    toggleCollapsed: () => setIsCollapsed((current) => !current),
  };
  return <SidebarContext.Provider value={value}>{children}</SidebarContext.Provider>;
}

export function useSidebar(): SidebarContextValue {
  const value = React.useContext(SidebarContext);
  if (!value) throw new Error("useSidebar must be used within SidebarProvider.");
  return value;
}
