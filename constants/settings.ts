export const SETTINGS_SECTIONS = [
  { id: "profile", label: "Profile" },
  { id: "appearance", label: "Appearance" },
  { id: "notifications", label: "Notifications" },
  { id: "ai-providers", label: "AI Providers" },
  { id: "storage", label: "Storage" },
  { id: "publishing", label: "Publishing" },
  { id: "security", label: "Security" },
  { id: "api-keys", label: "API Keys" },
  { id: "danger-zone", label: "Danger Zone" },
] as const;

export type SettingsSectionId = (typeof SETTINGS_SECTIONS)[number]["id"];

/* -------------------------------------------------------------------------
   Mock data. Every value below is replaced by the settings service later.
   ------------------------------------------------------------------------- */

export const PROFILE_DEFAULTS = {
  fullName: "Aarav Mehta",
  email: "aarav.mehta@northwind.io",
  jobTitle: "Head of Content",
  bio: "Leading omni-channel content operations for the Northwind brand portfolio.",
  timezone: "Asia/Kolkata",
  language: "en-GB",
} as const;

export const TIMEZONES = [
  { value: "Asia/Kolkata", label: "(GMT+05:30) India Standard Time" },
  { value: "Europe/London", label: "(GMT+00:00) Greenwich Mean Time" },
  { value: "America/New_York", label: "(GMT-05:00) Eastern Time" },
  { value: "America/Los_Angeles", label: "(GMT-08:00) Pacific Time" },
  { value: "Australia/Sydney", label: "(GMT+11:00) Australian Eastern Time" },
] as const;

export const LANGUAGES = [
  { value: "en-GB", label: "English (United Kingdom)" },
  { value: "en-US", label: "English (United States)" },
  { value: "de-DE", label: "German" },
  { value: "ja-JP", label: "Japanese" },
] as const;

export const DENSITY_OPTIONS = [
  { value: "comfortable", label: "Comfortable", description: "Roomier spacing across tables and lists." },
  { value: "compact", label: "Compact", description: "Fits more rows on screen." },
] as const;

export type NotificationChannelId = "publishing" | "ai" | "collaboration" | "billing" | "product";

export type NotificationPreference = {
  readonly id: NotificationChannelId;
  readonly label: string;
  readonly description: string;
  readonly email: boolean;
  readonly inApp: boolean;
};

export const NOTIFICATION_PREFERENCES: readonly NotificationPreference[] = [
  { id: "publishing", label: "Publishing activity", description: "Posts published, failed, or awaiting approval.", email: true, inApp: true },
  { id: "ai", label: "AI generation", description: "Completed generations and quota warnings.", email: false, inApp: true },
  { id: "collaboration", label: "Collaboration", description: "Mentions, comments, and review requests.", email: true, inApp: true },
  { id: "billing", label: "Billing", description: "Invoices, plan changes, and payment failures.", email: true, inApp: false },
  { id: "product", label: "Product updates", description: "New features and monthly changelog digest.", email: false, inApp: false },
];

export type AiProviderStatus = "connected" | "disconnected" | "error";

export type AiProvider = {
  readonly id: string;
  readonly name: string;
  readonly model: string;
  readonly status: AiProviderStatus;
  readonly monthlyTokens: number;
  readonly isDefault: boolean;
};

export const AI_PROVIDERS: readonly AiProvider[] = [
  { id: "openai", name: "OpenAI", model: "gpt-4.1", status: "connected", monthlyTokens: 4_820_000, isDefault: true },
  { id: "anthropic", name: "Anthropic", model: "claude-sonnet-4", status: "connected", monthlyTokens: 1_240_000, isDefault: false },
  { id: "google", name: "Google Vertex AI", model: "gemini-2.0-pro", status: "error", monthlyTokens: 96_000, isDefault: false },
  { id: "azure", name: "Azure OpenAI", model: "Not configured", status: "disconnected", monthlyTokens: 0, isDefault: false },
];

export const STORAGE_USAGE = {
  usedBytes: 412_316_860_416,
  totalBytes: 1_099_511_627_776,
  breakdown: [
    { id: "video", label: "Video", bytes: 268_435_456_000 },
    { id: "images", label: "Images", bytes: 96_636_764_160 },
    { id: "documents", label: "Documents", bytes: 32_212_254_720 },
    { id: "archives", label: "Archives", bytes: 15_032_385_536 },
  ],
  region: "ap-south-1",
} as const;

export const STORAGE_REGIONS = [
  { value: "ap-south-1", label: "Asia Pacific (Mumbai)" },
  { value: "eu-west-1", label: "Europe (Ireland)" },
  { value: "us-east-1", label: "US East (N. Virginia)" },
] as const;

export const RETENTION_OPTIONS = [
  { value: "90", label: "90 days" },
  { value: "365", label: "1 year" },
  { value: "1095", label: "3 years" },
  { value: "forever", label: "Keep forever" },
] as const;

export const PUBLISHING_DEFAULTS = {
  defaultTimezone: "Asia/Kolkata",
  autoQueue: true,
  requireApproval: true,
  appendUtm: true,
  retryFailed: true,
  dailyLimit: "12",
} as const;

export const APPROVAL_ROLES = [
  { value: "admin", label: "Workspace admins only" },
  { value: "editor", label: "Admins and editors" },
  { value: "anyone", label: "Any member" },
] as const;

export type SessionRecord = {
  readonly id: string;
  readonly device: string;
  readonly location: string;
  readonly lastActive: string;
  readonly isCurrent: boolean;
};

export const ACTIVE_SESSIONS: readonly SessionRecord[] = [
  { id: "s-1", device: "Chrome on Windows", location: "Pune, IN", lastActive: "2026-08-02T07:40:00.000Z", isCurrent: true },
  { id: "s-2", device: "Safari on macOS", location: "Bengaluru, IN", lastActive: "2026-08-01T16:12:00.000Z", isCurrent: false },
  { id: "s-3", device: "CCH AI iOS app", location: "Mumbai, IN", lastActive: "2026-07-30T09:05:00.000Z", isCurrent: false },
];

export type ApiKeyScope = "read" | "write" | "admin";

export type ApiKeyRecord = {
  readonly id: string;
  readonly label: string;
  readonly maskedKey: string;
  readonly scope: ApiKeyScope;
  readonly createdAt: string;
  readonly lastUsedAt: string | null;
};

export const API_KEYS: readonly ApiKeyRecord[] = [
  { id: "k-1", label: "Production publisher", maskedKey: "cch_live_••••••••••••4f2a", scope: "write", createdAt: "2026-02-14T10:00:00.000Z", lastUsedAt: "2026-08-02T06:55:00.000Z" },
  { id: "k-2", label: "Analytics export", maskedKey: "cch_live_••••••••••••91c7", scope: "read", createdAt: "2026-05-03T10:00:00.000Z", lastUsedAt: "2026-07-29T22:10:00.000Z" },
  { id: "k-3", label: "Staging sandbox", maskedKey: "cch_test_••••••••••••0b38", scope: "admin", createdAt: "2026-06-21T10:00:00.000Z", lastUsedAt: null },
];
