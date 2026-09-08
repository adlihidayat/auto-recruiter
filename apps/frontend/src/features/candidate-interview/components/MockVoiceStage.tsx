/**
 * What: Mock Voice Stage Component for fallback / offline testing.
 * Why: Allows developers and candidates to test the stage UI without requiring a live LiveKit server connection.
 * Boundaries: Standalone stage view; uses mock transcript data.
 */

import React from "react";
import { Mic, MicOff, PhoneOff } from "lucide-react";
import { InterviewerOrb } from "./InterviewerOrb";
import { StageVisualizer } from "./StageVisualizer";

interface MockVoiceStageProps {
  onLeave: () => void;
  realAudioLevel: number;
  isMuted: boolean;
  onToggleMute: () => void;
}

export function MockVoiceStage({
  onLeave,
  realAudioLevel,
  isMuted,
  onToggleMute,
}: MockVoiceStageProps) {
  const state = "speaking";
  const agentTranscriptions = [
    {
      text: "Hello! Welcome to your AI interview session. Could you please introduce yourself and outline your experience?",
    },
  ];

  return (
    <div className="w-full max-w-3xl flex flex-col gap-6">
      {/* Main Stage View */}
      <div className="relative w-full bg-[#191919] rounded-3xl border border-gray-800 shadow-2xl p-8 min-h-[420px] flex flex-col items-center justify-center overflow-hidden">
        {/* Agent Avatar & Orb */}
        <div className="relative flex flex-col items-center z-10">
          <InterviewerOrb state={state} />

          <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
            AI Interviewer{" "}
            <span className="text-xs font-semibold uppercase px-2.5 py-0.5 rounded-full bg-white/10 text-gray-300 border border-white/10">
              {state}
            </span>
          </h2>

          {/* Audio / Thinking Visualizer */}
          <StageVisualizer state={state} />

          {/* Dynamic Spoken Transcript */}
          <p className="text-sm text-gray-200 max-w-md text-center mt-6 bg-white/10 border border-white/15 p-4 rounded-2xl backdrop-blur-md shadow-xl leading-relaxed">
            &ldquo;{agentTranscriptions[0].text}&rdquo;
          </p>
        </div>
      </div>

      {/* Control Bar with Real-time Microphone Input Meter */}
      <div className="bg-white rounded-2xl border border-gray-200 p-4 shadow-lg flex items-center justify-between px-6 gap-6">
        {/* Mic Controls & Volume Meter */}
        <div className="flex items-center gap-4 flex-1 max-w-md">
          <button
            type="button"
            onClick={onToggleMute}
            className={`p-3 rounded-xl transition-colors cursor-pointer flex items-center justify-center ${
              isMuted
                ? "bg-red-50 text-red-600 border border-red-200 hover:bg-red-100"
                : "bg-emerald-50 text-emerald-600 border border-emerald-200 hover:bg-emerald-100"
            }`}
            title={isMuted ? "Unmute Mic" : "Mute Mic"}
          >
            {isMuted ? (
              <MicOff className="w-5 h-5" />
            ) : (
              <Mic className="w-5 h-5" />
            )}
          </button>

          {/* Volume Indicator Bar */}
          <div className="flex-1 space-y-1">
            <div className="flex justify-between text-xs font-medium text-gray-600">
              <span>Your Mic Input</span>
              <span className="font-semibold text-xs text-gray-900">
                {isMuted
                  ? "Muted"
                  : realAudioLevel > 15
                    ? "Receiving Sound"
                    : "Listening..."}
              </span>
            </div>
            <div className="w-full h-1 bg-gray-100 rounded-full overflow-hidden border border-gray-200">
              <div
                className={`h-full transition-all duration-75 ${
                  isMuted
                    ? "w-0"
                    : realAudioLevel > 20
                      ? "bg-orange-500"
                      : "bg-orange-400"
                }`}
                style={{
                  width: isMuted ? "0%" : `${realAudioLevel}%`,
                }}
              />
            </div>
          </div>
        </div>

        {/* Leave Action Button */}
        <button
          type="button"
          onClick={onLeave}
          className="px-5 py-2.5 bg-red-600 hover:bg-red-700 text-white rounded-xl text-sm font-semibold flex items-center gap-2 cursor-pointer shrink-0 transition-colors shadow-sm"
        >
          <PhoneOff className="w-4 h-4" />
          <span>Leave Interview</span>
        </button>
      </div>
    </div>
  );
}
