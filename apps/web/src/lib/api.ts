import type { Resource } from "@/types";

const API_BASE = "http://localhost:8000";

export interface AuditEntry {
  id: string;
  resource_id: string;
  action: string;
  actor: string | null;
  details: Record<string, unknown>;
  created_at: string;
}

export interface NewResourceInput {
  name: string;
  type: string;
  orchestrator: "docker" | "kubernetes";
  config: Record<string, unknown>;
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Erreur ${res.status}`);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

export const api = {
  listResources: () => request<Resource[]>("/resources/"),

  createResource: (input: NewResourceInput) =>
    request<Resource>("/resources/", {
      method: "POST",
      body: JSON.stringify(input),
    }),

  deleteResource: (id: string) =>
    request<void>(`/resources/${id}`, { method: "DELETE" }),

  triggerDeployment: (resourceId: string) =>
    request(`/deployments/${resourceId}`, { method: "POST" }),

  getAudit: (resourceId: string) =>
    request<AuditEntry[]>(`/audit/${resourceId}`),
};

export const WS_HEALTH_URL = "ws://localhost:8000/ws/health";
