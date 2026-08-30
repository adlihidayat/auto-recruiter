/**
 * What: Step 2 Agent Handoff Loading View.
 * Why: Renders multi-agent execution pipeline, horizontal progress bar, handoff logs timeline, and simulation controls.
 * Boundaries: Step 2 in the Create Interview Modal workflow.
 */

import React from "react";
import { Check, ArrowRight, RotateCcw } from "lucide-react";
import { AGENT_STEPS, MOCK_LOGS } from "./constants";
import { InterviewFormData } from "./types";

interface CreateInterviewLoadingStepProps {
  formData: InterviewFormData;
  elapsedTime: number;
  isPaused: boolean;
  isBackendDone: boolean;
  activeAgentIndex: number;
  mockProgressPercent: number;
  visibleLogs: typeof MOCK_LOGS;
  onReset: () => void;
  onContinue: () => void;
}

export const CreateInterviewLoadingStep: React.FC<CreateInterviewLoadingStepProps> = ({
  formData,
  elapsedTime,
  isPaused,
  isBackendDone,
  activeAgentIndex,
  mockProgressPercent,
  visibleLogs,
  onReset,
  onContinue,
}) => {
  return (
    <div className="animate-in fade-in zoom-in-95 duration-200">
      <div className="bg-[#f9fafb] rounded-[2rem] p-6 sm:p-8 w-full shadow-sm border border-gray-100">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <div className="flex items-center gap-3">
            <h2 className="text-xl font-bold text-gray-900">Agent Handoff</h2>
            <span className="bg-gray-200 text-gray-600 px-3 py-1 rounded-full text-xs font-semibold">
              4 agents
            </span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-sm font-mono text-gray-500">
              {(elapsedTime / 1000).toFixed(1)}s
            </span>
            <div
              className={`w-2.5 h-2.5 rounded-full bg-emerald-500 ${
                isPaused || isBackendDone ? "" : "animate-pulse"
              }`}
            />
          </div>
        </div>

        {/* Task Row */}
        <div className="flex items-center justify-between border-b border-dashed border-gray-300 pb-5 mb-8">
          <div className="flex items-center gap-4">
            <span className="text-xs font-bold text-gray-400 tracking-wider">
              TASK
            </span>
            <span className="text-[15px] font-medium text-gray-800">
              {formData.job_description.substring(0, 50) ||
                "Analyze and create interview plan"}
              {formData.job_description.length > 50 ? "..." : ""}
            </span>
          </div>
          <span className="text-xs font-mono text-gray-400">run_mock</span>
        </div>

        {/* Agents Progress */}
        <div className="relative mb-12">
          <div className="flex justify-between relative z-10 px-2 sm:px-6">
            {AGENT_STEPS.map((step, idx) => {
              const isActive = activeAgentIndex === idx && !isBackendDone;
              const isPast = activeAgentIndex > idx || isBackendDone;
              return (
                <div
                  key={idx}
                  className="flex flex-col items-center gap-3 bg-[#f9fafb]"
                >
                  <div
                    className={`relative w-16 h-16 rounded-2xl flex items-center justify-center transition-colors duration-500 ${
                      isPast || isActive
                        ? step.bg + " " + step.color
                        : "bg-gray-100 text-gray-400"
                    }`}
                  >
                    {step.icon}
                    {(isPast || isActive) && (
                      <div
                        className={`absolute -top-1.5 -right-1.5 w-5 h-5 rounded-full border-[3px] border-[#f9fafb] flex items-center justify-center ${step.badgeBg}`}
                      >
                        <Check
                          className="w-3 h-3 text-white"
                          strokeWidth={3}
                        />
                      </div>
                    )}
                  </div>
                  <div className="text-center">
                    <div
                      className={`text-[15px] font-bold ${
                        isActive ? "text-gray-900" : "text-gray-500"
                      }`}
                    >
                      {step.name}
                    </div>
                    <div className="text-[10px] font-bold text-gray-400 tracking-wider uppercase mt-0.5">
                      {step.role}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
          {/* Progress bar line */}
          <div className="absolute top-8 left-10 right-10 -z-0">
            <div className="w-full relative h-1 bg-gray-200 rounded-full">
              <div
                className="absolute top-0 left-0 h-1 bg-gradient-to-r from-blue-500 via-purple-500 to-orange-500 rounded-full transition-all duration-300 ease-linear"
                style={{ width: `${mockProgressPercent}%` }}
              />
              <div
                className="absolute top-1/2 -translate-y-1/2 w-4 h-4 bg-emerald-500 rounded-full border-2 border-white shadow-sm transition-all duration-300 ease-linear"
                style={{
                  left: `calc(${mockProgressPercent}% - 8px)`,
                  display: mockProgressPercent > 0 ? "block" : "none",
                }}
              />
            </div>
          </div>
        </div>

        {/* HANDOFF LOG */}
        <div className="border-t border-dashed border-gray-300 pt-6">
          <div className="flex justify-between items-center mb-6">
            <span className="text-xs font-bold text-gray-400 tracking-wider">
              HANDOFF LOG
            </span>
            <span className="text-xs font-mono text-gray-400">
              {visibleLogs.length} / {MOCK_LOGS.length}
            </span>
          </div>

          <div className="space-y-4 h-48 overflow-y-auto custom-scrollbar pr-2 flex flex-col justify-end">
            {visibleLogs.map((log, i) => (
              <div
                key={i}
                className="flex items-start gap-5 animate-in fade-in slide-in-from-bottom-2 duration-300"
              >
                <span className="text-[13px] font-mono text-gray-400 w-12 shrink-0">
                  {(log.time / 1000).toFixed(1)}s
                </span>
                <div className="flex items-center gap-3 mt-1.5 shrink-0">
                  <div className={`w-2 h-2 rounded-full ${log.dot}`} />
                </div>
                <div className="text-[15px] text-gray-600 leading-snug">
                  {log.text}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Bottom Actions */}
        <div className="mt-8 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <span
              className={`text-[15px] font-bold ${
                isBackendDone ? "text-emerald-600" : "text-gray-900"
              }`}
            >
              {isBackendDone
                ? "Success"
                : AGENT_STEPS[activeAgentIndex].name}
            </span>
            <span className="text-[15px] text-gray-500">
              · {isBackendDone ? "mock complete" : "running processes"}
            </span>
          </div>
          <div className="flex items-center gap-2 w-full sm:w-auto">
            <button
              onClick={onReset}
              className="px-5 py-2.5 bg-gray-200/80 text-gray-700 rounded-full text-[15px] font-semibold hover:bg-gray-300 transition-colors flex-1 sm:flex-none cursor-pointer"
            >
              Reset
            </button>
            <button
              onClick={onContinue}
              className="px-6 py-2.5 bg-[#191919] text-white rounded-full text-[15px] font-semibold flex items-center justify-center gap-2 hover:bg-black transition-colors flex-1 sm:flex-none shadow-md shadow-black/10 cursor-pointer"
            >
              {isBackendDone ? (
                <>
                  Continue <ArrowRight className="w-4 h-4" />
                </>
              ) : (
                <>
                  <RotateCcw className="w-4 h-4" /> Restart
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
