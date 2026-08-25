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
} from "lucide-react";
import Image from "next/image";
import {
  LiveKitRoom,
  RoomAudioRenderer,
  useVoiceAssistant,
  BarVisualizer,
} from "@livekit/components-react";
import "@livekit/components-styles";

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
        setAudioOutputs(outputs);

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
        console.error("Microphone access error:", err);
        // Fallback to default audio stream if exact deviceId constraints failed
        if (deviceId) {
          console.warn("Exact mic constraint failed, falling back to default stream");
          const fallbackStream = await navigator.mediaDevices.getUserMedia({ audio: true }).catch(() => null);
          if (fallbackStream) {
            streamRef.current = fallbackStream;
            setHasMicPermission(true);
            const fallbackTrack = fallbackStream.getAudioTracks()[0];
            if (fallbackTrack?.label) {
              setActiveMicLabel(fallbackTrack.label);
            }
          } else {
            setHasMicPermission(false);
          }
        } else {
          setHasMicPermission(false);
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
    <div className="min-h-screen bg-[#F8F9FA] text-[#272727] font-sans flex flex-col justify-between selection:bg-[#FE6100]/20 selection:text-[#FE6100]">
      {/* Main Body Content based on active phase */}
      <main className="flex-1 max-w-5xl w-full mx-auto p-6 flex flex-col justify-center items-center">
        {/* PHASE 1: PRE-ROOM / LOBBY */}
        {phase === "lobby" && (
          <div className="w-full max-w-xl bg-white rounded-3xl border border-[#E9E9E9] shadow-xl p-8 animate-in fade-in zoom-in-95 duration-200">
            <div className="text-center mb-8">
              <div className="w-16 h-16 rounded-2xl bg-black-50 flex items-center justify-center mx-auto mb-4 text-[#FE6100]">
                <Image
                  src="/logo.svg"
                  alt="Company Logo"
                  width={50}
                  height={50}
                />
              </div>
              <h1 className="text-2xl font-extrabold text-[#272727] tracking-tight">
                Senior Frontend Engineer Interview
              </h1>
              <p className="text-sm text-[#616161] mt-2">
                Welcome! Please check your audio settings before joining the AI
                interview room.
              </p>
            </div>

            {/* Audio Check Widget */}
            <div className="bg-[#F9FAFB] rounded-2xl border border-[#E9E9E9] p-5 mb-8 space-y-4">
              <h3 className="text-xs font-bold text-[#616161] uppercase tracking-wider">
                Device Test
              </h3>

              {/* Mic Input */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div
                    className={`p-2.5 rounded-xl ${isMuted ? "bg-red-50 text-red-500" : "bg-emerald-50 text-emerald-600"}`}
                  >
                    {isMuted ? (
                      <MicOff className="w-5 h-5" />
                    ) : (
                      <Mic className="w-5 h-5" />
                    )}
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-[#272727]">
                      Microphone
                    </p>
                    <p className="text-xs text-[#616161]">
                      {activeMicLabel ||
                        audioInputs.find((d) => d.deviceId === selectedInput)
                          ?.label ||
                        "Default Microphone"}
                    </p>
                  </div>
                </div>

                <button
                  onClick={() => setIsMuted(!isMuted)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                    isMuted
                      ? "bg-red-100 text-red-700 hover:bg-red-200"
                      : "bg-gray-200 text-[#272727] hover:bg-gray-300"
                  }`}
                >
                  {isMuted ? "Unmute" : "Mute"}
                </button>
              </div>

              {/* Volume Level bar */}
              <div className="space-y-1">
                <div className="flex justify-between text-xs text-[#616161] font-medium">
                  <span>Real Microphone Input Level</span>
                  <span>
                    {!hasMicPermission
                      ? "Mic Access Required"
                      : isMuted
                        ? "Muted"
                        : realAudioLevel > 5
                          ? "Receiving Sound"
                          : "Listening..."}
                  </span>
                </div>
                <div className="w-full h-2.5 bg-gray-200 rounded-full overflow-hidden">
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
                <div className="mt-3 p-3 bg-amber-50 border border-amber-200 rounded-xl flex items-center justify-between text-xs text-amber-800 font-medium">
                  <span>Microphone permission required for the interview</span>
                  <button
                    onClick={() => initMicrophone()}
                    className="px-3 py-1 bg-[#FE6100] text-white rounded-lg font-semibold hover:bg-[#e05600] transition-colors cursor-pointer"
                  >
                    Enable Mic
                  </button>
                </div>
              )}
            </div>

            {/* Quick Guidelines */}
            <div className="space-y-2 mb-8 text-xs text-[#616161]">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                <span>
                  Ensure you are in a quiet environment with a stable internet
                  connection.
                </span>
              </div>
              <div className="flex items-center gap-2">
                <Clock className="w-4 h-4 text-[#FE6100] flex-shrink-0" />
                <span>
                  Estimated Duration: 30 minutes (3 evaluation goals).
                </span>
              </div>
            </div>

            {/* Join Action Button */}
            <button
              onClick={() => setPhase("room")}
              className="w-full py-4 bg-[#FE6100] hover:bg-[#e05600] text-white rounded-2xl font-bold text-base shadow-lg shadow-[#FE6100]/25 transition-all flex items-center justify-center gap-2 cursor-pointer"
            >
              <Play className="w-5 h-5 fill-current" />
              <span>Enter Interview Room</span>
            </button>
          </div>
        )}

        {/* PHASE 2: LIVE INTERVIEW ROOM */}
        {phase === "room" && token && (
          <LiveKitRoom
            serverUrl={process.env.NEXT_PUBLIC_LIVEKIT_URL || "ws://localhost:7880"}
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
            <LiveKitVoiceStage onLeave={() => setPhase("completed")} />
          </LiveKitRoom>
        )}

        {/* PHASE 3: POST-INTERVIEW FINISH PAGE */}
        {phase === "completed" && (
          <div className="w-full max-w-lg bg-white rounded-3xl border border-[#E9E9E9] shadow-xl p-8 text-center animate-in fade-in zoom-in-95 duration-200">
            <div className="w-20 h-20 rounded-3xl bg-emerald-50 border border-emerald-100 flex items-center justify-center mx-auto mb-6 text-emerald-600">
              <CheckCircle2 className="w-10 h-10" />
            </div>

            <h1 className="text-2xl font-extrabold text-[#272727] tracking-tight">
              Interview Completed!
            </h1>

            <p className="text-sm text-[#616161] mt-3 leading-relaxed">
              Thank you for completing your AI interview. Your responses have
              been successfully recorded and are being processed by our
              evaluation engine.
            </p>

            <div className="mt-8 p-4 bg-gray-50 border border-[#E9E9E9] rounded-2xl text-xs text-[#616161] space-y-1 text-left">
              <p className="font-semibold text-[#272727]">What happens next?</p>
              <p>
                The recruiting team will review your report and reach out
                regarding next steps shortly.
              </p>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

function LiveKitVoiceStage({ onLeave }: { onLeave: () => void }) {
  const { state, audioTrack, agentTranscriptions } = useVoiceAssistant();
  return (
    <div className="w-full max-w-3xl flex flex-col gap-6">
      {/* Main Stage View */}
      <div className="relative w-full bg-[#18181B] rounded-3xl border border-gray-800 shadow-2xl p-8 min-h-[420px] flex flex-col items-center justify-center overflow-hidden">
        
        {/* Agent Avatar */}
        <div className="relative flex flex-col items-center z-10">
          <div className="relative mb-6">
            {state === "speaking" && (
              <div className="absolute -inset-3 rounded-full bg-[#FE6100]/20 animate-ping opacity-75" />
            )}
            <div className="w-28 h-28 rounded-full bg-gradient-to-tr from-[#FE6100] to-amber-400 p-1 shadow-xl flex items-center justify-center">
              <div className="w-full h-full bg-[#18181B] rounded-full flex items-center justify-center">
                <Sparkles className={`w-12 h-12 ${state === "speaking" ? "text-[#FE6100]" : "text-gray-400"}`} />
              </div>
            </div>
          </div>
          <h2 className="text-xl font-bold text-white tracking-tight">
            AI Interviewer <span className="text-xs font-normal text-gray-400">({state})</span>
          </h2>
          {/* Dynamic Spoken Transcript from Realtime Worker */}
          {agentTranscriptions.length > 0 && (
            <p className="text-sm text-gray-300 max-w-md text-center mt-6 bg-white/5 border border-white/10 p-4 rounded-2xl backdrop-blur-sm">
              &ldquo;{agentTranscriptions[agentTranscriptions.length - 1].text}&rdquo;
            </p>
          )}
          {/* Audio Visualizer */}
          <div className="h-8 mt-4">
            <BarVisualizer state={state} barCount={7} trackRef={audioTrack} />
          </div>
        </div>
      </div>
      {/* Control Bar */}
      <div className="bg-white rounded-2xl border border-[#E9E9E9] p-4 shadow-lg flex items-center justify-between px-8">
        <button
          onClick={onLeave}
          className="px-6 py-3 bg-red-600 hover:bg-red-700 text-white rounded-2xl text-sm font-bold flex items-center gap-2"
        >
          <PhoneOff className="w-4 h-4" />
          <span>Leave Interview</span>
        </button>
      </div>
    </div>
  );
}
