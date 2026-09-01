"use client";

import React, { useState, useEffect } from "react";
import {
  Mic,
  MicOff,
  PhoneOff,
  CheckCircle2,
  Sparkles,
  Play,
  Clock,
  ShieldCheck,
} from "lucide-react";
import {
  LiveKitRoom,
  RoomAudioRenderer,
  useVoiceAssistant,
  useLocalParticipant,
  BarVisualizer,
} from "@livekit/components-react";
import "@livekit/components-styles";
import Image from "next/image";

type Phase = "lobby" | "room" | "completed";

export default function CandidateInterviewPage({
  params,
}: {
  params: Promise<{ token: string }>;
}) {
  const [token, setToken] = useState<string>("mock-token");
  const [phase, setPhase] = useState<Phase>("lobby");

  // Audio & Devices state
  const [isMuted, setIsMuted] = useState(false);
  const [audioInputs, setAudioInputs] = useState<MediaDeviceInfo[]>([]);
  const [selectedInput, setSelectedInput] = useState<string>("");
  const [selectedOutput, setSelectedOutput] = useState<string>("");
  const [realAudioLevel, setRealAudioLevel] = useState<number>(0);
  const [hasMicPermission, setHasMicPermission] = useState<boolean>(false);

  // Audio Stream & Analyzer refs
  const streamRef = React.useRef<MediaStream | null>(null);
  const audioCtxRef = React.useRef<AudioContext | null>(null);
  const animFrameRef = React.useRef<number | null>(null);

  // Unwrap params
  useEffect(() => {
    params.then((res) => {
      if (res.token) {
        setToken(res.token);
      }
    });
  }, [params]);

  // Log active candidate room token
  useEffect(() => {
    if (token) {
      console.log("Candidate room token initialized:", token);
    }
  }, [token]);

  const [activeMicLabel, setActiveMicLabel] = useState<string>("");

  // Request real Microphone stream & setup Web Audio API Analyser
  const initMicrophone = React.useCallback(
    async (deviceId?: string) => {
      try {
        if (streamRef.current) {
          streamRef.current.getTracks().forEach((t) => t.stop());
        }
        if (animFrameRef.current) {
          cancelAnimationFrame(animFrameRef.current);
        }

        const constraints: MediaStreamConstraints = {
          audio: deviceId ? { deviceId: { exact: deviceId } } : true,
        };

        const stream = await navigator.mediaDevices.getUserMedia(constraints);
        streamRef.current = stream;
        setHasMicPermission(true);

        // Read active audio track properties from the actual stream
        const track = stream.getAudioTracks()[0];
        if (track) {
          if (track.label) {
            setActiveMicLabel(track.label);
          }
          const settings = track.getSettings();
          if (settings.deviceId) {
            setSelectedInput(settings.deviceId);
          }
        }

        // Refresh device list now that permissions are granted
        const devices = await navigator.mediaDevices.enumerateDevices();
        const inputs = devices.filter((d) => d.kind === "audioinput");
        const outputs = devices.filter((d) => d.kind === "audiooutput");
        setAudioInputs(inputs);

        if (!selectedOutput && outputs.length > 0) {
          setSelectedOutput(outputs[0].deviceId);
        }

        // Audio Context setup
        const AudioCtx =
          window.AudioContext ||
          (window as unknown as { webkitAudioContext: typeof AudioContext })
            .webkitAudioContext;
        const audioCtx = new AudioCtx();
        audioCtxRef.current = audioCtx;

        const source = audioCtx.createMediaStreamSource(stream);
        const analyser = audioCtx.createAnalyser();
        analyser.fftSize = 64;
        source.connect(analyser);

        const dataArray = new Uint8Array(analyser.frequencyBinCount);

        const updateLevel = () => {
          analyser.getByteFrequencyData(dataArray);
          let sum = 0;
          for (let i = 0; i < dataArray.length; i++) {
            sum += dataArray[i];
          }
          const average = sum / dataArray.length;
          // Normalize 0-255 to percentage 0-100
          const percentage = Math.min(100, Math.round((average / 128) * 100));
          setRealAudioLevel(percentage);
          animFrameRef.current = requestAnimationFrame(updateLevel);
        };

        updateLevel();
      } catch (err: unknown) {
        setHasMicPermission(false);
        if (
          err instanceof Error &&
          (err.name === "NotAllowedError" ||
            err.name === "PermissionDeniedError")
        ) {
          console.warn(
            "Microphone permission pending user gesture or browser permission allowance.",
          );
          return;
        }
        if (deviceId) {
          console.warn(
            "Exact mic constraint failed, falling back to default stream",
          );
          const fallbackStream = await navigator.mediaDevices
            .getUserMedia({ audio: true })
            .catch(() => null);
          if (fallbackStream) {
            streamRef.current = fallbackStream;
            setHasMicPermission(true);
            const fallbackTrack = fallbackStream.getAudioTracks()[0];
            if (fallbackTrack?.label) {
              setActiveMicLabel(fallbackTrack.label);
            }
          }
        }
      }
    },
    [selectedOutput],
  );

  // Handle Mute / Unmute stream tracks
  useEffect(() => {
    if (streamRef.current) {
      streamRef.current.getAudioTracks().forEach((track) => {
        track.enabled = !isMuted;
      });
    }
  }, [isMuted]);

  // Clean up audio tracks on unmount
  useEffect(() => {
    return () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((t) => t.stop());
      }
      if (audioCtxRef.current) {
        audioCtxRef.current.close();
      }
      if (animFrameRef.current) {
        cancelAnimationFrame(animFrameRef.current);
      }
    };
  }, []);

  // Initial load
  useEffect(() => {
    const startAudio = async () => {
      await initMicrophone();
    };
    startAudio();
  }, [initMicrophone]);

  return (
    <div className="min-h-screen bg-[#F6F6F6] text-gray-900 font-sans flex flex-col justify-between selection:bg-gray-200">
      {/* Main Body Content based on active phase */}
      <main className="flex-1 max-w-5xl w-full mx-auto p-4 md:p-8 flex flex-col justify-center items-center">
        {/* PHASE 1: PRE-ROOM / LOBBY PREPARATION */}
        {phase === "lobby" && (
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
                Welcome! Please check your microphone and audio input before
                entering the live interview.
              </p>
            </div>

            {/* Audio & Device Check Widget */}
            <div className="bg-gray-50 rounded-2xl border border-gray-200 mb-6 space-y-4 pb-4">
              <div className="flex items-center justify-between border-b px-4 py-3 border-gray-200">
                <h3 className="text-xs font-medium text-gray-600 tracking-wider">
                  Audio & Microphone Test
                </h3>
                <span className="flex items-center gap-1.5 text-xs text-emerald-600 font-medium bg-emerald-50 px-2 py-0.5 rounded-md border border-emerald-100">
                  <ShieldCheck className="w-3.5 h-3.5" /> Ready
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
                        audioInputs.find((d) => d.deviceId === selectedInput)
                          ?.label ||
                        "Default Microphone"}
                    </p>
                  </div>
                </div>

                <button
                  type="button"
                  onClick={() => setIsMuted(!isMuted)}
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
                          ? "bg-emerald-500"
                          : "bg-emerald-400"
                    }`}
                    style={{ width: isMuted ? "0%" : `${realAudioLevel}%` }}
                  />
                </div>
              </div>

              {!hasMicPermission && (
                <div className="px-4">
                  <div className="mt-3 p-3 bg-amber-50 border border-amber-200 rounded-xl flex items-center justify-between text-xs text-amber-800 font-medium">
                    <span>
                      Microphone permission required for the interview
                    </span>
                    <button
                      type="button"
                      onClick={() => initMicrophone()}
                      className="px-3 py-1 bg-gray-900 text-white rounded-lg font-semibold hover:bg-black transition-colors cursor-pointer"
                    >
                      Enable Mic
                    </button>
                  </div>
                </div>
              )}
            </div>

            {/* Preparation Guidelines */}
            <div className="space-y-2.5 mb-8 text-xs text-gray-600 ">
              <div className="flex items-center gap-2.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                <span>
                  Ensure you are in a quiet environment with a clear microphone.
                </span>
              </div>
              <div className="flex items-center gap-2.5">
                <Clock className="w-4 h-4 text-amber-600 flex-shrink-0" />
                <span>
                  Estimated Duration: 15–60 minutes (multi-goal evaluation).
                </span>
              </div>
            </div>

            {/* Join Action Button */}
            <button
              type="button"
              onClick={() => setPhase("room")}
              className="w-full py-2.5 bg-[#191919] hover:bg-black text-white rounded-lg font-bold text-sm transition-all flex items-center justify-center gap-2.5 cursor-pointer active:scale-[0.99]"
            >
              <Play className="w-4 h-4 fill-current" />
              <span>Enter Interview Room</span>
            </button>
          </div>
        )}

        {/* PHASE 2: LIVE INTERVIEW ROOM */}
        {phase === "room" &&
          token &&
          (token === "mock-token" || token.startsWith("mock") ? (
            <MockVoiceStage
              onLeave={() => setPhase("completed")}
              realAudioLevel={realAudioLevel}
              isMuted={isMuted}
              onToggleMute={() => setIsMuted(!isMuted)}
            />
          ) : (
            <LiveKitRoom
              serverUrl={
                process.env.NEXT_PUBLIC_LIVEKIT_URL || "ws://localhost:7880"
              }
              token={token}
              connect={true}
              audio={true}
              video={false}
              onDisconnected={() => setPhase("completed")}
              className="w-full max-w-3xl flex flex-col gap-6"
            >
              {/* RoomAudioRenderer MUST be included so you can hear the interviewer's voice */}
              <RoomAudioRenderer />
              {/* Custom LiveKit Voice Assistant Stage */}
              <LiveKitVoiceStage
                onLeave={() => setPhase("completed")}
                realAudioLevel={realAudioLevel}
                isMuted={isMuted}
                onToggleMute={() => setIsMuted(!isMuted)}
              />
            </LiveKitRoom>
          ))}

        {/* PHASE 3: POST-INTERVIEW FINISH PAGE */}
        {phase === "completed" && (
          <div className="w-full max-w-lg bg-white rounded-3xl border border-gray-200/90 shadow-xl p-8 text-center animate-in fade-in zoom-in-95 duration-200">
            <div className="w-20 h-20 rounded-3xl bg-emerald-50 border border-emerald-100 flex items-center justify-center mx-auto mb-6 text-emerald-600 shadow-xs">
              <CheckCircle2 className="w-10 h-10" />
            </div>

            <h1 className="text-lg font-semibold text-gray-900 tracking-tight">
              Interview Completed!
            </h1>

            <div className=" w-full flex justify-center">
              <p className="text-sm text-gray-600 max-w-100 mt-3 leading-relaxed">
                Thank you for taking the time to complete your interview. Your
                voice responses have been safely saved and sent for evaluation.
              </p>
            </div>

            <div className="mt-8 p-5 bg-gray-50 border border-gray-200 rounded-2xl text-xs text-gray-600 space-y-1.5 text-left">
              <p className="font-medium text-gray-900">What happens next?</p>
              <p className="leading-relaxed">
                The hiring team will review your structured evaluation report
                and reach out regarding next steps.
              </p>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

interface LiveKitVoiceStageProps {
  onLeave: () => void;
  realAudioLevel: number;
  isMuted: boolean;
  onToggleMute: () => void;
}

function MockVoiceStage({
  onLeave,
  realAudioLevel,
  isMuted,
  onToggleMute,
}: LiveKitVoiceStageProps) {
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
          <div className="relative mb-6">
            {state === "speaking" && (
              <div className="absolute -inset-3 rounded-full bg-emerald-500/20 animate-ping opacity-75" />
            )}
            <div className="w-24 h-24 rounded-full bg-gradient-to-tr from-emerald-500 to-teal-400 p-0.5 shadow-2xl flex items-center justify-center">
              <div className="w-full h-full bg-[#191919] rounded-full flex items-center justify-center ">
                <Sparkles
                  className="w-12 h-12 text-emerald-400"
                  strokeWidth="1"
                />
              </div>
            </div>
          </div>
          <h2 className="text-lg font-semibold text-white tracking-tight flex items-center gap-2">
            Interviewer{" "}
            <span className="text-xs font-semibold uppercase px-2.5 py-1 rounded-lg bg-white/10 text-gray-300">
              speaking
            </span>
          </h2>

          {/* Demo Audio Visualizer */}
          <div className="h-8 mt-4 flex items-center gap-1.5">
            {[40, 75, 55, 90, 60, 80, 45].map((height, i) => (
              <div
                key={i}
                className="w-0.5 bg-emerald-400 rounded-full animate-pulse"
                style={{
                  height: `${height}%`,
                  animationDelay: `${i * 120}ms`,
                }}
              />
            ))}
          </div>
          {/* Dynamic Spoken Transcript */}
          <p className="text-sm text-gray-200 max-w-md text-center mt-6 bg-white/10 p-4 rounded-2xl backdrop-blur-md shadow-xl leading-relaxed">
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
            className={`p-2 rounded-lg transition-colors cursor-pointer flex items-center justify-center ${
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

          {/* Volume Indicator Bar matching lobby preparation exactly */}
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
            <div className="w-full h-1.5 bg-gray-100 rounded-full overflow-hidden border border-gray-200">
              <div
                className={`h-full transition-all duration-75 ${
                  isMuted
                    ? "w-0"
                    : realAudioLevel > 20
                      ? "bg-emerald-500"
                      : "bg-emerald-400"
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
          className="px-3 py-1.5 bg-red-600 hover:bg-red-700 text-white rounded-lg text-sm font-semibold flex items-center gap-2 cursor-pointer shrink-0 transition-colors shadow-sm"
        >
          <PhoneOff className="w-4 h-4" />
          <span>Leave Interview</span>
        </button>
      </div>
    </div>
  );
}

function LiveKitVoiceStage({
  onLeave,
  realAudioLevel,
  isMuted,
  onToggleMute,
}: LiveKitVoiceStageProps) {
  const { state, audioTrack, agentTranscriptions } = useVoiceAssistant();
  const { localParticipant } = useLocalParticipant();

  const handleToggleMute = () => {
    onToggleMute();
    localParticipant?.setMicrophoneEnabled(isMuted);
  };

  return (
    <div className="w-full max-w-3xl flex flex-col gap-6">
      {/* Main Stage View */}
      <div className="relative w-full bg-[#191919] rounded-3xl border border-gray-800 shadow-2xl p-8 min-h-[420px] flex flex-col items-center justify-center overflow-hidden">
        {/* Agent Avatar & Orb */}
        <div className="relative flex flex-col items-center z-10">
          <div className="relative mb-6">
            {state === "speaking" && (
              <div className="absolute -inset-3 rounded-full bg-emerald-500/20 animate-ping opacity-75" />
            )}
            <div className="w-28 h-28 rounded-full bg-gradient-to-tr from-emerald-500 to-teal-400 p-1 shadow-2xl flex items-center justify-center">
              <div className="w-full h-full bg-[#191919] rounded-full flex items-center justify-center border border-white/10">
                <Sparkles
                  className={`w-12 h-12 transition-colors ${
                    state === "speaking" ? "text-emerald-400" : "text-gray-400"
                  }`}
                />
              </div>
            </div>
          </div>
          <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
            AI Interviewer{" "}
            <span className="text-xs font-semibold uppercase px-2.5 py-0.5 rounded-full bg-white/10 text-gray-300 border border-white/10">
              {state || "Connecting"}
            </span>
          </h2>

          {/* Dynamic Spoken Transcript from Realtime Worker */}
          {agentTranscriptions.length > 0 && (
            <p className="text-sm text-gray-200 max-w-md text-center mt-6 bg-white/10 border border-white/15 p-4 rounded-2xl backdrop-blur-md shadow-xl leading-relaxed">
              &ldquo;
              {agentTranscriptions[agentTranscriptions.length - 1].text}&rdquo;
            </p>
          )}

          {/* Audio Visualizer */}
          <div className="h-8 mt-4">
            <BarVisualizer state={state} barCount={7} trackRef={audioTrack} />
          </div>
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

          {/* Volume Indicator Bar matching lobby preparation exactly */}
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
            <div className="w-full h-2.5 bg-gray-100 rounded-full overflow-hidden border border-gray-200">
              <div
                className={`h-full transition-all duration-75 ${
                  isMuted
                    ? "w-0"
                    : realAudioLevel > 20
                      ? "bg-emerald-500"
                      : "bg-emerald-400"
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
