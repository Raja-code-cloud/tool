import type { RequestHandler } from "msw";

/**
 * Shared default handlers. Keep feature-specific handlers close to their tests
 * and register them with server.use() so global behavior stays predictable.
 */
export const handlers: RequestHandler[] = [];
