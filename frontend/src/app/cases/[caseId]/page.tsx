import Link from "next/link";
import { ArrowLeft } from "lucide-react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export default function CaseDetailPage({ params }: { params: { caseId: string } }) {
  return (
    <div className="space-y-6">
      <Link
        href="/macro-radar"
        className="text-sm text-muted-foreground hover:text-foreground inline-flex items-center gap-2"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to Macro Radar
      </Link>

      <Card>
        <CardHeader>
          <CardTitle className="font-display text-3xl tracking-tight">
            Historical Case: {params.caseId}
          </CardTitle>
          <CardDescription>
            The case library UI is not implemented yet.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            This link is generated from event analysis. The next step is to add backend case
            endpoints (browse + detail) and render the structured case data here.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
