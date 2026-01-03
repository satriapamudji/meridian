import { NextResponse } from "next/server";

import { getApiBaseUrl } from "@/lib/api";

/**
 * Parse a multiline textarea value into an array of non-empty strings.
 * Each line becomes one bullet item.
 */
const parseLines = (value: FormDataEntryValue | null): string[] | null => {
  if (!value || typeof value !== "string") {
    return null;
  }
  const lines = value
    .split("\n")
    .map((line) => line.trim())
    .filter((line) => line.length > 0);
  return lines.length > 0 ? lines : null;
};

const parseString = (value: FormDataEntryValue | null): string | null => {
  if (!value || typeof value !== "string") {
    return null;
  }
  const trimmed = value.trim();
  return trimmed.length > 0 ? trimmed : null;
};

export async function POST(request: Request) {
  const formData = await request.formData();

  const payload = {
    title: parseString(formData.get("title")),
    asset_type: parseString(formData.get("asset_type")),
    asset_symbol: parseString(formData.get("asset_symbol")),
    core_thesis: parseString(formData.get("core_thesis")),
    trigger_event: parseString(formData.get("trigger_event")),
    historical_precedent: parseString(formData.get("historical_precedent")),
    bull_case: parseLines(formData.get("bull_case")),
    bear_case: parseLines(formData.get("bear_case")),
    entry_consideration: parseString(formData.get("entry_consideration")),
    target: parseString(formData.get("target")),
    invalidation: parseString(formData.get("invalidation")),
    vehicle: parseString(formData.get("vehicle")),
    position_size: parseString(formData.get("position_size")),
    status: parseString(formData.get("status")) || "watching",
  };

  const response = await fetch(`${getApiBaseUrl()}/theses`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const message = await response.text();
    const errorParam = encodeURIComponent(message);
    return NextResponse.redirect(
      new URL(`/theses?mode=new&error=${errorParam}`, request.url),
      303,
    );
  }

  const created = await response.json();
  return NextResponse.redirect(
    new URL(`/theses?selected=${created.id}`, request.url),
    303,
  );
}
