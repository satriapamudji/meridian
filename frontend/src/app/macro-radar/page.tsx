import Link from "next/link";

import { getEvents, type MacroEvent } from "@/lib/api";
import { formatDateTime, formatScoreBand, formatStatus } from "@/lib/format";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

type SearchParams = Record<string, string | string[] | undefined>;

const getParam = (value: string | string[] | undefined) =>
  Array.isArray(value) ? value[0] : value;

const parseNumber = (value: string | undefined) => {
  if (!value) {
    return undefined;
  }
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : undefined;
};

const parseDate = (value: string | undefined) => {
  if (!value) {
    return undefined;
  }
  return /^\d{4}-\d{2}-\d{2}$/.test(value) ? value : undefined;
};

const normalizeFilter = (value: string | undefined) => {
  if (!value || value === "all") {
    return undefined;
  }
  return value;
};

const filterByDate = (event: MacroEvent, start: Date | undefined, end: Date | undefined) => {
  if (!start && !end) {
    return true;
  }
  if (!event.raw.published_at) {
    return false;
  }
  const published = new Date(event.raw.published_at);
  if (Number.isNaN(published.getTime())) {
    return false;
  }
  if (start && published < start) {
    return false;
  }
  if (end && published > end) {
    return false;
  }
  return true;
};

const buildOptions = (values: Array<string | null>) =>
  Array.from(new Set(values.filter(Boolean) as string[])).sort((left, right) =>
    left.localeCompare(right),
  );

const toStartOfDay = (value: string) => new Date(`${value}T00:00:00Z`);
const toEndOfDay = (value: string) => new Date(`${value}T23:59:59.999Z`);

