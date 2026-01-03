import Link from "next/link";

import { getHealth } from "@/lib/api";

const getBackendStatus = async () => {
  try {
    const result = await getHealth();
    return result.status;
  } catch {
    return "unavailable";
  }
};

export default async function HomePage() {
  const status = await getBackendStatus();
  const isOk = status === "ok";

  return (
    <>
      <section className="hero">
        <h1>Macro signal clarity, without the noise.</h1>
        <p>
          Meridian keeps policy shifts, macro shocks, and metals implications in one place.
          Start with the Macro Radar and drill into event analysis when it matters.
        </p>
        <div className="status-chip">
          Backend status: {isOk ? "ok" : "unavailable"}
        </div>
      </section>

      <section className="cards">
        <Link className="card" href="/macro-radar">
          <h3>Macro Radar</h3>
          <p>Priority events, raw facts, and interpretation with clear separation.</p>
        </Link>
        <Link className="card" href="/metals">
          <h3>Metals Intelligence</h3>
          <p>Curated knowledge base for gold, silver, and copper signals.</p>
        </Link>
        <Link className="card" href="/theses">
          <h3>Thesis Workspace</h3>
          <p>Track your macro theses and note how the narrative evolves.</p>
        </Link>
      </section>
    </>
  );
}
