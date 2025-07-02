"use client";

import { ContentScheduler } from "@/components/ContentScheduler";

export default function SchedulerPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-foreground mb-2">Content Scheduler</h1>
        <p className="text-muted-foreground">Plan and schedule your content across all platforms</p>
      </div>
      <ContentScheduler />
    </div>
  );
}