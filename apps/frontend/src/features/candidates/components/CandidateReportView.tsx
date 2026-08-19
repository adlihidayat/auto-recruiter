"use client";

import React, { useState, useEffect } from "react";
import { Info, FileText } from "lucide-react";
import {
  getCandidateReportApi,
  getCandidateTranscriptsApi,
  getCandidatesForInterviewApi,
} from "@/lib/api/client";

interface CandidateReportViewProps {
  interviewId?: string;
  candidateId?: string;
}

interface HighlightBar { text: string; type: "pass" | "fail" }
interface ScoreItem { label: string; status: string; type: "pass" | "fail" }
interface Interaction { turn: string; speaker: string; role: string; text: string }

const INITIAL_MOCK_DATA = {
  name: "Loading...",
  email: "loading@example.com",
  status: "Hold",
  statusColor: "bg-[#DC2626]",
  statusReason: "Did not meet core requirements",
  overallScore: 0,
  overallScoreSubtext: "Under average",
  shortSummaryParagraphs: ["Loading candidate report..."],
  highlightBars: [
    { text: "Loading traits...", type: "pass" },
  ] as HighlightBar[],
  knowledgeScore: {
    score: "0%",
    items: [] as ScoreItem[],
    note: "Loading...",
  },
  communicationScore: {
    score: "0%",
    items: [] as ScoreItem[],
    note: "Loading...",
  },
  interactions: [] as Interaction[],
};

