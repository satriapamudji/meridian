import { NextResponse } from "next/server";

import { getApiBaseUrl } from "@/lib/api";

export async function POST(
  request: Request,
  { params }: { params: { thesisId: string } },
) {
  const formData = await request.formData();

  const noteValue = formData.get("note");
  const note = typeof noteValue === "string" ? noteValue.trim() : "";

  if (!note) {
    const errorParam = encodeURIComponent("Note is required");
    return NextResponse.redirect(
      new URL(`/theses?selected=${params.thesisId}&error=${errorParam}`, request.url),
      303,
    );
  }

  const payload: Record<string, unknown> = { note };

  const priceValue = formData.get("price");
  if (priceValue && typeof priceValue === "string" && priceValue.trim()) {
    const parsed = parseFloat(priceValue.trim());
    if (!Number.isNaN(parsed)) {
      payload.price = parsed;
    }
  }

  const response = await fetch(
    `${getApiBaseUrl()}/theses/${params.thesisId}/updates`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    },
  );

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
