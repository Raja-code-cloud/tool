import { ApiError } from "@/lib/api/errors";
import type { ApiRequestConfig, ApiResponse } from "@/lib/api/types";
import { getAccessToken, getCsrfToken } from "@/lib/auth/token-store";

export interface ApiClient {
  request<T>(path: string, config?: ApiRequestConfig): Promise<ApiResponse<T>>;
  get<T>(path: string, config?: Omit<ApiRequestConfig, "method" | "body">): Promise<ApiResponse<T>>;
  post<T>(
    path: string,
    body?: unknown,
    config?: Omit<ApiRequestConfig, "method" | "body">,
  ): Promise<ApiResponse<T>>;
  put<T>(
    path: string,
    body?: unknown,
    config?: Omit<ApiRequestConfig, "method" | "body">,
  ): Promise<ApiResponse<T>>;
  patch<T>(
    path: string,
    body?: unknown,
    config?: Omit<ApiRequestConfig, "method" | "body">,
  ): Promise<ApiResponse<T>>;
  delete<T>(
    path: string,
    config?: Omit<ApiRequestConfig, "method" | "body">,
  ): Promise<ApiResponse<T>>;
}

export type ApiClientOptions = {
  readonly baseUrl: string;
  readonly defaultHeaders?: Readonly<Record<string, string>>;
  readonly fetchFn?: typeof fetch;
  readonly getAccessToken?: () => string | null;
  readonly onUnauthorized?: () => Promise<boolean>;
};

function buildUrl(baseUrl: string, path: string): string {
  const normalizedBase = baseUrl.endsWith("/") ? baseUrl.slice(0, -1) : baseUrl;
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  return `${normalizedBase}${normalizedPath}`;
}

function mapStatusToError(status: number, body: unknown): ApiError {
  if (status === 401) return new ApiError("Unauthorized", "unauthorized", status, body);
  if (status === 403) return new ApiError("Forbidden", "forbidden", status, body);
  if (status === 404) return new ApiError("Not found", "not_found", status, body);
  if (status === 422) return new ApiError("Validation failed", "validation_error", status, body);
  if (status >= 500) return new ApiError("Server error", "server_error", status, body);
  return new ApiError("Request failed", "unknown", status, body);
}

function buildAuthHeaders(
  options: ApiClientOptions,
  configHeaders: Readonly<Record<string, string>>,
  credentials?: RequestCredentials,
): Record<string, string> {
  const headers: Record<string, string> = { ...configHeaders };
  const tokenAccessor = options.getAccessToken ?? getAccessToken;
  const token = tokenAccessor();
  if (token && !headers.Authorization) {
    headers.Authorization = `Bearer ${token}`;
  }
  if (credentials === "include") {
    const csrf = getCsrfToken();
    if (csrf && !headers["X-CSRF-Token"]) {
      headers["X-CSRF-Token"] = csrf;
    }
  }
  return headers;
}

/** HTTP-backed API client with bearer token and cookie credential support. */
export function createApiClient(options: ApiClientOptions): ApiClient {
  const fetchFn = options.fetchFn ?? fetch;

  async function request<T>(
    path: string,
    config: ApiRequestConfig = {},
    isRetry = false,
  ): Promise<ApiResponse<T>> {
    const { method = "GET", headers = {}, body, signal, credentials } = config;
    const authHeaders = buildAuthHeaders(options, headers, credentials);
    const init: RequestInit = {
      method,
      credentials: credentials ?? "same-origin",
      headers: {
        Accept: "application/json",
        ...(body !== undefined ? { "Content-Type": "application/json" } : {}),
        ...options.defaultHeaders,
        ...authHeaders,
      },
      ...(signal !== undefined ? { signal } : {}),
    };
    if (body !== undefined) {
      init.body = JSON.stringify(body);
    }

    let response: Response;
    try {
      response = await fetchFn(buildUrl(options.baseUrl, path), init);
    } catch (error) {
      throw new ApiError(
        error instanceof Error ? error.message : "Network request failed",
        "network_error",
        0,
        error,
      );
    }

    const contentType = response.headers.get("content-type") ?? "";
    const isJson = contentType.includes("application/json");
    const data =
      response.status === 204
        ? (undefined as T)
        : isJson
          ? await response.json()
          : await response.text();

    if (!response.ok) {
      if (
        response.status === 401 &&
        !isRetry &&
        options.onUnauthorized &&
        !path.includes("/auth/login") &&
        !path.includes("/auth/refresh")
      ) {
        const refreshed = await options.onUnauthorized();
        if (refreshed) {
          return request<T>(path, config, true);
        }
      }
      throw mapStatusToError(response.status, data);
    }

    return { data: data as T, status: response.status, headers: response.headers };
  }

  return {
    request,
    get: (path, config) => request(path, { ...config, method: "GET" }),
    post: (path, body, config) => request(path, { ...config, method: "POST", body }),
    put: (path, body, config) => request(path, { ...config, method: "PUT", body }),
    patch: (path, body, config) => request(path, { ...config, method: "PATCH", body }),
    delete: (path, config) => request(path, { ...config, method: "DELETE" }),
  };
}

/** No-op client for mock-only mode. All requests throw until backend is configured. */
export function createDisabledApiClient(): ApiClient {
  const disabled = (): never => {
    throw new ApiError(
      "API client is not configured. Use mock repositories until backend integration.",
      "unknown",
      0,
    );
  };
  return {
    request: disabled,
    get: disabled,
    post: disabled,
    put: disabled,
    patch: disabled,
    delete: disabled,
  };
}