const isAnalysisReady = (event: MacroEvent) => {
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

const scoreBand = (score: number | null) => {
  if (score === null) {
    return "Unscored";
  }
  return formatScoreBand(score);
};

const scoreBadgeVariant = (band: string) => {
  if (band === "Priority") return "default";
  if (band === "Monitoring") return "secondary";
  if (band === "Logged") return "outline";
  return "outline";
};

const EventCard = ({ event }: { event: MacroEvent }) => {
  const score = event.raw.significance_score;
  const band = scoreBand(score);
  const analysisReady = isAnalysisReady(event);

  return (
    <Link href={`/macro-radar/${event.raw.id}`} className="block">
      <Card className="h-full transition-shadow hover:shadow-lg">
        <CardHeader className="space-y-2">
          <div className="flex items-start justify-between gap-4">
            <div className="flex items-center gap-2">
              <span className="text-2xl font-bold text-primary">
                {score === null ? "\u2014" : score}
              </span>
              <Badge variant={scoreBadgeVariant(band) as any}>{band}</Badge>
              <Badge variant={analysisReady ? "analyzed" : "pending"}>
                {analysisReady ? "analysis" : "pending"}
              </Badge>
            </div>
            <span className="text-xs uppercase tracking-wide text-muted-foreground">
              {event.raw.source}
            </span>
          </div>
          <CardTitle className="text-base leading-snug">{event.raw.headline}</CardTitle>
          <CardDescription className="flex flex-wrap items-center gap-2 text-xs">
            <span>{formatDateTime(event.raw.published_at)}</span>
            <span className="text-muted-foreground/60">\u2022</span>
            <span>Status: {formatStatus(event.raw.status)}</span>
          </CardDescription>
        </CardHeader>
      </Card>
    </Link>
  );
};

const Section = ({
  title,
  subtitle,
  events,
}: {
  title: string;
  subtitle: string;
  events: MacroEvent[];
}) => (
  <section className="space-y-4">
    <div className="flex items-start justify-between gap-4">
      <div>
        <h2 className="text-xl font-semibold">{title}</h2>
        <p className="text-sm text-muted-foreground">{subtitle}</p>
      </div>
      <Badge variant="secondary">{events.length}</Badge>
    </div>
    {events.length === 0 ? (
      <Card className="p-4">
        <p className="text-sm text-muted-foreground italic">No events match this section.</p>
      </Card>
    ) : (
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {events.map((event) => (
          <EventCard key={event.raw.id} event={event} />
        ))}
      </div>
    )}
  </section>
);

export default async function MacroRadarPage({ searchParams }: { searchParams?: SearchParams }) {
  const scoreMin = parseNumber(getParam(searchParams?.score_min));
  const scoreMax = parseNumber(getParam(searchParams?.score_max));
  const status = normalizeFilter(getParam(searchParams?.status));
  const source = normalizeFilter(getParam(searchParams?.source));
  const startDate = parseDate(getParam(searchParams?.start_date));
  const endDate = parseDate(getParam(searchParams?.end_date));
  const startDateValue = startDate ? toStartOfDay(startDate) : undefined;
  const endDateValue = endDate ? toEndOfDay(endDate) : undefined;

  const { events } = await getEvents({ limit: 200 });
  const sourceOptions = buildOptions(events.map((event) => event.raw.source));
  const statusOptions = buildOptions(events.map((event) => event.raw.status));
  const sourceChoices =
    source && !sourceOptions.includes(source) ? [source, ...sourceOptions] : sourceOptions;
  const statusChoices =
    status && !statusOptions.includes(status) ? [status, ...statusOptions] : statusOptions;

  const filteredEvents = events.filter((event) => {
    const score = event.raw.significance_score;
    if (scoreMin !== undefined && (score === null || score < scoreMin)) {
      return false;
    }
    if (scoreMax !== undefined && (score === null || score > scoreMax)) {
      return false;
    }
    if (status && event.raw.status !== status) {
      return false;
    }
    if (source && event.raw.source !== source) {
      return false;
    }
    return filterByDate(event, startDateValue, endDateValue);
  });

  const priorityEvents = filteredEvents.filter((event) => {
    const score = event.raw.significance_score;
    return score !== null && score >= 65;
  });
  const monitoringEvents = filteredEvents.filter((event) => {
    const score = event.raw.significance_score;
    return score !== null && score >= 50 && score <= 64;
  });
  const loggedEvents = filteredEvents.filter((event) => {
    const score = event.raw.significance_score;
    return score !== null && score < 50;
  });
  const unscoredEvents = filteredEvents.filter((event) => event.raw.significance_score === null);

  return (
    <div className="space-y-10 py-4">
      <Card>
        <CardHeader>
          <div className="flex items-start justify-between gap-4">
            <div>
              <CardTitle className="font-display text-3xl tracking-tight">
                Macro Radar
              </CardTitle>
              <CardDescription>
                Macro events organized by significance. Scores and status come from the backend.
              </CardDescription>
            </div>
            <Badge variant="secondary">{filteredEvents.length} events</Badge>
          </div>
        </CardHeader>
        <CardContent>
          <form method="get" className="space-y-4">
            <div className="grid gap-4 md:grid-cols-3 lg:grid-cols-6">
              <div className="space-y-1.5">
                <Label htmlFor="score_min">Score min</Label>
                <Input
                  id="score_min"
                  type="number"
                  name="score_min"
                  min={0}
                  max={100}
                  defaultValue={scoreMin ?? ""}
                  placeholder="0"
                />
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="score_max">Score max</Label>
                <Input
                  id="score_max"
                  type="number"
                  name="score_max"
                  min={0}
                  max={100}
                  defaultValue={scoreMax ?? ""}
                  placeholder="100"
                />
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="start_date">Start date</Label>
                <Input id="start_date" type="date" name="start_date" defaultValue={startDate ?? ""} />
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="end_date">End date</Label>
                <Input id="end_date" type="date" name="end_date" defaultValue={endDate ?? ""} />
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="source">Source</Label>
                <select
                  id="source"
                  name="source"
                  defaultValue={source ?? "all"}
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                >
                  <option value="all">All sources</option>
                  {sourceChoices.map((option) => (
                    <option key={option} value={option}>
                      {option}
                    </option>
                  ))}
                </select>
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="status">Status</Label>
                <select
                  id="status"
                  name="status"
                  defaultValue={status ?? "all"}
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                >
                  <option value="all">All statuses</option>
                  {statusChoices.map((option) => (
                    <option key={option} value={option}>
                      {option}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            <div className="flex flex-wrap gap-3">
              <Button type="submit">Apply filters</Button>
              <Button variant="outline" asChild>
                <Link href="/macro-radar">Reset</Link>
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      <Section
        title="Priority Radar"
        subtitle="Score 65 and above. Highest urgency for analysis."
        events={priorityEvents}
      />
      <Section
        title="Monitoring"
        subtitle="Score 50-64. Keep on watch."
        events={monitoringEvents}
      />
      <Section
        title="Logged"
        subtitle="Score below 50. Useful for context and history."
        events={loggedEvents}
      />
      <Section
        title="Unscored"
        subtitle="New events that still need significance scoring."
        events={unscoredEvents}
      />
    </div>
  );
}
