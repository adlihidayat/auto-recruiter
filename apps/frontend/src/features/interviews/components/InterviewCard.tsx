"use client";

/**
 * What: Interactive campaign card displaying targeted role, candidate metrics, pipeline badge, and quick actions.
 * Why: Serves as the primary list element on the HR recruiting dashboard.
 * Boundaries: Operates on props; clicking triggers popup via '?interview=<id>' search parameter.
 */

import React from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Users, Calendar, ArrowRight, Eye } from "lucide-react";
import { InterviewCampaign } from "../types";
import InterviewStatusBadge from "./InterviewStatusBadge";

interface InterviewCardProps {
  campaign: InterviewCampaign;
}

export default function InterviewCard({ campaign }: InterviewCardProps) {
  const router = useRouter();
  const searchParams = useSearchParams();

  const handleOpenDetailModal = () => {
    const currentParams = new URLSearchParams(searchParams.toString());
    currentParams.set("interview", campaign.id);
    router.push(`/?${currentParams.toString()}`, { scroll: false });
  };

  return (
    <div
      onClick={handleOpenDetailModal}
      className="glass-card rounded-2xl p-5 border border-slate-800/80 hover:border-indigo-500/40 transition-all duration-300 cursor-pointer group flex flex-col justify-between"
    >
      <div>
        {/* Top Header */}
        <div className="flex items-start justify-between gap-3 mb-3">
          <div>
            <span className="text-[10px] font-bold uppercase tracking-wider text-indigo-400 px-2 py-0.5 rounded bg-indigo-500/10 border border-indigo-500/20">
              {campaign.departmentName}
            </span>
            <h3 className="text-lg font-bold text-white tracking-tight mt-1.5 group-hover:text-indigo-300 transition-colors">
              {campaign.jobTitle}
            </h3>
          </div>
          <InterviewStatusBadge pipelineStage={campaign.currentPipelineStage} />
        </div>

        <p className="text-xs text-slate-400 line-clamp-2 mb-4">
          {campaign.agentSummary || "Automated technical evaluation & candidate screening pipeline."}
        </p>

        {/* Question suite mini tags */}
        <div className="flex items-center gap-1.5 flex-wrap mb-4">
          <span className="text-[10px] text-slate-500 font-medium">Suite:</span>
          {campaign.questionSuite.slice(0, 3).map((item) => (
            <span
              key={item.id}
              className="text-[10px] px-2 py-0.5 rounded bg-slate-900 text-slate-300 border border-slate-800"
            >
              {item.category}
            </span>
          ))}
          {campaign.questionSuite.length > 3 && (
            <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-900 text-slate-500 border border-slate-800">
              +{campaign.questionSuite.length - 3} more
            </span>
          )}
        </div>
      </div>

      {/* Footer Info & Actions */}
      <div className="pt-4 border-t border-slate-800/60 flex items-center justify-between">
        <div className="flex items-center gap-4 text-xs text-slate-400">
          <span className="flex items-center gap-1">
            <Users className="w-3.5 h-3.5 text-slate-500" />
            <strong className="text-white">{campaign.candidatesList.length}</strong> candidates
          </span>
          <span className="flex items-center gap-1 text-[11px] text-slate-500">
            <Calendar className="w-3 h-3 text-slate-600" />
            {campaign.createdAtTimestamp}
          </span>
        </div>

        <button
          onClick={(e) => {
            e.stopPropagation();
            handleOpenDetailModal();
          }}
          className="px-3 py-1.5 rounded-xl bg-indigo-600/20 hover:bg-indigo-600 border border-indigo-500/30 text-indigo-300 hover:text-white text-xs font-semibold transition-all flex items-center gap-1.5 group-hover:bg-indigo-600 group-hover:text-white shadow-sm"
        >
          <Eye className="w-3.5 h-3.5" /> Details <ArrowRight className="w-3 h-3" />
        </button>
      </div>
    </div>
  );
}
