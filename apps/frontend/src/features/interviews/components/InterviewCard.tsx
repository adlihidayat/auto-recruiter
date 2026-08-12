"use client";

/**
 * What: Interactive campaign card displaying targeted role, candidate metrics, pipeline badge, and quick actions.
 * Why: Serves as the primary list element on the HR recruiting dashboard.
 * Boundaries: Operates on props; clicking triggers popup via '?interview=<id>' search parameter.
 */

import React from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Users, CalendarDays, Clock } from "lucide-react";
import { InterviewCampaign } from "../types";

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
      className="bg-white rounded-2xl p-4.5 border border-[#F1F1F1] hover:border-gray-300 transition-all duration-200 cursor-pointer flex flex-col justify-between"
    >
      <div className="border-b border-[#F1F1F1]">
        {/* Top Header */}
        <h3 className="text-base font-semibold text-[#272727] tracking-tight mb-1 line-clamp-1">
          {campaign.jobTitle}
        </h3>

        <p className="text-sm font-medium text-[#616161] line-clamp-2 leading-relaxed mb-4.5">
          {campaign.agentSummary}
        </p>

        {/* Progress Bar */}
        <div className="mb-4.5">
          <div className="flex items-center justify-between text-xs font-semibold text-[#616161] mb-2">
            <span>Progress</span>
            <span>11/23</span>
          </div>
          <div className="h-2.5 w-full bg-gray-100 rounded-full overflow-hidden">
            <div
              className="h-full bg-[#ff6b2b] rounded-full"
              style={{ width: "48%" }}
            />
          </div>
        </div>

        {/* Candidates Avatars */}
        <div className="flex items-center gap-2 mb-4.5">
          <div className="px-2.5 py-2 bg-[#F4F4F4] rounded-lg text-xs font-medium text-[#272727] flex items-center gap-1.5">
            <Users className="w-3 h-3" />
            <span>Candidates</span>
          </div>
          <div className="h-5 w-px bg-[#F1F1F1]"></div>
          <div className="flex -space-x-2">
            <div className="w-6.5 h-6.5 rounded-lg bg-emerald-400 border-2 border-white z-30" />
            <div className="w-6.5 h-6.5 rounded-lg bg-blue-400 border-2 border-white z-20" />
            <div className="w-6.5 h-6.5 rounded-lg bg-amber-400 border-2 border-white z-10" />
            <div className="w-6.5 h-6.5 rounded-lg bg-purple-400 border-2 border-white z-0" />
          </div>
        </div>
      </div>

      {/* Footer Info & Actions */}
      <div className="flex items-center gap-3 text-xs font-semibold text-[#616161] mt-4.5">
        <span className="flex items-center gap-1">
          <Users className="w-2.5 h-2.5 text-[#616161]" />
          11/23
        </span>
        <span className="flex items-center gap-1">
          <CalendarDays className="w-2.5 h-2.5 text-[#616161]" />
          11/06/2026
        </span>
        <span className="flex items-center gap-1">
          <Clock className="w-2.5 h-2.5 text-[#616161]" />
          45m
        </span>
      </div>
    </div>
  );
}
