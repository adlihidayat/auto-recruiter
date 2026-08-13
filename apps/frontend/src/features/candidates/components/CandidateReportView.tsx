"use client";

import React from "react";
import {
  CheckCircle2,
  XCircle,
  AlertTriangle,
  MessageSquare,
  Target,
  User,
  Calendar,
  Briefcase,
  ShieldAlert,
  ChevronRight,
  Gauge,
  TrendingUp,
} from "lucide-react";
import { CandidateReport } from "../types";

const MOCK_REPORT: CandidateReport = {
  id: "cand-123",
  profile: {
    name: "andika saputra",
    roleApplied: {
      jobTitle: "Machine Learning Engineer",
      team: "Core AI",
    },
    interviewMetadata: {
      dateInterviewed: "12/12/2026",
      dateReportGenerated: "12/13/2026",
      interviewStage: "Technical Screen 2 of 3",
      interviewers: ["AI Agent (Auto-Recruiter)"],
    },
    goalsAssessedCount: "5 of 5",
    overallConfidence: "Medium-High",
  },
  mustHaveGate: {
    goals: [
      { id: "g1", label: "Model Deployment & Serving", met: true },
      { id: "g2", label: "Deep Learning Fundamentals", met: true },
      { id: "g3", label: "System Design (Scalability)", met: false },
    ],
    gateResult: "fail",
  },
  recommendation: {
    label: "Hold",
    reasoning:
      "The candidate demonstrates exceptional fluency in model deployment and deep learning, easily addressing complex architectural questions. However, they failed to meet the passing criteria for the system design scalability must-have goal, struggling to explain how to handle sudden spikes in inference requests.",
    ruleApplied:
      "Hold triggered because 1 out of 3 must-have goals (System Design) was not met.",
  },
  strengths: [
    {
      goalOrSignalLabel: "Model Deployment",
      citedQuote: "I typically use TensorRT combined with Triton Inference Server to batch requests dynamically, which cuts latency by about 40%.",
      turnReference: 14,
    },
    {
      goalOrSignalLabel: "Deep Learning Fundamentals",
      citedQuote: "For vanishing gradients in this specific architecture, I'd implement residual connections and switch to GeLU activations.",
      turnReference: 22,
    },
  ],
  concerns: [
    {
      goalOrSignalLabel: "System Design (Scalability)",
      gapTypeTag: "scored low",
      citedQuote: "I'm not sure how to handle a 10x spike. Maybe just add more instances?",
      turnReference: 35,
    },
    {
      goalOrSignalLabel: "CI/CD for ML",
      gapTypeTag: "insufficient evidence",
      citedQuote: "We used Jenkins at my last job, but someone else set it up.",
      turnReference: 41,
    },
  ],
  redFlags: [
    {
      description: "Candidate became defensive when pushed on scaling strategy, repeatedly stating 'it's not my job to configure auto-scaling'.",
      relatedGoalId: "g3",
      severity: "high",
    },
  ],
  communicationRead: {
    overallScore: 6.5,
    overallConfidence: "Medium",
    signals: [
      { label: "flow_control", sentence: "Tended to ramble on technical tangents.", rationale: "Needed redirection 3 times.", score: 5 },
      { label: "active_listening", sentence: "Answered the questions asked accurately.", rationale: "Acknowledged constraints before answering.", score: 8 },
      { label: "structure", sentence: "Answers lacked a clear framework.", rationale: "Did not use STAR or logical step-by-step methods.", score: 5 },
      { label: "assertiveness", sentence: "Confident in ML domain, hesitant elsewhere.", rationale: "Voice tone dropped significantly on system design.", score: 6 },
      { label: "objection_handling", sentence: "Became defensive under scrutiny.", rationale: "Responded negatively to pushback on scalability.", score: 4 },
    ],
  },
  goalDetails: [
    {
      id: "g1",
      title: "Model Deployment & Serving",
      criticality: "must-have",
      addressed: true,
      score: 9,
      confidence: "High",
      rationale: "Candidate demonstrated deep practical knowledge of modern serving stacks.",
      criteriaMatch: {
        passingCriteriaMet: true,
        wrongAnswerSignalsTriggered: false,
      },
      citations: [
        { quote: "Triton allows dynamic batching which is critical here.", turnReference: 14 },
      ],
      pushback: {
        triggered: true,
        responseType: "defended_with_new_info",
      },
    },
    {
      id: "g3",
      title: "System Design (Scalability)",
      criticality: "must-have",
      addressed: true,
      score: 4,
      confidence: "Medium-High",
      rationale: "Failed to provide a concrete scaling strategy beyond vertical scaling.",
      criteriaMatch: {
        passingCriteriaMet: false,
        wrongAnswerSignalsTriggered: true,
      },
      citations: [
        { quote: "Maybe just add more instances?", turnReference: 35 },
      ],
      pushback: {
        triggered: true,
        responseType: "defensive_no_new_info",
      },
    },
  ],
};

