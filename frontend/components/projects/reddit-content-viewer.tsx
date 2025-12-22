"use client";

import { useState } from "react";
import {
  ArrowBigUp,
  MessageSquare,
  ChevronDown,
  ChevronUp,
  ExternalLink,
  User,
  Clock,
} from "lucide-react";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { ScrollArea } from "@/components/ui/scroll-area";

interface RedditComment {
  id: string;
  author: string;
  content: string;
  upvotes: number;
  timestamp: string | null;
  replies?: RedditComment[];
}

interface RedditScrapedData {
  url: string;
  title: string;
  author: string;
  source: string;
  content: string;
  comments?: RedditComment[];
}

interface RedditContentViewerProps {
  data: RedditScrapedData;
}

function CommentItem({
  comment,
  depth = 0,
}: {
  comment: RedditComment;
  depth?: number;
}) {
  const [showReplies, setShowReplies] = useState(depth < 2);
  const hasReplies = comment.replies && comment.replies.length > 0;

  // Skip AutoModerator comments
  if (comment.author === "AutoModerator") {
    return null;
  }

  return (
    <div
      className={`${depth > 0 ? "ml-4 pl-4 border-l-2 border-muted" : ""}`}
    >
      <div className="py-3">
        <div className="flex items-center gap-2 mb-2">
          <Avatar className="h-6 w-6">
            <AvatarFallback className="text-xs bg-primary/10 text-primary">
              {comment.author.charAt(0).toUpperCase()}
            </AvatarFallback>
          </Avatar>
          <span className="text-sm font-medium text-foreground">
            u/{comment.author}
          </span>
          <div className="flex items-center gap-1 text-muted-foreground">
            <ArrowBigUp className="h-3 w-3" />
            <span className="text-xs">{comment.upvotes}</span>
          </div>
        </div>
        <p className="text-sm text-muted-foreground leading-relaxed">
          {comment.content}
        </p>
        {hasReplies && (
          <Button
            variant="ghost"
            size="sm"
            className="mt-2 h-6 text-xs px-2"
            onClick={() => setShowReplies(!showReplies)}
          >
            {showReplies ? (
              <>
                <ChevronUp className="h-3 w-3 mr-1" />
                Hide {comment.replies!.length} replies
              </>
            ) : (
              <>
                <ChevronDown className="h-3 w-3 mr-1" />
                Show {comment.replies!.length} replies
              </>
            )}
          </Button>
        )}
      </div>
      {hasReplies && showReplies && (
        <div className="space-y-0">
          {comment.replies!.map((reply) => (
            <CommentItem key={reply.id} comment={reply} depth={depth + 1} />
          ))}
        </div>
      )}
    </div>
  );
}

export function RedditContentViewer({ data }: RedditContentViewerProps) {
  const [showAllComments, setShowAllComments] = useState(false);
  const filteredComments =
    data.comments?.filter((c) => c.author !== "AutoModerator") || [];
  const displayComments = showAllComments
    ? filteredComments
    : filteredComments.slice(0, 5);

  return (
    <div className="space-y-4">
      {/* Post Header */}
      <Card className="overflow-hidden">
        <CardHeader className="pb-3">
          <div className="flex items-center gap-2 mb-2">
            <Badge variant="secondary" className="bg-orange-500/10 text-orange-600">
              r/recruitinghell
            </Badge>
            <span className="text-xs text-muted-foreground">•</span>
            <div className="flex items-center gap-1 text-muted-foreground">
              <User className="h-3 w-3" />
              <span className="text-xs">Posted by u/{data.author}</span>
            </div>
          </div>
          <h3 className="text-lg font-semibold leading-tight">{data.title}</h3>
        </CardHeader>
        <CardContent className="pt-0">
          <p className="text-sm text-muted-foreground leading-relaxed whitespace-pre-line">
            {data.content}
          </p>
          <div className="flex items-center gap-4 mt-4 pt-3 border-t">
            <a
              href={data.url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1 text-xs text-primary hover:underline"
            >
              <ExternalLink className="h-3 w-3" />
              View on Reddit
            </a>
            <div className="flex items-center gap-1 text-xs text-muted-foreground">
              <MessageSquare className="h-3 w-3" />
              {filteredComments.length} comments
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Comments Section */}
      {filteredComments.length > 0 && (
        <Card>
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <h4 className="text-sm font-semibold flex items-center gap-2">
                <MessageSquare className="h-4 w-4" />
                Top Comments
              </h4>
              <Badge variant="outline" className="text-xs">
                {filteredComments.length} total
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="pt-0">
            <ScrollArea className={showAllComments ? "max-h-96" : ""}>
              <div className="divide-y divide-muted">
                {displayComments.map((comment) => (
                  <CommentItem key={comment.id} comment={comment} />
                ))}
              </div>
            </ScrollArea>
            {filteredComments.length > 5 && (
              <Button
                variant="ghost"
                className="w-full mt-2"
                onClick={() => setShowAllComments(!showAllComments)}
              >
                {showAllComments ? (
                  <>
                    <ChevronUp className="h-4 w-4 mr-2" />
                    Show Less
                  </>
                ) : (
                  <>
                    <ChevronDown className="h-4 w-4 mr-2" />
                    Show {filteredComments.length - 5} More Comments
                  </>
                )}
              </Button>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
