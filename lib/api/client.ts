import { ApiError } from "@/lib/api/errors";
import type { ApiRequestConfig, ApiResponse } from "@/lib/api/types";

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

/** HTTP-backed API client for future backend integration. Not wired to features yet. */
export function createApiClient(options: ApiClientOptions): ApiClient {
  const fetchFn = options.fetchFn ?? fetch;

  async function request<T>(path: string, config: ApiRequestConfig = {}): Promise<ApiResponse<T>> {
    const { method = "GET", headers = {}, body, signal } = config;
    const init: RequestInit = {
      method,
      headers: {
        Accept: "application/json",
        ...(body !== undefined ? { "Content-Type": "application/json" } : {}),
        ...options.defaultHeaders,
        ...headers,
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
    const data = contentType.includes("application/json")
      ? await response.json()
      : await response.text();

    if (!response.ok) {
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
