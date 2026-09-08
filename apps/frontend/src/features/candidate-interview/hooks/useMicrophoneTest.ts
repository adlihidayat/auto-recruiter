/**
 * What: Custom React hook for pre-interview microphone testing and device enumeration.
 * Why: Encapsulates Web Audio API Analyser, MediaStream lifecycle, and live audio volume level calculation.
 * Boundaries: Does not handle LiveKit room connection or WebSocket streaming.
 */

import { useState, useEffect, useRef, useCallback } from "react";

export interface UseMicrophoneTestReturn {
  isMuted: boolean;
  setIsMuted: React.Dispatch<React.SetStateAction<boolean>>;
  audioInputs: MediaDeviceInfo[];
  selectedInput: string;
  setSelectedInput: React.Dispatch<React.SetStateAction<string>>;
  selectedOutput: string;
  setSelectedOutput: React.Dispatch<React.SetStateAction<string>>;
  realAudioLevel: number;
  hasMicPermission: boolean;
  activeMicLabel: string;
  initMicrophone: (deviceId?: string) => Promise<void>;
  releaseMicrophoneResources: () => void;
}

export function useMicrophoneTest(): UseMicrophoneTestReturn {
  const [isMuted, setIsMuted] = useState<boolean>(false);
  const [audioInputs, setAudioInputs] = useState<MediaDeviceInfo[]>([]);
  const [selectedInput, setSelectedInput] = useState<string>("");
  const [selectedOutput, setSelectedOutput] = useState<string>("");
  const [realAudioLevel, setRealAudioLevel] = useState<number>(0);
  const [hasMicPermission, setHasMicPermission] = useState<boolean>(false);
  const [activeMicLabel, setActiveMicLabel] = useState<string>("");

  const streamRef = useRef<MediaStream | null>(null);
  const audioCtxRef = useRef<AudioContext | null>(null);
  const animFrameRef = useRef<number | null>(null);

  const releaseMicrophoneResources = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
    if (audioCtxRef.current) {
      audioCtxRef.current.close();
      audioCtxRef.current = null;
    }
    if (animFrameRef.current) {
      cancelAnimationFrame(animFrameRef.current);
      animFrameRef.current = null;
    }
  }, []);

  const initMicrophone = useCallback(
    async (deviceId?: string) => {
      try {
        releaseMicrophoneResources();

        const constraints: MediaStreamConstraints = {
          audio: deviceId ? { deviceId: { exact: deviceId } } : true,
        };

        const stream = await navigator.mediaDevices.getUserMedia(constraints);
        streamRef.current = stream;
        setHasMicPermission(true);

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

        const devices = await navigator.mediaDevices.enumerateDevices();
        const inputs = devices.filter((d) => d.kind === "audioinput");
        const outputs = devices.filter((d) => d.kind === "audiooutput");
        setAudioInputs(inputs);

        if (!selectedOutput && outputs.length > 0) {
          setSelectedOutput(outputs[0].deviceId);
        }

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
    [selectedOutput, releaseMicrophoneResources],
  );

  useEffect(() => {
    if (streamRef.current) {
      streamRef.current.getAudioTracks().forEach((track) => {
        track.enabled = !isMuted;
      });
    }
  }, [isMuted]);

  useEffect(() => {
    return () => {
      releaseMicrophoneResources();
    };
  }, [releaseMicrophoneResources]);

  useEffect(() => {
    const startAudio = async () => {
      await initMicrophone();
    };
    startAudio();
  }, [initMicrophone]);

  return {
    isMuted,
    setIsMuted,
    audioInputs,
    selectedInput,
    setSelectedInput,
    selectedOutput,
    setSelectedOutput,
    realAudioLevel,
    hasMicPermission,
    activeMicLabel,
    initMicrophone,
    releaseMicrophoneResources,
  };
}
