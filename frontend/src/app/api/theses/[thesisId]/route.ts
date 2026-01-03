import { NextResponse } from "next/server";

import { getApiBaseUrl } from "@/lib/api";

/**
 * Parse a multiline textarea value into an array of non-empty strings.
 * Each line becomes one bullet item.
 */
const parseLines = (value: FormDataEntryValue | null): string[] | undefined => {
  if (!value || typeof value !== "string") {
    return undefined;
  }
  const lines = value
    .split("\n")
    .map((line) => line.trim())
    .filter((line) => line.length > 0);
  return lines.length > 0 ? lines : undefined;
};

const parseString = (value: FormDataEntryValue | null): string | undefined => {
  if (!value || typeof value !== "string") {
    return undefined;
  }
  const trimmed = value.trim();
  return trimmed.length > 0 ? trimmed : undefined;
};

export async function POST(
  request: Request,
  { params }: { params: { thesisId: string } },
) {
  const formData = await request.formData();

  // Build payload with only fields that were submitted
  const payload: Record<string, unknown> = {};

  const title = parseString(formData.get("title"));
  if (title !== undefined) payload.title = title;

  const asset_type = parseString(formData.get("asset_type"));
  if (asset_type !== undefined) payload.asset_type = asset_type;

  const asset_symbol = parseString(formData.get("asset_symbol"));
  if (asset_symbol !== undefined) payload.asset_symbol = asset_symbol;

  const core_thesis = parseString(formData.get("core_thesis"));
  if (core_thesis !== undefined) payload.core_thesis = core_thesis;

  const trigger_event = parseString(formData.get("trigger_event"));
  if (trigger_event !== undefined) payload.trigger_event = trigger_event;

  const historical_precedent = parseString(formData.get("historical_precedent"));
  if (historical_precedent !== undefined) payload.historical_precedent = historical_precedent;

  const bull_case = parseLines(formData.get("bull_case"));
  if (bull_case !== undefined) payload.bull_case = bull_case;

  const bear_case = parseLines(formData.get("bear_case"));
  if (bear_case !== undefined) payload.bear_case = bear_case;

  const entry_consideration = parseString(formData.get("entry_consideration"));
  if (entry_consideration !== undefined) payload.entry_consideration = entry_consideration;

  const target = parseString(formData.get("target"));
  if (target !== undefined) payload.target = target;

  const invalidation = parseString(formData.get("invalidation"));
  if (invalidation !== undefined) payload.invalidation = invalidation;

  const vehicle = parseString(formData.get("vehicle"));
  if (vehicle !== undefined) payload.vehicle = vehicle;

  const position_size = parseString(formData.get("position_size"));
  if (position_size !== undefined) payload.position_size = position_size;

  const status = parseString(formData.get("status"));
  if (status !== undefined) payload.status = status;

  const response = await fetch(`${getApiBaseUrl()}/theses/${params.thesisId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const message = await response.text();
    const errorParam = encodeURIComponent(message);
    return NextResponse.redirect(
      new URL(`/theses?selected=${params.thesisId}&error=${errorParam}`, request.url),
      303,
    );
  }

  return NextResponse.redirect(
    new URL(`/theses?selected=${params.thesisId}`, request.url),
    303,
  );
}
