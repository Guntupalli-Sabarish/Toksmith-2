"use client";

import { RedditContentViewer } from "./reddit-content-viewer";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { FileText, Globe, AlertCircle } from "lucide-react";

interface ScrapedContentProps {
  data: Record<string, unknown> | null;
  sourceType?: string | null;
}

function GenericContentViewer({ data }: { data: Record<string, unknown> }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base flex items-center gap-2">
          <Globe className="h-4 w-4" />
          Scraped Content
        </CardTitle>
        <CardDescription>Raw content extracted from the source</CardDescription>
      </CardHeader>
      <CardContent>
        <pre className="text-xs bg-muted p-4 rounded-lg overflow-auto max-h-96 whitespace-pre-wrap">
          {JSON.stringify(data, null, 2)}
        </pre>
      </CardContent>
    </Card>
  );
}

export function ScrapedContent({ data, sourceType }: ScrapedContentProps) {
  if (!data) {
    return (
      <Card>
        <CardContent className="py-12">
          <div className="text-center text-muted-foreground">
            <FileText className="h-12 w-12 mx-auto mb-3 opacity-50" />
            <p className="font-medium">No content scraped yet</p>
            <p className="text-sm mt-1">
              Click &quot;Scrape Content&quot; to extract content from the source URL
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Determine which viewer to use based on source type
  const source = sourceType || (data.source as string);

  if (source === "reddit") {
    try {
      return <RedditContentViewer data={data as any} />;
    } catch {
      return <GenericContentViewer data={data} />;
    }
  }

  // Twitter/X content
  if (source === "twitter") {
    // TODO: Create TwitterContentViewer
    return <GenericContentViewer data={data} />;
  }

  // StackOverflow content
  if (source === "stackoverflow") {
    // TODO: Create StackOverflowContentViewer
    return <GenericContentViewer data={data} />;
  }

  // Fallback to generic viewer
  return <GenericContentViewer data={data} />;
}
