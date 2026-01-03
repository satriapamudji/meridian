import Link from "next/link";

import { getTheses, getThesis, type Thesis } from "@/lib/api";
import { formatDateTime } from "@/lib/format";

type SearchParams = Record<string, string | string[] | undefined>;

const getParam = (value: string | string[] | undefined) =>
  Array.isArray(value) ? value[0] : value;

const arrayToLines = (arr: string[] | null): string =>
  arr && arr.length > 0 ? arr.join("\n") : "";

const formatDate = (value: string | null) => {
  if (!value) return "—";
  return formatDateTime(value);
};

const ThesisCard = ({
  thesis,
  isSelected,
}: {
  thesis: Thesis;
  isSelected: boolean;
}) => (
  <Link
    href={`/theses?selected=${thesis.id}`}
    className={`thesis-card${isSelected ? " thesis-card--selected" : ""}`}
  >
    <h4 className="thesis-card__title">{thesis.title}</h4>
    <div className="thesis-card__meta">
      <span>{thesis.asset_type}</span>
      {thesis.asset_symbol && <span>{thesis.asset_symbol}</span>}
      <span>{formatDate(thesis.updated_at)}</span>
    </div>
  </Link>
);

const Section = ({
  title,
  theses,
  selectedId,
}: {
  title: string;
  theses: Thesis[];
  selectedId: string | undefined;
}) => (
  <section className="radar-section">
    <div className="radar-section__header">
      <h2>{title}</h2>
      <span className="count-chip">{theses.length}</span>
    </div>
    {theses.length === 0 ? (
      <p className="empty-state">No theses in this category.</p>
    ) : (
      <div className="event-grid">
        {theses.map((thesis) => (
          <ThesisCard
            key={thesis.id}
            thesis={thesis}
            isSelected={thesis.id === selectedId}
          />
        ))}
      </div>
    )}
  </section>
);

