/**
 * What: Candidate Interview Page Route (`/interview/[token]`).
 * Why: Main container orchestrating session initialization, phase switching (lobby | room | completed), and phase view routing.
 * Boundaries: Does not contain inline device checking or voice visualizer logic; delegates to feature components.
 */

"use client";

import React, { useState, useEffect } from "react";
import { LiveKitRoom, RoomAudioRenderer } from "@livekit/components-react";
import "@livekit/components-styles";

import { useMicrophoneTest } from "@/features/candidate-interview/hooks/useMicrophoneTest";
import { PreInterviewLobby } from "@/features/candidate-interview/components/PreInterviewLobby";
import { PostInterviewCompleted } from "@/features/candidate-interview/components/PostInterviewCompleted";
import { MockVoiceStage } from "@/features/candidate-interview/components/MockVoiceStage";
import { LiveKitVoiceStage } from "@/features/candidate-interview/components/LiveKitVoiceStage";

type Phase = "lobby" | "room" | "completed";

export default function CandidateInterviewPage({
  params,
  searchParams,
}: {
  params: Promise<{ token?: string }>;
  searchParams?: Promise<{ token?: string }>;
}) {
  const [token, setToken] = useState<string>("");
  const [phase, setPhase] = useState<Phase>("lobby");
  const [isLoadingSession, setIsLoadingSession] = useState(true);
  const [sessionError, setSessionError] = useState<string | null>(null);
  const [isStartingRoom, setIsStartingRoom] = useState(false);

  const micTest = useMicrophoneTest();

  // Unwrap params and searchParams
  useEffect(() => {
    Promise.all([
      params ?? Promise.resolve({ token: undefined }),
      searchParams ?? Promise.resolve({ token: undefined }),
    ]).then(([pRes, sRes]) => {
      const activeToken = sRes?.token || pRes?.token;
      if (activeToken) {
        setToken(activeToken);
      } else {
        setToken("mock-token");
      }
    });
  }, [params, searchParams]);

  // Check Session Status on Load
  useEffect(() => {
    if (!token) return;

    if (token === "mock-token") {
      setTimeout(() => setIsLoadingSession(false), 0);
      return;
    }

    const checkSession = async () => {
      try {
        const backendUrl =
          process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";
        const res = await fetch(`${backendUrl}/api/session/${token}`);
        if (!res.ok) {
          throw new Error(
            "Failed to load interview session. The link might be invalid or expired.",
          );
        }
        const data = await res.json();

        if (data.status === "finished") {
          setPhase("completed");
        }
      } catch (err) {
        setSessionError(
          err instanceof Error ? err.message : "Failed to load session",
        );
      } finally {
        setIsLoadingSession(false);
      }
    };
    checkSession();
  }, [token]);

  const handleEnterRoom = async () => {
    // Release pre-interview test audio stream & AudioContext so mic hardware is free for LiveKit
    micTest.releaseMicrophoneResources();

    if (token !== "mock-token") {
      setIsStartingRoom(true);
      try {
        const backendUrl =
          process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";
        const res = await fetch(`${backendUrl}/api/session/${token}/start`, {
          method: "POST",
        });
        if (!res.ok) {
          throw new Error("Failed to start the interview session.");
        }
      } catch (err) {
        console.error(err);
        setSessionError(
          err instanceof Error ? err.message : "Failed to start session",
        );
        setIsStartingRoom(false);
        return;
      }
    }
    setPhase("room");
  };

  if (isLoadingSession) {
    return (
      <div className="min-h-screen bg-[#F6F6F6] flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-8 h-8 border-4 border-gray-200 border-t-gray-800 rounded-full animate-spin" />
          <p className="text-sm font-medium text-gray-600 tracking-wide">
            Loading session...
          </p>
        </div>
      </div>
    );
  }

  if (sessionError) {
    return (
      <div className="min-h-screen bg-[#F6F6F6] flex items-center justify-center p-4">
        <div className="bg-white p-6 py-8 rounded-3xl border border-red-100 shadow-xl max-w-md text-center flex flex-col items-center gap-0">
          <div className="w-12 h-12 bg-red-50 text-red-500 rounded-2xl flex items-center justify-center mb-6">
            <span className="font-bold text-2xl">!</span>
          </div>
          <h2 className="text-base font-semibold text-gray-900">
            Session Error
          </h2>
          <p className="text-sm text-gray-600 mb-6">{sessionError}</p>
          <button
            type="button"
            onClick={() => window.location.reload()}
            className="px-3 py-1.5 bg-[#191919] text-white text-sm font-medium rounded-lg hover:opacity-75 transition-colors cursor-pointer"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#F6F6F6] text-gray-900 font-sans flex flex-col justify-between selection:bg-gray-200">
      <main className="flex-1 max-w-5xl w-full mx-auto p-4 md:p-8 flex flex-col justify-center items-center">
        {/* PHASE 1: PRE-ROOM LOBBY */}
        {phase === "lobby" && (
          <PreInterviewLobby
            isMuted={micTest.isMuted}
            onToggleMute={() => micTest.setIsMuted(!micTest.isMuted)}
            audioInputs={micTest.audioInputs}
            selectedInput={micTest.selectedInput}
            activeMicLabel={micTest.activeMicLabel}
            realAudioLevel={micTest.realAudioLevel}
            hasMicPermission={micTest.hasMicPermission}
            onEnableMic={() => micTest.initMicrophone()}
            isStartingRoom={isStartingRoom}
            onEnterRoom={handleEnterRoom}
          />
        )}

        {/* PHASE 2: LIVE INTERVIEW ROOM */}
        {phase === "room" &&
          token &&
          (token === "mock-token" ? (
            <MockVoiceStage
              onLeave={() => setPhase("completed")}
              realAudioLevel={micTest.realAudioLevel}
              isMuted={micTest.isMuted}
              onToggleMute={() => micTest.setIsMuted(!micTest.isMuted)}
            />
          ) : (
            <LiveKitRoom
              serverUrl={
                process.env.NEXT_PUBLIC_LIVEKIT_URL || "ws://localhost:7880"
              }
              token={token}
              connect={true}
              audio={
                micTest.selectedInput
                  ? { deviceId: micTest.selectedInput }
                  : true
              }
              video={false}
              onDisconnected={() => {
                console.log(
                  "LiveKit room disconnected — transitioning to completed.",
                );
                setPhase("completed");
              }}
              className="w-full max-w-3xl flex flex-col gap-6"
            >
              <RoomAudioRenderer />
              <LiveKitVoiceStage
                onLeave={() => setPhase("completed")}
                isMuted={micTest.isMuted}
                onToggleMute={() => micTest.setIsMuted(!micTest.isMuted)}
              />
            </LiveKitRoom>
          ))}

        {/* PHASE 3: POST-INTERVIEW FINISHED */}
        {phase === "completed" && <PostInterviewCompleted />}
      </main>
    </div>
  );
}
