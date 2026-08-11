"use client";

/**
 * What: Modal dialog popup displaying detailed interview campaign info, candidate list, agent suite, and room launcher.
 * Why: Per frontend rules in GEMINI.md, interview details open as a popup driven by '?interview=<id>' search params.
 * Boundaries: Operates as a Client Component driven by URL params; does not navigate away from the current page.
 */

import React, { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import {
  X,
  Sparkles,
  Bot,
  Users,
  ExternalLink,
  ChevronRight,
  Award,
  Layers,
  HelpCircle,
  Clock,
  Radio,
} from "lucide-react";
import { InterviewCampaign } from "../types";
import InterviewStatusBadge from "./InterviewStatusBadge";

interface InterviewDetailDialogProps {
  interviewCampaignsList: InterviewCampaign[];
}

export default function InterviewDetailDialog({
  interviewCampaignsList,
}: InterviewDetailDialogProps) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const activeInterviewId = searchParams.get("interview");

  const [activeTab, setActiveTab] = useState<"overview" | "questions" | "candidates">("overview");

  if (!activeInterviewId) return null;

  const targetCampaign = interviewCampaignsList.find(
    (campaignItem) => campaignItem.id === activeInterviewId
  );

  if (!targetCampaign) return null;

  const handleCloseDialog = () => {
    const nextSearchParams = new URLSearchParams(searchParams.toString());
    nextSearchParams.delete("interview");
    const newQueryString = nextSearchParams.toString();
    const destinationUrl = newQueryString ? `/?${newQueryString}` : "/";
    router.push(destinationUrl, { scroll: false });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-in fade-in duration-200">
      <div className="relative w-full max-w-4xl max-h-[90vh] bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl overflow-hidden flex flex-col">
        {/* Modal Header */}
        <div className="px-6 py-5 border-b border-slate-800 flex items-start justify-between bg-slate-900/60">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <h2 className="text-xl font-bold text-white tracking-tight">
                {targetCampaign.jobTitle}
              </h2>
              <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                {targetCampaign.departmentName}
              </span>
              <span className="px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-800 text-slate-300">
                Level: {targetCampaign.targetSeniority}
              </span>
            </div>
            <div className="flex items-center gap-4 text-xs text-slate-400">
              <InterviewStatusBadge pipelineStage={targetCampaign.currentPipelineStage} />
              <span className="flex items-center gap-1">
                <Clock className="w-3.5 h-3.5 text-slate-500" />
                Created {targetCampaign.createdAtTimestamp}
              </span>
            </div>
          </div>

          <button
            onClick={handleCloseDialog}
            className="p-2 rounded-xl bg-slate-800/80 text-slate-400 hover:text-white hover:bg-slate-700 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tab Navigation */}
        <div className="px-6 border-b border-slate-800 bg-slate-950/40 flex items-center gap-6">
          <button
            onClick={() => setActiveTab("overview")}
            className={`py-3.5 text-xs font-semibold border-b-2 transition-all flex items-center gap-2 ${
              activeTab === "overview"
                ? "border-indigo-500 text-indigo-400"
                : "border-transparent text-slate-400 hover:text-slate-200"
            }`}
          >
            <Layers className="w-4 h-4" /> Agent Pipeline & Summary
          </button>

          <button
            onClick={() => setActiveTab("questions")}
            className={`py-3.5 text-xs font-semibold border-b-2 transition-all flex items-center gap-2 ${
              activeTab === "questions"
                ? "border-indigo-500 text-indigo-400"
                : "border-transparent text-slate-400 hover:text-slate-200"
            }`}
          >
            <HelpCircle className="w-4 h-4" /> Generated Question Suite ({targetCampaign.questionSuite.length})
          </button>

          <button
            onClick={() => setActiveTab("candidates")}
            className={`py-3.5 text-xs font-semibold border-b-2 transition-all flex items-center gap-2 ${
              activeTab === "candidates"
                ? "border-indigo-500 text-indigo-400"
                : "border-transparent text-slate-400 hover:text-slate-200"
            }`}
          >
            <Users className="w-4 h-4" /> Candidates ({targetCampaign.candidatesList.length})
          </button>
        </div>

        {/* Tab Contents */}
        <div className="p-6 overflow-y-auto flex-1 space-y-6">
          {activeTab === "overview" && (
            <div className="space-y-6">
              {/* Agent Status Pipeline Visualizer */}
              <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800">
                <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-4 flex items-center gap-2">
                  <Bot className="w-4 h-4 text-indigo-400" /> 3-Agent Workflow Progress
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {/* Step 1 */}
                  <div className="p-3.5 rounded-lg bg-slate-900 border border-slate-800 flex items-start gap-3">
                    <div className="w-7 h-7 rounded-full bg-amber-500/20 text-amber-400 flex items-center justify-center font-bold text-xs shrink-0">
                      1
                    </div>
                    <div>
                      <div className="text-xs font-bold text-slate-200">Question Maker</div>
                      <p className="text-[11px] text-slate-400 mt-0.5">
                        Synthesized {targetCampaign.questionSuite.length} targeted coding & system design prompts.
                      </p>
                    </div>
                  </div>

                  {/* Step 2 */}
                  <div className="p-3.5 rounded-lg bg-slate-900 border border-slate-800 flex items-start gap-3">
                    <div className="w-7 h-7 rounded-full bg-cyan-500/20 text-cyan-400 flex items-center justify-center font-bold text-xs shrink-0">
                      2
                    </div>
                    <div>
                      <div className="text-xs font-bold text-slate-200">Live Voice Agent</div>
                      <p className="text-[11px] text-slate-400 mt-0.5">
                        Conducting adaptive room interviews via LiveKit SDK.
                      </p>
                    </div>
                  </div>

                  {/* Step 3 */}
                  <div className="p-3.5 rounded-lg bg-slate-900 border border-slate-800 flex items-start gap-3">
                    <div className="w-7 h-7 rounded-full bg-purple-500/20 text-purple-400 flex items-center justify-center font-bold text-xs shrink-0">
                      3
                    </div>
                    <div>
                      <div className="text-xs font-bold text-slate-200">Interview Grader</div>
                      <p className="text-[11px] text-slate-400 mt-0.5">
                        Evaluates candidate transcripts against role rubrics.
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Action Banner for Live Interview Room */}
              <div className="p-5 rounded-xl bg-gradient-to-r from-indigo-950/60 via-slate-900 to-purple-950/60 border border-indigo-500/30 flex items-center justify-between">
                <div>
                  <div className="flex items-center gap-2 text-indigo-400 text-xs font-bold uppercase tracking-wider mb-1">
                    <Radio className="w-4 h-4 text-emerald-400 animate-pulse" /> Live Observer Room Available
                  </div>
                  <p className="text-xs text-slate-300">
                    HR team members can join or observe live candidate interviews in real time with LiveKit room tokens.
                  </p>
                </div>
                <Link
                  href={`/interviews/${targetCampaign.id}/live`}
                  className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold transition-all flex items-center gap-2 shrink-0 shadow-lg shadow-indigo-600/30"
                >
                  <Bot className="w-4 h-4" /> Open Live Room <ExternalLink className="w-3.5 h-3.5" />
                </Link>
              </div>

              {/* Summary Description */}
              {targetCampaign.agentSummary && (
                <div className="p-4 rounded-xl bg-slate-950/40 border border-slate-800">
                  <h4 className="text-xs font-semibold text-slate-300 mb-2 flex items-center gap-1.5">
                    <Sparkles className="w-3.5 h-3.5 text-amber-400" /> AI Campaign Brief
                  </h4>
                  <p className="text-xs text-slate-400 leading-relaxed">
                    {targetCampaign.agentSummary}
                  </p>
                </div>
              )}
            </div>
          )}

          {activeTab === "questions" && (
            <div className="space-y-3">
              {targetCampaign.questionSuite.map((qItem, idx) => (
                <div
                  key={qItem.id}
                  className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 flex items-start gap-4"
                >
                  <div className="w-7 h-7 rounded-lg bg-indigo-500/10 text-indigo-400 flex items-center justify-center font-bold text-xs shrink-0">
                    Q{idx + 1}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xs font-bold text-slate-200">{qItem.category}</span>
                      <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-slate-800 text-slate-400">
                        {qItem.difficultyLevel}
                      </span>
                      <span className="text-[11px] text-slate-500">Skill: {qItem.targetSkill}</span>
                    </div>
                    <p className="text-xs text-slate-300">{qItem.questionText}</p>
                  </div>
                </div>
              ))}
            </div>
          )}

          {activeTab === "candidates" && (
            <div className="space-y-3">
              {targetCampaign.candidatesList.map((candidate) => (
                <div
                  key={candidate.id}
                  className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 flex items-center justify-between hover:border-slate-700 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-full bg-slate-800 flex items-center justify-center font-bold text-xs text-slate-300">
                      {candidate.fullName.charAt(0)}
                    </div>
                    <div>
                      <div className="text-xs font-bold text-white">{candidate.fullName}</div>
                      <div className="text-[11px] text-slate-400">{candidate.emailAddress}</div>
                    </div>
                  </div>

                  <div className="flex items-center gap-4">
                    {candidate.overallScore ? (
                      <div className="text-right">
                        <div className="text-xs font-bold text-emerald-400 flex items-center gap-1 justify-end">
                          <Award className="w-3.5 h-3.5" /> {candidate.overallScore}/100
                        </div>
                        <div className="text-[10px] text-slate-500">Graded by AI</div>
                      </div>
                    ) : (
                      <span className="text-xs text-slate-500 italic">Interview pending</span>
                    )}

                    <Link
                      href={`/interviews/${targetCampaign.id}/candidates/${candidate.id}`}
                      className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium transition-colors flex items-center gap-1"
                    >
                      Report <ChevronRight className="w-3.5 h-3.5" />
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="px-6 py-4 border-t border-slate-800 bg-slate-950/60 flex items-center justify-end">
          <button
            onClick={handleCloseDialog}
            className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold transition-colors"
          >
            Close Dialog
          </button>
        </div>
      </div>
    </div>
  );
}
