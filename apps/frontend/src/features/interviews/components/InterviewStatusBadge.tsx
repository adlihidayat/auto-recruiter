/**
 * What: Visual status badge for tracking AI agent pipeline execution stages.
 * Why: Communicates pipeline state (question-maker, live interviewer, grader evaluation, completed) with badges and color coding.
 * Boundaries: Does not mutate state or trigger backend pipeline runs directly.
 */

import React from "react";
import { Sparkles, Mic, FileText, CheckCircle2, AlertCircle } from "lucide-react";
import { PipelineStage } from "../types";

interface InterviewStatusBadgeProps {
  pipelineStage: PipelineStage;
}

export default function InterviewStatusBadge({ pipelineStage }: InterviewStatusBadgeProps) {
  switch (pipelineStage) {
    case "QUESTION_MAKER":
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-amber-500/10 text-amber-400 border border-amber-500/20">
          <Sparkles className="w-3.5 h-3.5 animate-spin" />
          <span>Generating Suite (Agent 1)</span>
        </span>
      );
    case "INTERVIEWER_LIVE":
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
          <Mic className="w-3.5 h-3.5 animate-pulse" />
          <span>Live Interviews (Agent 2)</span>
        </span>
      );
    case "GRADER_EVALUATING":
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-purple-500/10 text-purple-400 border border-purple-500/20">
          <FileText className="w-3.5 h-3.5 animate-bounce" />
          <span>Grading Transcripts (Agent 3)</span>
        </span>
      );
    case "COMPLETED":
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
          <CheckCircle2 className="w-3.5 h-3.5" />
          <span>Pipeline Complete</span>
        </span>
      );
    case "FAILED":
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-rose-500/10 text-rose-400 border border-rose-500/20">
          <AlertCircle className="w-3.5 h-3.5" />
          <span>Pipeline Error</span>
        </span>
      );
  }
}
