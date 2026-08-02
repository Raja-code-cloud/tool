"use client";

import {
  AlertTriangle,
  CheckCircle2,
  Clock,
  Link2,
  Link2Off,
  ShieldAlert,
  XCircle,
} from "lucide-react";

import { StatusBadge } from "@/components/feedback";
import type { ConnectionStatus, HealthStatus, TokenStatus } from "@/lib/domain/social-account";

export function ConnectionStatusBadge({ status }: { status: ConnectionStatus }): React.JSX.Element {
  const connected = status === "connected";
  return (
    <StatusBadge variant={connected ? "success" : "neutral"}>
      {connected ? (
        <Link2 className="size-3" aria-hidden="true" />
      ) : (
        <Link2Off className="size-3" aria-hidden="true" />
      )}
      {connected ? "Connected" : "Disconnected"}
    </StatusBadge>
  );
}

const HEALTH_CONFIG: Record<
  HealthStatus,
  { variant: "success" | "warning" | "danger" | "info"; label: string; icon: typeof CheckCircle2 }
> = {
  healthy: { variant: "success", label: "Healthy", icon: CheckCircle2 },
  warning: { variant: "warning", label: "Warning", icon: AlertTriangle },
  error: { variant: "danger", label: "Error", icon: XCircle },
  needs_reauth: { variant: "danger", label: "Needs reauthentication", icon: ShieldAlert },
};

export function HealthStatusBadge({ status }: { status: HealthStatus }): React.JSX.Element {
  const config = HEALTH_CONFIG[status];
  const Icon = config.icon;
  return (
    <StatusBadge variant={config.variant}>
      <Icon className="size-3" aria-hidden="true" />
      {config.label}
    </StatusBadge>
  );
}

const TOKEN_CONFIG: Record<
  TokenStatus,
  { variant: "success" | "warning" | "danger" | "info"; label: string }
> = {
  active: { variant: "success", label: "Active" },
  expiring_soon: { variant: "warning", label: "Expiring soon" },
  expired: { variant: "danger", label: "Expired" },
  renew_required: { variant: "danger", label: "Renew required" },
};

export function TokenStatusBadge({ status }: { status: TokenStatus }): React.JSX.Element {
  const config = TOKEN_CONFIG[status];
  return (
    <StatusBadge variant={config.variant}>
      <Clock className="size-3" aria-hidden="true" />
      {config.label}
    </StatusBadge>
  );
}
