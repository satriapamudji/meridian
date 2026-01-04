import Link from "next/link";
import { ArrowLeft } from "lucide-react";

import { getEvent } from "@/lib/api";
import { formatDateTime, formatScoreBand, formatStatus } from "@/lib/format";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

const getScoreValue = (score: number | null) => (score === null ? "n/a" : score);

const toLabelList = (values: string[] | null) => {
  if (!values || values.length === 0) {
    return "none";
  }
  return values.join(", ");
};

const extractCaseId = (value: string | null) => {
  if (!value) {
    return null;
  }
  const match = value.match(/case[_\s-]?id\s*[:#-]?\s*([\w-]+)/i);
  return match ? match[1] : null;
};

const hasAnalysis = (event: Awaited<ReturnType<typeof getEvent>>) => {
  const rawFacts = event.analysis.raw_facts;
  const interpretation = event.analysis.interpretation;
  return Boolean(
    (rawFacts && rawFacts.length > 0) ||
      interpretation.metal_impacts ||
      interpretation.historical_precedent ||
      interpretation.counter_case ||
      interpretation.crypto_transmission,
  );
};

export default async function MacroEventDetailPage({
  params,
}: {
  params: { eventId: string };
}) {
  const event = await getEvent(params.eventId);
  const score = event.raw.significance_score;
  const scoreBand = score === null ? "Unscored" : formatScoreBand(score);
  const analysisPresent = hasAnalysis(event);
  const canAnalyze = event.raw.priority_flag;
  const caseId = extractCaseId(event.analysis.interpretation.historical_precedent);
  const metalImpacts = event.analysis.interpretation.metal_impacts ?? {};
  const cryptoTransmission = event.analysis.interpretation.crypto_transmission;
  const hasMetalImpacts = Object.keys(metalImpacts).length > 0;
  const hasCryptoTransmission =
    cryptoTransmission &&
    (cryptoTransmission.exists ||
      cryptoTransmission.path ||
      cryptoTransmission.relevant_assets.length > 0);

  return (
    <>
      <Card className="p-6">
        <div className="flex justify-between items-start gap-4">
          <div>
            <Link 
              href="/macro-radar" 
              className="text-sm text-muted-foreground hover:text-foreground flex items-center gap-1 mb-2"
            >
              <ArrowLeft className="w-4 h-4" />
              Back to Macro Radar
            </Link>
            <h1 className="text-3xl font-display font-bold tracking-tight mb-1">{event.raw.headline}</h1>
            <p className="text-muted-foreground">
              {event.raw.source} • {formatDateTime(event.raw.published_at)}
            </p>
          </div>
          <div className="flex flex-col items-end">
            <span className="text-xs text-muted-foreground uppercase">Score</span>
            <span className="text-4xl font-bold text-primary">{getScoreValue(score)}</span>
            <Badge variant="outline">{scoreBand}</Badge>
          </div>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4 pt-4 border-t">
          <div>
            <span className="text-xs text-muted-foreground uppercase block">Status</span>
            <span>{formatStatus(event.raw.status)}</span>
          </div>
          <div>
            <span className="text-xs text-muted-foreground uppercase block">Event type</span>
            <span>{event.raw.event_type ?? "unclassified"}</span>
          </div>
          <div>
            <span className="text-xs text-muted-foreground uppercase block">Regions</span>
            <span>{toLabelList(event.raw.regions)}</span>
          </div>
          <div>
            <span className="text-xs text-muted-foreground uppercase block">Entities</span>
            <span>{toLabelList(event.raw.entities)}</span>
          </div>
        </div>
        {!analysisPresent && (
          <Card className="bg-amber-50 border-amber-200 p-4 flex justify-between items-center mt-6">
            <div>
              <h3 className="font-semibold text-amber-900">Analysis missing</h3>
              <p className="text-sm text-amber-700">Trigger analysis to generate raw facts and interpretation.</p>
            </div>
            {canAnalyze ? (
              <form action={`/api/events/${event.raw.id}/analyze`} method="post">
                <Button type="submit">Analyze</Button>
              </form>
            ) : (
              <span className="text-sm text-muted-foreground">Analysis is enabled for priority events.</span>
            )}
          </Card>
        )}
      </Card>

      <section className="mt-8">
        <div className="mb-4">
          <h2 className="text-2xl font-display font-semibold">Raw facts</h2>
          <p className="text-muted-foreground">Uninterpreted facts extracted from the source.</p>
        </div>
        {event.analysis.raw_facts && event.analysis.raw_facts.length > 0 ? (
          <ul className="list-disc list-inside space-y-2 text-sm">
            {event.analysis.raw_facts.map((fact) => (
              <li key={fact}>{fact}</li>
            ))}
          </ul>
        ) : (
          <p className="text-muted-foreground italic">No raw facts available yet.</p>
        )}
        {event.raw.full_text ? (
          <div className="mt-4 p-4 bg-muted/30 rounded-lg">
            <h3 className="text-lg font-semibold mb-2">Source text</h3>
            <p className="text-sm text-muted-foreground whitespace-pre-wrap">{event.raw.full_text}</p>
          </div>
        ) : null}
      </section>

      <section className="mt-8">
        <div className="mb-4">
          <h2 className="text-2xl font-display font-semibold">Interpretation</h2>
          <p className="text-muted-foreground">Analysis and downstream implications derived from the event.</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Card className="p-4">
            <h3 className="text-lg font-semibold mb-3">Significance scoring</h3>
            <dl className="space-y-2">
              <div>
                <dt className="text-xs text-muted-foreground uppercase">Score</dt>
                <dd className="text-sm font-medium">{getScoreValue(score)}</dd>
              </div>
              <div>
                <dt className="text-xs text-muted-foreground uppercase">Band</dt>
                <dd className="text-sm font-medium">{scoreBand}</dd>
              </div>
              <div>
                <dt className="text-xs text-muted-foreground uppercase">Priority threshold</dt>
                <dd className="text-sm font-medium">65+</dd>
              </div>
              <div>
                <dt className="text-xs text-muted-foreground uppercase">Priority flag</dt>
                <dd className="text-sm font-medium">{event.raw.priority_flag ? "yes" : "no"}</dd>
              </div>
            </dl>
          </Card>

          <Card className="p-4 md:col-span-2">
            <h3 className="text-lg font-semibold mb-3">Metal impacts</h3>
            {hasMetalImpacts ? (
              <div className="space-y-2">
                {Object.entries(metalImpacts).map(([metal, impact]) => (
                  <div key={metal} className="grid grid-cols-4 gap-2 text-sm py-2 border-b last:border-0">
                    <div className="font-medium">
                      {metal.toUpperCase()}
                    </div>
                    <div>{impact.direction}</div>
                    <div>{impact.magnitude}</div>
                    <div>{impact.driver}</div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-muted-foreground italic">No metal impact analysis yet.</p>
            )}
          </Card>

          <Card className="p-4">
            <h3 className="text-lg font-semibold mb-3">Historical precedent</h3>
            <p className="text-sm">{event.analysis.interpretation.historical_precedent ?? "None yet."}</p>
            {caseId ? (
              <Link className="text-primary hover:underline text-sm block mt-2" href={`/cases/${caseId}`}>
                View case {caseId}
              </Link>
            ) : null}
          </Card>

          <Card className="p-4">
            <h3 className="text-lg font-semibold mb-3">Counter-case</h3>
            <p className="text-sm">{event.analysis.interpretation.counter_case ?? "No counter-case yet."}</p>
          </Card>

          <Card className="p-4 md:col-span-2">
            <h3 className="text-lg font-semibold mb-3">Crypto transmission</h3>
            {hasCryptoTransmission ? (
              <dl className="space-y-2">
                <div>
                  <dt className="text-xs text-muted-foreground uppercase">Exists</dt>
                  <dd className="text-sm font-medium">{cryptoTransmission?.exists ? "yes" : "no"}</dd>
                </div>
                <div>
                  <dt className="text-xs text-muted-foreground uppercase">Strength</dt>
                  <dd className="text-sm font-medium">{cryptoTransmission?.strength ?? "unknown"}</dd>
                </div>
                <div>
                  <dt className="text-xs text-muted-foreground uppercase">Relevant assets</dt>
                  <dd className="text-sm font-medium">
                    {cryptoTransmission?.relevant_assets.length
                      ? cryptoTransmission.relevant_assets.join(", ")
                      : "none"}
                  </dd>
                </div>
              </dl>
            ) : (
              <p className="text-muted-foreground italic">No crypto transmission path recorded.</p>
            )}
            {cryptoTransmission?.path ? (
              <p className="mt-2 text-sm text-muted-foreground italic">{cryptoTransmission.path}</p>
            ) : null}
          </Card>
        </div>
      </section>
    </>
  );
}
