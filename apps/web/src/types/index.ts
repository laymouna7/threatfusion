// Reflète le schéma pivot défini dans docs/adr/0003-modele-agregation-sante.md

export type HealthStatus = "healthy" | "degraded" | "down" | "unknown";

export interface ResourceHealth {
  resource_id: string;
  status: HealthStatus;
  orchestrator: "docker" | "kubernetes";
  last_checked: string;
  details: Record<string, string | number>;
}

export interface Resource {
  id: string;
  name: string;
  type: string;
  config: Record<string, unknown>;
  health?: ResourceHealth;
}
