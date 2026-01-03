import Link from "next/link";

import { getEvent } from "@/lib/api";
import { formatDateTime, formatScoreBand, formatStatus } from "@/lib/format";

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
      <section className="page-panel">
        <div className="page-header">
          <div>
            <Link href="/macro-radar" className="back-link">
              Back to Macro Radar
            </Link>
            <h1 className="page-title">{event.raw.headline}</h1>
            <p className="page-subtitle">
              {event.raw.source} • {formatDateTime(event.raw.published_at)}
            </p>
          </div>
          <div className="detail-score">
            <span className="detail-score__label">Score</span>
            <span className="detail-score__value">{getScoreValue(score)}</span>
            <span className="detail-score__band">{scoreBand}</span>
          </div>
        </div>
        <div className="detail-meta">
          <div>
            <span className="meta-label">Status</span>
            <span>{formatStatus(event.raw.status)}</span>
          </div>
          <div>
            <span className="meta-label">Event type</span>
            <span>{event.raw.event_type ?? "unclassified"}</span>
          </div>
          <div>
            <span className="meta-label">Regions</span>
            <span>{toLabelList(event.raw.regions)}</span>
          </div>
          <div>
            <span className="meta-label">Entities</span>
            <span>{toLabelList(event.raw.entities)}</span>
          </div>
        </div>
        {!analysisPresent && (
          <div className="analysis-callout">
            <div>
              <h3>Analysis missing</h3>
              <p>Trigger analysis to generate raw facts and interpretation.</p>
            </div>
            {canAnalyze ? (
              <form action={`/api/events/${event.raw.id}/analyze`} method="post">
                <button type="submit">Analyze</button>
              </form>
            ) : (
              <span className="analysis-note">Analysis is enabled for priority events.</span>
            )}
          </div>
        )}
      </section>

      <section className="detail-section detail-section--raw">
        <div className="detail-section__header">
          <h2>Raw facts</h2>
          <p>Uninterpreted facts extracted from the source.</p>
        </div>
        {event.analysis.raw_facts && event.analysis.raw_facts.length > 0 ? (
          <ul className="detail-list">
            {event.analysis.raw_facts.map((fact) => (
              <li key={fact}>{fact}</li>
            ))}
          </ul>
        ) : (
          <p className="empty-state">No raw facts available yet.</p>
        )}
        {event.raw.full_text ? (
          <div className="detail-source">
            <h3>Source text</h3>
            <p>{event.raw.full_text}</p>
          </div>
        ) : null}
      </section>

      <section className="detail-section detail-section--analysis">
        <div className="detail-section__header">
          <h2>Interpretation</h2>
          <p>Analysis and downstream implications derived from the event.</p>
        </div>
        <div className="detail-grid">
          <article className="detail-card">
            <h3>Significance scoring</h3>
            <dl>
              <div>
                <dt>Score</dt>
                <dd>{getScoreValue(score)}</dd>
              </div>
              <div>
                <dt>Band</dt>
                <dd>{scoreBand}</dd>
              </div>
              <div>
                <dt>Priority threshold</dt>
                <dd>65+</dd>
              </div>
              <div>
                <dt>Priority flag</dt>
                <dd>{event.raw.priority_flag ? "yes" : "no"}</dd>
              </div>
            </dl>
          </article>

          <article className="detail-card detail-card--wide">
            <h3>Metal impacts</h3>
            {hasMetalImpacts ? (
              <div className="detail-table">
                {Object.entries(metalImpacts).map(([metal, impact]) => (
                  <div key={metal} className="detail-table__row">
                    <div className="detail-table__cell detail-table__cell--title">
                      {metal.toUpperCase()}
                    </div>
                    <div className="detail-table__cell">{impact.direction}</div>
                    <div className="detail-table__cell">{impact.magnitude}</div>
                    <div className="detail-table__cell">{impact.driver}</div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="empty-state">No metal impact analysis yet.</p>
            )}
          </article>

          <article className="detail-card">
            <h3>Historical precedent</h3>
            <p>{event.analysis.interpretation.historical_precedent ?? "None yet."}</p>
            {caseId ? (
              <Link className="inline-link" href={`/cases/${caseId}`}>
                View case {caseId}
              </Link>
            ) : null}
          </article>

          <article className="detail-card">
            <h3>Counter-case</h3>
            <p>{event.analysis.interpretation.counter_case ?? "No counter-case yet."}</p>
          </article>

          <article className="detail-card detail-card--wide">
            <h3>Crypto transmission</h3>
            {hasCryptoTransmission ? (
              <dl>
                <div>
                  <dt>Exists</dt>
                  <dd>{cryptoTransmission?.exists ? "yes" : "no"}</dd>
                </div>
                <div>
                  <dt>Strength</dt>
                  <dd>{cryptoTransmission?.strength ?? "unknown"}</dd>
                </div>
                <div>
                  <dt>Relevant assets</dt>
                  <dd>
                    {cryptoTransmission?.relevant_assets.length
                      ? cryptoTransmission.relevant_assets.join(", ")
                      : "none"}
                  </dd>
                </div>
              </dl>
            ) : (
              <p className="empty-state">No crypto transmission path recorded.</p>
            )}
            {cryptoTransmission?.path ? (
              <p className="detail-note">{cryptoTransmission.path}</p>
            ) : null}
          </article>
        </div>
      </section>
    </>
  );
}
