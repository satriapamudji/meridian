import Link from "next/link";

import { getEvents, type MacroEvent } from "@/lib/api";
import { formatDateTime, formatStatus } from "@/lib/format";

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

const getScore = (event: MacroEvent) => event.raw.significance_score ?? 0;

const filterByDate = (
  event: MacroEvent,
  start: Date | undefined,
  end: Date | undefined,
) => {
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

const EventCard = ({ event }: { event: MacroEvent }) => {
  const score = getScore(event);
  const isPriority = score >= 65;
  return (
    <Link
      href={`/macro-radar/${event.raw.id}`}
      className={`event-card${isPriority ? " event-card--priority" : ""}`}
    >
      <div className="event-card__header">
        <span className="event-score">{score}</span>
        <span className="event-source">{event.raw.source}</span>
      </div>
      <h3>{event.raw.headline}</h3>
      <div className="event-card__meta">
        <span>{formatDateTime(event.raw.published_at)}</span>
        <span className="event-status">Analysis: {formatStatus(event.raw.status)}</span>
      </div>
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
  <section className="radar-section">
    <div className="radar-section__header">
      <div>
        <h2>{title}</h2>
        <p>{subtitle}</p>
      </div>
      <span className="count-chip">{events.length}</span>
    </div>
    {events.length === 0 ? (
      <p className="empty-state">No events match this section.</p>
    ) : (
      <div className="event-grid">
        {events.map((event) => (
          <EventCard key={event.raw.id} event={event} />
        ))}
      </div>
    )}
  </section>
);

export default async function MacroRadarPage({
  searchParams,
}: {
  searchParams?: SearchParams;
}) {
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
    const score = getScore(event);
    if (scoreMin !== undefined && score < scoreMin) {
      return false;
    }
    if (scoreMax !== undefined && score > scoreMax) {
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

  const priorityEvents = filteredEvents.filter((event) => getScore(event) >= 65);
  const monitoringEvents = filteredEvents.filter((event) => {
    const score = getScore(event);
    return score >= 50 && score <= 64;
  });
  const loggedEvents = filteredEvents.filter((event) => getScore(event) < 50);

  return (
    <>
      <section className="page-panel">
        <div className="page-header">
          <div>
            <h1 className="page-title">Macro Radar</h1>
            <p className="page-subtitle">
              Macro events organized by significance. Scores and status come from the backend.
            </p>
          </div>
          <span className="count-chip">{filteredEvents.length} events</span>
        </div>
        <form className="filters-panel" method="get">
          <div className="filters-grid">
            <label className="filter-field">
              <span>Score min</span>
              <input
                type="number"
                name="score_min"
                min={0}
                max={100}
                defaultValue={scoreMin ?? ""}
                placeholder="0"
              />
            </label>
            <label className="filter-field">
              <span>Score max</span>
              <input
                type="number"
                name="score_max"
                min={0}
                max={100}
                defaultValue={scoreMax ?? ""}
                placeholder="100"
              />
            </label>
            <label className="filter-field">
              <span>Start date</span>
              <input type="date" name="start_date" defaultValue={startDate ?? ""} />
            </label>
            <label className="filter-field">
              <span>End date</span>
              <input type="date" name="end_date" defaultValue={endDate ?? ""} />
            </label>
            <label className="filter-field">
              <span>Source</span>
              <select name="source" defaultValue={source ?? "all"}>
                <option value="all">All sources</option>
                {sourceChoices.map((option) => (
                  <option key={option} value={option}>
                    {option}
                  </option>
                ))}
              </select>
            </label>
            <label className="filter-field">
              <span>Status</span>
              <select name="status" defaultValue={status ?? "all"}>
                <option value="all">All statuses</option>
                {statusChoices.map((option) => (
                  <option key={option} value={option}>
                    {option}
                  </option>
                ))}
              </select>
            </label>
          </div>
          <div className="filter-actions">
            <button type="submit">Apply filters</button>
            <Link href="/macro-radar" className="filter-reset">
              Reset
            </Link>
          </div>
        </form>
      </section>

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
    </>
  );
}
