export type ProfileInput = {
  name?: string;
  age: number;
  gender: string;
  state: string;
  district?: string;
  annual_income: number;
  category: string;
  student: boolean;
  disability: boolean;
  occupation?: string;
  education_level?: string;
};

export type SchemeMatch = {
  id: number;
  name: string;
  ministry?: string;
  state: string;
  deadline?: string;
  source_url: string;
  reason: string;
  summary?: string;
};

function apiBaseUrl() {
  if (typeof window !== "undefined") {
    return "/api/backend";
  }
  return process.env.INTERNAL_API_URL ?? process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${apiBaseUrl()}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers
    }
  });
  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `Request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export async function checkEligibility(profile: ProfileInput) {
  return request<{ matches: SchemeMatch[] }>("/eligibility/check", {
    method: "POST",
    body: JSON.stringify({ profile, limit: 8 })
  });
}

export async function askYojana(query: string, profile: ProfileInput) {
  return request<{ answer: string; contexts: Array<Record<string, string | number>>; cached: boolean; latency_ms: number }>("/ask", {
    method: "POST",
    body: JSON.stringify({ query, profile })
  });
}

export async function ingestUrl(url: string, state?: string, schemeName?: string) {
  return request<{ scheme_id: number; document_id: number; chunks: number }>("/ingest/url", {
    method: "POST",
    body: JSON.stringify({ url, state, scheme_name: schemeName })
  });
}

export async function getSchemes() {
  return request<{ schemes: SchemeMatch[] }>("/schemes", { cache: "no-store" });
}

export async function getSources() {
  return request<{ sources: Array<{ id: number; title: string; source_url: string; doc_type: string; chunks: number }> }>("/sources", {
    cache: "no-store"
  });
}
