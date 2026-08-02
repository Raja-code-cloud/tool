/** Enforceable upper bounds for free-text wizard inputs (mirrored server-side when APIs connect). */
export const INPUT_LIMITS = {
  projectName: 200,
  description: 2_000,
  tags: 500,
  articleContent: 50_000,
} as const;

export type InputLimitKey = keyof typeof INPUT_LIMITS;

export function truncateToLimit(value: string, key: InputLimitKey): string {
  return value.slice(0, INPUT_LIMITS[key]);
}

export function isWithinLimit(value: string, key: InputLimitKey): boolean {
  return value.length <= INPUT_LIMITS[key];
}

export function limitExceededMessage(key: InputLimitKey): string {
  const labels: Record<InputLimitKey, string> = {
    projectName: "Project name",
    description: "Description",
    tags: "Tags",
    articleContent: "Article content",
  };
  return `${labels[key]} must be ${INPUT_LIMITS[key].toLocaleString()} characters or fewer.`;
}
