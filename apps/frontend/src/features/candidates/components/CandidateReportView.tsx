/* eslint-disable @typescript-eslint/no-explicit-any */
"use client";

import React, { useState, useEffect } from "react";
import {
  ChevronDown,
  ChevronUp,
  Triangle,
  MessageCircle,
  Bot,
  AudioLines,
  Brain,
} from "lucide-react";
import Link from "next/link";
import {
  getCandidateReportApi,
  getCandidateTranscriptsApi,
  getCandidatesForInterviewApi,
} from "@/lib/api/client";
import { CandidateReportSkeleton } from "@/components/common/PageSkeletonWrapper";

interface CandidateReportViewProps {
  interviewId?: string;
  candidateId?: string;
}

export default function CandidateReportView({
  interviewId,
  candidateId,
}: CandidateReportViewProps) {
  const [isLoading, setIsLoading] = useState(true);
  const [report, setReport] = useState<any>(null);
  const [transcripts, setTranscripts] = useState<any[]>([]);
  const [candidateInfo, setCandidateInfo] = useState<any>(null);

  const [expandedGoalId, setExpandedGoalId] = useState<string | null>("g_01");
  const [expandedTraitId, setExpandedTraitId] = useState<string | null>(
    "clarity",
  );

  const toggleGoal = (id: string) => {
    setExpandedGoalId((prev) => (prev === id ? null : id));
  };

  const toggleTrait = (trait: string) => {
    setExpandedTraitId((prev) => (prev === trait ? null : trait));
  };

  useEffect(() => {
    async function loadData() {
      if (!candidateId) return;
      try {
        const rawToken = document.cookie
          .split("; ")
          .find((row) => row.startsWith("access_token="))
          ?.split("=")[1];
        const tokenCookie = rawToken ? decodeURIComponent(rawToken) : null;
        if (!tokenCookie) return;

        const reportPromise = getCandidateReportApi(candidateId, tokenCookie).catch(() => null);
        const transcriptsPromise = getCandidateTranscriptsApi(candidateId, tokenCookie).catch(() => null);
        const candidatesPromise = interviewId
          ? getCandidatesForInterviewApi(interviewId, tokenCookie).catch(() => null)
          : Promise.resolve(null);

        const [reportRes, transcriptsRes, candidatesRes] = await Promise.all([
          reportPromise,
          transcriptsPromise,
          candidatesPromise,
        ]);

        if (reportRes) {
          const raw = reportRes.raw_report || {};
          setReport({
            ...raw,
            recommendation: raw.recommendation || (reportRes as any).recommendation || "Advance",
            reasoning: reportRes.reasoning || raw.reasoning || raw.status_reason || raw.short_summary,
            goals: raw.goals || [],
            communication: raw.communication || {},
          });
        }

        if (transcriptsRes && transcriptsRes.length > 0) {
          setTranscripts(transcriptsRes);
        }

        const cInfo = (candidatesRes as any[])?.find(
          (c: any) => c.id === candidateId,
        );
        if (cInfo) setCandidateInfo(cInfo);
      } catch (err) {
        console.warn("Failed to load candidate data", err);
      } finally {
        setIsLoading(false);
      }
    }
    loadData();
  }, [candidateId, interviewId]);

  if (isLoading) {
    return <CandidateReportSkeleton />;
  }

  // Real DB data with clean fallback
  const recommendation = report?.recommendation || "Advance";
  const reasoning =
    typeof report?.reasoning === "string"
      ? report.reasoning
      : Array.isArray(report?.reasoning)
        ? report.reasoning.join(" ")
        : "The candidate has completed the automated AI interview evaluation pipeline. Detailed scoring criteria, required signals, and turn-by-turn conversation transcripts are recorded below.";

  const communication = report?.communication || {
    overall: {
      is_passed: true,
      confidence: "high",
      rationale:
        "Candidate exhibited clear, structured communication across all traits.",
    },
    traits: {
      clarity: {
        is_passed: true,
        score: 10.0,
        rationale:
          "Clear and direct explanations without filler words or ambiguity.",
        criteria_match: {
          passing_met: [
            {
              quote:
                "I prefer sync.RWMutex over channels when guarding simple in-memory maps.",
            },
            {
              quote:
                "We implement client-side load balancing to avoid connection multiplexing issues.",
            },
          ],
        },
      },
      structure: {
        is_passed: true,
        score: 9.0,
        rationale: "Maintained logical flow throughout answers.",
        criteria_match: {
          passing_met: [
            {
              quote:
                "First I'll address L4 load balancing, then transition to client-side balancing.",
            },
          ],
        },
      },
    },
  };

  const goals = report?.goals || [
    {
      goal_id: "g_01",
      topic: "Go Performance & Concurrency",
      score: 10.0,
      confidence: "high",
      rationale:
        "The candidate correctly identified the use case for sync.RWMutex and mentioned the -race flag for detecting race conditions.",
      criteria_match: {
        passing_met: [
          {
            quote:
              "I prefer sync.RWMutex over channels when guarding simple in-memory maps.",
          },
          {
            quote:
              "I always run tests with the -race detector flag enabled in CI/CD.",
          },
        ],
      },
      interaction_history: [
        {
          turn_id: "t_01",
          role: "interviewer",
          content:
            "How do you handle race conditions in Go services? How do you handle race conditions in Go services? How do you handle race conditions in Go services?",
        },
        {
          turn_id: "t_02",
          role: "candidate",
          content:
            "I always run tests with the -race detector flag enabled in CI/CD. For shared state, I prefer sync.RWMutex over channels when guarding simple in-memory maps.",
        },
        {
          turn_id: "t_01",
          role: "interviewer",
          content: "How do you handle race conditions in Go services?",
        },
        {
          turn_id: "t_02",
          role: "candidate",
          content:
            "I always run tests with the -race detector flag enabled in CI/CD. For shared state, I prefer sync.RWMutex over channels when guarding simple in-memory maps.",
        },
      ],
    },
    {
      goal_id: "g_02",
      topic: "System Architecture & Database Indexing",
      score: 9.0,
      confidence: "high",
      rationale:
        "The candidate correctly identified the use of EXPLAIN ANALYZE and specific index types like B-tree and partial indexes.",
      criteria_match: {
        passing_met: [
          { quote: "I run EXPLAIN ANALYZE to inspect the query plan" },
        ],
      },
      interaction_history: [
        {
          turn_id: "t_03",
          role: "interviewer",
          content:
            "What steps do you take when a query is running slowly in production?",
        },
        {
          turn_id: "t_04",
          role: "candidate",
          content:
            "I run EXPLAIN ANALYZE to inspect the query plan and look for sequential scans. Then I add targeted B-tree indexes or partial indexes where appropriate.",
        },
        {
          turn_id: "t_01",
          role: "interviewer",
          content:
            "How do you handle race conditions in Go services? How do you handle race conditions in Go services? How do you handle race conditions in Go services?",
        },
        {
          turn_id: "t_02",
          role: "candidate",
          content:
            "I always run tests with the -race detector flag enabled in CI/CD. For shared state, I prefer sync.RWMutex over channels when guarding simple in-memory maps.",
        },
        {
          turn_id: "t_01",
          role: "interviewer",
          content: "How do you handle race conditions in Go services?",
        },
      ],
    },
  ];

  const fullName = candidateInfo?.first_name
    ? `${candidateInfo.first_name} ${candidateInfo.last_name || ""}`.trim()
    : "Alice Johnson";

  const email = candidateInfo?.email || "alice.j@example.com";

  const defaultTranscripts = [
    {
      role: "interviewer",
      time: "11:23 AM",
      content:
        "Hi Alice, let's start with a distributed systems question. How would you handle load balancing for a gRPC microservice?",
    },
    {
      role: "candidate",
      time: "11:24 AM",
      content:
        "For gRPC, standard L4 load balancing like a simple ClusterIP won't work well because of HTTP/2 connection multiplexing. I would propose an L7 solution like Envoy or Istio, or implement client-side load balancing.",
    },
    {
      role: "interviewer",
      time: "11:25 AM",
      content:
        "Great point. What about managing goroutines safely if a client suddenly disconnects?",
    },
    {
      role: "candidate",
      time: "11:26 AM",
      content:
        "I would use context propagation. By passing the request context down to all goroutines, we can listen for ctx.Done() and cleanly tear down resources if the deadline is exceeded or the client cancels.",
    },
  ];

  return (
    <div className="flex flex-col h-full bg-white overflow-y-auto">
      <div className="px-8 py-10 max-w-200 w-full mx-auto font-sans">
        {/* Breadcrumb */}
        <div className="flex items-center gap-2 text-sm font-medium text-gray-400 mb-10">
          <Link href="/" className="hover:text-gray-900 transition-colors">
            Home
          </Link>
          <span>/</span>
          <Link href="/" className="hover:text-gray-900 transition-colors">
            Interview List
          </Link>
          <span>/</span>
          <Link
            href={interviewId ? `/interviews/${interviewId}` : "/"}
            className="hover:text-gray-900 transition-colors cursor-pointer"
          >
            Campaign Details
          </Link>
          <span>/</span>
          <span className="text-gray-900">{fullName}</span>
        </div>

        {/* Minimalist Header */}
        <div className="mb-10">
          <div className="flex items-center gap-4 mb-0">
            <h1 className="text-[28px] font-bold text-gray-900 leading-tight mb-2 tracking-tight">
              {fullName}
            </h1>
            <div
              className={`px-2.5 py-1 text-xs font-bold uppercase tracking-wider rounded-md ${recommendation.includes("Advance") ? "bg-emerald-100 text-emerald-700" : "bg-gray-100 text-gray-700"}`}
            >
              {recommendation.includes("Advance") ? "Advance" : "Hold / Reject"}
            </div>
          </div>
          <p className="text-sm font-medium text-gray-600">{email}</p>
        </div>

        <p className="text-[14px] text-gray-600 leading-relaxed font-medium mb-8">
          {reasoning}
        </p>
        {/* General Summary (Clean white card) */}
        {/* <div className="bg-white border border-gray-200 rounded-xl p-6 mb-8">
          <div className="flex items-start justify-between mb-4">
            <h2 className="text-sm font-semibold text-gray-900">
              General Summary
            </h2>
            <div
              className={`px-2.5 py-1 text-xs font-bold uppercase tracking-wider rounded-md ${recommendation.includes("Advance") ? "bg-emerald-100 text-emerald-700" : "bg-gray-100 text-gray-700"}`}
            >
              Status:{" "}
              {recommendation.includes("Advance") ? "Advance" : "Hold / Reject"}
            </div>
          </div>
        </div> */}

        {/* Core Analysis Breakdown */}
        <div className="mb-8">
          <div className="flex items-center gap-2 mb-4">
            {/* <Target className="w-4 h-4 text-gray-600" /> */}
            <h2 className="text-sm font-semibold text-gray-600">
              Core Analysis Breakdown
            </h2>
          </div>

          <div className="bg-white border border-gray-200 rounded-xl overflow-hidden">
            <div className="divide-y divide-gray-100">
              {goals.map((goal: any, idx: number) => {
                const goalKey = goal.goal_id || `g_${idx}`;
                const isExpanded = expandedGoalId === goalKey;
                const isPassed = goal.score >= 7;

                return (
                  <div key={idx} className="transition-colors">
                    {/* Header Row */}
                    <button
                      type="button"
                      onClick={() => toggleGoal(goalKey)}
                      className="w-full flex items-center justify-between py-4 px-5 hover:bg-gray-50 text-left cursor-pointer transition-colors"
                    >
                      <div className="flex items-center gap-3">
                        <div className="w-5 h-5 shrink-0 flex items-center justify-center bg-[#6affe4] rounded">
                          <Brain
                            className="w-3 h-3 text-gray-600"
                            strokeWidth={3}
                          />
                        </div>
                        <span className="text-[14px] font-semibold text-gray-900 capitalize">
                          {goal.goal_id}
                        </span>
                        <span
                          className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                            isPassed
                              ? "bg-emerald-100 text-emerald-700"
                              : "bg-red-100 text-red-700"
                          }`}
                        >
                          {isPassed ? "PASS" : "FAIL"}
                        </span>
                      </div>
                      <div className="flex items-center gap-3">
                        <span className="text-xs font-semibold text-gray-600">
                          {goal.score}/10
                        </span>
                        {isExpanded ? (
                          <ChevronUp className="w-4 h-4 text-gray-400" />
                        ) : (
                          <ChevronDown className="w-4 h-4 text-gray-400" />
                        )}
                      </div>
                    </button>

                    {/* Dropdown Details (matching Shopify tool permissions gray box style) */}
                    {isExpanded && (
                      <div className="px-5 pb-5 pt-1 bg-white ">
                        <div className="p-4 bg-[#FAFAFA]  border border-gray-100 rounded-xl space-y-3">
                          <div className="mb-4">
                            <h4 className="text-xs font-bold text-gray-900 uppercase tracking-wider mb-1">
                              Rationale & Analysis
                            </h4>
                            <p className="text-[13px] font-medium text-gray-600 leading-relaxed">
                              {goal.rationale}
                            </p>
                          </div>

                          {goal.criteria_match?.passing_met?.length > 0 && (
                            <div>
                              <h4 className="text-xs font-bold text-gray-900 uppercase tracking-wider mb-2">
                                Evidence
                              </h4>
                              <div className="space-y-1.5">
                                {goal.criteria_match.passing_met.map(
                                  (match: any, i: number) => (
                                    <div
                                      key={i}
                                      className="flex items-center gap-2"
                                    >
                                      <Triangle
                                        fill="true"
                                        color=""
                                        className="w-2 h-2 rotate-90"
                                      />
                                      <p className="text-[12px] font-medium text-gray-600 italic">
                                        &quot;{match.quote}&quot;
                                      </p>
                                    </div>
                                  ),
                                )}
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Communication & Traits breakdown */}
        <div className="mb-8">
          <div className="flex items-center gap-2 mb-4">
            {/* <TrendingDown className="w-4 h-4 text-gray-600" /> */}
            <h2 className="text-sm font-semibold text-gray-600">
              Communication & Traits breakdown
            </h2>
          </div>

          <div className="bg-white border border-gray-200 rounded-xl overflow-hidden">
            <div className="divide-y divide-gray-100">
              {Object.entries(communication.traits || {}).map(
                ([trait, data]: [string, any]) => {
                  const isExpanded = expandedTraitId === trait;
                  const isPassed = data.is_passed ?? data.score >= 7;
                  const evidenceList =
                    data.criteria_match?.passing_met || data.evidence || [];

                  return (
                    <div key={trait} className="transition-colors">
                      <button
                        type="button"
                        onClick={() => toggleTrait(trait)}
                        className="w-full flex items-center justify-between py-4 px-5 hover:bg-gray-50 text-left cursor-pointer transition-colors"
                      >
                        <div className="flex items-center gap-3">
                          <div className="w-5 h-5 shrink-0 flex items-center justify-center bg-[#6affe4] rounded">
                            <AudioLines
                              className="w-4 h-4 text-gray-600"
                              strokeWidth={3}
                            />
                          </div>
                          <span className="text-[14px] font-semibold text-gray-900 capitalize">
                            {trait.replace("_", " ")}
                          </span>
                          <span
                            className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                              isPassed
                                ? "bg-emerald-100 text-emerald-700"
                                : "bg-red-100 text-red-700"
                            }`}
                          >
                            {isPassed ? "PASS" : "FAIL"}
                          </span>
                        </div>
                        <div className="flex items-center gap-3">
                          <span className="text-xs font-semibold text-gray-600">
                            {data.score}/10
                          </span>
                          {isExpanded ? (
                            <ChevronUp className="w-4 h-4 text-gray-400" />
                          ) : (
                            <ChevronDown className="w-4 h-4 text-gray-400" />
                          )}
                        </div>
                      </button>

                      {/* Dropdown Details (matching Core Analysis style) */}
                      {isExpanded && (
                        <div className="px-5 pb-5 pt-1 bg-white ">
                          <div className="p-4 bg-[#FAFAFA] border border-gray-100 rounded-xl space-y-3">
                            <div className="mb-4">
                              <h4 className="text-xs font-bold text-gray-900 uppercase tracking-wider mb-1">
                                Rationale & Analysis
                              </h4>
                              <p className="text-[13px] font-medium text-gray-600 leading-relaxed">
                                {data.rationale}
                              </p>
                            </div>

                            {evidenceList.length > 0 && (
                              <div>
                                <h4 className="text-xs font-bold text-gray-900 uppercase tracking-wider mb-2">
                                  Evidence
                                </h4>
                                <div className="space-y-1.5">
                                  {evidenceList.map((match: any, i: number) => (
                                    <div
                                      key={i}
                                      className="flex items-center gap-2"
                                    >
                                      <Triangle
                                        fill="true"
                                        color=""
                                        className="w-2 h-2 rotate-90"
                                      />
                                      <p className="text-[12px] font-medium text-gray-600 italic">
                                        &quot;{match.quote}&quot;
                                      </p>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                  );
                },
              )}
            </div>
          </div>
        </div>

        {/* Transcript Section - Separated by Goal with Connecting Line */}
        <div className="mb-10">
          <div className="flex items-center gap-2 mb-4">
            <h2 className="text-sm font-semibold text-gray-600">
              Interview Transcript
            </h2>
          </div>

          <div className="border border-gray-200 rounded-xl bg-white p-6 h-125 overflow-y-scroll">
            <div className="space-y-8">
              {goals.map((goalItem: any, goalIdx: number) => {
                const interactions =
                  goalItem.interaction_history ||
                  (transcripts.length > 0
                    ? transcripts.filter(
                        (t: any) => t.goal_id === goalItem.goal_id,
                      )
                    : goalIdx === 0
                      ? defaultTranscripts.slice(0, 2)
                      : defaultTranscripts.slice(2));

                if (!interactions || interactions.length === 0) return null;

                return (
                  <div key={goalIdx} className="mb-8 last:mb-0">
                    {/* Goal Group Header / Label */}
                    <div className="flex items-center gap-2 mb-5">
                      <span className="text-[11px] font-bold text-gray-600 uppercase tracking-wider">
                        {goalItem.goal_id}:{" "}
                        {goalItem.topic || "Goal Evaluation"}
                      </span>
                      <div className="flex-1 h-px bg-gray-100" />
                    </div>

                    {/* Interactions Thread with Fluid Connecting Line */}
                    <div>
                      {interactions.map((interaction: any, turnIdx: number) => {
                        const isCandidate = interaction.role === "candidate";
                        const speakerName = isCandidate
                          ? fullName
                          : "AI Interviewer";
                        const isLastInGoal =
                          turnIdx === interactions.length - 1;

                        return (
                          <div
                            key={turnIdx}
                            className="flex items-stretch gap-3.5"
                          >
                            {/* Fluid Connecting Line Column */}
                            <div className="w-5 shrink-0 flex flex-col items-center">
                              {/* Avatar */}
                              <div className="w-5 h-5 rounded-full shrink-0 z-10 flex items-center justify-center">
                                {isCandidate ? (
                                  <div className="w-5 h-5 rounded-full bg-slate-100 flex items-center justify-center text-slate-700 font-bold text-[10px]">
                                    {fullName.charAt(0)}
                                  </div>
                                ) : (
                                  <div className="w-5 h-5 rounded-full bg-[#b7ddff] flex items-center justify-center text-gray-900 font-bold text-xs shadow-xs">
                                    <Bot className="w-3 h-3 text-gray-900" />
                                  </div>
                                )}
                              </div>

                              {/* Fluid Vertical Line - Expands to fill item height automatically */}
                              {!isLastInGoal && (
                                <div className="w-px flex-1 bg-gray-300" />
                              )}
                            </div>

                            {/* Message Content */}
                            <div
                              className={`flex-1 ${!isLastInGoal ? "pb-6" : "pb-1"}`}
                            >
                              <div className="flex items-baseline gap-2 mb-1">
                                <span className="text-xs font-bold text-gray-900 uppercase tracking-wider">
                                  {speakerName}
                                </span>
                              </div>
                              <p className="text-xs font-medium text-gray-600 leading-relaxed">
                                {interaction.content}
                              </p>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
