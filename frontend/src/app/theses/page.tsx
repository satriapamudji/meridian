import Link from "next/link";

import { getTheses, getThesis, type Thesis } from "@/lib/api";
import { formatDateTime } from "@/lib/format";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

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
  <Link href={`/theses?selected=${thesis.id}`}>
    <Card
      className={`p-3 cursor-pointer hover:shadow-md transition-shadow ${
        isSelected ? "ring-2 ring-primary" : ""
      }`}
    >
      <h4 className="font-medium text-sm">{thesis.title}</h4>
      <div className="flex gap-2 text-xs text-muted-foreground mt-1">
        <span>{thesis.asset_type}</span>
        {thesis.asset_symbol && <span>{thesis.asset_symbol}</span>}
        <span>{formatDate(thesis.updated_at)}</span>
      </div>
    </Card>
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
  <section className="space-y-3">
    <div className="flex justify-between items-center">
      <h2 className="font-semibold">{title}</h2>
      <Badge variant="secondary">{theses.length}</Badge>
    </div>
    {theses.length === 0 ? (
      <p className="text-muted-foreground text-sm">No theses in this category.</p>
    ) : (
      <div className="space-y-2">
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
    <Card className="p-6 lg:col-span-2">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">{title}</h2>
        {!isNew && thesis && (
          <Button variant="outline" size="sm" asChild>
            <a
              href={`${process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000"}/theses/${thesis.id}/export.md`}
              target="_blank"
              rel="noopener noreferrer"
            >
              Export Markdown
            </a>
          </Button>
        )}
      </div>

      <form action={action} method="post" className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-1.5">
            <Label htmlFor="title">Title *</Label>
            <Input
              type="text"
              id="title"
              name="title"
              required
              defaultValue={thesis?.title ?? ""}
            />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="status">Status</Label>
            <select
              id="status"
              name="status"
              defaultValue={thesis?.status ?? "watching"}
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
            >
              <option value="watching">Watching</option>
              <option value="active">Active</option>
              <option value="closed">Closed</option>
            </select>
            <span className="text-xs text-muted-foreground">
              Active requires bear case + invalidation
            </span>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-1.5">
            <Label htmlFor="asset_type">Asset Type *</Label>
            <Input
              type="text"
              id="asset_type"
              name="asset_type"
              required
              placeholder="Gold, Silver, Copper..."
              defaultValue={thesis?.asset_type ?? ""}
            />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="asset_symbol">Asset Symbol</Label>
            <Input
              type="text"
              id="asset_symbol"
              name="asset_symbol"
              placeholder="GC=F, SI=F..."
              defaultValue={thesis?.asset_symbol ?? ""}
            />
          </div>
        </div>

        <div className="space-y-1.5 md:col-span-2">
          <Label htmlFor="core_thesis">Core Thesis *</Label>
          <textarea
            id="core_thesis"
            name="core_thesis"
            required
            placeholder="One paragraph: why this, why now"
            defaultValue={thesis?.core_thesis ?? ""}
            className="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
          />
        </div>

        <div className="space-y-1.5 md:col-span-2">
          <Label htmlFor="trigger_event">Trigger Event</Label>
          <Input
            type="text"
            id="trigger_event"
            name="trigger_event"
            placeholder="What macro event or signal initiated this thesis"
            defaultValue={thesis?.trigger_event ?? ""}
          />
        </div>

        <div className="space-y-1.5 md:col-span-2">
          <Label htmlFor="historical_precedent">Historical Precedent</Label>
          <textarea
            id="historical_precedent"
            name="historical_precedent"
            placeholder="Similar past events and outcomes"
            defaultValue={thesis?.historical_precedent ?? ""}
            className="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-1.5">
            <Label htmlFor="bull_case">Bull Case</Label>
            <textarea
              id="bull_case"
              name="bull_case"
              placeholder="One bullet per line"
              defaultValue={arrayToLines(thesis?.bull_case ?? null)}
              className="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
            />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="bear_case">Bear Case / Counter-Case</Label>
            <textarea
              id="bear_case"
              name="bear_case"
              placeholder="One bullet per line (required for active)"
              defaultValue={arrayToLines(thesis?.bear_case ?? null)}
              className="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-1.5">
            <Label htmlFor="entry_consideration">Entry Consideration</Label>
            <Input
              type="text"
              id="entry_consideration"
              name="entry_consideration"
              placeholder="Price level or condition"
              defaultValue={thesis?.entry_consideration ?? ""}
            />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="target">Target</Label>
            <Input
              type="text"
              id="target"
              name="target"
              placeholder="Price target"
              defaultValue={thesis?.target ?? ""}
            />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="invalidation">Invalidation</Label>
            <Input
              type="text"
              id="invalidation"
              name="invalidation"
              placeholder="What kills this thesis (required for active)"
              defaultValue={thesis?.invalidation ?? ""}
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-1.5">
            <Label htmlFor="vehicle">Vehicle</Label>
            <Input
              type="text"
              id="vehicle"
              name="vehicle"
              placeholder="GLD, SLV, futures..."
              defaultValue={thesis?.vehicle ?? ""}
            />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="position_size">Position Size</Label>
            <Input
              type="text"
              id="position_size"
              name="position_size"
              placeholder="starter, full, etc."
              defaultValue={thesis?.position_size ?? ""}
            />
          </div>
        </div>

        <div className="flex gap-2 pt-4">
          <Button type="submit">{isNew ? "Create Thesis" : "Save Changes"}</Button>
          <Button variant="ghost" asChild>
            <Link href="/theses">Cancel</Link>
          </Button>
        </div>
      </form>

      {!isNew && thesis && thesis.updates.length > 0 && (
        <div className="mt-6 pt-6 border-t">
          <h3 className="text-lg font-semibold mb-4">Updates Log</h3>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Date</TableHead>
                <TableHead>Note</TableHead>
                <TableHead>Price</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {thesis.updates.map((update, idx) => (
                <TableRow key={idx}>
                  <TableCell>{formatDate(update.date)}</TableCell>
                  <TableCell>{update.note}</TableCell>
                  <TableCell>{update.price ?? "—"}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}

      {!isNew && thesis && (
        <div className="mt-6 pt-6 border-t">
          <h3 className="text-lg font-semibold mb-4">Add Update</h3>
          <form
            action={`/api/theses/${thesis.id}/updates`}
            method="post"
            className="flex gap-2 items-end"
          >
            <div className="flex-1 space-y-1.5">
              <Input
                type="text"
                name="note"
                placeholder="Note (required)"
                required
              />
            </div>
            <div className="w-32 space-y-1.5">
              <Input
                type="number"
                name="price"
                placeholder="Price"
                step="any"
              />
            </div>
            <Button type="submit">Add</Button>
          </form>
        </div>
      )}
    </Card>
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
      <Card className="p-6">
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-display font-bold tracking-tight">
              Thesis Workspace
            </h1>
            <p className="text-muted-foreground">
              Track macro theses. Watching → Active (with invalidation) → Closed.
            </p>
          </div>
          <Button asChild>
            <Link href="/theses?mode=new">+ New Thesis</Link>
          </Button>
        </div>
        {error && (
          <div className="bg-destructive/10 text-destructive p-3 rounded-md text-sm mt-4">
            {decodeURIComponent(error)}
          </div>
        )}
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6">
        <div className="lg:col-span-1 space-y-6">
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
