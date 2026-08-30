import React from "react";
import {
  ExternalLink,
  CheckCircle2,
  AlertTriangle,
} from "lucide-react";
import Link from "next/link";

export default async function InterviewDetailPage({
  params,
}: {
  params: Promise<{ interviewId: string }>;
}) {
  const { interviewId } = await params;

  // Mocking the complete Interview backend schema with multiple plans
  const interviewData = {
    id: interviewId || "int_01",
    creator_id: "usr_1001",
    job_name: "Distributed Systems Engineer",
    job_description:
      "We need a senior engineer skilled in Go microservices, gRPC, and PostgreSQL optimization under high concurrency.",
    difficulty: "senior",
    num_goals: 4,
    total_duration_minutes: 30,
    domain_hint: "Distributed Systems & Go",
    communication_weight: 0.3,
    scheduled_at: "2026-08-30T10:00:00Z",
    status: "scheduled",
    created_at: "2026-08-11T00:00:00Z",
    updated_at: "2026-08-29T00:00:00Z",
    plans: [
      {
        goal_id: "g_01",
        topic: "Distributed Systems Architecture and Go Performance",
        goal: "Evaluate candidate's ability to design resilient microservices with gRPC and optimize Go concurrency under load.",
        interview_time_in_minute: 15,
        suggested_opening:
          "We are scaling a Go-based microservice architecture using gRPC...",
        passing_criteria: [
          "Identifies that L4 load balancing is insufficient for gRPC due to HTTP/2 multiplexing",
          "Proposes L7 solutions like Envoy/Istio or client-side balancing",
          "Mentions context propagation for deadline handling and goroutine lifecycle safety",
        ],
        pushback_triggers: [
          {
            trigger:
              "Candidate claims standard ClusterIP load balancing works for gRPC without modification.",
            severity: "critical",
            pushback_type: "concrete",
          },
        ],
        wrong_answer_signals: [
          "Claims Kubernetes kube-proxy automatically balances gRPC requests",
          "Suggests spawning unbounded goroutines for every incoming request",
        ],
      },
      {
        goal_id: "g_02",
        topic: "PostgreSQL Database Optimization & Indexing",
        goal: "Evaluate candidate's approach to troubleshooting slow PostgreSQL queries and designing partial indexes.",
        interview_time_in_minute: 15,
        suggested_opening:
          "Our main database query latency spikes under high traffic. How do you analyze execution plans?",
        passing_criteria: [
          "Mentions using EXPLAIN ANALYZE to identify sequential scans vs index scans",
          "Explains the benefits of partial indexes and B-tree indexing strategies",
        ],
        pushback_triggers: [
          {
            trigger:
              "Candidate suggests adding indexes indiscriminately to every column.",
            severity: "warning",
            pushback_type: "concrete",
          },
        ],
        wrong_answer_signals: [
          "Suggests restarting the database during high traffic without checking logs",
        ],
      },
    ],
  };

  const interviewPlans = interviewData.plans;

  // Mock candidates
  const candidates = [
    {
      id: "c_1",
      name: "Alice Johnson",
      email: "alice.j@example.com",
      status: "passed",
      synced: "11 minutes ago",
    },
    {
      id: "c_2",
      name: "Bob Smith",
      email: "bob.smith@example.com",
      status: "rejected",
      synced: "11 minutes ago",
    },
    {
      id: "c_3",
      name: "Charlie Davis",
      email: "charlie.d@example.com",
      status: "pending",
      synced: "2 hours ago",
    },
    {
      id: "c_4",
      name: "Alice Johnson",
      email: "alice.j@example.com",
      status: "passed",
      synced: "11 minutes ago",
    },
    {
      id: "c_5",
      name: "Bob Smith",
      email: "bob.smith@example.com",
      status: "rejected",
      synced: "11 minutes ago",
    },
    {
      id: "c_6",
      name: "Charlie Davis",
      email: "charlie.d@example.com",
      status: "pending",
      synced: "2 hours ago",
    },
    {
      id: "c_7",
      name: "Bob Smith",
      email: "bob.smith@example.com",
      status: "rejected",
      synced: "11 minutes ago",
    },
    {
      id: "c_8",
      name: "Charlie Davis",
      email: "charlie.d@example.com",
      status: "pending",
      synced: "2 hours ago",
    },
    {
      id: "c_9",
      name: "Bob Smith",
      email: "bob.smith@example.com",
      status: "rejected",
      synced: "11 minutes ago",
    },
    {
      id: "c_10",
      name: "Charlie Davis",
      email: "charlie.d@example.com",
      status: "pending",
      synced: "2 hours ago",
    },
  ];

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
          <span className="font-medium text-gray-900">
            Distributed Systems Engineer
          </span>
        </div>

        {/* Header Section */}
        <div className="flex flex-col gap-2 mb-8">
          <div className="w-10 h-10 rounded-xl bg-orange-50 flex items-center justify-center border border-orange-100 text-xl">
            😀️
          </div>
          <div className="flex justify-between gap-1">
            <div>
              <div className="flex items-center gap-3 mt-2">
                <h1 className="text-2xl font-bold text-gray-900">
                  Distributed Systems Engineer
                </h1>
                <span className="px-2 py-0.5 bg-emerald-100 text-emerald-700 text-xs font-semibold rounded-md">
                  Active
                </span>
              </div>
              <div className="flex items-center gap-3 mt-1">
                <span className="text-gray-600 text-sm">Engineering</span>
                <span className="text-gray-600 text-sm">/</span>
                <span className="text-gray-600 text-sm">Senior</span>
                <span className="text-gray-600 text-sm">/</span>
                <span className="text-gray-600 text-sm">
                  {interviewData.created_at}
                </span>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <button className="flex items-center gap-1.5 px-3 py-1.5 border border-gray-200 text-gray-900 text-sm font-medium rounded-lg hover:bg-gray-50 transition-colors">
                Edit <ExternalLink className="w-3.5 h-3.5" />
              </button>
              <button className="flex items-center gap-1.5 px-3 py-1.5 bg-[#EA3536] text-white text-sm font-medium rounded-lg hover:bg-red-600 transition-colors">
                Delete Interview
              </button>
            </div>
          </div>
        </div>

        {/* Hero Banner (Mimicking the pastel green banner) */}
        <div className="w-full h-32 rounded-2xl bg-gradient-to-r from-emerald-100 to-teal-100 border border-emerald-200 mb-10 flex items-center justify-center p-6 relative overflow-hidden">
          <div className="absolute inset-0 opacity-20 bg-[radial-gradient(#10b981_1px,transparent_1px)] [background-size:16px_16px]"></div>
          <div className="relative bg-white/90 backdrop-blur-sm px-6 py-2.5 rounded-full border border-white/50 flex items-center gap-3 text-sm font-medium text-gray-800">
            <div className="w-5 h-5 rounded bg-emerald-100 text-base flex items-center justify-center">
              😀️
            </div>
            {interviewData.job_name}
          </div>
        </div>

        {/* Interview Plan Section (Supports multiple goals) */}
        <div className="mb-10">
          <h2 className="text-base font-semibold text-gray-900 mb-3">
            Interview Plan ({interviewPlans.length} Goals)
          </h2>
          <div className="space-y-6">
            {interviewPlans.map((planItem, planIdx) => (
              <div
                key={planIdx}
                className="border border-gray-200 rounded-xl overflow-hidden bg-white shadow-xs"
              >
                <div className="flex border-b border-gray-100">
                  {/* <div className="w-48 px-4 py-4 text-sm font-medium text-gray-900 flex items-start pt-4 gap-2 border-r border-gray-100 bg-gray-50/50">
                    Goal ({planItem.goal_id})
                  </div> */}
                  <div className="flex-1 px-4 py-4 text-sm text-gray-900 leading-relaxed font-medium">
                    Goal : {planItem.goal}
                  </div>
                </div>

                {/* <div className="flex border-b border-gray-100">
                  <div className="w-48 px-4 py-4 text-sm font-medium text-gray-900 flex items-center gap-2 border-r border-gray-100 bg-gray-50/50">
                    Duration
                  </div>
                  <div className="flex-1 px-4 py-4 text-sm text-gray-900 font-semibold">
                    {planItem.interview_time_in_minute} minutes
                  </div>
                </div> */}

                {/* <div className="flex items-center justify-between px-4 py-3 bg-gray-50 border-b border-gray-100 text-sm font-medium text-gray-900">
                  <div className="flex items-center gap-2">
                    <span>Passing Criteria</span>
                  </div>
                </div> */}

                <div className="p-4 space-y-4 bg-[#FAFAFA]">
                  <div>
                    <h3 className="text-xs font-semibold text-gray-900 uppercase tracking-wider mb-2">
                      Required Signals:
                    </h3>
                    <ul className="space-y-2">
                      {planItem.passing_criteria.map((crit, idx) => (
                        <li
                          key={idx}
                          className="flex items-start gap-2 text-sm text-gray-900"
                        >
                          <CheckCircle2 className="w-4 h-4 text-emerald-500 mt-0.5 flex-shrink-0" />
                          {crit}
                        </li>
                      ))}
                    </ul>
                  </div>

                  {planItem.wrong_answer_signals?.length > 0 && (
                    <div>
                      <h3 className="text-xs font-semibold text-gray-900 uppercase tracking-wider mb-2 mt-4">
                        Red Flags:
                      </h3>
                      <ul className="space-y-2">
                        {planItem.wrong_answer_signals.map((trigger, idx) => (
                          <li
                            key={idx}
                            className="flex items-start gap-2 text-sm text-gray-900"
                          >
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
        </div>

        {/* Candidates List (Stores equivalent) */}
        <div className="mb-10">
          <h2 className="text-base font-semibold text-gray-900 mb-3">
            Candidates
          </h2>
          <div className="border border-gray-200 rounded-xl  bg-white flex flex-col">
            <div className="overflow-y-scroll h-96">
              {candidates.map((candidate, idx) => (
                <Link
                  href={`/interviews/${interviewId}/candidates/${candidate.id}`}
                  key={candidate.id}
                  className={`flex items-center justify-between px-4 py-4 ${idx !== candidates.length - 1 ? "border-b border-gray-100" : ""} hover:bg-gray-50 transition-colors cursor-pointer group`}
                >
                  <div className="flex items-center gap-3">
                    <div className="w-6 h-6 rounded-full bg-[#eaeaea] flex items-center justify-center flex-shrink-0 text-black text-xs font-bold uppercase">
                      {candidate.name.charAt(0)}
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">
                        {candidate.name}
                      </span>
                      <span className="text-sm text-gray-600">
                        {candidate.email}
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <span className="text-xs text-gray-400">
                      Evaluated {candidate.synced}
                    </span>
                    {candidate.status === "passed" && (
                      <span className="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_0_2px_rgba(16,185,129,0.2)]" />
                    )}
                    {candidate.status === "rejected" && (
                      <span className="w-2 h-2 rounded-full bg-red-500 shadow-[0_0_0_2px_rgba(239,68,68,0.2)]" />
                    )}
                    {candidate.status === "pending" && (
                      <span className="w-2 h-2 rounded-full bg-amber-500 shadow-[0_0_0_2px_rgba(245,158,11,0.2)]" />
                    )}
                  </div>
                </Link>
              ))}
            </div>

            {/* Quick Actions (Tool permissions equivalent) */}
            <div className="p-4 bg-[#FAFAFA] border-t border-gray-100 rounded-b-xl">
              <h3 className="text-sm font-semibold text-gray-900 mb-4">
                Pipeline Automation
              </h3>

              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium text-gray-900">
                        Auto-reject unqualified candidates
                      </span>
                      <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                    </div>
                    <p className="text-xs text-gray-600 mt-0.5">
                      Immediately send rejection email if composite score is
                      below 50%.
                    </p>
                  </div>
                  {/* Toggle switch mock */}
                  <div className="w-10 h-6 bg-blue-500 rounded-full p-1 flex items-center justify-end cursor-pointer shadow-inner">
                    <div className="w-4 h-4 bg-white rounded-full" />
                  </div>
                </div>

                <div className="flex justify-between items-center">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium text-gray-900">
                        Notify hiring manager on Pass
                      </span>
                      <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                    </div>
                    <p className="text-xs text-gray-600 mt-0.5">
                      Send a Slack message when a candidate scores above 85%.
                    </p>
                  </div>
                  <div className="w-10 h-6 bg-blue-500 rounded-full p-1 flex items-center justify-end cursor-pointer shadow-inner">
                    <div className="w-4 h-4 bg-white rounded-full" />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
