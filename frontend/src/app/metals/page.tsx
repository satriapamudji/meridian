import { Gem } from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

export default function MetalsPage() {
  return (
    <div className="container mx-auto p-6 max-w-4xl space-y-8">
      <div className="flex items-center gap-3 mb-8">
        <div className="p-3 bg-primary/10 rounded-full">
          <Gem className="h-8 w-8 text-primary" />
        </div>
        <h1 className="text-3xl font-display font-bold tracking-tight">
          Metals Intelligence
        </h1>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Coming Soon</CardTitle>
          <CardDescription>
            Intelligence platform for precious and industrial metals
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">
            This space will surface metals knowledge base insights, price ratios,
            and supply/demand analysis once the UI lands.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
