/**
 * What: Stage Audio Visualizer & Thinking Status Indicator Component.
 * Why: Displays volume spectrum bars for spoken audio or animated thinking spinner when agent is processing.
 * Boundaries: Pure UI component; integrates with LiveKit TrackReferenceOrPlaceholder.
 */

import React from "react";
import {
  TrackReferenceOrPlaceholder,
  useTrackVolume,
  isTrackReference,
} from "@livekit/components-react";

interface StageVisualizerProps {
  state: string;
  audioTrack?: TrackReferenceOrPlaceholder;
}

export function StageVisualizer({ state, audioTrack }: StageVisualizerProps) {
  const isThinking = state === "thinking" || state === "reasoning";
  const volume = useTrackVolume(
    isTrackReference(audioTrack) ? audioTrack : undefined,
  ); // returns 0-1
  const volMultiplier = volume ? Math.max(0.3, volume * 3) : 1;

  if (isThinking) {
    return (
      <div className="h-8 mt-4 flex items-center justify-center gap-3">
        {/* Animated Wavy Circular Wave Indicator */}
        <div className="relative flex items-center justify-center w-7 h-7">
          <div className="absolute inset-0 rounded-full border border-orange-400/60 animate-ping opacity-75" />
          <div className="absolute inset-0.5 rounded-full border-2 border-red-300 border-t-transparent animate-[spin_1.2s_linear_infinite]" />
          <div className="w-2.5 h-2.5 rounded-full bg-orange-400 animate-pulse" />
        </div>
        <span className="text-xs font-semibold text-orange-400 tracking-wider uppercase animate-pulse">
          Thinking...
        </span>
      </div>
    );
  }

  return (
    <div className="h-8 mt-4 flex items-center gap-1.5">
      {[40, 65, 45, 80, 50, 70, 35].map((height, i) => (
        <div
          key={i}
          className={`w-0.5 bg-orange-300 rounded-full ${!audioTrack ? "animate-pulse" : "transition-all duration-75"}`}
          style={{
            height: audioTrack
              ? `${Math.min(100, height * volMultiplier)}%`
              : `${height}%`,
            animationDelay: `${i * 120}ms`,
          }}
        />
      ))}
    </div>
  );
}
