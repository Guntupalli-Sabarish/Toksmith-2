"use client";

import { useEffect } from "react";
import Link from "next/link";
import {
  Plus,
  Video,
  Zap,
  TrendingUp,
  Clock,
  ArrowUpRight,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { useAuthStore, useProjectsStore } from "@/lib/stores";

const statusColors: Record<string, string> = {
  draft: "bg-muted text-muted-foreground",
  pending: "bg-yellow-500/10 text-yellow-600",
  scraped: "bg-blue-500/10 text-blue-600",
  script_generated: "bg-purple-500/10 text-purple-600",
  audio_generated: "bg-indigo-500/10 text-indigo-600",
  video_generated: "bg-teal-500/10 text-teal-600",
  completed: "bg-green-500/10 text-green-600",
  failed: "bg-red-500/10 text-red-600",
};

export default function DashboardPage() {
  const { stats, fetchStats } = useAuthStore();
  const { projects, fetchProjects, isLoading } = useProjectsStore();

  useEffect(() => {
    fetchStats();
    fetchProjects({ per_page: 5 });
  }, [fetchStats, fetchProjects]);

  const creditsUsedPercent = stats
    ? (stats.credits_used / (stats.credits_used + stats.credits_remaining)) *
      100
    : 0;

  return (
    <div className="space-y-8">
      {/* Welcome Header */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground">
            Create and manage your AI-powered video content
          </p>
        </div>
        <Link href="/dashboard/projects/new">
          <Button size="lg" className="gap-2">
            <Plus className="h-5 w-5" />
            New Project
          </Button>
        </Link>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Total Projects
            </CardTitle>
            <Video className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {stats ? (
              <div className="text-3xl font-bold">{stats.total_projects}</div>
            ) : (
              <Skeleton className="h-9 w-16" />
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Videos Generated
            </CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {stats ? (
              <div className="text-3xl font-bold">
                {stats.total_videos_generated}
              </div>
            ) : (
              <Skeleton className="h-9 w-16" />
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Credits Remaining
            </CardTitle>
            <Zap className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {stats ? (
              <>
                <div className="text-3xl font-bold text-primary">
                  {stats.credits_remaining}
                </div>
                <Progress value={100 - creditsUsedPercent} className="mt-2 h-1.5" />
              </>
            ) : (
              <Skeleton className="h-9 w-16" />
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Subscription
            </CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {stats ? (
              <Badge
                variant="secondary"
                className="text-base capitalize px-3 py-1"
              >
                {stats.subscription_tier}
              </Badge>
            ) : (
              <Skeleton className="h-8 w-20" />
            )}
          </CardContent>
        </Card>
      </div>

      {/* Recent Projects */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle>Recent Projects</CardTitle>
            <CardDescription>
              Your latest video generation projects
            </CardDescription>
          </div>
          <Link href="/dashboard/projects">
            <Button variant="ghost" size="sm" className="gap-1">
              View all
              <ArrowUpRight className="h-4 w-4" />
            </Button>
          </Link>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-4">
              {[...Array(3)].map((_, i) => (
                <div
                  key={i}
                  className="flex items-center justify-between p-4 rounded-lg border"
                >
                  <div className="space-y-2">
                    <Skeleton className="h-5 w-48" />
                    <Skeleton className="h-4 w-32" />
                  </div>
                  <Skeleton className="h-6 w-20" />
                </div>
              ))}
            </div>
          ) : projects.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <div className="rounded-full bg-muted p-4 mb-4">
                <Video className="h-8 w-8 text-muted-foreground" />
              </div>
              <h3 className="text-lg font-semibold mb-1">No projects yet</h3>
              <p className="text-muted-foreground mb-4 max-w-sm">
                Create your first project to start generating amazing videos
              </p>
              <Link href="/dashboard/projects/new">
                <Button>
                  <Plus className="h-4 w-4 mr-2" />
                  Create Project
                </Button>
              </Link>
            </div>
          ) : (
            <div className="space-y-3">
              {projects.map((project) => (
                <Link
                  key={project.id}
                  href={`/dashboard/projects/${project.id}`}
                  className="flex items-center justify-between p-4 rounded-lg border hover:bg-accent/50 transition-colors group"
                >
                  <div className="flex-1 min-w-0">
                    <h4 className="font-medium truncate group-hover:text-primary transition-colors">
                      {project.title || "Untitled Project"}
                    </h4>
                    <p className="text-sm text-muted-foreground truncate">
                      {project.source_url || "No source URL"}
                    </p>
                  </div>
                  <div className="flex items-center gap-3 ml-4">
                    <Badge
                      variant="secondary"
                      className={`capitalize ${statusColors[project.status]}`}
                    >
                      {project.status.replace("_", " ")}
                    </Badge>
                    <ArrowUpRight className="h-4 w-4 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity" />
                  </div>
                </Link>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card className="group cursor-pointer hover:border-primary/50 transition-colors">
          <Link href="/dashboard/projects/new?source=reddit">
            <CardHeader>
              <div className="h-10 w-10 rounded-lg bg-orange-500/10 flex items-center justify-center mb-2 group-hover:bg-orange-500/20 transition-colors">
                <span className="text-lg">🔥</span>
              </div>
              <CardTitle className="text-base">Reddit to Video</CardTitle>
              <CardDescription>
                Turn viral Reddit threads into engaging short videos
              </CardDescription>
            </CardHeader>
          </Link>
        </Card>

        <Card className="group cursor-pointer hover:border-primary/50 transition-colors">
          <Link href="/dashboard/projects/new?source=twitter">
            <CardHeader>
              <div className="h-10 w-10 rounded-lg bg-blue-500/10 flex items-center justify-center mb-2 group-hover:bg-blue-500/20 transition-colors">
                <span className="text-lg">🐦</span>
              </div>
              <CardTitle className="text-base">Twitter to Video</CardTitle>
              <CardDescription>
                Convert Twitter threads into captivating content
              </CardDescription>
            </CardHeader>
          </Link>
        </Card>

        <Card className="group cursor-pointer hover:border-primary/50 transition-colors">
          <Link href="/dashboard/projects/new?source=custom">
            <CardHeader>
              <div className="h-10 w-10 rounded-lg bg-purple-500/10 flex items-center justify-center mb-2 group-hover:bg-purple-500/20 transition-colors">
                <span className="text-lg">✍️</span>
              </div>
              <CardTitle className="text-base">Custom Script</CardTitle>
              <CardDescription>
                Write or paste your own script for video generation
              </CardDescription>
            </CardHeader>
          </Link>
        </Card>
      </div>
    </div>
  );
}
