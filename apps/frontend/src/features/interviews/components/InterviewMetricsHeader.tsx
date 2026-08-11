/**
 * What: Top metric overview cards component for HR recruiting campaign health.
 * Why: Displays key metrics (Active Interviews, Agents Working, Candidates Evaluated, Quality Score).
 * Boundaries: Display component only; accepts pre-computed counts via props.
 */

import React from "react";
import { Briefcase, Bot, Users, Award, TrendingUp } from "lucide-react";

interface InterviewMetricsHeaderProps {
  totalActiveCampaigns: number;
  totalCandidatesEvaluated: number;
  averageQualityScore: number;
}

export default function InterviewMetricsHeader({
  totalActiveCampaigns,
  totalCandidatesEvaluated,
  averageQualityScore,
}: InterviewMetricsHeaderProps) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
      {/* Metric 1 */}
      <div className="glass-card rounded-2xl p-5 border border-slate-800 transition-all hover:translate-y-[-2px]">
        <div className="flex items-center justify-between mb-3">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
            Active Campaigns
          </span>
          <div className="w-9 h-9 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
            <Briefcase className="w-5 h-5" />
          </div>
        </div>
        <div className="flex items-baseline justify-between">
          <div className="text-3xl font-extrabold text-white tracking-tight">
            {totalActiveCampaigns}
          </div>
          <span className="text-xs text-emerald-400 font-medium flex items-center gap-0.5">
            <TrendingUp className="w-3.5 h-3.5" /> +2 this week
          </span>
        </div>
        <p className="text-[11px] text-slate-500 mt-1">Sourced & Managed by AI Agents</p>
      </div>

      {/* Metric 2 */}
      <div className="glass-card rounded-2xl p-5 border border-slate-800 transition-all hover:translate-y-[-2px]">
        <div className="flex items-center justify-between mb-3">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
            3-Agent Pipeline Status
          </span>
          <div className="w-9 h-9 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400">
            <Bot className="w-5 h-5" />
          </div>
        </div>
        <div className="flex items-baseline justify-between">
          <div className="text-3xl font-extrabold text-white tracking-tight">Active</div>
          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            Optimal Latency
          </span>
        </div>
        <p className="text-[11px] text-slate-500 mt-1">{"Question → Voice → Grader"}</p>
      </div>

      {/* Metric 3 */}
      <div className="glass-card rounded-2xl p-5 border border-slate-800 transition-all hover:translate-y-[-2px]">
        <div className="flex items-center justify-between mb-3">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
            Candidates Screened
          </span>
          <div className="w-9 h-9 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400">
            <Users className="w-5 h-5" />
          </div>
        </div>
        <div className="flex items-baseline justify-between">
          <div className="text-3xl font-extrabold text-white tracking-tight">
            {totalCandidatesEvaluated}
          </div>
          <span className="text-xs text-slate-400 font-medium">Across all roles</span>
        </div>
        <p className="text-[11px] text-slate-500 mt-1">Transcripts auto-scored</p>
      </div>

      {/* Metric 4 */}
      <div className="glass-card rounded-2xl p-5 border border-slate-800 transition-all hover:translate-y-[-2px]">
        <div className="flex items-center justify-between mb-3">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
            Avg Talent Match Score
          </span>
          <div className="w-9 h-9 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400">
            <Award className="w-5 h-5" />
          </div>
        </div>
        <div className="flex items-baseline justify-between">
          <div className="text-3xl font-extrabold text-white tracking-tight">
            {averageQualityScore}%
          </div>
          <span className="text-xs text-amber-400 font-medium">Target &gt; 80%</span>
        </div>
        <p className="text-[11px] text-slate-500 mt-1">Based on rubric criteria</p>
      </div>
    </div>
  );
}
