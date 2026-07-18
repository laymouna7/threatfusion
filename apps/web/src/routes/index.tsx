import { useEffect, useState } from "react";
import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/")({
  component: HomeComponent,
});

const TITLE_TEXT = `Threat Fusion`;

function HomeComponent() {
  const [status, setStatus] = useState<"loading" | "online" | "offline">("loading");

  useEffect(() => {
    let active = true;

    async function check() {
      try {
        const res = await fetch("http://localhost:8000/health");
        if (!res.ok) throw new Error("not ok");
        if (active) setStatus("online");
      } catch {
        if (active) setStatus("offline");
      }
    }

    check();
    const interval = setInterval(check, 10000);
    return () => {
      active = false;
      clearInterval(interval);
    };
  }, []);

  return (
    <div className="container mx-auto max-w-3xl px-4 py-2">
      <pre className="overflow-x-auto font-mono text-sm">{TITLE_TEXT}</pre>
      <div className="grid gap-6">
        <section className="rounded-lg border p-4">
          <h2 className="mb-2 font-medium">API Status</h2>
          {status === "loading" && (
            <p className="text-sm text-muted-foreground">Checking...</p>
          )}
          {status === "offline" && (
            <p className="text-sm text-red-500">Offline — unreachable</p>
          )}
          {status === "online" && (
            <p className="text-sm text-green-600">Online — healthy</p>
          )}
        </section>
      </div>
    </div>
  );
}
