import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { api, type AuditEntry } from "@/lib/api";
import { useHealthSocket } from "@/hooks/use-health-socket";
import type { HealthStatus, Resource } from "@/types";

export const Route = createFileRoute("/")({
  component: Dashboard,
});

const STATUS_STYLES: Record<HealthStatus, string> = {
  healthy: "bg-green-100 text-green-800",
  degraded: "bg-amber-100 text-amber-800",
  down: "bg-red-100 text-red-800",
  unknown: "bg-gray-100 text-gray-600",
};

function StatusBadge({ status }: { status?: HealthStatus }) {
  const value = status ?? "unknown";
  return (
    <span
      className={`rounded px-2.5 py-1 text-xs font-medium ${STATUS_STYLES[value]}`}
    >
      {value}
    </span>
  );
}

function NewResourceForm({
  onCreated,
  onCancel,
}: {
  onCreated: (r: Resource) => void;
  onCancel: () => void;
}) {
  const [name, setName] = useState("");
  const [type, setType] = useState("api");
  const [orchestrator, setOrchestrator] = useState<"docker" | "kubernetes">(
    "docker"
  );
  const [image, setImage] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      const resource = await api.createResource({
        name,
        type,
        orchestrator,
        config: image ? { image } : {},
      });
      onCreated(resource);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erreur inconnue");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="mb-6 rounded border border-gray-200 p-4"
    >
      <div className="grid gap-3 sm:grid-cols-2">
        <div>
          <label className="mb-1 block text-xs font-medium text-gray-600">
            Nom
          </label>
          <input
            required
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="auth-service"
            className="w-full rounded border border-gray-300 px-2.5 py-1.5 text-sm"
          />
        </div>
        <div>
          <label className="mb-1 block text-xs font-medium text-gray-600">
            Type
          </label>
          <input
            required
            value={type}
            onChange={(e) => setType(e.target.value)}
            placeholder="api"
            className="w-full rounded border border-gray-300 px-2.5 py-1.5 text-sm"
          />
        </div>
        <div>
          <label className="mb-1 block text-xs font-medium text-gray-600">
            Orchestrateur
          </label>
          <select
            value={orchestrator}
            onChange={(e) =>
              setOrchestrator(e.target.value as "docker" | "kubernetes")
            }
            className="w-full rounded border border-gray-300 px-2.5 py-1.5 text-sm"
          >
            <option value="docker">docker</option>
            <option value="kubernetes">kubernetes</option>
          </select>
        </div>
        <div>
          <label className="mb-1 block text-xs font-medium text-gray-600">
            Image (optionnel)
          </label>
          <input
            value={image}
            onChange={(e) => setImage(e.target.value)}
            placeholder="myapp/auth:1.0"
            className="w-full rounded border border-gray-300 px-2.5 py-1.5 text-sm"
          />
        </div>
      </div>

      {error && <p className="mt-2 text-xs text-red-600">{error}</p>}

      <div className="mt-3 flex gap-2">
        <button
          type="submit"
          disabled={submitting}
          className="rounded bg-gray-900 px-3 py-1.5 text-xs font-medium text-white disabled:opacity-50"
        >
          {submitting ? "Création..." : "Créer"}
        </button>
        <button
          type="button"
          onClick={onCancel}
          className="rounded border border-gray-300 px-3 py-1.5 text-xs font-medium"
        >
          Annuler
        </button>
      </div>
    </form>
  );
}

function AuditPanel({ resourceId }: { resourceId: string }) {
  const [entries, setEntries] = useState<AuditEntry[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .getAudit(resourceId)
      .then(setEntries)
      .catch((err) =>
        setError(err instanceof Error ? err.message : "Erreur")
      );
  }, [resourceId]);

  if (error) return <p className="text-xs text-red-600">{error}</p>;
  if (!entries) return <p className="text-xs text-gray-400">Chargement...</p>;
  if (entries.length === 0)
    return <p className="text-xs text-gray-400">Aucune action enregistrée.</p>;

  return (
    <ul className="space-y-1.5">
      {entries.map((entry) => (
        <li key={entry.id} className="text-xs text-gray-600">
          <span className="font-medium text-gray-900">{entry.action}</span>
          {" — "}
          {new Date(entry.created_at).toLocaleString()}
        </li>
      ))}
    </ul>
  );
}

