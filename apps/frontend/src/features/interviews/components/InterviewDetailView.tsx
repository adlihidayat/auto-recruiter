"use client";

/**
 * What: Real Interview Detail Client View component.
 * Why: Fetches and displays actual interview parameters, AI-generated goal plans, and registered candidate statuses from PostgreSQL backend.
 * Boundaries: Connects client UI to FastAPI backend endpoints via typed API client.
 */

import React, { useState, useEffect } from "react";
import { ExternalLink, CheckCircle2, AlertTriangle, Trash2, AlertCircle } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  getInterviewDetailApi,
  getInterviewGoalsApi,
  getCandidatesForInterviewApi,
  deleteInterviewApi,
  BackendInterviewResponse,
  BackendGoalResponse,
  BackendCandidateResponse,
} from "@/lib/api/client";
import { InterviewDetailSkeleton } from "@/components/common/PageSkeletonWrapper";

interface InterviewDetailViewProps {
  interviewId: string;
}

export default function InterviewDetailView({ interviewId }: InterviewDetailViewProps) {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(true);
  const [isDeleting, setIsDeleting] = useState(false);
  const [unavailableCandidate, setUnavailableCandidate] = useState<BackendCandidateResponse | null>(null);
  const [interview, setInterview] = useState<BackendInterviewResponse | null>(null);
  const [goals, setGoals] = useState<BackendGoalResponse[]>([]);
  const [candidates, setCandidates] = useState<BackendCandidateResponse[]>([]);

  useEffect(() => {
    let isCancelled = false;

    async function loadData() {
      try {
        const rawToken = document.cookie
          .split("; ")
          .find((row) => row.startsWith("access_token="))
          ?.split("=")[1];
        const tokenCookie = rawToken ? decodeURIComponent(rawToken) : null;
        if (!tokenCookie) {
          if (!isCancelled) setIsLoading(false);
          return;
        }

        const [detailRes, goalsRes, candRes] = await Promise.all([
          getInterviewDetailApi(interviewId, tokenCookie).catch(() => null),
          getInterviewGoalsApi(interviewId, tokenCookie).catch(() => []),
          getCandidatesForInterviewApi(interviewId, tokenCookie).catch(() => []),
        ]);

        if (!isCancelled) {
          if (detailRes) setInterview(detailRes);
          if (goalsRes) setGoals(goalsRes);
          if (candRes) setCandidates(candRes);
          setIsLoading(false);
        }
      } catch (err) {
        console.warn("Failed to load interview details from DB", err);
        if (!isCancelled) setIsLoading(false);
      }
    }

    loadData();

    return () => {
      isCancelled = true;
    };
  }, [interviewId]);

  const handleDelete = async () => {
    if (!window.confirm("Are you sure you want to delete this interview campaign?")) return;
    setIsDeleting(true);
    try {
      const rawToken = document.cookie
        .split("; ")
        .find((row) => row.startsWith("access_token="))
        ?.split("=")[1];
      const tokenCookie = rawToken ? decodeURIComponent(rawToken) : null;
      if (tokenCookie) {
        await deleteInterviewApi(interviewId, tokenCookie);
        router.push("/");
        router.refresh();
      }
    } catch (err) {
      console.error("Failed to delete interview", err);
      setIsDeleting(false);
    }
  };

  if (isLoading) {
    return <InterviewDetailSkeleton />;
  }

  // Fallback metadata if missing
  const jobName = interview?.job_name || "Interview Detail";
  const difficulty = interview?.difficulty || "Mid";
  const status = interview?.status || "active";
  const formattedDate = interview?.created_at
    ? new Date(interview.created_at).toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
        year: "numeric",
      })
    : "Recently";

  return (
    <div className="flex flex-col h-full bg-white overflow-y-auto">
      <div className="px-8 py-8 max-w-[900px] w-full mx-auto">
        {/* Breadcrumb */}
        <div className="flex items-center gap-2 text-sm text-gray-600 mb-8">
          <Link href="/" className="hover:text-gray-900 transition-colors">
            Home
          </Link>
          <span className="text-gray-300">/</span>
          <Link href="/" className="hover:text-gray-900 transition-colors">
            Interview List
          </Link>
          <span className="text-gray-300">/</span>
          <span className="font-medium text-gray-900 truncate max-w-xs">{jobName}</span>
        </div>

        {/* Header Section */}
        <div className="flex flex-col gap-2 mb-8">
          <div className="w-10 h-10 rounded-xl bg-orange-50 flex items-center justify-center border border-orange-100 text-xl">
            😀️
          </div>
          <div className="flex justify-between gap-1 items-start">
            <div>
              <div className="flex items-center gap-3 mt-2">
                <h1 className="text-2xl font-bold text-gray-900">{jobName}</h1>
                <span className="px-2 py-0.5 bg-emerald-100 text-emerald-700 text-xs font-semibold rounded-md capitalize">
                  {status}
                </span>
              </div>
              <div className="flex items-center gap-3 mt-1 text-sm text-gray-600">
                <span>{interview?.domain_hint || "General"}</span>
                <span>/</span>
                <span className="capitalize">{difficulty}</span>
                <span>/</span>
                <span>{formattedDate}</span>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <button
                type="button"
                onClick={() => router.push("/")}
                className="flex items-center gap-1.5 px-3 py-1.5 border border-gray-200 text-gray-900 text-sm font-medium rounded-lg hover:bg-gray-50 transition-colors cursor-pointer"
              >
                Back <ExternalLink className="w-3.5 h-3.5" />
              </button>
              <button
                type="button"
                onClick={handleDelete}
                disabled={isDeleting}
                className="flex items-center gap-1.5 px-3 py-1.5 bg-[#EA3536] text-white text-sm font-medium rounded-lg hover:bg-red-600 transition-colors cursor-pointer disabled:opacity-50"
              >
                <Trash2 className="w-3.5 h-3.5" />
                {isDeleting ? "Deleting..." : "Delete Interview"}
              </button>
            </div>
          </div>
        </div>

        {/* Hero Banner */}
        <div className="w-full h-32 rounded-2xl bg-gradient-to-r from-emerald-100 to-teal-100 border border-emerald-200 mb-10 flex items-center justify-center p-6 relative overflow-hidden">
          <div className="absolute inset-0 opacity-20 bg-[radial-gradient(#10b981_1px,transparent_1px)] [background-size:16px_16px]"></div>
          <div className="relative bg-white/90 backdrop-blur-sm px-6 py-2.5 rounded-full border border-white/50 flex items-center gap-3 text-sm font-medium text-gray-800">
            <div className="w-5 h-5 rounded bg-emerald-100 text-base flex items-center justify-center">
              😀️
            </div>
            {jobName}
          </div>
        </div>

        {/* Interview Plan Section */}
        <div className="mb-10">
          <h2 className="text-base font-semibold text-gray-900 mb-3">
            Interview Plan ({goals.length} Goals)
          </h2>
          {goals.length === 0 ? (
            <div className="p-6 border border-gray-200 rounded-xl bg-gray-50 text-center text-sm text-gray-500">
              No specific evaluation goals generated yet.
            </div>
          ) : (
            <div className="space-y-6">
              {goals.map((planItem, planIdx) => (
                <div
                  key={planItem.id || planIdx}
                  className="border border-gray-200 rounded-xl overflow-hidden bg-white shadow-xs"
                >
                  <div className="flex border-b border-gray-100">
                    <div className="flex-1 px-4 py-4 text-sm text-gray-900 leading-relaxed font-medium">
                      <span className="font-semibold text-gray-500 mr-2">Goal ({planItem.goal_ref || `g_0${planIdx + 1}`}):</span>
                      {planItem.goal || planItem.topic}
                    </div>
                  </div>

                  <div className="p-4 space-y-4 bg-[#FAFAFA]">
                    {planItem.passing_criteria && planItem.passing_criteria.length > 0 && (
                      <div>
                        <h3 className="text-xs font-semibold text-gray-900 uppercase tracking-wider mb-2">
                          Required Signals:
                        </h3>
                        <ul className="space-y-2">
                          {planItem.passing_criteria.map((crit, idx) => (
                            <li key={idx} className="flex items-start gap-2 text-sm text-gray-900">
                              <CheckCircle2 className="w-4 h-4 text-emerald-500 mt-0.5 flex-shrink-0" />
                              {crit}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {planItem.wrong_answer_signals && planItem.wrong_answer_signals.length > 0 && (
                      <div>
                        <h3 className="text-xs font-semibold text-gray-900 uppercase tracking-wider mb-2 mt-4">
                          Red Flags:
                        </h3>
                        <ul className="space-y-2">
                          {planItem.wrong_answer_signals.map((trigger, idx) => (
                            <li key={idx} className="flex items-start gap-2 text-sm text-gray-900">
                              <AlertTriangle className="w-4 h-4 text-amber-500 mt-0.5 flex-shrink-0" />
                              {trigger}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Candidates List */}
        <div className="mb-10">
          <h2 className="text-base font-semibold text-gray-900 mb-3">
            Candidates ({candidates.length})
          </h2>
          <div className="border border-gray-200 rounded-xl bg-white flex flex-col">
            {candidates.length === 0 ? (
              <div className="p-6 text-center text-sm text-gray-500">
                No candidates registered for this campaign yet.
              </div>
            ) : (
              <div className="overflow-y-auto max-h-96 divide-y divide-gray-100">
                {candidates.map((candidate) => {
                  const candName =
                    `${candidate.first_name || ""} ${candidate.last_name || ""}`.trim() ||
                    candidate.email;
                  const statusLower = (candidate.status || "not-started").toLowerCase();

                  const isFinished =
                    statusLower === "finished" ||
                    statusLower === "evaluated" ||
                    statusLower === "completed" ||
                    statusLower === "passed" ||
                    statusLower === "rejected";

                  const isInProgress =
                    statusLower === "in_progress" ||
                    statusLower === "in-progress" ||
                    statusLower === "pending" ||
                    statusLower === "interviewer_live" ||
                    statusLower === "grader_evaluating";

                  // Status dot color matching dashboard table (Gray = Not Started, Blue = On Progress, Green = Finished)
                  let statusDotClass = "bg-gray-400 shadow-[0_0_0_2px_rgba(156,163,175,0.2)]";
                  let statusText = "Not Started";
                  if (isFinished) {
                    statusDotClass = "bg-emerald-500 shadow-[0_0_0_2px_rgba(16,185,129,0.2)]";
                    statusText = "Finished";
                  } else if (isInProgress) {
                    statusDotClass = "bg-blue-500 shadow-[0_0_0_2px_rgba(59,130,246,0.2)]";
                    statusText = "On Progress";
                  }

                  // Determine recommendation badge beside email if finished
                  let recBadge = null;
                  if (isFinished) {
                    const rawRec = candidate.recommendation || "";
                    const score = candidate.composite_score;

                    if (
                      rawRec.toLowerCase().includes("advance with") ||
                      (score !== null && score !== undefined && score >= 50 && score < 80)
                    ) {
                      recBadge = (
                        <span className="px-2 py-0.5 text-[11px] font-semibold rounded-md bg-amber-50 text-amber-700 border border-amber-200">
                          Advance with follow up
                        </span>
                      );
                    } else if (
                      rawRec.toLowerCase().includes("advance") ||
                      (score !== null && score !== undefined && score >= 80)
                    ) {
                      recBadge = (
                        <span className="px-2 py-0.5 text-[11px] font-semibold rounded-md bg-emerald-50 text-emerald-700 border border-emerald-200">
                          Advance
                        </span>
                      );
                    } else {
                      recBadge = (
                        <span className="px-2 py-0.5 text-[11px] font-semibold rounded-md bg-red-50 text-red-700 border border-red-200">
                          Hold
                        </span>
                      );
                    }
                  }

                  return (
                    <div
                      key={candidate.id}
                      onClick={() => {
                        if (isFinished) {
                          router.push(
                            `/interviews/${interviewId}/candidates/${candidate.id}`,
                          );
                        } else {
                          setUnavailableCandidate(candidate);
                        }
                      }}
                      className="flex items-center justify-between px-4 py-4 hover:bg-gray-50 transition-colors cursor-pointer group"
                    >
                      <div className="flex items-center gap-3">
                        <div className="w-6 h-6 rounded-full bg-[#eaeaea] flex items-center justify-center flex-shrink-0 text-black text-xs font-bold uppercase">
                          {candName.charAt(0)}
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">
                            {candName}
                          </span>
                          <span className="text-sm text-gray-600">{candidate.email}</span>
                          {recBadge}
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <span className="text-xs text-gray-500 font-medium capitalize">
                          Status: {statusText}
                        </span>
                        <span className={`w-2 h-2 rounded-full ${statusDotClass}`} />
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Report Not Available Modal Overlay */}
      {unavailableCandidate && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-xs p-4 animate-in fade-in duration-150">
          <div className="bg-white rounded-2xl border border-gray-200 shadow-xl max-w-md w-full p-6 text-center space-y-4">
            <div className="w-12 h-12 rounded-full bg-amber-50 text-amber-600 flex items-center justify-center mx-auto border border-amber-100">
              <AlertCircle className="w-6 h-6" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-gray-900 mb-1">
                Report Not Available
              </h3>
              <p className="text-xs text-gray-600 leading-relaxed">
                The evaluation report for{" "}
                <span className="font-semibold text-gray-900">
                  {`${unavailableCandidate.first_name || ""} ${unavailableCandidate.last_name || ""}`.trim() || unavailableCandidate.email}
                </span>{" "}
                is not available yet. Reports are generated automatically once the candidate completes their AI interview.
              </p>
            </div>
            <button
              type="button"
              onClick={() => setUnavailableCandidate(null)}
              className="w-full py-2.5 bg-gray-900 text-white rounded-xl text-xs font-semibold hover:bg-black transition-colors cursor-pointer"
            >
              Okay, got it
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