const ThesisForm = ({
  thesis,
  isNew,
}: {
  thesis: Thesis | null;
  isNew: boolean;
}) => {
  const action = isNew ? "/api/theses" : `/api/theses/${thesis?.id}`;
  const title = isNew ? "New Thesis" : "Edit Thesis";

  return (
    <div className="thesis-editor">
      <div className="thesis-editor__header">
        <h2>{title}</h2>
        {!isNew && thesis && (
          <a
            href={`${process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000"}/theses/${thesis.id}/export.md`}
            className="form-actions a"
            target="_blank"
            rel="noopener noreferrer"
          >
            Export Markdown
          </a>
        )}
      </div>

      <form action={action} method="post" className="thesis-form">
        <div className="thesis-form__row">
          <div className="form-field">
            <label htmlFor="title">Title *</label>
            <input
              type="text"
              id="title"
              name="title"
              required
              defaultValue={thesis?.title ?? ""}
            />
          </div>
          <div className="form-field">
            <label htmlFor="status">Status</label>
            <select id="status" name="status" defaultValue={thesis?.status ?? "watching"}>
              <option value="watching">Watching</option>
              <option value="active">Active</option>
              <option value="closed">Closed</option>
            </select>
            <span className="form-hint">
              Active requires bear case + invalidation
            </span>
          </div>
        </div>

        <div className="thesis-form__row">
          <div className="form-field">
            <label htmlFor="asset_type">Asset Type *</label>
            <input
              type="text"
              id="asset_type"
              name="asset_type"
              required
              placeholder="Gold, Silver, Copper..."
              defaultValue={thesis?.asset_type ?? ""}
            />
          </div>
          <div className="form-field">
            <label htmlFor="asset_symbol">Asset Symbol</label>
            <input
              type="text"
              id="asset_symbol"
              name="asset_symbol"
              placeholder="GC=F, SI=F..."
              defaultValue={thesis?.asset_symbol ?? ""}
            />
          </div>
        </div>

        <div className="form-field form-field--full">
          <label htmlFor="core_thesis">Core Thesis *</label>
          <textarea
            id="core_thesis"
            name="core_thesis"
            required
            placeholder="One paragraph: why this, why now"
            defaultValue={thesis?.core_thesis ?? ""}
          />
        </div>

        <div className="form-field form-field--full">
          <label htmlFor="trigger_event">Trigger Event</label>
          <input
            type="text"
            id="trigger_event"
            name="trigger_event"
            placeholder="What macro event or signal initiated this thesis"
            defaultValue={thesis?.trigger_event ?? ""}
          />
        </div>

        <div className="form-field form-field--full">
          <label htmlFor="historical_precedent">Historical Precedent</label>
          <textarea
            id="historical_precedent"
            name="historical_precedent"
            placeholder="Similar past events and outcomes"
            defaultValue={thesis?.historical_precedent ?? ""}
          />
        </div>

        <div className="thesis-form__row">
          <div className="form-field">
            <label htmlFor="bull_case">Bull Case</label>
            <textarea
              id="bull_case"
              name="bull_case"
              placeholder="One bullet per line"
              defaultValue={arrayToLines(thesis?.bull_case ?? null)}
            />
          </div>
          <div className="form-field">
            <label htmlFor="bear_case">Bear Case / Counter-Case</label>
            <textarea
              id="bear_case"
              name="bear_case"
              placeholder="One bullet per line (required for active)"
              defaultValue={arrayToLines(thesis?.bear_case ?? null)}
            />
          </div>
        </div>

        <div className="thesis-form__row">
          <div className="form-field">
            <label htmlFor="entry_consideration">Entry Consideration</label>
            <input
              type="text"
              id="entry_consideration"
              name="entry_consideration"
              placeholder="Price level or condition"
              defaultValue={thesis?.entry_consideration ?? ""}
            />
          </div>
          <div className="form-field">
            <label htmlFor="target">Target</label>
            <input
              type="text"
              id="target"
              name="target"
              placeholder="Price target"
              defaultValue={thesis?.target ?? ""}
            />
          </div>
          <div className="form-field">
            <label htmlFor="invalidation">Invalidation</label>
            <input
              type="text"
              id="invalidation"
              name="invalidation"
              placeholder="What kills this thesis (required for active)"
              defaultValue={thesis?.invalidation ?? ""}
            />
          </div>
        </div>

        <div className="thesis-form__row">
          <div className="form-field">
            <label htmlFor="vehicle">Vehicle</label>
            <input
              type="text"
              id="vehicle"
              name="vehicle"
              placeholder="GLD, SLV, futures..."
              defaultValue={thesis?.vehicle ?? ""}
            />
          </div>
          <div className="form-field">
            <label htmlFor="position_size">Position Size</label>
            <input
              type="text"
              id="position_size"
              name="position_size"
              placeholder="starter, full, etc."
              defaultValue={thesis?.position_size ?? ""}
            />
          </div>
        </div>

        <div className="form-actions">
          <button type="submit">{isNew ? "Create Thesis" : "Save Changes"}</button>
          <Link href="/theses">Cancel</Link>
        </div>
      </form>

      {!isNew && thesis && thesis.updates.length > 0 && (
        <div className="updates-section">
          <h3>Updates Log</h3>
          <table className="updates-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Note</th>
                <th>Price</th>
              </tr>
            </thead>
            <tbody>
              {thesis.updates.map((update, idx) => (
                <tr key={idx}>
                  <td>{formatDate(update.date)}</td>
                  <td>{update.note}</td>
                  <td>{update.price ?? "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {!isNew && thesis && (
        <div className="updates-section">
          <h3>Add Update</h3>
          <form
            action={`/api/theses/${thesis.id}/updates`}
            method="post"
            className="add-update-form"
          >
            <input
              type="text"
              name="note"
              placeholder="Note (required)"
              required
            />
            <input
              type="number"
              name="price"
              placeholder="Price"
              step="any"
            />
            <button type="submit">Add</button>
          </form>
        </div>
      )}
    </div>
  );
};

export default async function ThesesPage({
  searchParams,
}: {
  searchParams?: SearchParams;
}) {
  const selectedId = getParam(searchParams?.selected);
  const mode = getParam(searchParams?.mode);
  const error = getParam(searchParams?.error);
  const isNewMode = mode === "new";

  const theses = await getTheses();

  const watching = theses.filter((t) => t.status === "watching");
  const active = theses.filter((t) => t.status === "active");
  const closed = theses.filter((t) => t.status === "closed");

  let selectedThesis: Thesis | null = null;
  if (selectedId) {
    try {
      selectedThesis = await getThesis(selectedId);
    } catch {
      // Thesis not found, ignore
    }
  }

  const showEditor = isNewMode || selectedThesis !== null;

  return (
    <>
      <section className="page-panel">
        <div className="page-header">
          <div>
            <h1 className="page-title">Thesis Workspace</h1>
            <p className="page-subtitle">
              Track macro theses. Watching → Active (with invalidation) → Closed.
            </p>
          </div>
          <Link href="/theses?mode=new" className="filter-actions">
            <span
              style={{
                padding: "8px 14px",
                borderRadius: "999px",
                background: "var(--accent)",
                color: "#fff",
                fontWeight: 600,
                fontSize: "0.9rem",
              }}
            >
              + New Thesis
            </span>
          </Link>
        </div>
        {error && (
          <div className="error-banner" style={{ marginTop: 16 }}>
            {decodeURIComponent(error)}
          </div>
        )}
      </section>

      <div className="thesis-layout">
        <div className="thesis-sections">
          <Section title="Watching" theses={watching} selectedId={selectedId} />
          <Section title="Active" theses={active} selectedId={selectedId} />
          <Section title="Closed" theses={closed} selectedId={selectedId} />
        </div>

        {showEditor && (
          <ThesisForm thesis={selectedThesis} isNew={isNewMode} />
        )}
      </div>
    </>
  );
}
