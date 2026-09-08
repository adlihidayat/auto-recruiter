/**
 * What: Pre-interview Lobby Preparation View (Phase 1).
 * Why: Allows candidates to test their microphone input, check volume levels, and view preparation instructions before joining.
 * Boundaries: Rendered when session phase is "lobby". Handles mic setup UI and triggers room entry.
 */

import React from "react";
import Image from "next/image";
import {
  Mic,
  MicOff,
  CheckCircle2,
  Play,
  Clock,
  ShieldCheck,
} from "lucide-react";

interface PreInterviewLobbyProps {
  isMuted: boolean;
  onToggleMute: () => void;
  audioInputs: MediaDeviceInfo[];
  selectedInput: string;
  activeMicLabel: string;
  realAudioLevel: number;
  hasMicPermission: boolean;
  onEnableMic: () => void;
  isStartingRoom: boolean;
  onEnterRoom: () => void;
}

export function PreInterviewLobby({
  isMuted,
  onToggleMute,
  audioInputs,
  selectedInput,
  activeMicLabel,
  realAudioLevel,
  hasMicPermission,
  onEnableMic,
  isStartingRoom,
  onEnterRoom,
}: PreInterviewLobbyProps) {
  return (
    <div className="w-full max-w-xl bg-white rounded-3xl border border-gray-200 shadow-xl p-6 md:p-8 animate-in fade-in zoom-in-95 duration-200">
      {/* Header / Branding */}
      <div className="text-center mb-8 pt-5 flex flex-col items-center">
        <Image
          src="/logo.svg"
          alt="Logo"
          width={35}
          height={35}
          className="mx-auto mb-3"
        />
        <h1 className="text-lg font-semibold text-gray-900 tracking-tight">
          AI Voice Interview Session
        </h1>
        <p className="text-sm text-gray-600 mt-2 max-w-100 text-center">
          Welcome! Please check your microphone and audio input before entering
          the live interview.
        </p>
      </div>

      {/* Audio & Device Check Widget */}
      <div className="bg-gray-50 rounded-2xl border border-gray-200 mb-6 space-y-4 pb-4">
        <div className="flex items-center justify-between border-b px-4 py-3 border-gray-200">
          <h3 className="text-xs font-medium text-gray-600 tracking-wider">
            Audio & Microphone Test
          </h3>
          <span className="flex items-center gap-1.5 text-xs text-emerald-600 font-medium bg-emerald-50 px-2 py-0.5 rounded-md border border-emerald-100">
            <ShieldCheck className="w-3 h-3" /> Ready
          </span>
        </div>

        {/* Mic Input Info */}
        <div className="flex items-center justify-between px-4">
          <div className="flex items-center gap-3">
            <div
              className={`p-2.5 rounded-xl transition-colors ${
                isMuted
                  ? "bg-red-50 text-red-500 border border-red-100"
                  : "bg-emerald-50 text-emerald-600 border border-emerald-100"
              }`}
            >
              {isMuted ? (
                <MicOff className="w-5 h-5" />
              ) : (
                <Mic className="w-5 h-5" />
              )}
            </div>
            <div>
              <p className="text-sm font-semibold text-gray-900">
                Microphone Device
              </p>
              <p className="text-xs text-gray-600 truncate max-w-[220px]">
                {activeMicLabel ||
                  audioInputs.find((d) => d.deviceId === selectedInput)?.label ||
                  "Default Microphone"}
              </p>
            </div>
          </div>

          <button
            type="button"
            onClick={onToggleMute}
            className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition-all cursor-pointer ${
              isMuted
                ? "bg-red-100 text-red-700 hover:bg-red-200"
                : "bg-gray-100 text-gray-700 hover:bg-gray-200 border border-gray-200"
            }`}
          >
            {isMuted ? "Unmute" : "Mute"}
          </button>
        </div>

        {/* Live Audio Level Meter */}
        <div className="space-y-1.5 px-4 pt-0 pb-2">
          <div className="flex justify-between text-xs text-gray-600 font-medium">
            <span>Input Signal Level</span>
            <span className="font-medium text-gray-600">
              {!hasMicPermission
                ? "Mic Access Required"
                : isMuted
                  ? "Muted"
                  : realAudioLevel > 15
                    ? "Receiving Sound"
                    : "Listening..."}
            </span>
          </div>
          <div className="w-full h-1.5 bg-gray-200/80 rounded-full overflow-hidden border border-gray-200">
            <div
              className={`h-full transition-all duration-75 ${
                isMuted
                  ? "w-0"
                  : realAudioLevel > 20
                    ? "bg-orange-500"
                    : "bg-orange-400"
              }`}
              style={{ width: isMuted ? "0%" : `${realAudioLevel}%` }}
            />
          </div>
        </div>

        {!hasMicPermission && (
          <div className="px-4">
            <div className="mt-3 p-3 bg-amber-50 border border-amber-200 rounded-xl flex items-center justify-between text-xs text-amber-800 font-medium">
              <span>Microphone permission required for the interview</span>
              <button
                type="button"
                onClick={onEnableMic}
                className="px-3 py-1 bg-[#191919] text-white rounded-lg font-semibold hover:bg-black transition-colors cursor-pointer"
              >
                Enable Mic
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Preparation Guidelines */}
      <div className="space-y-2.5 mb-8 text-xs text-gray-600">
        <div className="flex items-center gap-2.5">
          <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
          <span>
            Ensure you are in a quiet environment with a clear microphone.
          </span>
        </div>
        <div className="flex items-center gap-2.5">
          <Clock className="w-4 h-4 text-emerald-600 flex-shrink-0" />
          <span>Estimated Duration: 15–60 minutes (multi-goal evaluation).</span>
        </div>
      </div>

      {/* Join Action Button */}
      <button
        type="button"
        onClick={onEnterRoom}
        disabled={isStartingRoom}
        className="w-full py-2.5 bg-[#191919] hover:bg-black text-white rounded-lg font-semibold text-sm transition-all flex items-center justify-center gap-2.5 cursor-pointer active:scale-[0.99] disabled:opacity-70 disabled:cursor-not-allowed"
      >
        {isStartingRoom ? (
          <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
        ) : (
          <Play className="w-2.5 h-2.5 fill-current" />
        )}
        <span>
          {isStartingRoom ? "Starting Interview..." : "Enter Interview Room"}
        </span>
      </button>
    </div>
  );
}
