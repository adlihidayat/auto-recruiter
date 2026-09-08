/**
 * What: Animated Orb Avatar Component for the AI Interviewer.
 * Why: Displays dynamic visual feedback (ping ring for speaking, wavy SVG rings for thinking, breathing halo for listening).
 * Boundaries: Pure UI component; receives state string ("speaking" | "thinking" | "listening" | etc.).
 */

import React from "react";
import { Sparkles } from "lucide-react";

interface InterviewerOrbProps {
  state: string;
}

export function InterviewerOrb({ state }: InterviewerOrbProps) {
  const isSpeaking = state === "speaking";
  const isThinking = state === "thinking" || state === "reasoning";
  const isListening = state === "listening";

  return (
    <div className="relative mb-6 flex items-center justify-center">
      {/* Speaking Ping Ring */}
      {isSpeaking && (
        <div className="absolute -inset-3 rounded-full bg-orange-500/20 animate-ping opacity-75" />
      )}

      {/* Thinking Circular Wavy Animated Rings */}
      {isThinking && (
        <>
          {/* Outer Wave Pulse Ring */}
          <div className="absolute -inset-6 rounded-full border-2 border-orange-400/30 animate-ping opacity-60" />

          {/* Outer Clockwise Rotating Dashed Wavy Circle */}
          <svg
            className="absolute -inset-5 w-38 h-38 animate-[spin_8s_linear_infinite] text-orange-400/70 pointer-events-none"
            viewBox="0 0 100 100"
          >
            <circle
              cx="50"
              cy="50"
              r="46"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeDasharray="6 10"
              strokeLinecap="round"
            />
          </svg>

          {/* Inner Counter-Rotating Wavy Ring */}
          <svg
            className="absolute -inset-3 w-34 h-34 animate-[spin_5s_linear_infinite_reverse] text-red-300/80 pointer-events-none"
            viewBox="0 0 100 100"
          >
            <circle
              cx="50"
              cy="50"
              r="40"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.5"
              strokeDasharray="4 6 12 6"
              strokeLinecap="round"
            />
          </svg>
        </>
      )}

      {/* Listening Breathing Halo */}
      {isListening && (
        <div className="absolute -inset-3 rounded-full bg-red-500/20 animate-pulse opacity-75" />
      )}

      {/* Main Central Orb */}
      <div className="w-28 h-28 rounded-full bg-gradient-to-tr from-orange-300 to-red-300 p-0.5 shadow-2xl flex items-center justify-center relative z-10">
        <div className="w-full h-full bg-[#191919] rounded-full flex items-center justify-center border border-white/10">
          <Sparkles
            className={`w-12 h-12 transition-colors ${
              isSpeaking
                ? "text-orange-300"
                : isThinking
                  ? "text-red-300 animate-pulse"
                  : "text-gray-400"
            }`}
            strokeWidth="1"
          />
        </div>
      </div>
    </div>
  );
}
