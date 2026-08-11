"use client";

/**
 * What: Main HR Recruiting Dashboard client component container.
 * Why: Manages active campaign state, filtering, creation modal toggles, and modal detail views.
 * Boundaries: Operates on local client state until connected to FastAPI backend OpenAPI client.
 */

import React, { useState } from "react";
import { Plus, Search, Bot, CheckCircle2 } from "lucide-react";
import { InterviewCampaign } from "../types";
import InterviewMetricsHeader from "./InterviewMetricsHeader";
import InterviewCard from "./InterviewCard";
import InterviewDetailDialog from "./InterviewDetailDialog";
import CreateInterviewModal from "./CreateInterviewModal";

const INITIAL_MOCK_CAMPAIGNS: InterviewCampaign[] = [
  {
    id: "campaign-1",
    jobTitle: "Senior Python & FastAPI Engineer",
    departmentName: "Core Backend",
    targetSeniority: "Senior",
    currentPipelineStage: "COMPLETED",
    activeCandidateCount: 3,
    evaluatedCandidateCount: 5,
    createdAtTimestamp: "2 days ago",
    agentSummary:
      "Question-Maker Agent generated 5 system design & async Python scenarios. Candidates evaluated by Grader Agent with high technical depth scores.",
    questionSuite: [
      {
        id: "q-1",
        category: "FastAPI / Async",
        questionText: "How do dependency injection context managers handle connection pooling in FastAPI under heavy concurrency?",
        difficultyLevel: "Hard",
        targetSkill: "Async IO",
      },
      {
        id: "q-2",
        category: "System Design",
        questionText: "Design a fault-tolerant message queue consumer loop for processing audio packets in real-time.",
        difficultyLevel: "Staff",
        targetSkill: "Distributed Systems",
      },
    ],
    candidatesList: [
      {
        id: "cand-1",
        fullName: "Alex Rivera",
        emailAddress: "alex.rivera@techdev.io",
        status: "Passed",
        overallScore: 92,
        technicalDepthScore: 95,
        communicationScore: 88,
        interviewCompletedAt: "Yesterday",
      },
      {
        id: "cand-2",
        fullName: "Samantha Vance",
        emailAddress: "samantha.v@cloudsystems.com",
        status: "Passed",
        overallScore: 86,
        technicalDepthScore: 87,
        communicationScore: 84,
        interviewCompletedAt: "2 days ago",
      },
    ],
  },
  {
    id: "campaign-2",
    jobTitle: "AI Agent & LangGraph Specialist",
    departmentName: "AI / ML Team",
    targetSeniority: "Lead",
    currentPipelineStage: "INTERVIEWER_LIVE",
    activeCandidateCount: 4,
    evaluatedCandidateCount: 2,
    createdAtTimestamp: "1 day ago",
    agentSummary:
      "Interviewer Agent actively running live voice interviews via LiveKit. Automated guardrails active against prompt injection.",
    questionSuite: [
      {
        id: "q-3",
        category: "LangGraph State Machine",
        questionText: "Explain conditional routing mechanisms and state persistence across cyclical LangGraph execution graphs.",
        difficultyLevel: "Hard",
        targetSkill: "LangGraph",
      },
      {
        id: "q-4",
        category: "Guardrails & Safety",
        questionText: "How do you implement input classification guards to prevent indirect prompt injection in agentic tool calling?",
        difficultyLevel: "Hard",
        targetSkill: "AI Safety",
      },
    ],
    candidatesList: [
      {
        id: "cand-3",
        fullName: "David Chen",
        emailAddress: "d.chen@ai-labs.org",
        status: "In_Progress",
      },
      {
        id: "cand-4",
        fullName: "Elena Rostova",
        emailAddress: "elena.r@neuralcore.io",
        status: "Evaluated",
        overallScore: 89,
        technicalDepthScore: 91,
        communicationScore: 86,
        interviewCompletedAt: "3 hours ago",
      },
    ],
  },
  {
    id: "campaign-3",
    jobTitle: "Fullstack Next.js 15 Engineer",
    departmentName: "Product",
    targetSeniority: "Mid-Level",
    currentPipelineStage: "QUESTION_MAKER",
    activeCandidateCount: 2,
    evaluatedCandidateCount: 0,
    createdAtTimestamp: "4 hours ago",
    agentSummary:
      "Agent 1 (Question Maker) synthesizing React Server Components, Suspense boundary, and Tailwind v4 evaluation scenarios.",
    questionSuite: [
      {
        id: "q-5",
        category: "Next.js App Router",
        questionText: "Explain how Server Components handle async searchParams destructuring and edge middleware auth routing.",
        difficultyLevel: "Medium",
        targetSkill: "Next.js 15",
      },
    ],
    candidatesList: [
      {
        id: "cand-5",
        fullName: "Marcus Brody",
        emailAddress: "marcus.b@devstudio.com",
        status: "Invited",
      },
    ],
  },
];

