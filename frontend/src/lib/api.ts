export type HealthResponse = {
  status: string;
};

export type MacroEventRaw = {
  id: string;
  source: string;
  headline: string;
  published_at: string | null;
  event_type: string | null;
  regions: string[] | null;
  entities: string[] | null;
  significance_score: number | null;
  priority_flag: boolean;
  status: string | null;
  full_text?: string | null;
};

export type MetalImpact = {
  direction: string;
  magnitude: string;
  driver: string;
};

export type CryptoTransmission = {
  exists: boolean;
  path: string;
  strength: string;
  relevant_assets: string[];
};

export type MacroEvent = {
  raw: MacroEventRaw;
  analysis: {
    raw_facts: string[] | null;
    interpretation: {
      metal_impacts: Record<string, MetalImpact> | null;
      historical_precedent: string | null;
      counter_case: string | null;
      crypto_transmission: CryptoTransmission | null;
    };
  };
};

export type ListEventsResponse = {
  events: MacroEvent[];
};

export type ListEventsParams = {
  priorityOnly?: boolean;
  scoreMin?: number;
  scoreMax?: number;
  status?: string;
  startDate?: string;
  endDate?: string;
  limit?: number;
};

const DEFAULT_BASE_URL = "http://localhost:8000";

const resolveBaseUrl = () => {
  const configured = process.env.NEXT_PUBLIC_API_BASE_URL;
  if (!configured) {
    return DEFAULT_BASE_URL;
  }
  return configured.endsWith("/") ? configured.slice(0, -1) : configured;
};

export const getApiBaseUrl = () => resolveBaseUrl();

export const fetchJson = async <T>(
  path: string,
  init?: RequestInit,
): Promise<T> => {
  const baseUrl = getApiBaseUrl();
  const url = `${baseUrl}${path.startsWith("/") ? path : `/${path}`}`;
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

export const getEvents = async (
  params: ListEventsParams = {},
): Promise<ListEventsResponse> => {
  const searchParams = new URLSearchParams();
  if (params.priorityOnly) {
    searchParams.set("priority_only", "true");
  }
  if (params.scoreMin !== undefined) {
    searchParams.set("score_min", params.scoreMin.toString());
  }
  if (params.scoreMax !== undefined) {
    searchParams.set("score_max", params.scoreMax.toString());
  }
  if (params.status) {
    searchParams.set("status", params.status);
  }
  if (params.startDate) {
    searchParams.set("start_date", params.startDate);
  }
  if (params.endDate) {
    searchParams.set("end_date", params.endDate);
  }
  if (params.limit !== undefined) {
    searchParams.set("limit", params.limit.toString());
  }
  const query = searchParams.toString();
  const path = query ? `/events?${query}` : "/events";
  return fetchJson<ListEventsResponse>(path);
};

export const getEvent = async (eventId: string): Promise<MacroEvent> => {
  return fetchJson<MacroEvent>(`/events/${eventId}`);
};

// ---------------------------------------------------------------------------
// Thesis Workspace
// ---------------------------------------------------------------------------

export type ThesisUpdateEntry = {
  date: string;
  note: string;
  price?: number | null;
};

export type Thesis = {
  id: string;
  created_at: string;
  updated_at: string;
  title: string;
  asset_type: string;
  asset_symbol: string | null;
  trigger_event: string | null;
  core_thesis: string;
  bull_case: string[] | null;
  bear_case: string[] | null;
  historical_precedent: string | null;
  entry_consideration: string | null;
  target: string | null;
  invalidation: string | null;
  vehicle: string | null;
  position_size: string | null;
  entry_date: string | null;
  entry_price: number | null;
  status: string;
  price_at_creation: number | null;
  current_price: number | null;
  price_change_percent: number | null;
  updates: ThesisUpdateEntry[];
};

export type ListThesesParams = {
  status?: string;
};

export const getTheses = async (
  params: ListThesesParams = {},
): Promise<Thesis[]> => {
  const searchParams = new URLSearchParams();
  if (params.status) {
    searchParams.set("status", params.status);
  }
  const query = searchParams.toString();
  const path = query ? `/theses?${query}` : "/theses";
  return fetchJson<Thesis[]>(path);
};

export const getThesis = async (thesisId: string): Promise<Thesis> => {
  return fetchJson<Thesis>(`/theses/${thesisId}`);
};