function ResourceCard({
  resource,
  status,
  onDeploy,
  onDelete,
}: {
  resource: Resource;
  status?: HealthStatus;
  onDeploy: (id: string) => Promise<void>;
  onDelete: (id: string) => void;
}) {
  const [expanded, setExpanded] = useState(false);
  const [deploying, setDeploying] = useState(false);

  async function handleDeploy() {
    setDeploying(true);
    try {
      await onDeploy(resource.id);
    } finally {
      setDeploying(false);
    }
  }

  return (
    <div className="rounded border border-gray-200 p-4">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-gray-900">{resource.name}</p>
          <p className="mt-0.5 text-xs text-gray-500">{resource.type}</p>
        </div>
        <StatusBadge status={status} />
      </div>

      <div className="mt-3 flex gap-2">
        <button
          onClick={handleDeploy}
          disabled={deploying}
          className="rounded border border-gray-300 px-2.5 py-1 text-xs font-medium disabled:opacity-50"
        >
          {deploying ? "Déploiement..." : "Déployer"}
        </button>
        <button
          onClick={() => setExpanded((v) => !v)}
          className="rounded border border-gray-300 px-2.5 py-1 text-xs font-medium"
        >
          {expanded ? "Masquer l'audit" : "Voir l'audit"}
        </button>
        <button
          onClick={() => onDelete(resource.id)}
          className="ml-auto rounded px-2.5 py-1 text-xs font-medium text-red-600 hover:bg-red-50"
        >
          Supprimer
        </button>
      </div>

      {expanded && (
        <div className="mt-3 border-t border-gray-100 pt-3">
          <AuditPanel resourceId={resource.id} />
        </div>
      )}
    </div>
  );
}

function Dashboard() {
  const [resources, setResources] = useState<Resource[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const healthByResource = useHealthSocket();

  function loadResources() {
    setLoading(true);
    api
      .listResources()
      .then(setResources)
      .catch((err) =>
        setError(err instanceof Error ? err.message : "Erreur de chargement")
      )
      .finally(() => setLoading(false));
  }

  useEffect(() => {
    loadResources();
  }, []);

  async function handleDeploy(id: string) {
    await api.triggerDeployment(id);
  }

  async function handleDelete(id: string) {
    await api.deleteResource(id);
    setResources((prev) => prev.filter((r) => r.id !== id));
  }

  return (
    <div className="mx-auto max-w-3xl px-4 py-6">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h1 className="text-lg font-medium text-gray-900">Ressources</h1>
          <p className="text-xs text-gray-500">
            {resources.length} ressource{resources.length !== 1 ? "s" : ""}{" "}
            surveillée{resources.length !== 1 ? "s" : ""}
          </p>
        </div>
        <button
          onClick={() => setShowForm((v) => !v)}
          className="rounded bg-gray-900 px-3 py-1.5 text-xs font-medium text-white"
        >
          + Nouvelle ressource
        </button>
      </div>

      {showForm && (
        <NewResourceForm
          onCancel={() => setShowForm(false)}
          onCreated={(r) => {
            setResources((prev) => [r, ...prev]);
            setShowForm(false);
          }}
        />
      )}

      {loading && <p className="text-sm text-gray-500">Chargement...</p>}
      {error && <p className="text-sm text-red-600">{error}</p>}

      {!loading && !error && resources.length === 0 && (
        <p className="text-sm text-gray-500">
          Aucune ressource enregistrée pour l'instant.
        </p>
      )}

      <div className="grid gap-3 sm:grid-cols-2">
        {resources.map((resource) => (
          <ResourceCard
            key={resource.id}
            resource={resource}
            status={healthByResource[resource.id]?.status}
            onDeploy={handleDeploy}
            onDelete={handleDelete}
          />
        ))}
      </div>
    </div>
  );
}
