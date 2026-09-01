/**
 * What: Step 2 Agent Handoff Loading View.
 * Why: Renders multi-agent execution pipeline, horizontal progress bar, handoff logs timeline, and simulation controls.
 * Boundaries: Step 2 in the Create Interview Modal workflow.
 */

import React from "react";
import { Check, ArrowRight, RotateCcw, Loader2 } from "lucide-react";
import { AGENT_STEPS, MOCK_LOGS, MockLogItem } from "./constants";
import { InterviewFormData } from "./types";

interface CreateInterviewLoadingStepProps {
  formData: InterviewFormData;
  elapsedTime: number;
  isPaused: boolean;
  isBackendDone: boolean;
  apiError: string | null;
  activeAgentIndex: number;
  mockProgressPercent: number;
  visibleLogs: MockLogItem[];
  onReset: () => void;
  onContinue: () => void;
}

export const CreateInterviewLoadingStep: React.FC<
  CreateInterviewLoadingStepProps
> = ({
  formData,
  elapsedTime,
  isPaused,
  isBackendDone,
  apiError,
  activeAgentIndex,
  mockProgressPercent,
  visibleLogs,
  onReset,
  onContinue,
}) => {
  return (
    <div className="animate-in fade-in zoom-in-95 duration-200 w-130 h-full">
      <div className="bg-white rounded-[2rem] w-full">
        {/* Header */}
        <div className="flex justify-between items-center mb-6 px-4 pt-2">
          <div className="flex items-center gap-3">
            <h2 className="text-base font-semibold text-gray-900">
              Creating interview Plan
            </h2>
            <span className="bg-gray-100 text-gray-600 px-2 py-1 rounded-md text-xs font-semibold">
              4 agents
            </span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-mono text-gray-500">
              {(elapsedTime / 1000).toFixed(1)}s
            </span>
            <div
              className={`w-2.5 h-2.5 rounded-full bg-emerald-500 ${
                isPaused || isBackendDone ? "" : "animate-pulse"
              }`}
            />
          </div>
        </div>

        <div className=" bg-[#f4f4f581] pt-4 pb-6 rounded-xl">
          {/* Task Row */}
          <div className="flex items-center justify-between border-b border-dashed border-gray-200 pb-5 mb-6 px-4">
            <div className="flex items-center gap-1">
              <span className="text-xs font-semibold text-gray-600 tracking-wider">
                Task :
              </span>
              <span className="text-xs font-medium text-gray-800 w-60 truncate">
                {formData.job_name.substring(0, 50) ||
                  "Analyze and create interview plan"}
              </span>
            </div>
            <span className="text-xs font-mono text-gray-600">#12f157dds</span>
          </div>

          {/* Agents Progress */}
          <div className="relative">
            <div className="flex justify-between relative z-10 px-2 sm:px-6">
              {AGENT_STEPS.map((step, idx) => {
                const isActive = activeAgentIndex === idx && !isBackendDone;
                const isPast = activeAgentIndex > idx || isBackendDone;
                return (
                  <div key={idx} className="flex flex-col items-center gap-3 ">
                    <div
                      className={`relative w-12 h-12 rounded-2xl flex items-center justify-center transition-colors duration-500 ${
                        isPast || isActive
                          ? `${step.bg + " " + step.color} border border-[${step.color}]`
                          : "bg-white text-gray-400"
                      }`}
                    >
                      {step.icon}
                      {isPast && (
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
                        className={`text-sm font-medium ${
                          isActive ? "text-gray-900" : "text-gray-600"
                        }`}
                      >
                        {step.name}
                      </div>
                      <div className="text-[10px] font-medium text-gray-600  mt-0.5">
                        {step.role}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
            {/* Progress bar line */}
            <div className="absolute top-6 left-10 right-10 -z-0">
              <div className="w-full relative h-1 bg-gray-200 rounded-full">
                <div
                  className="absolute top-0 left-0 h-0.5 bg-gradient-to-r from-blue-700 via-purple-700 to-orange-700 rounded-full transition-all duration-300 ease-linear"
                  style={{ width: `${mockProgressPercent}%` }}
                />
                <div
                  className="absolute top-1/2 -translate-y-1/2 w-3.5 h-3.5 bg-orange-400 rounded-full shadow-sm transition-all duration-300 ease-linear"
                  style={{
                    left: `calc(${mockProgressPercent}% - 8px)`,
                    display: mockProgressPercent > 0 ? "block" : "none",
                  }}
                />
              </div>
            </div>
          </div>
        </div>

        {/* HANDOFF LOG */}
        <div className=" px-4">
          <div className="flex justify-between items-center py-3">
            <span className="text-sm font-medium text-gray-600 tracking-wider ">
              Agent Log
            </span>
            <span className="text-xs font-mono text-gray-400">
              {visibleLogs.length} / {MOCK_LOGS.length}
            </span>
          </div>

          <div className="space-y-3 h-44 overflow-y-auto custom-scrollbar pr-2 flex flex-col justify-end bg-amber-40">
            {visibleLogs.map((log, i) => (
              <div
                key={i}
                className="flex items-start gap-5 animate-in fade-in slide-in-from-bottom-2 duration-300"
              >
                <span className="text-[13px] font-mono text-gray-600 w-12 shrink-0">
                  {(log.time / 1000).toFixed(1)}s
                </span>
                <div className="flex items-center gap-3 mt-1.5 shrink-0">
                  {log.isPending ? (
                    <Loader2 className="w-3.5 h-3.5 text-amber-500 animate-spin -ml-0.5" />
                  ) : (
                    <div className={`w-2 h-2 rounded-full ${log.dot}`} />
                  )}
                </div>
                <div className="text-sm text-gray-600 leading-snug">
                  {log.text}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Bottom Actions */}
        <div className="pt-3 mt-3 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 px-4 border-t border-gray-200">
          <div className="flex items-center gap-1">
            <span
              className={`text-sm font-medium ${
                isBackendDone
                  ? apiError
                    ? "text-red-600 font-semibold"
                    : "text-emerald-600 font-semibold"
                  : "text-gray-900"
              }`}
            >
              {isBackendDone
                ? apiError
                  ? "Failed"
                  : "Success"
                : AGENT_STEPS[activeAgentIndex].name}
              {"  "}·
            </span>
            <span className="text-xs text-gray-500">
              {isBackendDone
                ? apiError
                  ? "process error"
                  : "process complete"
                : "running processes"}
            </span>
          </div>
          <div className="flex items-center gap-2 w-full sm:w-auto">
            <button
              onClick={onReset}
              className="px-3 py-1.5 border border-gray-200 text-gray-700 rounded-md text-sm font-medium hover:bg-gray-300 transition-colors flex-1 sm:flex-none cursor-pointer"
            >
              Cancel
            </button>
            <button
              onClick={isBackendDone && !apiError ? onContinue : onReset}
              className={`px-3 py-1.5 rounded-md text-sm font-medium flex items-center justify-center gap-2 transition-colors flex-1 sm:flex-none shadow-md cursor-pointer ${
                isBackendDone && apiError
                  ? "bg-red-600 text-white hover:bg-red-700 shadow-red-600/10"
                  : "bg-[#191919] text-white hover:bg-black shadow-black/10"
              }`}
            >
              {isBackendDone && !apiError ? (
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
