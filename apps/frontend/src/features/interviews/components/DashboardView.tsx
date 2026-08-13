"use client";

/**
 * What: Main HR Recruiting Dashboard client component container.
 * Why: Manages active campaign state, filtering, creation modal toggles, and modal detail views.
 * Boundaries: Operates on local client state until connected to FastAPI backend OpenAPI client.
 */

import React, { useState } from "react";
import {
  MessageSquarePlus,
  CalendarDays,
  CheckSquare,
  Clock,
  XSquare,
} from "lucide-react";
import { InterviewCampaign } from "../types";
import InterviewCard from "./InterviewCard";
import InterviewDetailDialog from "./InterviewDetailDialog";
import CreateInterviewModal from "./CreateInterviewModal";

const INITIAL_MOCK_CAMPAIGNS: InterviewCampaign[] = Array(12)
  .fill(null)
  .map((_, i) => ({
    id: `campaign-${i}`,
    jobTitle:
      i % 2 === 0
        ? "Marketing Lead officer"
        : i % 3 === 0
          ? "Product manager"
          : "Engineer CTO officer",
    departmentName: "Core",
    targetSeniority: "Senior",
    currentPipelineStage: "COMPLETED",
    activeCandidateCount: 23,
    evaluatedCandidateCount: 11,
    createdAtTimestamp: "11/06/2026",
    agentSummary:
      "Urstanding of the following non-negotiable architectural boundaries for t...",
    questionSuite: [],
    candidatesList: [],
  }));

export default function DashboardView() {
  const [campaignsList, setCampaignsList] = useState<InterviewCampaign[]>(
    INITIAL_MOCK_CAMPAIGNS,
  );
  const [activeTab, setActiveTab] = useState<
    "ALL" | "FINISHED" | "IN_PROGRESS" | "NOT_STARTED"
  >("ALL");
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);

  const handleCampaignCreated = (newCampaign: InterviewCampaign) => {
    setCampaignsList((prevCampaigns) => [newCampaign, ...prevCampaigns]);
  };

  return (
    <main className="max-w-350 mx-auto px-7 pb-7">
      <div className="bg-white rounded-[36px] p-7 lg:p-7 min-h-[80vh]">
        {/* Header Section */}
        <div className="mb-7">
          <div className="flex items-center gap-4.5 mb-2">
            <h1 className="text-xl font-medium text-[#272727] tracking-tight">
              Overview
            </h1>
            <span className="px-3 py-1 bg-[#F6F6F6] text-[#616161] rounded-full text-xs font-medium">
              Tuesday, 12 april 2026
            </span>
          </div>
          <p className="text-[#616161] text-sm font-medium">
            now what &quot;done&quot; looks like: with the fixture correction
            applied
          </p>
        </div>

        {/* Progress & Action Section */}
        <div className="flex items-center gap-7 mb-7">
          <div className="flex items-end gap-1 h-5.5">
            {/* Mock Orange Bar Chart */}
            {[...Array(17)].map((_, i) => (
              <div
                key={i}
                className={`w-1 rounded-full ${i < 13 ? "h-full bg-[#FE6100]" : i < 15 ? "h-full bg-[#FFD3B8]/40" : "h-full bg-[#E9E9E9]"}`}
              />
            ))}
          </div>

          <div className="text-base font-semibold text-gray-900">
            17/36 Interview
          </div>

          <button
            onClick={() => setIsCreateModalOpen(true)}
            className="ml-2 px-4 py-3 bg-white border border-[#d9d9d9] rounded-full text-sm font-medium text-[#272727] flex items-center gap-2 hover:bg-gray-50 transition-colors"
          >
            <MessageSquarePlus className="w-4 h-4" /> Create Interview
          </button>
        </div>

        {/* Tabs Section */}
        <div className="flex items-center gap-7 border-b border-[#F1F1F1] mb-7">
          <button
            onClick={() => setActiveTab("ALL")}
            className={`pb-4 flex items-center gap-2 text-sm font-medium transition-colors relative ${
              activeTab === "ALL"
                ? "text-[#272727]"
                : "text-[#B8B8B8] hover:text-gray-600"
            }`}
          >
            <CheckSquare className="w-3.5 h-3.5" /> All (36)
            {activeTab === "ALL" && (
              <span className="absolute bottom-0 left-0 w-full h-0.5 bg-gray-900" />
            )}
          </button>

          <button
            onClick={() => setActiveTab("FINISHED")}
            className={`pb-4 flex items-center gap-2 text-sm font-medium transition-colors relative ${
              activeTab === "FINISHED"
                ? "text-[#272727]"
                : "text-[#B8B8B8] hover:text-gray-600"
            }`}
          >
            <CalendarDays className="w-3.5 h-3.5" /> Finished (17)
            {activeTab === "FINISHED" && (
              <span className="absolute bottom-0 left-0 w-full h-0.5 bg-gray-900" />
            )}
          </button>

          <button
            onClick={() => setActiveTab("IN_PROGRESS")}
            className={`pb-4 flex items-center gap-2 text-sm font-medium transition-colors relative ${
              activeTab === "IN_PROGRESS"
                ? "text-[#272727]"
                : "text-[#B8B8B8] hover:text-gray-600"
            }`}
          >
            <Clock className="w-3.5 h-3.5" /> In-progressed (9)
            {activeTab === "IN_PROGRESS" && (
              <span className="absolute bottom-0 left-0 w-full h-0.5 bg-gray-900" />
            )}
          </button>

          <button
            onClick={() => setActiveTab("NOT_STARTED")}
            className={`pb-4 flex items-center gap-2 text-sm font-medium transition-colors relative ${
              activeTab === "NOT_STARTED"
                ? "text-[#272727]"
                : "text-[#B8B8B8] hover:text-gray-600"
            }`}
          >
            <XSquare className="w-3.5 h-3.5" /> Not started (3)
            {activeTab === "NOT_STARTED" && (
              <span className="absolute bottom-0 left-0 w-full h-0.5 bg-gray-900" />
            )}
          </button>
        </div>

        {/* Campaigns Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
          {campaignsList.map((campaignItem) => (
            <InterviewCard key={campaignItem.id} campaign={campaignItem} />
          ))}
        </div>

        {/* Deep-linkable Interview Detail Popup Modal driven by ?interview=<id> searchParam */}
        <InterviewDetailDialog interviewCampaignsList={campaignsList} />

        {/* Campaign Creation Modal */}
        <CreateInterviewModal
          isOpen={isCreateModalOpen}
          onClose={() => setIsCreateModalOpen(false)}
          onCampaignCreated={handleCampaignCreated}
        />
      </div>
    </main>
  );
}
