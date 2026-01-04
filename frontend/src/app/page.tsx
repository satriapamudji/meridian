import Link from "next/link";
import { getHealth } from "@/lib/api";
import {
  Card,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

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
    <div className="space-y-12 py-8">
      <section className="flex flex-col space-y-4">
        <h1 className="font-display text-4xl font-bold tracking-tight md:text-5xl">
          Macro signal clarity, without the noise.
        </h1>
        <p className="max-w-2xl text-lg text-muted-foreground">
          Meridian keeps policy shifts, macro shocks, and metals implications in one place.
          Start with the Macro Radar and drill into event analysis when it matters.
        </p>
        <div>
          <Badge variant={isOk ? "analyzed" : "destructive"} className="text-sm">
            Backend status: {isOk ? "ok" : "unavailable"}
          </Badge>
        </div>
      </section>

      <section className="grid gap-6 md:grid-cols-3">
        <Link href="/macro-radar" className="group block">
          <Card className="h-full transition-shadow hover:shadow-lg">
            <CardHeader>
              <CardTitle>Macro Radar</CardTitle>
              <CardDescription>
                Priority events, raw facts, and interpretation with clear separation.
              </CardDescription>
            </CardHeader>
          </Card>
        </Link>
        <Link href="/metals" className="group block">
          <Card className="h-full transition-shadow hover:shadow-lg">
            <CardHeader>
              <CardTitle>Metals Intelligence</CardTitle>
              <CardDescription>
                Curated knowledge base for gold, silver, and copper signals.
              </CardDescription>
            </CardHeader>
          </Card>
        </Link>
        <Link href="/theses" className="group block">
          <Card className="h-full transition-shadow hover:shadow-lg">
            <CardHeader>
              <CardTitle>Thesis Workspace</CardTitle>
              <CardDescription>
                Track your macro theses and note how the narrative evolves.
              </CardDescription>
            </CardHeader>
          </Card>
        </Link>
      </section>
    </div>
  );
}