export default function CandidateReportView({
  interviewId,
  candidateId,
}: CandidateReportViewProps) {
  const [candidateData, setCandidateData] = useState(INITIAL_MOCK_DATA);

  useEffect(() => {
    async function loadReportAndTranscripts() {
      if (!candidateId) return;

      try {
        const rawToken = document.cookie
          .split("; ")
          .find((row) => row.startsWith("access_token="))
          ?.split("=")[1];
        const tokenCookie = rawToken ? decodeURIComponent(rawToken) : null;

        if (!tokenCookie) return;

        const promises: Promise<unknown>[] = [
          getCandidateReportApi(candidateId, tokenCookie).catch(() => null),
          getCandidateTranscriptsApi(candidateId, tokenCookie).catch(() => null),
        ];

        if (interviewId) {
          promises.push(
            getCandidatesForInterviewApi(interviewId, tokenCookie).catch(() => null)
          );
        } else {
          promises.push(Promise.resolve(null));
        }

        const [reportRes, transcriptsRes, candidatesRes] = (await Promise.all(
          promises
        )) as [
          { raw_report?: Record<string, unknown>; reasoning?: string; overall_confidence?: string } | null,
          Array<{ role: string; content: string }> | null,
          Array<{ id: string; first_name?: string; last_name?: string; email?: string; recommendation?: string; composite_score?: number }> | null
        ];

        const candidateInfo = candidatesRes?.find(
          (c) => c.id === candidateId
        );

        if (reportRes || transcriptsRes || candidateInfo) {
          const raw = reportRes?.raw_report || {};

          // Map transcripts to interaction turns
          const mappedInteractions = transcriptsRes && transcriptsRes.length > 0
            ? transcriptsRes.map((t: { role: string; content: string }, idx: number) => ({
                turn: `[T${idx + 1}]`,
                speaker: t.role === "candidate" ? "Candidate" : "Interviewer",
                role: t.role === "candidate" ? "candidate" : "interviewer",
                text: t.content,
              }))
            : [];

          const recStr = candidateInfo?.recommendation || "Hold";
          let statusColor = "bg-[#DC2626]";
          let statusReason = "Did not meet core requirements";
          if (recStr.includes("Advance with follow-up") || recStr.includes("follow-up")) {
            statusColor = "bg-[#828282]"; // Grey
            statusReason = "Passed with minor concerns";
          } else if (recStr.includes("Advance") || recStr.includes("Pass") || recStr.includes("Accept")) {
            statusColor = "bg-[#00C835]"; // Green
            statusReason = "Passed all criteria needed";
          }

          const oScore = candidateInfo?.composite_score ?? 0;
          let scoreSubtext = "Under average";
          if (oScore > 70 || oScore > 7) {
            scoreSubtext = "Pretty high";
          } else if (oScore >= 60 || oScore >= 6) {
            scoreSubtext = "Average";
          }

          const allGoodTraits: HighlightBar[] = [];
          const allBadTraits: HighlightBar[] = [];
          
          const goals = (raw?.goals || raw?.goal_breakdown || []) as Array<{ score?: number; rationale?: string; key_observations?: string }>;
          const comm = raw?.communication || raw?.communication_traits || null;

          // Parse goals for good and bad traits
          for (const goal of goals) {
            const gScore = goal.score ?? 0;
            const gText = goal.rationale || goal.key_observations || "No rationale provided.";
            if (gScore >= 8.0) {
              allGoodTraits.push({ text: gText, type: "pass" });
            } else {
              allBadTraits.push({ text: gText, type: "fail" });
            }
          }

          // Supplement bad traits from communication if needed
          if (comm) {
            // Check if it's the { traits: {} } structure or flat { clarity: 9.0 } structure
            const commDict = (comm as Record<string, unknown>).traits ? (comm as Record<string, unknown>).traits : comm;
            for (const [tName, tData] of Object.entries(commDict as Record<string, unknown>)) {
              if (typeof tData === "object" && tData !== null) {
                const td = tData as { is_passed?: boolean; rationale?: string };
                if (td.is_passed === false) {
                  allBadTraits.push({ text: td.rationale || `Failed communication trait: ${tName}`, type: "fail" });
                } else if (td.is_passed === true) {
                  allGoodTraits.push({ text: td.rationale || `Passed communication trait: ${tName}`, type: "pass" });
                }
              } else if (typeof tData === "number") {
                // Flat structure fallback e.g. "clarity": 9.0
                if (tData < 8.0) {
                  allBadTraits.push({ text: `Needs improvement in ${tName.replace("_", " ")}`, type: "fail" });
                } else if (tData >= 8.0) {
                  allGoodTraits.push({ text: `Strong ${tName.replace("_", " ")} skills`, type: "pass" });
                }
              }
            }
          }

          let finalBadTraits: HighlightBar[] = [];
          let finalGoodTraits: HighlightBar[] = [];

          if (allGoodTraits.length === 0) {
            finalBadTraits = allBadTraits.slice(0, 4);
          } else if (allBadTraits.length === 0) {
            finalGoodTraits = allGoodTraits.slice(0, 4);
          } else {
            finalBadTraits = allBadTraits.slice(0, 2);
            finalGoodTraits = allGoodTraits.slice(0, 4 - finalBadTraits.length);
          }

          const combinedTraits = [...finalGoodTraits, ...finalBadTraits];
          const highlightBars = combinedTraits.length > 0 ? combinedTraits : INITIAL_MOCK_DATA.highlightBars;

          const summaryText = reportRes?.reasoning || "";
          const paragraphs = summaryText
            ? summaryText.split("\n").filter((p: string) => p.trim().length > 0)
            : ["No summary available."];

          // Parse knowledge & communication for matrix (mock structure with real data)
          let knowledgeItems: ScoreItem[] = [];
          let commItems: ScoreItem[] = [];
          let kScoreText = "0%";
          let cScoreText = "0%";

          if (goals.length > 0) {
            const sumScore = goals.reduce((acc: number, g: { score?: number }) => acc + (g.score || 0), 0);
            kScoreText = `${Math.round((sumScore / (goals.length * 10)) * 100)}%`;
            knowledgeItems = goals.map((g: { score?: number; topic?: string }, i: number) => ({
              label: `Goal ${i + 1}`,
              status: (g.score || 0) >= 8.0 ? "Pass" : "Failed",
              type: (g.score || 0) >= 8.0 ? "pass" : "fail",
            }));
          }

          if (comm) {
            const commDict = (comm as Record<string, unknown>).traits ? (comm as Record<string, unknown>).traits : comm;
            const overallPassed = (comm as Record<string, unknown>).overall
              ? ((comm as Record<string, unknown>).overall as { is_passed?: boolean }).is_passed ?? true
              : true;
            cScoreText = overallPassed ? "Pass" : "Fail";
            
            commItems = Object.entries(commDict as Record<string, unknown>).map(([k, tv]) => {
              const isPass = typeof tv === "number" ? tv >= 8.0 : (tv as { is_passed?: boolean }).is_passed;
              return {
                label: k.replace("_", " "),
                status: isPass ? "Pass" : "Failed",
                type: isPass ? "pass" : "fail",
              };
            });
          }

          const fullName = candidateInfo?.first_name
            ? `${candidateInfo.first_name} ${candidateInfo.last_name || ""}`.trim()
            : "Unknown Candidate";

          setCandidateData({
            name: fullName,
            email: candidateInfo?.email || "Unknown Email",
            status: recStr,
            statusColor,
            statusReason,
            overallScore: Math.round(oScore * 10) / 10,
            overallScoreSubtext: scoreSubtext,
            shortSummaryParagraphs: paragraphs,
            highlightBars,
            knowledgeScore: {
              score: kScoreText,
              items: knowledgeItems,
              note: "Detailed knowledge evaluation",
            },
            communicationScore: {
              score: cScoreText,
              items: commItems,
              note: ((comm as Record<string, unknown>)?.overall as { rationale?: string })?.rationale || "Detailed communication evaluation",
            },
            interactions: mappedInteractions,
          });
        }
      } catch (err) {
        console.warn("Failed to load candidate report or transcripts", err);
      }
    }

    loadReportAndTranscripts();
  }, [candidateId, interviewId]);

  return (
    <div className="max-w-350 mx-auto px-6 py-6 pb-20 font-sans">
      {/* Top 2-Column Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 mb-6">
        {/* Left Card: Candidate Info & Short Summary */}
        <div className="lg:col-span-6 bg-white rounded-[28px] border border-[#F1F1F1] p-7 shadow-2xs flex flex-col justify-between">
          <div>
            {/* Profile Header */}
            <div className="flex items-center gap-4 pb-5 border-b border-[#F1F1F1]">
              <div className="w-10 h-10 rounded-full bg-[#EFEFEF] shrink-0" />
              <div>
                <h2 className="text-base font-semibold text-[#272727] leading-snug">
                  {candidateData.name}
                </h2>
                <p className="text-sm text-[#616161]">{candidateData.email}</p>
              </div>
            </div>

            {/* Short Summary Section */}
            <div className="pt-5 mb-6">
              <h3 className="text-base font-semibold text-[#272727] mb-3">
                Short Summary
              </h3>
              <div className="space-y-3 text-sm font-medium text-[#616161] leading-relaxed">
                {candidateData.shortSummaryParagraphs.map((para, idx) => (
                  <p key={idx}>{para}</p>
                ))}
              </div>
            </div>

            {/* Vertical Highlight Bars */}
            <div className="space-y-2.5">
              {candidateData.highlightBars.map((bar, idx) => (
                <div
                  key={idx}
                  className="flex items-center gap-3 text-sm text-[#616161] font-medium"
                >
                  <div
                    className={`w-1 h-6 rounded-full shrink-0 ${
                      bar.type === "pass" ? "bg-[#00C835]" : "bg-[#D30609]"
                    }`}
                  />
                  <span className="truncate">{bar.text}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Card: Status & Score Matrix */}
        <div className="lg:col-span-6 bg-white rounded-[28px] border border-[#F1F1F1] p-7 shadow-2xs flex flex-col justify-between">
          <div>
            {/* Top Status & Overall Score Header */}
            <div className="flex items-start justify-between pb-6 border-b border-[#F1F1F1]">
              {/* Left Status Block */}
              <div className="">
                <span className="text-sm font-medium text-[#272727] uppercase tracking-wider block mb-2.5">
                  Status
                </span>
                <div className="flex items-center gap-2.5 mb-2.5">
                  <div className={`w-2.5 h-7 ${candidateData.statusColor} rounded-full shrink-0`} />
                  <span className="text-2xl font-semibold text-[#272727]">
                    {candidateData.status}
                  </span>
                </div>
                <p className="text-sm font-medium text-[#616161]">
                  {candidateData.statusReason}
                </p>
              </div>

              {/* Right Overall Score Block */}
              <div className="text-right">
                <span className="text-sm font-medium text-[#272727] uppercase tracking-wider block mb-2.5">
                  Overall Score
                </span>
                <span className="text-2xl font-semibold text-[#272727] block leading-none mb-2.5">
                  {candidateData.overallScore}
                </span>
                <p className="text-sm font-medium text-[#616161]">
                  {candidateData.overallScoreSubtext}
                </p>
              </div>
            </div>

            {/* Dual Score Columns */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-6">
              {/* Column 1: Knowledge Score */}
              <div className="flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between mb-2.5">
                    <span className="text-sm font-medium text-[#272727]">
                      Knowledge Score
                    </span>
                    <Info className="w-3.5 h-3.5 text-[#616161] cursor-pointer" />
                  </div>
                  <div className="text-2xl font-semibold text-[#272727] mb-4.5">
                    {candidateData.knowledgeScore.score}
                  </div>

                  {/* Goal List */}
                  <div className="space-y-2.5 mb-4.5">
                    {candidateData.knowledgeScore.items.map((item, idx) => (
                      <div
                        key={idx}
                        className="flex items-center justify-between text-sm"
                      >
                        <div className="flex items-center gap-2 text-[#272727] font-medium">
                          <div className="w-1.5 h-1.5 rounded-full bg-[#FE6100] shrink-0" />
                          <span>{item.label}</span>
                        </div>
                        <div className="flex-1 border-b border-dotted border-[#D9D9D9] mx-2" />
                        <span
                          className={`font-medium ${
                            item.type === "pass"
                              ? "text-[#22C55E]"
                              : "text-[#DC2626]"
                          }`}
                        >
                          {item.status}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <p className="text-xs font-medium text-[#FE6100] leading-snug mb-4.5">
                    {candidateData.knowledgeScore.note}
                  </p>
                  <button className="w-full flex items-center justify-end gap-1.5 text-sm font-semibold text-[#272727] underline hover:text-black transition-colors cursor-pointer">
                    <FileText className="w-3.5 h-3.5" />
                    See Detail
                  </button>
                </div>
              </div>

              {/* Column 2: Communication Score */}
              <div className="flex flex-col justify-between md:border-l md:border-[#F1F1F1] md:pl-6">
                <div>
                  <div className="flex items-center justify-between mb-2.5">
                    <span className="text-sm font-medium text-[#272727]">
                      Communication Score
                    </span>
                    <Info className="w-3.5 h-3.5 text-[#616161] cursor-pointer" />
                  </div>
                  <div className="text-2xl font-semibold text-[#272727] mb-4.5">
                    {candidateData.communicationScore.score}
                  </div>

                  {/* Signal List */}
                  <div className="space-y-2.5 mb-4.5">
                    {candidateData.communicationScore.items.map((item, idx) => (
                      <div
                        key={idx}
                        className="flex items-center justify-between text-sm"
                      >
                        <div className="flex items-center gap-2 text-[#272727] font-medium">
                          <div className="w-1.5 h-1.5 rounded-full bg-[#FE6100] shrink-0" />
                          <span>{item.label}</span>
                        </div>
                        <div className="flex-1 border-b border-dotted border-[#D9D9D9] mx-2" />
                        <span
                          className={`font-medium ${
                            item.type === "pass"
                              ? "text-[#22C55E]"
                              : "text-[#DC2626]"
                          }`}
                        >
                          {item.status}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <p className="text-[11px] font-medium text-[#FE6100] leading-snug mb-4.5">
                    {candidateData.communicationScore.note}
                  </p>
                  <button className="w-full flex items-center justify-end gap-1.5 text-sm font-semibold text-[#272727] underline hover:text-black transition-colors cursor-pointer">
                    <FileText className="w-3.5 h-3.5" />
                    See Detail
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Card: Interview Interaction */}
      <div className="bg-white rounded-[28px] border border-[#F1F1F1] p-7 shadow-2xs">
        <h3 className="text-base font-semibold text-[#272727] pb-4 mb-6 border-b border-[#F1F1F1]">
          Interview Interaction
        </h3>

        <div className="relative pl-1">
          {/* Continuous vertical timeline line */}
          <div className="absolute top-2.5 bottom-6 left-12 w-px bg-[#D9D9D9]" />

          <div className="space-y-6">
            {candidateData.interactions.map((interaction, idx) => (
              <div key={idx} className="relative flex items-start gap-4">
                {/* Turn Label */}
                <span className="w-6 shrink-0 font-semibold text-base text-[#272727] pt-0.5">
                  {interaction.turn}
                </span>

                {/* Timeline Bullet Dot */}
                <div className="relative z-10 flex items-center justify-center pt-1 shrink-0">
                  <div
                    className={`w-2.5 h-2.5 rounded-full ${
                      interaction.role === "candidate"
                        ? "bg-[#FE6100]"
                        : "bg-[#B8B8B8]"
                    }`}
                  />
                </div>

                {/* Speaker & Transcript Content */}
                <div className="flex-1">
                  <span className="font-semibold text-base text-[#272727]">
                    {interaction.speaker}
                  </span>
                  <p className="text-sm font-medium text-[#616161] leading-relaxed mt-1">
                    {interaction.text}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
