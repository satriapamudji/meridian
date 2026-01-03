export type HealthResponse = {
  status: string;
};

const DEFAULT_BASE_URL = "http://localhost:8000";

const resolveBaseUrl = () => {
  const configured = process.env.NEXT_PUBLIC_API_BASE_URL;
  if (!configured) {
    return DEFAULT_BASE_URL;
  }
  return configured.endsWith("/") ? configured.slice(0, -1) : configured;
};

const API_BASE_URL = resolveBaseUrl();

export const fetchJson = async <T>(
  path: string,
  init?: RequestInit,
): Promise<T> => {
  const url = `${API_BASE_URL}${path.startsWith("/") ? path : `/${path}`}`;
  const response = await fetch(url, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
    cache: "no-store",
  });
  if (!response.ok) {
    const message = await response.text();
    throw new Error(`API error ${response.status}: ${message}`);
  }
  return response.json() as Promise<T>;
};

export const getHealth = async (): Promise<HealthResponse> => {
  return fetchJson<HealthResponse>("/health");
};
