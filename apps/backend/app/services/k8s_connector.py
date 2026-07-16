"""
Connecteur Kubernetes : interroge l'API K8s et traduit le statut d'un pod
vers le même schéma pivot que le connecteur Docker (ADR 0003).

Symétrique à docker_connector.py : même signature de sortie (ResourceHealth),
seule la logique de traduction interne diffère.
"""

from datetime import datetime, timezone

from kubernetes import client as k8s_client
from kubernetes import config as k8s_config
from kubernetes.client.exceptions import ApiException

from app.schemas.health import ResourceHealth

# Mapping de la phase native K8s vers notre statut unifié
_K8S_PHASE_MAP = {
    "Running": "healthy",
    "Pending": "degraded",
    "Succeeded": "healthy",
    "Failed": "down",
    "Unknown": "unknown",
}


def get_k8s_client() -> k8s_client.CoreV1Api:
    """
    Charge la config K8s (in-cluster si déployé dans K8s, sinon ~/.kube/config
    en local) et retourne un client de l'API Core (pods, etc.).
    """
    try:
        k8s_config.load_incluster_config()
    except k8s_config.ConfigException:
        k8s_config.load_kube_config()
    return k8s_client.CoreV1Api()


def check_pod_health(resource_id, pod_name: str, namespace: str = "default") -> ResourceHealth:
    """Interroge un pod par son nom et retourne son état dans le format pivot."""
    try:
        api = get_k8s_client()
        pod = api.read_namespaced_pod(name=pod_name, namespace=namespace)

        restart_count = sum(
            cs.restart_count for cs in (pod.status.container_statuses or [])
        )

        return ResourceHealth(
            resource_id=resource_id,
            status=_K8S_PHASE_MAP.get(pod.status.phase, "unknown"),
            orchestrator="kubernetes",
            last_checked=datetime.now(timezone.utc),
            details={
                "namespace": namespace,
                "phase": pod.status.phase,
                "restart_count": restart_count,
                "node": pod.spec.node_name,
            },
        )
    except ApiException as e:
        if e.status == 404:
            return ResourceHealth(
                resource_id=resource_id,
                status="down",
                orchestrator="kubernetes",
                last_checked=datetime.now(timezone.utc),
                details={"error": "pod introuvable"},
            )
        return ResourceHealth(
            resource_id=resource_id,
            status="unknown",
            orchestrator="kubernetes",
            last_checked=datetime.now(timezone.utc),
            details={"error": str(e)},
        )
