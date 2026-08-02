export const WORKSPACE = {
  name: "Cloud Content Hub AI",
  shortName: "CCH AI",
  description: "Plan, generate, schedule, and analyse omni-channel content from a single AI-native workspace.",
} as const;

export type WorkspaceUser = {
  readonly name: string;
  readonly email: string;
  readonly role: string;
};

/** Mock session. Replaced by the auth provider in a later milestone. */
export const CURRENT_USER: WorkspaceUser = {
  name: "Aarav Mehta",
  email: "aarav.mehta@northwind.io",
  role: "Workspace Admin",
};

/** Mock badge count. Replaced by the notifications service in a later milestone. */
export const UNREAD_NOTIFICATION_COUNT = 3;
