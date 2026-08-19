"use client";

/**
 * What: Modal drawer displaying detailed interview campaign info and candidate list.
 * Why: Per frontend rules in GEMINI.md, interview details open as a popup driven by '?interview=<id>' search params.
 * Boundaries: Operates as a Client Component driven by URL params; does not navigate away from the current page.
 */

import React, { useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Image from "next/image";
import {
  CalendarDays,
  User,
  Info,
  TrendingUp,
  ChevronDown,
  MoreVertical,
  SlidersHorizontal,
  X,
  Share2,
  Pencil,
  Trash2,
  CircleGauge,
} from "lucide-react";
import { InterviewCampaign } from "../types";
import { getCandidatesForInterviewApi } from "@/lib/api/client";

interface InterviewDetailDialogProps {
  interviewCampaignsList: InterviewCampaign[];
}

export default function InterviewDetailDialog({
  interviewCampaignsList,
}: InterviewDetailDialogProps) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const activeInterviewId = searchParams.get("interview");

  const [isDescriptionExpanded, setIsDescriptionExpanded] = useState(true);

  const baseCandidates = [
    {
      id: "candidate-1",
      name: "andika saputra",
      email: "andika.saputra@company.com",
      stageStatus: "Done",
      recommendation: "Advance" as const,
      img: "https://i.pravatar.cc/150?u=1",
    },
    {
      id: "candidate-2",
      name: "sari putri",
      email: "sari.putri@example.com",
      stageStatus: "Done",
      recommendation: "Advance with follow-up" as const,
      img: "https://i.pravatar.cc/150?u=2",
    },
    {
      id: "candidate-3",
      name: "Fahril arrasyid",
      email: "Fahril-arrasyid@gmail.com",
      stageStatus: "On-Interview",
      recommendation: "Hold" as const,
      img: "https://i.pravatar.cc/150?u=3",
    },
    {
      id: "candidate-4",
      name: "rizky hadi",
      email: "rizky.hadi@mail.com",
      stageStatus: "On-Interview",
      recommendation: "Hold" as const,
      img: "https://i.pravatar.cc/150?u=4",
    },
    {
      id: "candidate-5",
      name: "ijal dilan",
      email: "ijaldilan@gmail.com",
      stageStatus: "Not-started",
      recommendation: "Hold" as const,
      img: "https://i.pravatar.cc/150?u=5",
    },
    {
      id: "candidate-6",
      name: "lina maulani",
      email: "lina.maulani@gmail.com",
      stageStatus: "Not-started",
      recommendation: "Hold" as const,
      img: "https://i.pravatar.cc/150?u=6",
    },
  ];

  const defaultMockCandidates = Array(4)
    .fill(baseCandidates)
    .flat()
    .map((c, i) => ({
      ...c,
      id: `mock-cand-${i + 1}`,
      email: `${i + 1}.${c.email}`,
    }));

  const [candidatesListState, setCandidatesListState] = useState(
    defaultMockCandidates,
  );
  const [candidateNoticeMessage, setCandidateNoticeMessage] = useState<string | null>(null);

  const handleCandidateClick = (candidate: {
    id: string;
    stageStatus: string;
    name: string;
  }) => {
    if (candidate.stageStatus === "Done") {
      setCandidateNoticeMessage(null);
      router.push(`/interviews/${activeInterviewId}/candidates/${candidate.id}`);
    } else {
      setCandidateNoticeMessage(`"${candidate.name}" has not finished their interview yet.`);
      setTimeout(() => {
        setCandidateNoticeMessage(null);
      }, 3500);
    }
  };

  useEffect(() => {
    async function loadCandidates() {
      if (!activeInterviewId) return;
      try {
        const rawToken = document.cookie
          .split("; ")
          .find((row) => row.startsWith("access_token="))
          ?.split("=")[1];
        const tokenCookie = rawToken ? decodeURIComponent(rawToken) : null;

        if (tokenCookie) {
          const backendCandidates = await getCandidatesForInterviewApi(
            activeInterviewId,
            tokenCookie,
          );
          if (backendCandidates) {
            const mapped = backendCandidates.map((cand, idx) => {
              const fullName =
                cand.first_name && cand.last_name
                  ? `${cand.first_name} ${cand.last_name}`
                  : cand.first_name || cand.email.split("@")[0];

              let stageStatus = "Not-started";
              const sUpper = cand.status?.toUpperCase() || "";
              if (
                sUpper.includes("EVALUAT") ||
                sUpper.includes("DONE") ||
                sUpper.includes("COMPLET") ||
                sUpper.includes("FINISH") ||
                sUpper.includes("PASSED") ||
                sUpper.includes("REJECTED") ||
                (cand.composite_score !== null &&
                  cand.composite_score !== undefined)
              ) {
                stageStatus = "Done";
              } else if (
                sUpper.includes("PROGRESS") ||
                sUpper.includes("INTERVIEW") ||
                sUpper.includes("INVITED")
              ) {
                stageStatus = "On-Interview";
              }

              let recLabel: "Advance" | "Advance with follow-up" | "Hold" =
                "Hold";
              const rUpper = cand.recommendation?.toUpperCase() || "";
              if (rUpper.includes("FOLLOW") || rUpper.includes("FOLLOW-UP")) {
                recLabel = "Advance with follow-up";
              } else if (
                rUpper.includes("ADVANCE") ||
                rUpper.includes("PASS") ||
                rUpper.includes("ACCEPT")
              ) {
                recLabel = "Advance";
              } else {
                recLabel = "Hold";
              }

              return {
                id: cand.id,
                name: fullName,
                email: cand.email,
                stageStatus,
                recommendation: recLabel,
                img: `https://i.pravatar.cc/150?u=${idx + 1}`,
              };
            });
            setCandidatesListState(mapped);
          }
        }
      } catch (err) {
        console.warn("Failed to fetch candidates from backend", err);
      }
    }

    loadCandidates();
  }, [activeInterviewId]);

  useEffect(() => {
    if (activeInterviewId) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
    return () => {
      document.body.style.overflow = "";
    };
  }, [activeInterviewId]);

  if (!activeInterviewId) return null;

  const targetCampaign = interviewCampaignsList.find(
    (campaignItem) => campaignItem.id === activeInterviewId,
  );

  if (!targetCampaign) return null;

  const handleCloseDialog = () => {
    const nextSearchParams = new URLSearchParams(searchParams.toString());
    nextSearchParams.delete("interview");
    const newQueryString = nextSearchParams.toString();
    const destinationUrl = newQueryString ? `/?${newQueryString}` : "/";
    router.push(destinationUrl, { scroll: false });
  };

  // Candidate Metrics
  const totalCandidates = candidatesListState.length;
  const finishedCandidates = candidatesListState.filter(
    (c) => c.stageStatus === "Done",
  ).length;
  const inProgressCandidates = candidatesListState.filter(
    (c) => c.stageStatus === "On-Interview",
  ).length;
  const notStartedCandidates = candidatesListState.filter(
    (c) => c.stageStatus === "Not-started",
  ).length;

  const isInterviewFinished =
    targetCampaign.currentPipelineStage === "COMPLETED" ||
    (totalCandidates > 0 && finishedCandidates === totalCandidates);

  // Status Bar 3-Color Percentages (Orange, Light Orange, Gray)
  const orangePct =
    totalCandidates > 0 ? (finishedCandidates / totalCandidates) * 100 : 0;
  const lightOrangePct =
    totalCandidates > 0 ? (inProgressCandidates / totalCandidates) * 100 : 0;
  const grayPct =
    totalCandidates > 0 ? (notStartedCandidates / totalCandidates) * 100 : 0;

  // Passing Rate 3-Color Percentages (Green, Gray, Red)
  const advanceCandidates = candidatesListState.filter(
    (c) => c.recommendation === "Advance",
  ).length;
  const followUpCandidates = candidatesListState.filter(
    (c) => c.recommendation === "Advance with follow-up",
  ).length;
  const holdCandidates = candidatesListState.filter(
    (c) => c.recommendation === "Hold",
  ).length;

  const greenPct =
    totalCandidates > 0 ? (advanceCandidates / totalCandidates) * 100 : 0;
  const passGrayPct =
    totalCandidates > 0 ? (followUpCandidates / totalCandidates) * 100 : 0;
  const redPct =
    totalCandidates > 0 ? (holdCandidates / totalCandidates) * 100 : 0;

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-black/20 animate-in fade-in duration-200">
      {/* Clickable overlay to close */}
      <div className="absolute inset-0" onClick={handleCloseDialog} />

      {/* Drawer Container */}
      <div className="relative w-full max-w-162.5 h-full bg-white shadow-2xl flex flex-col animate-in slide-in-from-right duration-300">
        {/* Drawer Header */}
        <div className="px-7 py-4.5 flex items-center justify-between border-b border-[#F1F1F1]">
          <div className="flex items-center gap-3">
            <button
              onClick={handleCloseDialog}
              className="w-7 h-7 rounded-lg text-[#616161] hover:bg-gray-200 hover:text-[#272727] transition-colors flex items-center justify-center"
              title="Close"
            >
              <X className="w-4 h-4" />
            </button>
            <div className="h-4 w-px bg-[#F1F1F1]" />
            <span className="text-sm px-2 font-medium text-[#616161]">
              Interview Detail
            </span>
          </div>
          <div className="flex items-center gap-2">
            <button
              className="w-7 h-7 rounded-lg text-[#616161] hover:bg-gray-200 hover:text-[#272727] transition-colors flex items-center justify-center"
              title="Share"
            >
              <Share2 className="w-4 h-4" />
            </button>
            <button
              className="w-7 h-7 rounded-lg text-[#616161] hover:bg-gray-200 hover:text-[#272727] transition-colors flex items-center justify-center"
              title="Edit"
            >
              <Pencil className="w-4 h-4" />
            </button>
            <button
              className="w-7 h-7 rounded-lg text-[#616161] hover:bg-red-50 hover:text-red-600 transition-colors flex items-center justify-center"
              title="Delete"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Scrollable Content */}
        <div className="flex-1 overflow-y-auto p-7.5">
          {/* Title and Pills */}
          <div className="mb-7.5">
            <h2 className="text-xl font-semibold text-[#272727] mb-2.5">
              {targetCampaign.jobTitle}
            </h2>
            <div className="flex items-center gap-3">
              <span className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-[#F4F4F4] text-[#2563EB] text-xs font-medium">
                <CalendarDays className="w-3.5 h-3.5" />{" "}
                {targetCampaign.createdAtTimestamp}
              </span>
              <span className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#F4F4F4] text-[#DC2626] text-xs font-medium">
                <User className="w-3.5 h-3.5" /> {targetCampaign.departmentName}
              </span>
            </div>
          </div>

          {/* Status Cards */}
          <div className="grid grid-cols-2 gap-4 mb-7.5">
            {/* Card 1: Interview Status */}
            <div className="border border-[#F1F1F1] rounded-2xl p-1">
              <div className="flex items-center justify-between p-2.5">
                <div className="flex items-center gap-2 text-[#616161] text-sm font-medium">
                  <User className="w-4 h-4" /> Interview Status
                </div>
                <Info className="w-4 h-4 text-[#616161]" />
              </div>
              <div className="bg-[#FBFBFB] rounded-md p-2.5">
                <div className="text-2xl font-semibold text-[#272727] mb-2.5">
                  {finishedCandidates} / {totalCandidates}
                </div>

                <div className="flex items-center gap-1 text-xs font-medium text-[#059669] mb-2.5">
                  <TrendingUp className="w-3.5 h-3.5" />
                  <span className="text-[#616161]">
                    {isInterviewFinished ? "Interview Finished" : "In Progress"}
                  </span>
                </div>

                <div className="flex items-center h-2">
                  <div
                    className="h-full bg-[#FE6100] rounded-full mb-1 transition-all duration-300"
                    style={{ width: `${orangePct}%` }}
                  />
                  <div
                    className="h-full bg-[#FFD3B8] rounded-full mb-1 transition-all duration-300"
                    style={{ width: `${lightOrangePct}%` }}
                  />
                  <div
                    className="h-full bg-[#E9E9E9] rounded-full transition-all duration-300"
                    style={{ width: `${grayPct}%` }}
                  />
                </div>
              </div>
            </div>

            {/* Card 2: Passing Rate */}
            <div className="border border-[#F1F1F1] rounded-2xl p-1">
              <div className="flex items-center justify-between p-2.5">
                <div className="flex items-center gap-2 text-[#616161] text-sm font-medium">
                  <CircleGauge className="w-4 h-4" /> Passing Rate
                </div>
                <Info className="w-4 h-4 text-[#616161]" />
              </div>
              <div className="bg-[#FBFBFB] rounded-md p-2.5">
                <div className="text-2xl font-semibold text-[#272727] mb-2.5">
                  {isInterviewFinished
                    ? `${advanceCandidates} / ${totalCandidates}`
                    : "-/-"}
                </div>

                <div className="flex items-center gap-1 text-xs font-medium text-[#059669] mb-2.5">
                  <span className="text-[#616161]">
                    {isInterviewFinished
                      ? `${greenPct.toFixed(0)}% Advance Rate`
                      : "Not finished yet"}
                  </span>
                </div>

                <div className="flex items-center gap-1 h-2">
                  {isInterviewFinished ? (
                    <>
                      <div
                        className="h-full bg-[#16A34A] rounded-full transition-all duration-300"
                        style={{ width: `${greenPct}%` }}
                      />
                      <div
                        className="h-full bg-[#616161] rounded-full transition-all duration-300"
                        style={{ width: `${passGrayPct}%` }}
                      />
                      <div
                        className="h-full bg-[#DC2626] rounded-full transition-all duration-300"
                        style={{ width: `${redPct}%` }}
                      />
                    </>
                  ) : (
                    <div className="h-full bg-[#E9E9E9] rounded-full w-full" />
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Description Section */}
          <div className="mb-7.5 relative">
            <button
              onClick={() => setIsDescriptionExpanded(!isDescriptionExpanded)}
              className="flex items-center gap-2 text-base font-semibold text-[#272727] mb-3"
            >
              Description{" "}
              <ChevronDown
                className={`w-4 h-4 transition-transform ${isDescriptionExpanded ? "rotate-180" : ""}`}
              />
            </button>
            <p
              className={`text-sm font-medium text-[#616161] leading-relaxed overflow-y-hidden ${isDescriptionExpanded ? "h-20" : "h-max"}`}
            >
              {targetCampaign.agentSummary}
            </p>
            {isDescriptionExpanded && (
              <div className="absolute bottom-0 left-0 right-0 h-16 bg-linear-to-t from-white to-transparent pointer-events-none" />
            )}
          </div>

          {candidateNoticeMessage && (
            <div className="mb-3 px-3.5 py-2.5 bg-amber-50 border border-amber-200 text-amber-800 text-xs font-medium rounded-xl flex items-center justify-between animate-in fade-in duration-200">
              <span>{candidateNoticeMessage}</span>
              <button
                onClick={() => setCandidateNoticeMessage(null)}
                className="text-amber-600 hover:text-amber-900 font-bold ml-2"
              >
                ✕
              </button>
            </div>
          )}

          <div className="flex items-center justify-between mb-3">
            <h3 className="text-base font-semibold text-[#272727]">
              Candidates ({candidatesListState.length})
            </h3>
            <button className="text-[#616161] hover:text-[#272727] transition-colors">
              <SlidersHorizontal className="w-4 h-4" />
            </button>
          </div>
          {/* Candidates List */}
          <div className="border border-[#F1F1F1] rounded-[14px] overflow-y-auto max-h-95 mb-8">
            {/* Candidates List Header */}
            {candidatesListState.map((candidate, idx) => (
              <div
                key={candidate.id || idx}
                onClick={() => handleCandidateClick(candidate)}
                className={`px-2.5 py-2.5 flex items-center justify-between cursor-pointer hover:bg-gray-50/80 transition-colors ${idx !== candidatesListState.length - 1 ? "border-b border-[#F1F1F1]" : ""}`}
              >
                <div className="flex items-center gap-2.5">
                  <div className="w-9.5 h-9.5 rounded-full bg-gray-200 overflow-hidden shrink-0 relative">
                    <Image
                      src={candidate.img}
                      alt={candidate.name}
                      fill
                      className="object-cover"
                      unoptimized
                    />
                  </div>
                  <div>
                    <div className="text-sm font-medium text-[#272727]">
                      {candidate.name}
                    </div>
                    <div className="text-sm font-medium text-[#616161]">
                      {candidate.email}
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-4">
                  {!isInterviewFinished ? (
                    <>
                      {candidate.stageStatus === "Done" && (
                        <span className="px-3 py-1 bg-[#DCFCE7] text-[#16A34A] rounded-full text-xs font-medium">
                          Done
                        </span>
                      )}
                      {candidate.stageStatus === "On-Interview" && (
                        <span className="px-3 py-1 bg-[#EFF6FF] text-[#2563EB] rounded-full text-xs font-medium">
                          On-Interview
                        </span>
                      )}
                      {candidate.stageStatus === "Not-started" && (
                        <span className="px-3 py-1 bg-[#F4F4F4] text-[#616161] rounded-full text-xs font-medium">
                          Not-started
                        </span>
                      )}
                    </>
                  ) : (
                    <>
                      {candidate.recommendation === "Advance" && (
                        <span className="px-3 py-1 bg-[#DCFCE7] text-[#16A34A] rounded-full text-xs font-medium">
                          Advance
                        </span>
                      )}
                      {candidate.recommendation ===
                        "Advance with follow-up" && (
                        <span className="px-3 py-1 bg-[#F4F4F4] text-[#616161] rounded-full text-xs font-medium">
                          Advance w/ follow-up
                        </span>
                      )}
                      {candidate.recommendation === "Hold" && (
                        <span className="px-3 py-1 bg-[#FEF2F2] text-[#DC2626] rounded-full text-xs font-medium">
                          Hold
                        </span>
                      )}
                    </>
                  )}

                  <button className="text-[#B8B8B8] hover:text-[#616161] transition-colors">
                    <MoreVertical className="w-5 h-5" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
