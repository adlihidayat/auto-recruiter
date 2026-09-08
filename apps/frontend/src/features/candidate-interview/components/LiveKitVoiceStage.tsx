/**
 * What: LiveKit Voice Stage Component (Phase 2 Live Room).
 * Why: Renders live audio assistant status, candidate mic volume level, real-time transcripts, and call control bar.
 * Boundaries: Rendered inside `<LiveKitRoom />`; consumes `useVoiceAssistant` and `useLocalParticipant`.
 */

import React from "react";
import { Mic, MicOff, PhoneOff } from "lucide-react";
import { LocalAudioTrack } from "livekit-client";
import {
  useVoiceAssistant,
  useLocalParticipant,
  useTrackVolume,
} from "@livekit/components-react";
import { InterviewerOrb } from "./InterviewerOrb";
import { StageVisualizer } from "./StageVisualizer";

interface LiveKitVoiceStageProps {
  onLeave: () => void;
  isMuted: boolean;
  onToggleMute: () => void;
}

export function LiveKitVoiceStage({
  onLeave,
  isMuted,
  onToggleMute,
}: LiveKitVoiceStageProps) {
  const { state, audioTrack, agentTranscriptions } = useVoiceAssistant();
  const { localParticipant, microphoneTrack } = useLocalParticipant();
  const micVolume = useTrackVolume(
    microphoneTrack?.track
      ? (microphoneTrack.track as unknown as LocalAudioTrack)
      : undefined,
  );

  // Apply noise gate (0.05) and scale normally to 100%
  const rawVol = micVolume || 0;
  const activeLevel =
    rawVol > 0.05
      ? Math.min(100, Math.round(((rawVol - 0.05) / 0.95) * 100))
      : 0;

  const handleToggleMute = () => {
    onToggleMute();
    localParticipant?.setMicrophoneEnabled(isMuted);
  };

  return (
    <div className="w-full max-w-3xl flex flex-col gap-6">
      {/* Main Stage View */}
      <div className="relative w-full bg-[#191919] rounded-3xl border border-gray-800 shadow-2xl p-8 pt-14 min-h-[420px] flex flex-col items-center justify-center overflow-hidden">
        {/* Agent Avatar & Orb */}
        <div className="relative flex flex-col items-center z-10">
          <InterviewerOrb state={state || "connecting"} />

          <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
            AI Interviewer{" "}
            <span className="text-xs font-semibold uppercase px-2.5 py-0.5 rounded-full bg-white/10 text-gray-300 border border-white/10">
              {state || "Connecting"}
            </span>
          </h2>

          {/* Audio / Thinking Visualizer */}
          <div>
            <StageVisualizer
              state={state || "connecting"}
              audioTrack={audioTrack}
            />
          </div>

          {/* Dynamic Spoken Transcript from Realtime Worker */}
          {agentTranscriptions.length > 0 && (
            <p className="text-sm text-gray-200 max-w-lg text-center mt-6 bg-white/10 border border-white/15 p-4 rounded-2xl backdrop-blur-md leading-relaxed">
              &ldquo;
              {agentTranscriptions[agentTranscriptions.length - 1].text}&rdquo;
            </p>
          )}
        </div>
      </div>

      {/* Control Bar with Real-time Microphone Input Meter */}
      <div className="bg-white rounded-2xl border border-gray-200 p-4 shadow-lg flex items-center justify-between px-6 gap-6">
        {/* Mic Controls & Volume Meter */}
        <div className="flex items-center gap-4 flex-1 max-w-md">
          <button
            type="button"
            onClick={handleToggleMute}
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
          <div className="flex-1 space-y-2">
            <div className="flex justify-between text-xs font-medium text-gray-600">
              <span>Your Mic Input</span>
              <span className="font-semibold text-xs text-gray-900">
                {isMuted
                  ? "Muted"
                  : activeLevel > 15
                    ? "Receiving Sound"
                    : "Listening..."}
              </span>
            </div>
            <div className="w-full h-1.5 bg-gray-100 rounded-full overflow-hidden border border-gray-200">
              <div
                className={`h-full transition-all duration-150 ${
                  isMuted
                    ? "w-0"
                    : activeLevel > 20
                      ? "bg-orange-500"
                      : "bg-orange-400"
                }`}
                style={{ width: isMuted ? "0%" : `${activeLevel}%` }}
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
