"use client";

/**
 * What: Modal drawer displaying detailed interview campaign info and candidate list.
 * Why: Per frontend rules in GEMINI.md, interview details open as a popup driven by '?interview=<id>' search params.
 * Boundaries: Operates as a Client Component driven by URL params; does not navigate away from the current page.
 */

import React, { useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import UserAvatar from "@/components/common/UserAvatar";
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
  Check,
  Loader2,
  AlertTriangle,
} from "lucide-react";
import { InterviewCampaign } from "../types";
import {
  getCandidatesForInterviewApi,
  updateInterviewApi,
  deleteInterviewApi,
  UpdateInterviewPayload,
} from "@/lib/api/client";

interface InterviewDetailDialogProps {
  interviewCampaignsList: InterviewCampaign[];
  onCampaignDeleted?: (deletedId: string) => void;
  onCampaignUpdated?: () => void;
}

export default function InterviewDetailDialog({
  interviewCampaignsList,
  onCampaignDeleted,
  onCampaignUpdated,
}: InterviewDetailDialogProps) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const activeInterviewId = searchParams.get("interview");

  const [isDescriptionExpanded, setIsDescriptionExpanded] = useState(true);
  const [isShareNoticeVisible, setIsShareNoticeVisible] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isDeleteConfirmOpen, setIsDeleteConfirmOpen] = useState(false);
  const [isActionSubmitting, setIsActionSubmitting] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);

  // Edit form state
  const [editFormData, setEditFormData] = useState({
    job_name: "",
    job_description: "",
    difficulty: "mid",
    domain_hint: "",
    scheduled_at: "",
  });

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
  const [candidateNoticeMessage, setCandidateNoticeMessage] = useState<
    string | null
  >(null);

  const [activeCandidateMenuId, setActiveCandidateMenuId] = useState<string | null>(null);
  const [candidateFilter, setCandidateFilter] = useState<'ALL' | 'Not-started' | 'On-Interview' | 'Done'>('ALL');
  const [isFilterMenuOpen, setIsFilterMenuOpen] = useState(false);
  const [prevInterviewId, setPrevInterviewId] = useState<string | null>(activeInterviewId);

  if (activeInterviewId !== prevInterviewId) {
    setPrevInterviewId(activeInterviewId);
    setCandidateFilter('ALL');
    setIsFilterMenuOpen(false);
    setActiveCandidateMenuId(null);
  }

  const displayedCandidates = candidatesListState.filter(c => {
    if (candidateFilter === 'ALL') return true;
    return c.stageStatus === candidateFilter;
  });

  const handleCandidateClick = (candidate: {
    id: string;
    stageStatus: string;
    name: string;
  }) => {
    if (candidate.stageStatus === "Done") {
      setCandidateNoticeMessage(null);
      router.push(
        `/interviews/${activeInterviewId}/candidates/${candidate.id}`,
      );
    } else {
      setCandidateNoticeMessage(
        `"${candidate.name}" has not finished their interview yet.`,
      );
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

  // 1. Share Handler
  const handleShare = () => {
    if (typeof window !== "undefined") {
      navigator.clipboard.writeText(window.location.href);
      setIsShareNoticeVisible(true);
      setTimeout(() => setIsShareNoticeVisible(false), 3000);
    }
  };

  // 2. Open Edit Modal pre-filled
  const handleOpenEdit = () => {
    setActionError(null);
    setEditFormData({
      job_name: targetCampaign?.jobTitle || "",
      job_description: targetCampaign?.agentSummary || "",
      difficulty: "mid",
      domain_hint: "",
      scheduled_at: "",
    });
    setIsEditModalOpen(true);
  };

  // 3. Save Edit Changes
  const handleSaveEdit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeInterviewId) return;

    try {
      setIsActionSubmitting(true);
      setActionError(null);

      const rawToken = document.cookie
        .split("; ")
        .find((row) => row.startsWith("access_token="))
        ?.split("=")[1];
      const tokenCookie = rawToken ? decodeURIComponent(rawToken) : null;

      if (!tokenCookie) {
        throw new Error("You must be logged in to update an interview.");
      }

      const payload: UpdateInterviewPayload = {
        job_name: editFormData.job_name,
        job_description: editFormData.job_description,
        difficulty: editFormData.difficulty,
        domain_hint: editFormData.domain_hint || undefined,
        scheduled_at: editFormData.scheduled_at
          ? new Date(editFormData.scheduled_at).toISOString()
          : undefined,
      };

      await updateInterviewApi(activeInterviewId, payload, tokenCookie);
      setIsEditModalOpen(false);
      onCampaignUpdated?.();
      router.refresh();
    } catch (err: unknown) {
      setActionError((err as Error).message || "Failed to update interview.");
    } finally {
      setIsActionSubmitting(false);
    }
  };

  // 4. Confirm Delete Campaign
  const handleConfirmDelete = async () => {
    if (!activeInterviewId) return;

    try {
      setIsActionSubmitting(true);
      setActionError(null);

      const rawToken = document.cookie
        .split("; ")
        .find((row) => row.startsWith("access_token="))
        ?.split("=")[1];
      const tokenCookie = rawToken ? decodeURIComponent(rawToken) : null;

      if (!tokenCookie) {
        throw new Error("You must be logged in to delete an interview.");
      }

      await deleteInterviewApi(activeInterviewId, tokenCookie);
      setIsDeleteConfirmOpen(false);
      onCampaignDeleted?.(activeInterviewId);
      handleCloseDialog();
      router.refresh();
    } catch (err: unknown) {
      setActionError((err as Error).message || "Failed to delete interview.");
    } finally {
      setIsActionSubmitting(false);
    }
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
              onClick={handleShare}
              className="w-7 h-7 rounded-lg text-[#616161] hover:bg-gray-200 hover:text-[#272727] transition-colors flex items-center justify-center cursor-pointer relative"
              title="Share Link"
            >
              {isShareNoticeVisible ? (
                <Check className="w-4 h-4 text-emerald-600" />
              ) : (
                <Share2 className="w-4 h-4" />
              )}
            </button>
            <button
              onClick={handleOpenEdit}
              className="w-7 h-7 rounded-lg text-[#616161] hover:bg-gray-200 hover:text-[#272727] transition-colors flex items-center justify-center cursor-pointer"
              title="Edit Interview"
            >
              <Pencil className="w-4 h-4" />
            </button>
            <button
              onClick={() => {
                setActionError(null);
                setIsDeleteConfirmOpen(true);
              }}
              className="w-7 h-7 rounded-lg text-[#616161] hover:bg-red-50 hover:text-red-600 transition-colors flex items-center justify-center cursor-pointer"
              title="Delete Interview"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        </div>

        {isShareNoticeVisible && (
          <div className="mx-7.5 mt-3 px-4 py-2 bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-semibold rounded-xl flex items-center gap-2 animate-in fade-in duration-150">
            <Check className="w-4 h-4 text-emerald-600 shrink-0" />
            <span>Interview detail link copied to clipboard!</span>
          </div>
        )}

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
                <div className="relative group flex items-center">
                  <button className="cursor-help p-1 hover:bg-gray-100 rounded-md transition-colors">
                    <Info className="w-4 h-4 text-[#616161]" />
                  </button>
                  <div className="absolute bottom-full right-0 mb-2 hidden group-hover:block w-52 p-2.5 bg-gray-900 text-white text-xs font-medium rounded-xl shadow-xl z-50 pointer-events-none">
                    Shows candidate progress through the interview pipeline.
                    <div className="absolute top-full right-3 border-4 border-transparent border-t-gray-900"></div>
                  </div>
                </div>
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
                <div className="relative group flex items-center">
                  <button className="cursor-help p-1 hover:bg-gray-100 rounded-md transition-colors">
                    <Info className="w-4 h-4 text-[#616161]" />
                  </button>
                  <div className="absolute bottom-full right-0 mb-2 hidden group-hover:block w-56 p-2.5 bg-gray-900 text-white text-xs font-medium rounded-xl shadow-xl z-50 pointer-events-none">
                    Shows the distribution of candidate scores and recommendations.
                    <div className="absolute top-full right-3 border-4 border-transparent border-t-gray-900"></div>
                  </div>
                </div>
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
              Candidates ({displayedCandidates.length})
            </h3>
            <div className="relative">
              <button 
                title="Filter Candidates" 
                onClick={() => setIsFilterMenuOpen(!isFilterMenuOpen)} 
                className={`text-[#616161] hover:text-[#272727] transition-colors cursor-pointer p-1 rounded-md hover:bg-gray-100 ${isFilterMenuOpen ? 'bg-gray-100' : ''}`}
              >
                <SlidersHorizontal className="w-4 h-4" />
              </button>
              {isFilterMenuOpen && (
                <>
                  <div className="fixed inset-0 z-40" onClick={() => setIsFilterMenuOpen(false)} />
                  <div className="absolute right-0 mt-2 w-48 bg-white rounded-xl shadow-xl border border-[#E9E9E9] py-2 z-50 animate-in fade-in zoom-in-95 duration-150">
                    <div className="px-3 pb-2 text-xs font-bold text-[#616161] border-b border-[#F1F1F1] mb-1">Filter Status</div>
                    {(['ALL', 'Not-started', 'On-Interview', 'Done'] as const).map(status => (
                      <button 
                        key={status}
                        onClick={() => { setCandidateFilter(status); setIsFilterMenuOpen(false); }}
                        className={`w-full text-left px-4 py-2 text-sm text-[#272727] hover:bg-gray-50 transition-colors flex items-center justify-between ${candidateFilter === status ? 'font-semibold text-[#FE6100]' : ''}`}
                      >
                        {status === 'ALL' ? 'All' : status.replace('-', ' ')}
                        {candidateFilter === status && <Check className="w-3.5 h-3.5" />}
                      </button>
                    ))}
                  </div>
                </>
              )}
            </div>
          </div>
          {/* Candidates List Container without inner clipping */}
          <div className="border border-[#F1F1F1] rounded-[14px] mb-8">
            {displayedCandidates.length === 0 && (
              <div className="py-8 text-center text-[#616161] text-sm font-medium">
                No candidates found.
              </div>
            )}
            {/* Candidates List Header */}
            {displayedCandidates.map((candidate, idx) => {
              const isLastItem = idx === displayedCandidates.length - 1;
              const isNearBottom = (idx >= displayedCandidates.length - 2 && displayedCandidates.length >= 3) || (isLastItem && displayedCandidates.length > 1);
              return (
              <div
                key={candidate.id || idx}
                onClick={() => handleCandidateClick(candidate)}
                className={`px-2.5 py-2.5 flex items-center justify-between cursor-pointer hover:bg-gray-50/80 transition-colors ${idx !== displayedCandidates.length - 1 ? "border-b border-[#F1F1F1]" : ""}`}
              >
                <div className="flex items-center gap-2.5">
                  <UserAvatar className="w-9.5 h-9.5" />
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
                      {candidate.stageStatus === "finished" && (
                        <span className="px-3 py-1 bg-[#DCFCE7] text-[#16A34A] rounded-full text-xs font-medium">
                          finished
                        </span>
                      )}
                      {candidate.stageStatus === "in-progress" && (
                        <span className="px-3 py-1 bg-[#EFF6FF] text-[#2563EB] rounded-full text-xs font-medium">
                          in-progress
                        </span>
                      )}
                      {candidate.stageStatus === "not-started" && (
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

                  <div className="relative flex items-center">
                    <button 
                      title="Candidate Options" 
                      onClick={(e) => { 
                        e.stopPropagation(); 
                        setActiveCandidateMenuId(activeCandidateMenuId === candidate.id ? null : candidate.id); 
                      }} 
                      className={`text-[#B8B8B8] hover:text-[#616161] transition-colors cursor-pointer p-1 rounded-md hover:bg-gray-100 ${activeCandidateMenuId === candidate.id ? 'bg-gray-100' : ''}`}
                    >
                      <MoreVertical className="w-5 h-5" />
                    </button>
                    
                    {activeCandidateMenuId === candidate.id && (
                      <>
                        <div className="fixed inset-0 z-40" onClick={(e) => { e.stopPropagation(); setActiveCandidateMenuId(null); }} />
                        <div className={`absolute right-0 ${isNearBottom ? 'bottom-full mb-1' : 'top-full mt-1'} w-32 bg-white rounded-xl shadow-xl border border-[#E9E9E9] py-1 z-50 animate-in fade-in zoom-in-95 duration-150`}>
                          <button 
                            onClick={(e) => {
                              e.stopPropagation();
                              setActiveCandidateMenuId(null);
                              handleCandidateClick(candidate);
                            }}
                            className="w-full text-left px-4 py-2 text-sm text-[#272727] hover:bg-gray-50 transition-colors"
                          >
                            Open
                          </button>
                          <button 
                            onClick={(e) => {
                              e.stopPropagation();
                              setActiveCandidateMenuId(null);
                              // Simple local delete for now
                              setCandidatesListState(prev => prev.filter(c => c.id !== candidate.id));
                              setCandidateNoticeMessage(`Removed candidate "${candidate.name}".`);
                              setTimeout(() => setCandidateNoticeMessage(null), 3000);
                            }}
                            className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors font-medium"
                          >
                            Delete
                          </button>
                        </div>
                      </>
                    )}
                  </div>
                </div>
              </div>
            )})}
          </div>
        </div>
      </div>

      {/* Edit Interview Modal */}
      {isEditModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm animate-in fade-in duration-150">
          <div className="bg-white rounded-3xl border border-[#F1F1F1] p-6 shadow-2xl w-full max-w-lg space-y-5 animate-in zoom-in-95 duration-150">
            <div className="flex items-center justify-between border-b border-[#F1F1F1] pb-3">
              <h3 className="text-lg font-bold text-[#272727]">Edit Interview Position</h3>
              <button
                onClick={() => setIsEditModalOpen(false)}
                className="p-1.5 text-gray-400 hover:text-gray-700 rounded-full hover:bg-gray-100 cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {actionError && (
              <div className="p-3 bg-red-50 text-red-600 text-xs font-semibold rounded-xl border border-red-100">
                {actionError}
              </div>
            )}

            <form onSubmit={handleSaveEdit} className="space-y-4 text-left">
              <div>
                <label className="block text-xs font-semibold text-[#272727] mb-1.5">
                  Job Name *
                </label>
                <input
                  type="text"
                  value={editFormData.job_name}
                  onChange={(e) =>
                    setEditFormData({ ...editFormData, job_name: e.target.value })
                  }
                  className="w-full px-3.5 py-2.5 bg-white border border-[#E9E9E9] rounded-xl text-sm font-medium text-[#272727] focus:outline-none focus:border-[#FE6100]"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#272727] mb-1.5">
                  Job Description *
                </label>
                <textarea
                  value={editFormData.job_description}
                  onChange={(e) =>
                    setEditFormData({
                      ...editFormData,
                      job_description: e.target.value,
                    })
                  }
                  className="w-full h-28 px-3.5 py-2.5 bg-white border border-[#E9E9E9] rounded-xl text-sm font-medium text-[#272727] focus:outline-none focus:border-[#FE6100] resize-none"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-[#272727] mb-1.5">
                    Difficulty
                  </label>
                  <select
                    value={editFormData.difficulty}
                    onChange={(e) =>
                      setEditFormData({
                        ...editFormData,
                        difficulty: e.target.value,
                      })
                    }
                    className="w-full px-3.5 py-2.5 bg-white border border-[#E9E9E9] rounded-xl text-sm font-medium text-[#272727] focus:outline-none focus:border-[#FE6100] cursor-pointer"
                  >
                    <option value="junior">Junior</option>
                    <option value="mid">Mid</option>
                    <option value="senior">Senior</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-[#272727] mb-1.5">
                    Domain Hint
                  </label>
                  <input
                    type="text"
                    value={editFormData.domain_hint}
                    onChange={(e) =>
                      setEditFormData({
                        ...editFormData,
                        domain_hint: e.target.value,
                      })
                    }
                    className="w-full px-3.5 py-2.5 bg-white border border-[#E9E9E9] rounded-xl text-sm font-medium text-[#272727] focus:outline-none focus:border-[#FE6100]"
                    placeholder="e.g. React & TypeScript"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#272727] mb-1.5">
                  Scheduled Date (Optional)
                </label>
                <input
                  type="datetime-local"
                  value={editFormData.scheduled_at}
                  onChange={(e) =>
                    setEditFormData({
                      ...editFormData,
                      scheduled_at: e.target.value,
                    })
                  }
                  className="w-full px-3.5 py-2.5 bg-white border border-[#E9E9E9] rounded-xl text-sm font-medium text-[#272727] focus:outline-none focus:border-[#FE6100]"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-3 border-t border-[#F1F1F1]">
                <button
                  type="button"
                  onClick={() => setIsEditModalOpen(false)}
                  disabled={isActionSubmitting}
                  className="px-5 py-2 rounded-full text-xs font-semibold text-[#616161] hover:bg-gray-100 cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isActionSubmitting}
                  className="px-6 py-2.5 bg-[#FE6100] text-white rounded-full text-xs font-bold hover:bg-[#e05600] flex items-center gap-1.5 cursor-pointer shadow-md shadow-[#FE6100]/20 disabled:opacity-50"
                >
                  {isActionSubmitting ? (
                    <>
                      <Loader2 className="w-3.5 h-3.5 animate-spin" /> Saving...
                    </>
                  ) : (
                    "Save Changes"
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {isDeleteConfirmOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm animate-in fade-in duration-150">
          <div className="bg-white rounded-3xl border border-[#F1F1F1] p-6 shadow-2xl w-full max-w-sm text-center space-y-4 animate-in zoom-in-95 duration-150">
            <div className="w-12 h-12 rounded-full bg-red-100 text-red-600 flex items-center justify-center mx-auto">
              <AlertTriangle className="w-6 h-6" />
            </div>
            <div>
              <h3 className="text-base font-bold text-[#272727]">Delete Interview Campaign?</h3>
              <p className="text-xs text-[#616161] mt-1 font-medium leading-relaxed">
                Are you sure you want to delete <span className="font-semibold text-gray-900">&quot;{targetCampaign.jobTitle}&quot;</span>? This action will permanently remove all candidates, goals, and evaluation reports.
              </p>
            </div>

            {actionError && (
              <div className="p-2.5 bg-red-50 text-red-600 text-xs font-medium rounded-xl">
                {actionError}
              </div>
            )}

            <div className="flex items-center justify-center gap-3 pt-2">
              <button
                type="button"
                onClick={() => setIsDeleteConfirmOpen(false)}
                disabled={isActionSubmitting}
                className="px-5 py-2.5 rounded-full text-xs font-semibold text-[#616161] hover:bg-gray-100 cursor-pointer"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleConfirmDelete}
                disabled={isActionSubmitting}
                className="px-5 py-2.5 bg-red-600 hover:bg-red-700 text-white rounded-full text-xs font-bold flex items-center gap-1.5 shadow-md shadow-red-600/20 cursor-pointer disabled:opacity-50"
              >
                {isActionSubmitting ? (
                  <>
                    <Loader2 className="w-3.5 h-3.5 animate-spin" /> Deleting...
                  </>
                ) : (
                  "Delete Campaign"
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
