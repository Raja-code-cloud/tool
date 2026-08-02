export type PlatformId = "linkedin" | "facebook" | "instagram" | "x" | "medium" | "youtube";

export type PlatformVisual = {
  readonly id: PlatformId;
  readonly label: string;
  readonly color: string;
  readonly bgClass: string;
  readonly borderClass: string;
  readonly textClass: string;
};