export default function DashboardView() {
  const [campaignsList, setCampaignsList] = useState<InterviewCampaign[]>(INITIAL_MOCK_CAMPAIGNS);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedFilter, setSelectedFilter] = useState<"ALL" | "LIVE" | "COMPLETED">("ALL");
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);

  const handleCampaignCreated = (newCampaign: InterviewCampaign) => {
    setCampaignsList((prevCampaigns) => [newCampaign, ...prevCampaigns]);
  };

  const filteredCampaigns = campaignsList.filter((campaign) => {
    const matchesSearch =
      campaign.jobTitle.toLowerCase().includes(searchQuery.toLowerCase()) ||
      campaign.departmentName.toLowerCase().includes(searchQuery.toLowerCase());

    if (!matchesSearch) return false;

    if (selectedFilter === "LIVE") return campaign.currentPipelineStage === "INTERVIEWER_LIVE";
    if (selectedFilter === "COMPLETED") return campaign.currentPipelineStage === "COMPLETED";
    return true;
  });

  const totalActive = campaignsList.length;
  const totalScreened = campaignsList.reduce(
    (accum, campaign) => accum + campaign.candidatesList.length,
    0
  );

  return (
    <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Top Banner / Hero */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-8">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              Recruiting Dashboard
            </h1>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center gap-1">
              <CheckCircle2 className="w-3 h-3" /> Live Operations
            </span>
          </div>
          <p className="text-xs sm:text-sm text-slate-400">
            Monitor AI agent workflows, launch interview campaigns, and observe live candidate sessions.
          </p>
        </div>

        <button
          onClick={() => setIsCreateModalOpen(true)}
          className="px-4 py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 via-purple-600 to-indigo-700 hover:from-indigo-500 hover:to-purple-500 text-white text-xs font-semibold shadow-lg shadow-indigo-600/30 transition-all flex items-center gap-2 cursor-pointer shrink-0"
        >
          <Plus className="w-4 h-4" /> New AI Campaign
        </button>
      </div>

      {/* Metric Overview Cards */}
      <InterviewMetricsHeader
        totalActiveCampaigns={totalActive}
        totalCandidatesEvaluated={totalScreened}
        averageQualityScore={89}
      />

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4 mb-6">
        <div className="flex items-center gap-2 overflow-x-auto pb-1 sm:pb-0">
          <button
            onClick={() => setSelectedFilter("ALL")}
            className={`px-3.5 py-1.5 rounded-xl text-xs font-medium transition-all ${
              selectedFilter === "ALL"
                ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/20"
                : "bg-slate-900/80 text-slate-400 hover:text-slate-200 border border-slate-800"
            }`}
          >
            All Campaigns ({campaignsList.length})
          </button>
          <button
            onClick={() => setSelectedFilter("LIVE")}
            className={`px-3.5 py-1.5 rounded-xl text-xs font-medium transition-all ${
              selectedFilter === "LIVE"
                ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/20"
                : "bg-slate-900/80 text-slate-400 hover:text-slate-200 border border-slate-800"
            }`}
          >
            Live Interviews (Agent 2)
          </button>
          <button
            onClick={() => setSelectedFilter("COMPLETED")}
            className={`px-3.5 py-1.5 rounded-xl text-xs font-medium transition-all ${
              selectedFilter === "COMPLETED"
                ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/20"
                : "bg-slate-900/80 text-slate-400 hover:text-slate-200 border border-slate-800"
            }`}
          >
            Completed
          </button>
        </div>

        <div className="relative w-full sm:w-64">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-500" />
          <input
            type="text"
            placeholder="Filter campaigns..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-slate-900 border border-slate-800 rounded-xl pl-9 pr-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
          />
        </div>
      </div>

      {/* Campaigns Grid */}
      {filteredCampaigns.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredCampaigns.map((campaignItem) => (
            <InterviewCard key={campaignItem.id} campaign={campaignItem} />
          ))}
        </div>
      ) : (
        <div className="glass-panel rounded-2xl p-12 text-center border border-slate-800">
          <Bot className="w-12 h-12 text-slate-600 mx-auto mb-3" />
          <h3 className="text-base font-bold text-slate-300">No campaigns found</h3>
          <p className="text-xs text-slate-500 max-w-sm mx-auto mt-1">
            No active recruiting campaigns match your current search query or filter selection.
          </p>
        </div>
      )}

      {/* Deep-linkable Interview Detail Popup Modal driven by ?interview=<id> searchParam */}
      <InterviewDetailDialog interviewCampaignsList={campaignsList} />

      {/* Campaign Creation Modal */}
      <CreateInterviewModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onCampaignCreated={handleCampaignCreated}
      />
    </main>
  );
}