const getRecommendationColor = (label: string) => {
  if (label.includes("Advance")) return "bg-[#DCFCE7] text-[#16A34A] border-[#16A34A]/20";
  if (label.includes("Hold")) return "bg-[#FEF2F2] text-[#DC2626] border-[#DC2626]/20";
  return "bg-[#F4F4F4] text-[#616161] border-[#E9E9E9]";
};

const getGapTypeColor = (type: string) => {
  switch (type) {
    case "scored low": return "bg-[#FEF2F2] text-[#DC2626]";
    case "insufficient evidence": return "bg-[#FEF9C3] text-[#CA8A04]";
    case "single data point": return "bg-[#EFF6FF] text-[#2563EB]";
    default: return "bg-[#F4F4F4] text-[#616161]";
  }
};

export default function CandidateReportView() {
  const report = MOCK_REPORT;

  return (
    <div className="max-w-[1000px] mx-auto px-6 py-12 pb-24">
      {/* 1. Candidate Profile Header */}
      <div className="mb-10">
        <h1 className="text-3xl font-bold text-[#272727] mb-2 tracking-tight">
          {report.profile.name}
        </h1>
        <div className="flex flex-wrap items-center gap-3 mb-6 text-sm">
          <span className="flex items-center gap-1.5 font-semibold text-[#272727]">
            <Briefcase className="w-4 h-4 text-[#616161]" />
            {report.profile.roleApplied.jobTitle} <span className="text-[#B8B8B8] font-normal">({report.profile.roleApplied.team})</span>
          </span>
          <span className="h-4 w-px bg-[#F1F1F1]" />
          <span className="flex items-center gap-1.5 font-semibold text-[#616161]">
            <Target className="w-4 h-4" />
            {report.profile.interviewMetadata.interviewStage}
          </span>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="p-4 rounded-xl border border-[#F1F1F1] bg-white">
            <div className="text-xs font-semibold text-[#616161] mb-1 flex items-center gap-1.5">
              <Calendar className="w-3.5 h-3.5" /> Date Interviewed
            </div>
            <div className="text-sm font-bold text-[#272727]">{report.profile.interviewMetadata.dateInterviewed}</div>
          </div>
          <div className="p-4 rounded-xl border border-[#F1F1F1] bg-white">
            <div className="text-xs font-semibold text-[#616161] mb-1 flex items-center gap-1.5">
              <User className="w-3.5 h-3.5" /> Interviewer
            </div>
            <div className="text-sm font-bold text-[#272727] truncate">{report.profile.interviewMetadata.interviewers[0]}</div>
          </div>
          <div className="p-4 rounded-xl border border-[#F1F1F1] bg-white">
            <div className="text-xs font-semibold text-[#616161] mb-1 flex items-center gap-1.5">
              <Target className="w-3.5 h-3.5" /> Goals Assessed
            </div>
            <div className="text-sm font-bold text-[#272727]">{report.profile.goalsAssessedCount}</div>
          </div>
          <div className="p-4 rounded-xl border border-[#F1F1F1] bg-white">
            <div className="text-xs font-semibold text-[#616161] mb-1 flex items-center gap-1.5">
              <Gauge className="w-3.5 h-3.5" /> Confidence
            </div>
            <div className="text-sm font-bold text-[#272727]">{report.profile.overallConfidence}</div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-10">
        {/* 2. Must-have gate */}
        <div className="col-span-1 border border-[#F1F1F1] rounded-2xl bg-white p-6 shadow-sm">
          <h2 className="text-base font-bold text-[#272727] mb-4 flex items-center gap-2">
            <ShieldAlert className="w-5 h-5 text-[#616161]" /> Must-have Gate
          </h2>
          <div className="space-y-3 mb-6">
            {report.mustHaveGate.goals.map((g) => (
              <div key={g.id} className="flex items-start gap-3">
                {g.met ? (
                  <CheckCircle2 className="w-5 h-5 text-[#16A34A] shrink-0 mt-0.5" />
                ) : (
                  <XCircle className="w-5 h-5 text-[#DC2626] shrink-0 mt-0.5" />
                )}
                <div>
                  <div className="text-sm font-semibold text-[#272727]">{g.label}</div>
                  <div className={`text-xs font-medium ${g.met ? "text-[#16A34A]" : "text-[#DC2626]"}`}>
                    {g.met ? "Met" : "Not met"}
                  </div>
                </div>
              </div>
            ))}
          </div>
          <div className={`p-3 rounded-xl border flex items-center justify-between font-bold text-sm ${report.mustHaveGate.gateResult === 'pass' ? 'bg-[#DCFCE7] text-[#16A34A] border-[#16A34A]/20' : 'bg-[#FEF2F2] text-[#DC2626] border-[#DC2626]/20'}`}>
            <span>Gate Result</span>
            <span className="uppercase">{report.mustHaveGate.gateResult}</span>
          </div>
        </div>

        {/* 3. Overall recommendation */}
        <div className="col-span-1 lg:col-span-2 border border-[#F1F1F1] rounded-2xl bg-white p-6 shadow-sm flex flex-col justify-center">
          <div className="mb-4">
            <span className={`inline-flex items-center px-4 py-1.5 rounded-full text-sm font-bold border ${getRecommendationColor(report.recommendation.label)}`}>
              Recommendation: {report.recommendation.label}
            </span>
          </div>
          <p className="text-[15px] leading-relaxed text-[#272727] font-medium mb-6">
            {report.recommendation.reasoning}
          </p>
          <div className="p-4 rounded-xl bg-[#F6F6F6] text-sm text-[#616161] font-medium border border-[#E9E9E9]">
            <span className="font-bold text-[#272727]">Rule Applied:</span> {report.recommendation.ruleApplied}
            <div className="text-xs text-[#B8B8B8] mt-1 italic">Note: This logic explicitly determines the outcome; it is not an average.</div>
          </div>
        </div>
      </div>

      {/* 4. Strengths & Concerns */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-10">
        <div className="border border-[#F1F1F1] rounded-2xl bg-white p-6 shadow-sm">
          <h2 className="text-base font-bold text-[#272727] mb-5 flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-[#16A34A]" /> Strengths
          </h2>
          <div className="space-y-6">
            {report.strengths.map((s, idx) => (
              <div key={idx} className="pb-5 border-b border-[#F1F1F1] last:border-0 last:pb-0">
                <div className="text-sm font-bold text-[#272727] mb-2">{s.goalOrSignalLabel}</div>
                <blockquote className="pl-3 border-l-2 border-[#16A34A] text-[13px] text-[#616161] italic mb-1.5">
                  &quot;{s.citedQuote}&quot;
                </blockquote>
                <div className="text-[11px] font-semibold text-[#B8B8B8]">[Turn {s.turnReference}]</div>
              </div>
            ))}
          </div>
        </div>

        <div className="border border-[#F1F1F1] rounded-2xl bg-white p-6 shadow-sm">
          <h2 className="text-base font-bold text-[#272727] mb-5 flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-[#DC2626] rotate-180" /> Concerns & Gaps
          </h2>
          <div className="space-y-6">
            {report.concerns.map((c, idx) => (
              <div key={idx} className="pb-5 border-b border-[#F1F1F1] last:border-0 last:pb-0">
                <div className="flex items-center gap-2 mb-2">
                  <div className="text-sm font-bold text-[#272727]">{c.goalOrSignalLabel}</div>
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${getGapTypeColor(c.gapTypeTag)}`}>
                    {c.gapTypeTag}
                  </span>
                </div>
                <blockquote className="pl-3 border-l-2 border-[#DC2626] text-[13px] text-[#616161] italic mb-1.5">
                  &quot;{c.citedQuote}&quot;
                </blockquote>
                <div className="text-[11px] font-semibold text-[#B8B8B8]">[Turn {c.turnReference}]</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* 5. Red flags */}
      <div className="mb-10">
        <h2 className="text-base font-bold text-[#272727] mb-4 flex items-center gap-2">
          <AlertTriangle className="w-5 h-5 text-[#DC2626]" /> Red Flags
        </h2>
        {report.redFlags.length === 0 ? (
          <div className="p-6 border border-[#F1F1F1] rounded-2xl bg-white text-sm text-[#616161] italic">
            No red flags detected during this interview.
          </div>
        ) : (
          <div className="space-y-3">
            {report.redFlags.map((rf, idx) => (
              <div key={idx} className="p-4 rounded-xl border border-[#DC2626]/20 bg-[#FEF2F2] flex items-start gap-4">
                <AlertTriangle className="w-5 h-5 text-[#DC2626] shrink-0 mt-0.5" />
                <div>
                  <div className="text-sm font-medium text-[#272727] leading-relaxed mb-2">
                    {rf.description}
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="px-2 py-0.5 rounded bg-white border border-[#DC2626]/10 text-[10px] font-bold text-[#DC2626] uppercase">
                      Severity: {rf.severity}
                    </span>
                    {rf.relatedGoalId && (
                      <span className="text-[11px] font-semibold text-[#616161]">
                        Related to Goal: {rf.relatedGoalId}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 6. Communication Read */}
      <div className="mb-10 border border-[#F1F1F1] rounded-2xl bg-white p-6 shadow-sm">
        <div className="flex flex-col md:flex-row md:items-center justify-between mb-8 gap-4 border-b border-[#F1F1F1] pb-6">
          <h2 className="text-lg font-bold text-[#272727] flex items-center gap-2">
            <MessageSquare className="w-5 h-5 text-[#616161]" /> Communication Read
          </h2>
          <div className="flex items-center gap-4">
            <div className="flex flex-col items-end">
              <span className="text-xs font-semibold text-[#616161]">Overall Score</span>
              <span className="text-2xl font-bold text-[#272727]">{report.communicationRead.overallScore}/10</span>
            </div>
            <div className="h-8 w-px bg-[#F1F1F1]" />
            <div className="flex flex-col items-end">
              <span className="text-xs font-semibold text-[#616161]">Confidence</span>
              <span className="text-sm font-bold text-[#272727]">{report.communicationRead.overallConfidence}</span>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {report.communicationRead.signals.map((sig, idx) => (
            <div key={idx} className="p-4 rounded-xl bg-[#F6F6F6] border border-[#F1F1F1]">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-bold text-[#272727] uppercase tracking-wider">{sig.label.replace('_', ' ')}</span>
                <span className="text-xs font-bold text-[#2563EB] bg-[#EFF6FF] px-2 py-0.5 rounded">{sig.score}/10</span>
              </div>
              <p className="text-sm font-semibold text-[#272727] mb-1">{sig.sentence}</p>
              <p className="text-[13px] text-[#616161] italic">{sig.rationale}</p>
            </div>
          ))}
        </div>
      </div>

      {/* 7. Per-goal detail */}
      <div className="mb-16">
        <h2 className="text-lg font-bold text-[#272727] mb-6 flex items-center gap-2">
          <Target className="w-5 h-5 text-[#616161]" /> Goal Breakdowns
        </h2>
        <div className="space-y-6">
          {report.goalDetails.map((gd) => (
            <div key={gd.id} className="border border-[#F1F1F1] rounded-2xl bg-white shadow-sm overflow-hidden">
              <div className="bg-[#F6F6F6] px-6 py-4 border-b border-[#F1F1F1] flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                  <div className="flex items-center gap-3 mb-1">
                    <h3 className="text-base font-bold text-[#272727]">{gd.title}</h3>
                    <span className="px-2 py-0.5 rounded bg-white border border-[#E9E9E9] text-[10px] font-bold text-[#616161] uppercase">
                      {gd.criticality.replace('-', ' ')}
                    </span>
                  </div>
                  <div className="text-[11px] font-semibold text-[#616161]">Goal ID: {gd.id} • Addressed: {gd.addressed ? 'Yes' : 'No'}</div>
                </div>
                <div className="flex items-center gap-4 shrink-0 bg-white p-2 rounded-xl border border-[#F1F1F1]">
                  <div className="flex flex-col items-center px-2">
                    <span className="text-[10px] font-bold text-[#B8B8B8] uppercase">Score</span>
                    <span className="text-lg font-bold text-[#272727]">{gd.score !== null ? gd.score : '-'}</span>
                  </div>
                  <div className="h-6 w-px bg-[#F1F1F1]" />
                  <div className="flex flex-col items-center px-2">
                    <span className="text-[10px] font-bold text-[#B8B8B8] uppercase">Confidence</span>
                    <span className="text-xs font-bold text-[#272727]">{gd.confidence || '-'}</span>
                  </div>
                </div>
              </div>

              <div className="p-6">
                <p className="text-[15px] font-medium text-[#272727] leading-relaxed mb-6">
                  {gd.rationale}
                </p>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                  <div>
                    <h4 className="text-xs font-bold text-[#616161] uppercase tracking-wider mb-3">Criteria Match</h4>
                    <div className="space-y-2">
                      <div className="flex items-center gap-2 text-sm font-medium text-[#272727]">
                        {gd.criteriaMatch.passingCriteriaMet ? <CheckCircle2 className="w-4 h-4 text-[#16A34A]" /> : <XCircle className="w-4 h-4 text-[#B8B8B8]" />}
                        Passing Criteria Met
                      </div>
                      <div className="flex items-center gap-2 text-sm font-medium text-[#272727]">
                        {gd.criteriaMatch.wrongAnswerSignalsTriggered ? <AlertTriangle className="w-4 h-4 text-[#DC2626]" /> : <CheckCircle2 className="w-4 h-4 text-[#B8B8B8]" />}
                        Wrong Answer Signals Triggered
                      </div>
                    </div>
                  </div>

                  {gd.pushback.triggered && (
                    <div>
                      <h4 className="text-xs font-bold text-[#616161] uppercase tracking-wider mb-3">Pushback Response</h4>
                      <div className="p-3 rounded-lg bg-[#EFF6FF] border border-[#2563EB]/10 text-sm font-bold text-[#2563EB] flex items-center gap-2">
                        <ChevronRight className="w-4 h-4" />
                        {gd.pushback.responseType?.replace(/_/g, ' ')}
                      </div>
                    </div>
                  )}
                </div>

                <div className="pt-5 border-t border-[#F1F1F1]">
                  <h4 className="text-xs font-bold text-[#616161] uppercase tracking-wider mb-3">Evidence Citations</h4>
                  <div className="space-y-3">
                    {gd.citations.map((cit, idx) => (
                      <div key={idx} className="pl-3 border-l-2 border-[#E9E9E9]">
                        <blockquote className="text-[13px] text-[#616161] italic mb-1">
                          &quot;{cit.quote}&quot;
                        </blockquote>
                        <div className="text-[10px] font-bold text-[#B8B8B8]">Turn {cit.turnReference}</div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 8. Footer meta */}
      <div className="pt-6 border-t border-[#F1F1F1] text-center">
        <p className="text-xs font-medium text-[#616161] mb-2">
          <span className="font-bold text-[#272727]">Confidence Caveat:</span> Low confidence scores indicate thin evidence; consider conducting a human follow-up on these specific goals.
        </p>
        <p className="text-[11px] text-[#B8B8B8] font-medium italic">
          Disclaimer: This is an AI-assisted pre-screen report intended to augment human evaluation, not a final hiring decision.
        </p>
      </div>
    </div>
  );
}
