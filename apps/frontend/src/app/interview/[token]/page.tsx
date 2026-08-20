"use client";

import React, { useState, useEffect } from "react";
import {
  Mic,
  MicOff,
  Settings,
  PhoneOff,
  CheckCircle2,
  Sparkles,
  User,
  ChevronDown,
  X,
  Play,
  ShieldCheck,
  Clock,
} from "lucide-react";
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
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [audioInputs, setAudioInputs] = useState<MediaDeviceInfo[]>([]);
  const [audioOutputs, setAudioOutputs] = useState<MediaDeviceInfo[]>([]);
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
      if (res.token) setToken(res.token);
    });
  }, [params]);

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

        // Refresh device list now that permissions are granted
        const devices = await navigator.mediaDevices.enumerateDevices();
        const inputs = devices.filter((d) => d.kind === "audioinput");
        const outputs = devices.filter((d) => d.kind === "audiooutput");
        setAudioInputs(inputs);
        setAudioOutputs(outputs);

        if (!selectedInput && inputs.length > 0) {
          setSelectedInput(inputs[0].deviceId);
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
        setHasMicPermission(false);
      }
    },
    [selectedInput],
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
      {/* Top Navigation Bar */}

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
                      {audioInputs.find((d) => d.deviceId === selectedInput)
                        ?.label || "Default Microphone"}
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
        {phase === "room" && (
          <div className="w-full max-w-3xl flex flex-col gap-6 animate-in fade-in duration-300">
            {/* Main Stage View */}
            <div className="relative w-full bg-[#18181B] rounded-3xl border border-gray-800 shadow-2xl p-8 min-h-[420px] flex flex-col items-center justify-center overflow-hidden">
              {/* Subtle ambient light glow */}
              <div className="absolute w-72 h-72 rounded-full bg-[#FE6100]/10 blur-3xl pointer-events-none" />

              {/* AI Avatar / Participant Display */}
              <div className="relative flex flex-col items-center z-10">
                <div className="relative mb-6">
                  {/* Glowing speech ring when AI is active */}
                  <div className="absolute -inset-3 rounded-full bg-[#FE6100]/20 animate-ping opacity-75" />
                  <div className="w-28 h-28 rounded-full bg-gradient-to-tr from-[#FE6100] to-amber-400 p-1 shadow-xl relative z-10 flex items-center justify-center">
                    <div className="w-full h-full bg-[#18181B] rounded-full flex items-center justify-center">
                      <Sparkles className="w-12 h-12 text-[#FE6100]" />
                    </div>
                  </div>
                </div>

                <h2 className="text-xl font-bold text-white tracking-tight">
                  Interviewer
                </h2>

                <p className="text-sm text-gray-300 max-w-md text-center mt-6 bg-white/5 border border-white/10 p-4 rounded-2xl backdrop-blur-sm">
                  &ldquo;Welcome to your interview! Could you please introduce
                  yourself and share your experience with frontend
                  architecture?&rdquo;
                </p>
              </div>

              {/* Candidate Self Audio Indicator */}
              <div className="absolute bottom-4 left-4 flex items-center gap-2 bg-black/60 backdrop-blur-md px-3.5 py-2 rounded-xl border border-white/10 text-white text-xs font-medium">
                <div className="w-6 h-6 rounded-full bg-gray-700 flex items-center justify-center">
                  <User className="w-3.5 h-3.5 text-gray-300" />
                </div>
                <span>You (Candidate)</span>
                {isMuted ? (
                  <MicOff className="w-3.5 h-3.5 text-red-400" />
                ) : (
                  <div className="flex items-center gap-0.5 h-3">
                    <span className="w-0.5 bg-emerald-400 rounded-full animate-bounce h-2" />
                    <span className="w-0.5 bg-emerald-400 rounded-full animate-bounce h-3 delay-75" />
                    <span className="w-0.5 bg-emerald-400 rounded-full animate-bounce h-1 delay-150" />
                  </div>
                )}
              </div>

              {/* Settings Dropdown Panel */}
              {isSettingsOpen && (
                <div className="absolute top-4 right-4 w-80 bg-[#27272A] border border-gray-700 rounded-2xl p-4 shadow-2xl z-30 text-white text-xs space-y-4 animate-in fade-in zoom-in-95 duration-150">
                  <div className="flex items-center justify-between border-b border-gray-700 pb-2">
                    <span className="font-bold text-sm">Audio Settings</span>
                    <button
                      onClick={() => setIsSettingsOpen(false)}
                      className="text-gray-400 hover:text-white p-1"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>

                  {/* Microphone selection */}
                  <div>
                    <label className="block text-gray-400 mb-1.5 font-medium">
                      Microphone Input
                    </label>
                    <div className="relative">
                      <select
                        value={selectedInput}
                        onChange={(e) => setSelectedInput(e.target.value)}
                        className="w-full bg-[#18181B] border border-gray-600 rounded-xl px-3 py-2 text-white appearance-none focus:outline-none focus:border-[#FE6100]"
                      >
                        {audioInputs.map((d) => (
                          <option key={d.deviceId} value={d.deviceId}>
                            {d.label || `Microphone ${d.deviceId.slice(0, 5)}`}
                          </option>
                        ))}
                      </select>
                      <ChevronDown className="w-4 h-4 text-gray-400 absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none" />
                    </div>
                  </div>

                  {/* Speaker selection */}
                  <div>
                    <label className="block text-gray-400 mb-1.5 font-medium">
                      Speaker Output
                    </label>
                    <div className="relative">
                      <select
                        value={selectedOutput}
                        onChange={(e) => setSelectedOutput(e.target.value)}
                        className="w-full bg-[#18181B] border border-gray-600 rounded-xl px-3 py-2 text-white appearance-none focus:outline-none focus:border-[#FE6100]"
                      >
                        {audioOutputs.map((d) => (
                          <option key={d.deviceId} value={d.deviceId}>
                            {d.label || `Speaker ${d.deviceId.slice(0, 5)}`}
                          </option>
                        ))}
                      </select>
                      <ChevronDown className="w-4 h-4 text-gray-400 absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none" />
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Simple Floating Control Bar */}
            <div className="bg-white rounded-2xl border border-[#E9E9E9] p-4 shadow-lg flex items-center justify-between px-8">
              <div className="flex items-center gap-3">
                {/* Mute/Unmute Mic */}
                <button
                  onClick={() => setIsMuted(!isMuted)}
                  className={`p-3.5 rounded-2xl border transition-all flex items-center gap-2 text-sm font-semibold cursor-pointer ${
                    isMuted
                      ? "bg-red-50 border-red-200 text-red-600 hover:bg-red-100"
                      : "bg-gray-100 border-gray-200 text-[#272727] hover:bg-gray-200"
                  }`}
                >
                  {isMuted ? (
                    <MicOff className="w-5 h-5" />
                  ) : (
                    <Mic className="w-5 h-5" />
                  )}
                  <span>{isMuted ? "Mic Off" : "Mic On"}</span>
                </button>

                {/* Device Settings Toggle */}
                <button
                  onClick={() => setIsSettingsOpen(!isSettingsOpen)}
                  className={`p-3.5 rounded-2xl border transition-all flex items-center gap-2 text-sm font-semibold cursor-pointer ${
                    isSettingsOpen
                      ? "bg-orange-50 border-orange-200 text-[#FE6100]"
                      : "bg-gray-100 border-gray-200 text-[#272727] hover:bg-gray-200"
                  }`}
                >
                  <Settings className="w-5 h-5" />
                  <span>Settings</span>
                </button>
              </div>

              {/* End Interview / Leave */}
              <button
                onClick={() => setPhase("completed")}
                className="px-6 py-3 bg-red-600 hover:bg-red-700 text-white rounded-2xl text-sm font-bold flex items-center gap-2 shadow-md shadow-red-600/20 transition-all cursor-pointer"
              >
                <PhoneOff className="w-4 h-4" />
                <span>Leave Interview</span>
              </button>
            </div>
          </div>
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
