import { useEffect, useRef, useState } from "react";
import { WS_HEALTH_URL } from "@/lib/api";
import type { ResourceHealth } from "@/types";

/**
 * S'abonne au flux WebSocket de santé et maintient une map à jour
 * resource_id -> dernier statut connu. Se reconnecte automatiquement
 * si la connexion tombe (le backend ou Redis peut redémarrer).
 */
export function useHealthSocket() {
  const [healthByResource, setHealthByResource] = useState<
    Record<string, ResourceHealth>
  >({});
  const socketRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    let cancelled = false;
    let retryTimeout: ReturnType<typeof setTimeout>;

    function connect() {
      if (cancelled) return;
      const socket = new WebSocket(WS_HEALTH_URL);
      socketRef.current = socket;

      socket.onmessage = (event) => {
        try {
          const health: ResourceHealth = JSON.parse(event.data);
          setHealthByResource((prev) => ({
            ...prev,
            [health.resource_id]: health,
          }));
        } catch {
          // message mal formé, on l'ignore silencieusement
        }
      };

      socket.onclose = () => {
        if (!cancelled) {
          retryTimeout = setTimeout(connect, 3000);
        }
      };
    }

    connect();

    return () => {
      cancelled = true;
      clearTimeout(retryTimeout);
      socketRef.current?.close();
    };
  }, []);

  return healthByResource;
}
