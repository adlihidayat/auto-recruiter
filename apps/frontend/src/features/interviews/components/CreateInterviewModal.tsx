"use client";

/**
 * What: Modal component for launching a new AI-driven recruiting campaign.
 * Why: Allows HR users to submit target job criteria which triggers Question-Maker Agent (Agent 1).
 * Boundaries: Form state and UI modal toggle; submits job parameters to campaign creation workflow.
 */

import React, { useState } from "react";
import { X, Sparkles, Bot, PlusCircle } from "lucide-react";
import { InterviewCampaign } from "../types";

interface CreateInterviewModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCampaignCreated: (newCampaign: InterviewCampaign) => void;
}

export default function CreateInterviewModal({
  isOpen,
  onClose,
  onCampaignCreated,
}: CreateInterviewModalProps) {
  const [jobTitle, setJobTitle] = useState("");
  const [departmentName, setDepartmentName] = useState("Engineering");
  const [targetSeniority, setTargetSeniority] = useState<
    "Junior" | "Mid-Level" | "Senior" | "Lead" | "Principal"
  >("Senior");
  const [roleDescription, setRoleDescription] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!isOpen) return null;

  const handleSubmitForm = (event: React.FormEvent) => {
    event.preventDefault();
    if (!jobTitle.trim()) return;

    setIsSubmitting(true);

    // Simulate Agent 1 (Question Maker) synthesizing initial question suite
    setTimeout(() => {
      const generatedCampaign: InterviewCampaign = {
        id: `campaign-${Date.now()}`,
        jobTitle: jobTitle.trim(),
        departmentName,
        targetSeniority,
        currentPipelineStage: "QUESTION_MAKER",
        activeCandidateCount: 0,
        evaluatedCandidateCount: 0,
        createdAtTimestamp: "Just now",
        agentSummary:
          roleDescription.trim() ||
          "AI Question-Maker Agent is actively compiling tailored algorithmic and system design prompts for this role.",
        questionSuite: [
          {
            id: "q-101",
            category: "Core Architecture",
            questionText: `Design a scalable microservices structure for ${jobTitle.trim()} workflow with failover mechanisms.`,
            difficultyLevel: targetSeniority === "Senior" ? "Hard" : "Medium",
            targetSkill: "System Design",
          },
          {
            id: "q-102",
            category: "Problem Solving",
            questionText:
              "Explain how you handle concurrency deadlocks and race conditions in production API services.",
            difficultyLevel: "Medium",
            targetSkill: "Concurrency",
          },
        ],
        candidatesList: [],
      };

      onCampaignCreated(generatedCampaign);
      setIsSubmitting(false);
      onClose();

      // Reset form
      setJobTitle("");
      setRoleDescription("");
    }, 600);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-in fade-in duration-200">
      <div className="relative w-full max-w-lg bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="px-6 py-5 border-b border-slate-800 flex items-center justify-between bg-slate-900/60">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
              <Sparkles className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white tracking-tight">
                Launch AI Recruiting Campaign
              </h3>
              <p className="text-[11px] text-slate-400">
                Trigger Agent 1 (Question Maker) to build interview suites
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg bg-slate-800 text-slate-400 hover:text-white transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmitForm} className="p-6 space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5">
              Target Job Title *
            </label>
            <input
              type="text"
              required
              value={jobTitle}
              onChange={(e) => setJobTitle(e.target.value)}
              placeholder="e.g. Senior Backend Engineer (Python/FastAPI)"
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/50"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                Department
              </label>
              <select
                value={departmentName}
                onChange={(e) => setDepartmentName(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
              >
                <option value="Engineering">Engineering</option>
                <option value="AI / ML Team">AI / ML Team</option>
                <option value="Product">Product</option>
                <option value="Infrastructure">Infrastructure</option>
                <option value="Security">Security</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                Seniority Level
              </label>
              <select
                value={targetSeniority}
                onChange={(e) =>
                  setTargetSeniority(
                    e.target.value as
                      | "Junior"
                      | "Mid-Level"
                      | "Senior"
                      | "Lead"
                      | "Principal",
                  )
                }
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
              >
                <option value="Junior">Junior</option>
                <option value="Mid-Level">Mid-Level</option>
                <option value="Senior">Senior</option>
                <option value="Lead">Lead</option>
                <option value="Principal">Principal</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5">
              Role Context / Specific Rubric Goals
            </label>
            <textarea
              rows={3}
              value={roleDescription}
              onChange={(e) => setRoleDescription(e.target.value)}
              placeholder="Describe key technical stack, evaluation criteria, or specific requirements for Question-Maker Agent..."
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/50"
            />
          </div>

          {/* Footer Actions */}
          <div className="pt-3 border-t border-slate-800/80 flex items-center justify-end gap-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting || !jobTitle.trim()}
              className="px-4 py-2 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white text-xs font-semibold transition-all disabled:opacity-50 flex items-center gap-1.5 shadow-lg shadow-indigo-600/30"
            >
              {isSubmitting ? (
                <>
                  <Bot className="w-4 h-4 animate-spin" /> Synthesizing Agent
                  Plan...
                </>
              ) : (
                <>
                  <PlusCircle className="w-4 h-4" /> Initialize Campaign
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
