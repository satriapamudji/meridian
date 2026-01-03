import { NextResponse } from "next/server";

import { getApiBaseUrl } from "@/lib/api";

export async function POST(
  request: Request,
  { params }: { params: { eventId: string } },
) {
  const response = await fetch(`${getApiBaseUrl()}/events/${params.eventId}/analyze`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ overwrite: false, provider: "local" }),
  });

  if (!response.ok) {
    const message = await response.text();
    return NextResponse.json({ error: message }, { status: response.status });
  }

  return NextResponse.redirect(
    new URL(`/macro-radar/${params.eventId}`, request.url),
    303,
  );
}
