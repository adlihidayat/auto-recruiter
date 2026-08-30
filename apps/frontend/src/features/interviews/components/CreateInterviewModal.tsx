"use client";

import React, { useState, useRef, useEffect } from "react";
import { useRouter } from "next/navigation";
import {
  X,
  Plus,
  Trash2,
  ChevronDown,
  ChevronUp,
  CheckCircle2,
  Copy,
  Check,
  ExternalLink,
  Link as LinkIcon,
  Globe,
  Filter,
  Binoculars,
  PenTool,
  RotateCcw,
  ArrowRight,
} from "lucide-react";
import {
  CreateInterviewPayload,
  createInterviewApi,
  getCandidatesForInterviewApi,
  BackendCandidateResponse,
  BackendInterviewResponse,
} from "@/lib/api/client";

interface CreateInterviewModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCampaignCreated: () => void;
}

type ModalStep = "form" | "loading" | "success";

const AGENT_STEPS = [
  {
    name: "Context",
    role: "ANALYZER",
    color: "text-blue-500",
    bg: "bg-blue-100",
    badgeBg: "bg-blue-500",
    icon: <Filter className="w-5 h-5" />,
  },
  {
    name: "Research",
    role: "STRATEGIST",
    color: "text-purple-500",
    bg: "bg-purple-100",
    badgeBg: "bg-purple-500",
    icon: <Binoculars className="w-5 h-5" />,
  },
  {
    name: "Planning",
    role: "AGENT",
    color: "text-orange-500",
    bg: "bg-orange-100",
    badgeBg: "bg-orange-500",
    icon: <PenTool className="w-5 h-5" />,
  },
  {
    name: "Finished",
    role: "SYSTEM",
    color: "text-emerald-500",
    bg: "bg-emerald-100",
    badgeBg: "bg-emerald-500",
    icon: <CheckCircle2 className="w-5 h-5" />,
  },
];

const MOCK_LOGS = [
  // Agent 0: Context (0s - 5s)
  {
    time: 1200,
    dot: "bg-blue-400",
    text: "analyzing job description & requirements",
  },
  {
    time: 2800,
    dot: "bg-blue-400",
    text: "extracting key technical skills & domain keywords",
  },
  {
    time: 4500,
    dot: "bg-blue-500",
    text: (
      <>
        <span className="font-semibold text-gray-900">
          Context <ArrowRight className="w-3 h-3 inline -mt-0.5 mx-0.5" />{" "}
          Research
        </span>{" "}
        domain context attached
      </>
    ),
  },
  // Agent 1: Research (5s - 10s)
  {
    time: 6200,
    dot: "bg-purple-400",
    text: "benchmarking industry standards for seniority level",
  },
  {
    time: 7800,
    dot: "bg-purple-400",
    text: "identifying core evaluation metrics & interview depth",
  },
  {
    time: 9500,
    dot: "bg-purple-500",
    text: (
      <>
        <span className="font-semibold text-gray-900">
          Research <ArrowRight className="w-3 h-3 inline -mt-0.5 mx-0.5" />{" "}
          Planning
        </span>{" "}
        skill matrix compiled
      </>
    ),
  },
  // Agent 2: Planning (10s - 15s)
  {
    time: 11200,
    dot: "bg-orange-400",
    text: "formulating goal structure & scoring criteria",
  },
  {
    time: 12800,
    dot: "bg-orange-400",
    text: "configuring dynamic interviewer agent system prompt",
  },
  {
    time: 14500,
    dot: "bg-orange-500",
    text: (
      <>
        <span className="font-semibold text-gray-900">
          Planning <ArrowRight className="w-3 h-3 inline -mt-0.5 mx-0.5" />{" "}
          Finished
        </span>{" "}
        interview campaign plan locked
      </>
    ),
  },
  // Agent 3: Finished (15s - 20s)
  {
    time: 16200,
    dot: "bg-emerald-400",
    text: "provisioning LiveKit room infrastructure",
  },
  {
    time: 18000,
    dot: "bg-emerald-400",
    text: "generating candidate access tokens & invite links",
  },
  {
    time: 20000,
    dot: "bg-emerald-500",
    text: "recording final sign-off & deploying campaign",
  },
];

const EMOJIS = [
  "💼",
  "🚀",
  "💻",
  "🧠",
  "🔥",
  "🎯",
  "⭐",
  "🎨",
  "🛠️",
  "📈",
  "🌍",
  "⚡",
  "🤖",
  "📊",
  "🤝",
  "💡",
];

export default function CreateInterviewModal({
  isOpen,
  onClose,
  onCampaignCreated,
}: CreateInterviewModalProps) {
  const router = useRouter();
  const [modalStep, setModalStep] = useState<ModalStep>("form");
  const [loadingStepIndex, setLoadingStepIndex] = useState(0);
  const [loadingProgressPercent, setLoadingProgressPercent] = useState(0);
  const [isBackendDone, setIsBackendDone] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Agent Handoff Mock State
  const [isPaused, setIsPaused] = useState(false);
  const [elapsedTime, setElapsedTime] = useState(0);

  useEffect(() => {
    if (modalStep !== "loading" || isPaused || isBackendDone) return;
    const interval = setInterval(() => {
      setElapsedTime((prev) => {
        const next = prev + 100;
        if (next >= 20000) {
          setIsBackendDone(true);
          return 20000;
        }
        return next;
      });
    }, 100);
    return () => clearInterval(interval);
  }, [modalStep, isPaused, isBackendDone]);

  // Canvas Confetti Popper State & Effect
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    if (modalStep !== "success" || !canvasRef.current) return;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const width = (canvas.width = canvas.offsetWidth || 500);
    const height = (canvas.height = canvas.offsetHeight || 500);

    const colors = [
      "#FF5E62",
      "#FFD166",
      "#06D6A0",
      "#118AB2",
      "#8338EC",
      "#FF9F1C",
      "#E71D36",
    ];
    const particles = Array.from({ length: 65 }, () => ({
      x: width / 2 + (Math.random() - 0.5) * 80,
      y: height / 2 - 30 + (Math.random() - 0.5) * 40,
      vx: (Math.random() - 0.5) * 14,
      vy: Math.random() * -15 - 5,
      size: Math.random() * 8 + 4,
      color: colors[Math.floor(Math.random() * colors.length)],
      rotation: Math.random() * 360,
      rotationSpeed: (Math.random() - 0.5) * 12,
      shape: Math.random() > 0.4 ? "rect" : "circle",
    }));

    let animationFrameId: number;
    const startTime = performance.now();

    const render = (now: number) => {
      const elapsed = now - startTime;
      ctx.clearRect(0, 0, width, height);

      particles.forEach((p) => {
        p.x += p.vx;
        p.y += p.vy;
        p.vy += 0.38; // gravity
        p.vx *= 0.98; // air drag
        p.rotation += p.rotationSpeed;

        ctx.save();
        ctx.translate(p.x, p.y);
        ctx.rotate((p.rotation * Math.PI) / 180);
        ctx.fillStyle = p.color;

        if (p.shape === "rect") {
          ctx.fillRect(-p.size / 2, -p.size / 2, p.size, p.size * 1.5);
        } else {
          ctx.beginPath();
          ctx.arc(0, 0, p.size / 2, 0, Math.PI * 2);
          ctx.fill();
        }
        ctx.restore();
      });

      if (elapsed < 3500) {
        animationFrameId = requestAnimationFrame(render);
      }
    };

    animationFrameId = requestAnimationFrame(render);

    return () => {
      cancelAnimationFrame(animationFrameId);
    };
  }, [modalStep]);

  // Derived mock state
  const mockProgressPercent = Math.min(100, (elapsedTime / 20000) * 100);
  const activeAgentIndex = Math.min(3, Math.floor((elapsedTime / 20000) * 4));
  const visibleLogs = MOCK_LOGS.filter((log) => log.time <= elapsedTime);

  const [showEmojiPicker, setShowEmojiPicker] = useState(false);
  const emojiPickerRef = useRef<HTMLDivElement>(null);

  const [formData, setFormData] = useState({
    icon: "💼",
    job_name: "",
    job_description: "",
    difficulty: "mid",
    num_goals: 3,
    total_duration_minutes: 30,
    domain_hint: "",
    communication_weight: 0.2,
    scheduled_at: "",
  });

  const [candidates, setCandidates] = useState([
    {
      email: "alex.johnson@example.com",
      first_name: "Alex",
      last_name: "Johnson",
    },
    { email: "sarah.chen@example.com", first_name: "Sarah", last_name: "Chen" },
    {
      email: "michael.brown@example.com",
      first_name: "Michael",
      last_name: "Brown",
    },
  ]);

  const [createdInterview, setCreatedInterview] =
    useState<BackendInterviewResponse | null>(null);
  const [createdCandidates, setCreatedCandidates] = useState<
    BackendCandidateResponse[]
  >([]);

  const [copiedCandidateId, setCopiedCandidateId] = useState<string | null>(
    null,
  );

  // Close emoji picker when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        emojiPickerRef.current &&
        !emojiPickerRef.current.contains(event.target as Node)
      ) {
        setShowEmojiPicker(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const resetFormState = () => {
    setModalStep("form");
    setError(null);
    setLoadingStepIndex(0);
    setLoadingProgressPercent(0);
    setIsBackendDone(false);
    setCreatedInterview(null);
    setCreatedCandidates([]);
    setCopiedCandidateId(null);
    setFormData({
      icon: "💼",
      job_name: "",
      job_description: "",
      difficulty: "mid",
      num_goals: 3,
      total_duration_minutes: 30,
      domain_hint: "",
      communication_weight: 0.2,
      scheduled_at: "",
    });
    setCandidates([{ email: "", first_name: "", last_name: "" }]);
    setShowEmojiPicker(false);
  };

  const handleClose = () => {
    if (modalStep === "success") {
      onCampaignCreated();
    }
    resetFormState();
    onClose();
  };

  if (!isOpen) return null;

  const handleAddCandidate = () => {
    setCandidates([
      ...candidates,
      { email: "", first_name: "", last_name: "" },
    ]);
  };

  const handleRemoveCandidate = (index: number) => {
    setCandidates(candidates.filter((_, i) => i !== index));
  };

  const handleCandidateChange = (
    index: number,
    field: "email" | "first_name" | "last_name",
    value: string,
  ) => {
    const newCandidates = [...candidates];
    newCandidates[index][field] = value;
    setCandidates(newCandidates);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // Validation
    if (
      !formData.job_name ||
      !formData.job_description ||
      !formData.domain_hint
    ) {
      setError(
        "Please fill in all required fields (Job Name, Description, Domain Hint).",
      );
      return;
    }

    const validCandidates = candidates.filter((c) => c.email.trim() !== "");
    if (validCandidates.length === 0) {
      setError("At least one candidate with a valid email is required.");
      return;
    }

    // MOCK ACTIVATION
    setModalStep("loading");
    setElapsedTime(0);
    setIsPaused(false);
    setIsBackendDone(false);

    /* COMMENTED OUT BACKEND CALL
    try {
      setModalStep("loading");
      setLoadingStepIndex(0);
      setLoadingProgressPercent(0);
      setIsBackendDone(false);

      const rawToken = document.cookie
        .split("; ")
        .find((row) => row.startsWith("access_token="))
        ?.split("=")[1];
      const tokenCookie = rawToken ? decodeURIComponent(rawToken) : null;

      if (!tokenCookie) {
        throw new Error("You must be logged in to create an interview.");
      }

      const startTime = Date.now();
      const TOTAL_STEPS_TIME_MS = 30000;

      const progressTimer = setInterval(() => {
        const elapsed = Date.now() - startTime;
        const currentStep = Math.min(
          3,
          Math.floor((elapsed / TOTAL_STEPS_TIME_MS) * 4),
        );
        setLoadingStepIndex(currentStep);

        const targetPercent = Math.min(
          85,
          Math.floor((elapsed / TOTAL_STEPS_TIME_MS) * 85),
        );
        setLoadingProgressPercent(targetPercent);
      }, 250);

      const { icon: _, ...restFormData } = formData;
      const payload: CreateInterviewPayload = {
        ...restFormData,
        scheduled_at: restFormData.scheduled_at
          ? new Date(restFormData.scheduled_at).toISOString()
          : undefined,
        candidates: validCandidates,
      };

      const creationResult = await createInterviewApi(payload, tokenCookie);
      setCreatedInterview(creationResult.interview);

      let fetchedCandidates: BackendCandidateResponse[] =
        creationResult.candidates || [];

      if (fetchedCandidates.length === 0 && creationResult.interview?.id) {
        try {
          fetchedCandidates = await getCandidatesForInterviewApi(
            creationResult.interview.id,
            tokenCookie,
          );
        } catch (err) {
          console.warn("Failed to fetch created candidates:", err);
        }
      }

      clearInterval(progressTimer);
      setIsBackendDone(true);
      setLoadingStepIndex(4);
      setLoadingProgressPercent(100);

      setTimeout(() => {
        setCreatedCandidates(fetchedCandidates);
        setModalStep("success");
      }, 600);
    } catch (err: unknown) {
      setModalStep("form");
      setError(
        (err as Error).message ||
          "Failed to create interview. Please try again.",
      );
    }
    */
  };

  const handleCopyLink = (candidate: BackendCandidateResponse) => {
    const origin =
      typeof window !== "undefined"
        ? window.location.origin
        : "http://localhost:3000";
    const token = candidate.room_token || candidate.id;
    const roomUrl = `${origin}/interview?token=${token}`;

    navigator.clipboard.writeText(roomUrl);
    setCopiedCandidateId(candidate.id);
    setTimeout(() => {
      setCopiedCandidateId(null);
    }, 2000);
  };

  const handleDone = () => {
    handleClose();
  };

  const handleSeeDetail = () => {
    if (modalStep === "success") {
      onCampaignCreated();
    }
    resetFormState();
    onClose();
    const targetId = createdInterview?.id || "campaign-0";
    router.push(`/interviews/${targetId}`);
  };

  return (
    <div
      className={`fixed inset-0 z-50 flex items-center justify-center ${modalStep === "loading" && ""}`}
    >
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/40 backdrop-blur-sm transition-opacity"
        onClick={modalStep === "loading" ? undefined : handleClose}
      />
      <div className=" rounded-3xl overflow-hidden">
        {/* Modal Content Card */}
        <div
          className={`relative w-full max-h-[90vh] overflow-y-scroll bg-white rounded-3xl shadow-2xl ${modalStep === "form" && "p-8 max-w-xl "} ${modalStep === "loading" && "p-4"} ${modalStep === "success" && "p-8"} custom-scrollbar`}
        >
          {/* Close Button (Subtle) */}
          {modalStep !== "loading" && (
            <button
              onClick={handleClose}
              className="absolute top-6 right-6 p-2 text-gray-400 hover:text-gray-900 transition-colors rounded-full hover:bg-gray-100 cursor-pointer"
            >
              <X className="w-5 h-5" />
            </button>
          )}

          {/* STEP 1: FORM INPUTS */}
          {modalStep === "form" && (
            <>
              <div className="mb-4 pb-4 border-b border-gray-200 pr-8">
                <h2 className="text-base font-semibold text-gray-900 tracking-tight mb-0">
                  Create interview
                </h2>
                <p className="text-sm text-gray-500 font-medium">
                  Set up a new AI interview campaign and configure evaluation
                  goals.
                </p>
              </div>

              {error && (
                <div className="mb-6 p-4 rounded-xl bg-red-50 text-sm font-medium text-red-600 border border-red-100">
                  {error}
                </div>
              )}

              <form onSubmit={handleSubmit} className="space-y-6">
                <div className="flex gap-x-2.5">
                  {/* Interview Icon (Emoji Picker) */}
                  <div className=" relative group w-fit" ref={emojiPickerRef}>
                    <button
                      type="button"
                      onClick={() => setShowEmojiPicker(!showEmojiPicker)}
                      className=" absolute hidden z-10 group-hover:flex text-center font-semibold text-xs items-center justify-center w-full h-full bg-black/40 text-white rounded-lg transition-all ease-in-out duration-600"
                    >
                      change icon
                    </button>
                    <div className="w-16 h-16 flex items-center justify-center text-4xl cursor-pointer bg-gray-100 rounded-lg">
                      <span className=" -translate-y-1 z-0">
                        {formData.icon}
                      </span>
                    </div>
                    {showEmojiPicker && (
                      <div className="absolute left-0 top-full mt-2 w-52 bg-white border border-gray-200 rounded-2xl shadow-md p-2 z-50">
                        <div className=" mb-2 flex justify-between items-center px-2 pt-2">
                          <span className=" text-xs  font-semibold">
                            Interview Icon
                          </span>
                          <button
                            type="button"
                            onClick={() => setShowEmojiPicker(false)}
                            className=" text-gray-600 hover:text-gray-900 transition-colors rounded-full hover:bg-gray-100 cursor-pointer"
                          >
                            <X className="w-4 h-4" />
                          </button>
                        </div>
                        <div className=" grid grid-cols-4 gap-1 animate-in fade-in zoom-in-95 duration-150">
                          {EMOJIS.map((e) => (
                            <button
                              key={e}
                              type="button"
                              onClick={() => {
                                setFormData({ ...formData, icon: e });
                                setShowEmojiPicker(false);
                              }}
                              className="w-11 h-11 flex items-center justify-center text-2xl hover:bg-gray-200 rounded-xl transition-colors cursor-pointer"
                            >
                              {e}
                            </button>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Job Name */}
                  <div className="flex-1">
                    <label className="block text-sm font-medium text-gray-900 mb-2">
                      Job Name
                    </label>
                    <input
                      type="text"
                      value={formData.job_name}
                      onChange={(e) =>
                        setFormData({ ...formData, job_name: e.target.value })
                      }
                      className="w-full px-3 py-1.5 bg-white border border-gray-200 rounded-lg text-sm text-gray-900 font-medium placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-900/10 focus:border-gray-900 transition-all"
                      placeholder="e.g. Senior Frontend Engineer"
                    />
                  </div>
                </div>

                {/* Job Description */}
                <div>
                  <label className="block text-sm font-medium text-gray-900 mb-2">
                    Job Description
                  </label>
                  <textarea
                    value={formData.job_description}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        job_description: e.target.value,
                      })
                    }
                    className="w-full h-28 px-3 py-1.5 bg-white border border-gray-200 rounded-xl text-sm text-gray-900 font-medium placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-900/10 focus:border-gray-900 transition-all resize-none"
                    placeholder="Paste the job description here..."
                  />
                </div>

                <div className="grid grid-cols-2 gap-2.5">
                  {/* Scheduled Date */}
                  <div>
                    <label className="block text-sm font-medium text-gray-900 mb-2">
                      Scheduled (Optional)
                    </label>
                    <input
                      type="datetime-local"
                      value={formData.scheduled_at}
                      onChange={(e) =>
                        setFormData({
                          ...formData,
                          scheduled_at: e.target.value,
                        })
                      }
                      className="w-full px-3 py-1.5 bg-white border border-gray-200 rounded-lg text-sm text-gray-900 font-medium focus:outline-none focus:ring-2 focus:ring-gray-900/10 focus:border-gray-900 transition-all"
                    />
                  </div>

                  {/* Domain Hint */}
                  <div>
                    <label className="block text-sm font-medium text-gray-900 mb-2">
                      Domain Hint
                    </label>
                    <div className="relative flex items-center">
                      <div className="absolute left-3 text-gray-900 pointer-events-none">
                        <Globe className="w-3.5 h-3.5" />
                      </div>
                      <input
                        type="text"
                        value={formData.domain_hint}
                        onChange={(e) =>
                          setFormData({
                            ...formData,
                            domain_hint: e.target.value,
                          })
                        }
                        className="w-full pl-8.5 px-3 py-1.5 bg-white border border-gray-200 rounded-lg text-sm text-gray-900 font-medium placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-900/10 focus:border-gray-900 transition-all"
                        placeholder="e.g. React & TypeScript"
                      />
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-2.5">
                  {/* Total Duration */}
                  <div>
                    <label className="block text-sm font-medium text-gray-900 mb-2">
                      Duration (Minutes)
                    </label>
                    <div className="relative">
                      <input
                        type="number"
                        min="5"
                        max="120"
                        step="5"
                        value={formData.total_duration_minutes}
                        onChange={(e) =>
                          setFormData({
                            ...formData,
                            total_duration_minutes:
                              parseInt(e.target.value) || 5,
                          })
                        }
                        className="w-full px-3 py-1.5 pr-8 bg-white border border-gray-200 rounded-lg text-sm text-gray-900 font-medium placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-900/10 focus:border-gray-900 transition-all [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
                      />
                      <div className="absolute right-2.5 top-1/2 -translate-y-1/2 flex flex-col items-center justify-center text-gray-400 pointer-events-auto">
                        <button
                          type="button"
                          onClick={() =>
                            setFormData((prev) => ({
                              ...prev,
                              total_duration_minutes: Math.min(
                                120,
                                (prev.total_duration_minutes || 0) + 5,
                              ),
                            }))
                          }
                          className="hover:text-gray-900 transition-colors cursor-pointer leading-none"
                        >
                          <ChevronUp className="w-3 h-3" />
                        </button>
                        <button
                          type="button"
                          onClick={() =>
                            setFormData((prev) => ({
                              ...prev,
                              total_duration_minutes: Math.max(
                                5,
                                (prev.total_duration_minutes || 5) - 5,
                              ),
                            }))
                          }
                          className="hover:text-gray-900 transition-colors cursor-pointer leading-none"
                        >
                          <ChevronDown className="w-3 h-3" />
                        </button>
                      </div>
                    </div>
                  </div>

                  {/* Difficulty */}
                  <div>
                    <label className="block text-sm font-medium text-gray-900 mb-2">
                      Seniority / Difficulty
                    </label>
                    <div className="relative">
                      <select
                        value={formData.difficulty}
                        onChange={(e) =>
                          setFormData({
                            ...formData,
                            difficulty: e.target.value,
                          })
                        }
                        className="w-full px-3 py-1.5 bg-white border border-gray-200 rounded-lg text-sm text-gray-900 font-medium focus:outline-none focus:ring-2 focus:ring-gray-900/10 focus:border-gray-900 transition-all appearance-none cursor-pointer"
                      >
                        <option value="junior">Junior</option>
                        <option value="mid">Mid-Level</option>
                        <option value="senior">Senior</option>
                      </select>
                      <ChevronDown className="w-4 h-4 text-gray-500 absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none" />
                    </div>
                  </div>

                  {/* Number of Goals */}
                  <div>
                    <label className="block text-sm font-medium text-gray-900 mb-2">
                      Goals Count
                    </label>
                    <div className="relative">
                      <input
                        type="number"
                        min="1"
                        max="10"
                        value={formData.num_goals}
                        onChange={(e) =>
                          setFormData({
                            ...formData,
                            num_goals: parseInt(e.target.value) || 1,
                          })
                        }
                        className="w-full px-3 py-1.5 pr-8 bg-white border border-gray-200 rounded-lg text-sm text-gray-900 font-medium placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-900/10 focus:border-gray-900 transition-all [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
                      />
                      <div className="absolute right-2.5 top-1/2 -translate-y-1/2 flex flex-col items-center justify-center text-gray-400 pointer-events-auto">
                        <button
                          type="button"
                          onClick={() =>
                            setFormData((prev) => ({
                              ...prev,
                              num_goals: Math.min(
                                10,
                                (prev.num_goals || 0) + 1,
                              ),
                            }))
                          }
                          className="hover:text-gray-900 transition-colors cursor-pointer leading-none"
                        >
                          <ChevronUp className="w-3 h-3" />
                        </button>
                        <button
                          type="button"
                          onClick={() =>
                            setFormData((prev) => ({
                              ...prev,
                              num_goals: Math.max(1, (prev.num_goals || 1) - 1),
                            }))
                          }
                          className="hover:text-gray-900 transition-colors cursor-pointer leading-none"
                        >
                          <ChevronDown className="w-3 h-3" />
                        </button>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Communication Weight Slider */}
                <div className="">
                  <div className="flex items-center justify-between mb-2">
                    <label className="block text-sm font-medium text-gray-900">
                      Communication vs Knowledge
                    </label>
                    <span className="text-xs font-medium text-[#191919] bg-gray-100 px-1 py-0.5 rounded-md">
                      {Math.round(formData.communication_weight * 100)}%
                    </span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.01"
                    value={formData.communication_weight}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        communication_weight: parseFloat(e.target.value),
                      })
                    }
                    style={{
                      background: `linear-gradient(to right, #F97316 0%, #F97316 ${
                        formData.communication_weight * 100
                      }%, #E5E7EB ${
                        formData.communication_weight * 100
                      }%, #E5E7EB 100%)`,
                    }}
                    className="w-full h-1 rounded-full appearance-none cursor-pointer accent-[#191919]"
                  />
                  <div className="flex items-center justify-between mt-1 text-xs font-semibold text-gray-500">
                    <span>Knowledge Focus</span>
                    <span>Communication Focus</span>
                  </div>
                </div>

                {/* Candidates Section */}
                <div className="">
                  <div className="flex items-center justify-between mb-4">
                    <label className="block text-sm font-medium text-gray-900">
                      Candidates <span className="text-red-500">*</span>
                    </label>
                    <button
                      type="button"
                      onClick={handleAddCandidate}
                      className="px-3 py-1.5 bg-gray-100 hover:bg-gray-200 text-gray-900 rounded-lg text-xs font-bold flex items-center gap-1.5 transition-colors cursor-pointer"
                    >
                      <Plus className="w-3.5 h-3.5" /> Add Candidate
                    </button>
                  </div>

                  <div className="space-y-2.5">
                    {candidates.map((candidate, index) => (
                      <div
                        key={index}
                        className="flex items-start gap-3 relative group"
                      >
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-2.5 w-full">
                          <input
                            type="email"
                            placeholder="Email address"
                            value={candidate.email}
                            onChange={(e) =>
                              handleCandidateChange(
                                index,
                                "email",
                                e.target.value,
                              )
                            }
                            className="w-full px-3 py-1.5 bg-white border border-gray-200 rounded-lg text-sm text-gray-900 font-medium placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-900/10 focus:border-gray-900 transition-all"
                            required
                          />
                          <input
                            type="text"
                            placeholder="First name"
                            value={candidate.first_name}
                            onChange={(e) =>
                              handleCandidateChange(
                                index,
                                "first_name",
                                e.target.value,
                              )
                            }
                            className="w-full px-3 py-1.5 bg-white border border-gray-200 rounded-lg text-sm text-gray-900 font-medium placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-900/10 focus:border-gray-900 transition-all"
                          />
                          <input
                            type="text"
                            placeholder="Last name"
                            value={candidate.last_name}
                            onChange={(e) =>
                              handleCandidateChange(
                                index,
                                "last_name",
                                e.target.value,
                              )
                            }
                            className="w-full px-3 py-1.5 bg-white border border-gray-200 rounded-lg text-sm text-gray-900 font-medium placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-900/10 focus:border-gray-900 transition-all"
                          />
                        </div>
                        {candidates.length > 1 && (
                          <button
                            type="button"
                            onClick={() => handleRemoveCandidate(index)}
                            className="w-8.5 h-8.5 bg-red-500 border border-gray-200 rounded-lg flex items-center justify-center text-white hover:text-red-100 hover:border-red-200 hover:bg-red-700 transition-all cursor-pointer shrink-0"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        )}
                      </div>
                    ))}
                  </div>
                </div>

                <div className="">
                  <p className="text-[13px] text-gray-500 font-medium mb-8 leading-relaxed">
                    The candidates will receive LiveKit voice access tokens.
                    Make sure the difficulty and duration accurately reflect
                    your expectations for this role.
                  </p>

                  <button
                    type="submit"
                    className="w-full bg-[#191919] text-sm hover:bg-black text-white rounded-xl py-2.5 text-base font-medium transition-all shadow-lg shadow-black/10 cursor-pointer flex items-center justify-center"
                  >
                    Continue
                  </button>
                </div>
              </form>
            </>
          )}

          {/* STEP 2: LOADING / AI GENERATION SEQUENCE (AGENT HANDOFF) */}
          {modalStep === "loading" && (
            <div className="animate-in fade-in zoom-in-95 duration-200 w-130 h-full">
              <div className="bg-white rounded-[2rem] w-full">
                {/* Header */}
                <div className="flex justify-between items-center mb-6 px-4 pt-2">
                  <div className="flex items-center gap-3">
                    <h2 className="text-base font-semibold text-gray-900">
                      Creating interview Plan
                    </h2>
                    <span className="bg-gray-100 text-gray-600 px-2 py-1 rounded-md text-xs font-semibold">
                      4 agents
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono text-gray-500">
                      {(elapsedTime / 1000).toFixed(1)}s
                    </span>
                    <div
                      className={`w-2.5 h-2.5 rounded-full bg-emerald-500 ${
                        isPaused || isBackendDone ? "" : "animate-pulse"
                      }`}
                    />
                  </div>
                </div>

                <div className=" bg-[#f4f4f581] pt-4 pb-6 rounded-xl">
                  {/* Task Row */}
                  <div className="flex items-center justify-between border-b border-dashed border-gray-200 pb-5 mb-6 px-4">
                    <div className="flex items-center gap-1">
                      <span className="text-xs font-semibold text-gray-600 tracking-wider">
                        Task :
                      </span>
                      <span className="text-xs font-medium text-gray-800">
                        {formData.job_description.substring(0, 50) ||
                          "Analyze and create interview plan"}
                        {formData.job_description.length > 50 ? "..." : ""}
                      </span>
                    </div>
                    <span className="text-xs font-mono text-gray-600">
                      #12f157dds{/* interview_id */}
                    </span>
                  </div>

                  {/* Agents Progress */}
                  <div className="relative">
                    <div className="flex justify-between relative z-10 px-2 sm:px-6">
                      {AGENT_STEPS.map((step, idx) => {
                        const isActive =
                          activeAgentIndex === idx && !isBackendDone;
                        const isPast = activeAgentIndex > idx || isBackendDone;
                        return (
                          <div
                            key={idx}
                            className="flex flex-col items-center gap-3 "
                          >
                            <div
                              className={`relative w-12 h-12 rounded-2xl flex items-center justify-center transition-colors duration-500 ${
                                isPast || isActive
                                  ? `${step.bg + " " + step.color} border border-[${step.color}]`
                                  : "bg-white text-gray-400"
                              }`}
                            >
                              {step.icon}
                              {isPast && (
                                <div
                                  className={`absolute -top-1.5 -right-1.5 w-5 h-5 rounded-full border-[3px] border-[#f9fafb] flex items-center justify-center ${step.badgeBg}`}
                                >
                                  <Check
                                    className="w-3 h-3 text-white"
                                    strokeWidth={3}
                                  />
                                </div>
                              )}
                            </div>
                            <div className="text-center">
                              <div
                                className={`text-sm font-medium ${
                                  isActive ? "text-gray-900" : "text-gray-600"
                                }`}
                              >
                                {step.name}
                              </div>
                              <div className="text-[10px] font-medium text-gray-600  mt-0.5">
                                {step.role}
                              </div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                    {/* Progress bar line */}
                    <div className="absolute top-6 left-10 right-10 -z-0">
                      <div className="w-full relative h-1 bg-gray-200 rounded-full">
                        <div
                          className="absolute top-0 left-0 h-0.5 bg-gradient-to-r from-blue-700 via-purple-700 to-orange-700 rounded-full transition-all duration-300 ease-linear"
                          style={{ width: `${mockProgressPercent}%` }}
                        />
                        <div
                          className="absolute top-1/2 -translate-y-1/2 w-3.5 h-3.5 bg-orange-400 rounded-full shadow-sm transition-all duration-300 ease-linear"
                          style={{
                            left: `calc(${mockProgressPercent}% - 8px)`,
                            display: mockProgressPercent > 0 ? "block" : "none",
                          }}
                        />
                      </div>
                    </div>
                  </div>
                </div>

                {/* HANDOFF LOG */}
                <div className=" px-4">
                  <div className="flex justify-between items-center py-3">
                    <span className="text-sm font-medium text-gray-600 tracking-wider ">
                      Agent Log
                    </span>
                    <span className="text-xs font-mono text-gray-400">
                      {visibleLogs.length} / {MOCK_LOGS.length}
                    </span>
                  </div>

                  <div className="space-y-3 h-44 overflow-y-auto custom-scrollbar pr-2 flex flex-col justify-end bg-amber-40">
                    {visibleLogs.map((log, i) => (
                      <div
                        key={i}
                        className="flex items-start gap-5 animate-in fade-in slide-in-from-bottom-2 duration-300"
                      >
                        <span className="text-[13px] font-mono text-gray-600 w-12 shrink-0">
                          {(log.time / 1000).toFixed(1)}s
                        </span>
                        <div className="flex items-center gap-3 mt-1.5 shrink-0">
                          <div className={`w-2 h-2 rounded-full ${log.dot}`} />
                        </div>
                        <div className="text-sm text-gray-600 leading-snug">
                          {log.text}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Bottom Actions */}
                <div className="pt-3 mt-3 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 px-4 border-t border-gray-200">
                  <div className="flex items-center gap-1">
                    <span
                      className={`text-sm font-medium ${
                        isBackendDone ? "text-emerald-600" : "text-gray-900"
                      }`}
                    >
                      {isBackendDone
                        ? "Success"
                        : AGENT_STEPS[activeAgentIndex].name}
                      {"  "}·
                    </span>
                    <span className="text-xs text-gray-500">
                      {isBackendDone ? "mock complete" : "running processes"}
                    </span>
                  </div>
                  <div className="flex items-center gap-2 w-full sm:w-auto">
                    <button
                      onClick={() => {
                        setElapsedTime(0);
                        setIsBackendDone(false);
                        setIsPaused(false);
                      }}
                      className="px-3 py-1.5 border border-gray-200 text-gray-700 rounded-md text-sm font-medium hover:bg-gray-300 transition-colors flex-1 sm:flex-none cursor-pointer"
                    >
                      Cancel
                    </button>
                    {/* <button
                      onClick={() => setIsPaused(!isPaused)}
                      className="px-3 py-1 bg-gray-200/80 text-gray-700 rounded-md text-sm font-medium flex items-center justify-center gap-2 hover:bg-gray-300 transition-colors flex-1 sm:flex-none cursor-pointer"
                    >
                      {isPaused ? (
                        <Play className="w-4 h-4" />
                      ) : (
                        <Pause className="w-4 h-4" />
                      )}
                      {isPaused ? "Resume" : "Pause"}
                    </button> */}
                    <button
                      onClick={() => {
                        if (isBackendDone) {
                          setModalStep("success");
                        } else {
                          setElapsedTime(0);
                          setIsBackendDone(false);
                          setIsPaused(false);
                        }
                      }}
                      className="px-3 py-1.5 bg-[#191919] text-white rounded-md text-sm font-medium flex items-center justify-center gap-2 hover:bg-black transition-colors flex-1 sm:flex-none cursor-pointer"
                    >
                      {isBackendDone ? (
                        <>
                          Continue <ArrowRight className="w-4 h-4" />
                        </>
                      ) : (
                        <>
                          <RotateCcw className="w-4 h-4" /> Restart
                        </>
                      )}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* STEP 3: SUCCESS STATE & LIVEKIT ROOM TOKENS */}
          {modalStep === "success" &&
            (() => {
              const displayCandidates =
                createdCandidates.length > 0
                  ? createdCandidates
                  : candidates.map((c, i) => ({
                      id: `cand-${i}`,
                      first_name:
                        c.first_name ||
                        (i === 0 ? "Alex" : i === 1 ? "Sarah" : "Michael"),
                      last_name:
                        c.last_name ||
                        (i === 0 ? "Johnson" : i === 1 ? "Chen" : "Brown"),
                      email:
                        c.email ||
                        (i === 0
                          ? "alex.johnson@example.com"
                          : i === 1
                            ? "sarah.chen@example.com"
                            : "michael.brown@example.com"),
                      room_token: `mock_room_token_${i + 1}`,
                    }));

              return (
                <div className="relative space-y-4 animate-in fade-in zoom-in-95 duration-200 w-130">
                  {/* Canvas Confetti Popper Overlay */}
                  <canvas
                    ref={canvasRef}
                    className="pointer-events-none absolute inset-0 -z-0 w-full h-full overflow-hidden"
                  />

                  {/* Featured Hero Banner Card (Twin Screenshot Style + Golden Rosette Award Badge) */}
                  <div className=" relative rounded-3xl p-6 relative overflow-hidden flex justify-center gap-6 pt-14 pb-28">
                    <div className=" absolute bottom-2.5 text-center">
                      <h2 className="text-xl font-semibold text-gray-900 tracking-tight">
                        Interview Created
                      </h2>
                      <p className="text-xs text-gray-500 font-medium mt-1">
                        Candidates can now access LiveKit AI voice interview
                        rooms.
                      </p>
                    </div>
                    {/*Golden Star Rosette Award Ribbon Medal (Matching Image 1 Reference) */}
                    <div className="relative w-36 h-36 flex items-center justify-center shrink-0 overflow-visible self-center group scale-[1.60] transform origin-center">
                      {/* Radial Pink Burst Lines (Matching Image 1 burst rays) */}
                      <svg
                        className="absolute w-32 h-32 text-rose-400/80 animate-pulse pointer-events-none"
                        viewBox="0 0 100 100"
                      >
                        <line
                          x1="15"
                          y1="15"
                          x2="26"
                          y2="26"
                          stroke="currentColor"
                          strokeWidth="2.5"
                          strokeLinecap="round"
                        />
                        <line
                          x1="85"
                          y1="15"
                          x2="74"
                          y2="26"
                          stroke="currentColor"
                          strokeWidth="2.5"
                          strokeLinecap="round"
                        />
                        <line
                          x1="10"
                          y1="50"
                          x2="22"
                          y2="50"
                          stroke="currentColor"
                          strokeWidth="2.5"
                          strokeLinecap="round"
                        />
                        <line
                          x1="90"
                          y1="50"
                          x2="78"
                          y2="50"
                          stroke="currentColor"
                          strokeWidth="2.5"
                          strokeLinecap="round"
                        />
                        <line
                          x1="18"
                          y1="85"
                          x2="28"
                          y2="74"
                          stroke="currentColor"
                          strokeWidth="2.5"
                          strokeLinecap="round"
                        />
                        <line
                          x1="82"
                          y1="85"
                          x2="72"
                          y2="74"
                          stroke="currentColor"
                          strokeWidth="2.5"
                          strokeLinecap="round"
                        />
                        <line
                          x1="50"
                          y1="8"
                          x2="50"
                          y2="20"
                          stroke="currentColor"
                          strokeWidth="2.5"
                          strokeLinecap="round"
                        />
                      </svg>

                      {/* Floating Geometric Confetti (Image 1: squares, triangles, circles, stars) */}
                      <div className="absolute inset-0 pointer-events-none">
                        <div className="absolute top-1 left-2 w-2.5 h-2.5 bg-pink-400 rotate-12 animate-bounce" />
                        <div className="absolute top-2 left-8 text-rose-500 font-extrabold text-xs animate-pulse">
                          +
                        </div>
                        <div className="absolute top-5 right-2 w-0 h-0 border-l-[5px] border-l-transparent border-r-[5px] border-r-transparent border-b-[8px] border-b-purple-500 rotate-45 animate-pulse" />
                        <div className="absolute bottom-2 left-3 w-2.5 h-2.5 rounded-full border-2 border-orange-400 animate-ping opacity-75" />
                        <div className="absolute bottom-1 right-6 w-2.5 h-2.5 bg-amber-400 -rotate-12 animate-bounce" />
                        <div className="absolute bottom-8 right-1 w-2 h-2 rounded-full bg-indigo-400 animate-pulse" />
                      </div>

                      {/* Golden Award Medal Rosette */}
                      <div className="relative z-10 flex flex-col items-center justify-center transition-transform duration-500 ease-out group-hover:scale-105">
                        <div className="relative w-24 h-24 flex items-center justify-center">
                          {/* Purple Ribbon Tails hanging down */}
                          <div className="absolute bottom-[-10px] left-3 w-7 h-10 bg-purple-600 rounded-b-md transform -rotate-15 shadow-sm overflow-hidden">
                            <div className="w-full h-full bg-gradient-to-b from-purple-500 to-indigo-700" />
                          </div>
                          <div className="absolute bottom-[-10px] right-3 w-7 h-10 bg-purple-600 rounded-b-md transform rotate-15 shadow-sm overflow-hidden">
                            <div className="w-full h-full bg-gradient-to-b from-purple-500 to-indigo-700" />
                          </div>

                          {/* Outer Scalloped Golden Badge */}
                          <div className="w-20 h-20 rounded-full bg-gradient-to-tr from-amber-500 via-yellow-400 to-amber-300 border-4 border-amber-200 shadow-md flex items-center justify-center relative">
                            {/* Inner Golden Circle with Central Star */}
                            <div className="w-14 h-14 rounded-full bg-gradient-to-tr from-amber-300 to-yellow-200 border-2 border-amber-400 flex items-center justify-center shadow-inner">
                              <svg
                                className="w-8 h-8 text-amber-600 drop-shadow-xs"
                                fill="currentColor"
                                viewBox="0 0 24 24"
                              >
                                <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
                              </svg>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Candidate Share Section */}
                  <div className="space-y-3">
                    <div className="flex items-center justify-between px-1">
                      <span className="text-sm font-semibold text-gray-900">
                        Share candidate links
                      </span>
                      {/* Toggle Switch */}
                      <div className="w-10 h-6 bg-[#0080FF] rounded-full p-1 flex items-center justify-end cursor-pointer shadow-inner">
                        <div className="w-4 h-4 bg-white rounded-full shadow-md" />
                      </div>
                    </div>

                    {/* 3 Candidates list matching interview detail style */}
                    <div className="rounded-2xl overflow-hidden border border-gray-200">
                      <div className=" max-h-[190px] overflow-y-scroll custom-scrollbar ">
                        {displayCandidates.map((cItem, idx) => {
                          const c = cItem as Record<string, string | undefined>;
                          const candidateName =
                            c.first_name || c.last_name
                              ? `${c.first_name || ""} ${c.last_name || ""}`.trim()
                              : `Candidate ${idx + 1}`;

                          const tokenValue =
                            c.room_token || c.id || `token_${idx}`;
                          const origin =
                            typeof window !== "undefined"
                              ? window.location.origin
                              : "http://localhost:3000";
                          const roomUrl = `${origin}/interview?token=${tokenValue}`;
                          const candidateId = c.id || `cand-${idx}`;
                          const isCopied = copiedCandidateId === candidateId;

                          return (
                            <div
                              key={candidateId}
                              className="bg-white border-b border-gray-200 px-3.5 py-2.5 flex items-center justify-between gap-3  hover:border-gray-300 transition-colors"
                            >
                              <div className="flex items-center gap-2.5 min-w-0 flex-1">
                                <div className="w-6 h-6 rounded-full bg-gray-200 flex items-center justify-center flex-shrink-0 text-black text-sm font-medium uppercase">
                                  {candidateName.charAt(0)}
                                </div>
                                <div className="flex items-center gap-2 truncate">
                                  <span className="text-xs font-medium text-gray-900 truncate">
                                    {candidateName}
                                  </span>
                                  {/* <span className="text-xs text-gray-400 font-mono truncate hidden sm:inline">
                                    {c.email}
                                  </span> */}
                                </div>
                              </div>

                              <div className="flex items-center gap-2 shrink-0">
                                <div className="bg-gray-50 border border-gray-200 rounded-md px-2.5 py-1 flex items-center gap-2 max-w-[160px] overflow-hidden">
                                  <LinkIcon className="w-3 h-3 text-gray-400 shrink-0" />
                                  <input
                                    type="text"
                                    readOnly
                                    value={roomUrl}
                                    className="w-full bg-transparent text-[11px] font-mono text-gray-700 focus:outline-none truncate"
                                  />
                                </div>

                                <button
                                  type="button"
                                  onClick={() => {
                                    navigator.clipboard.writeText(roomUrl);
                                    setCopiedCandidateId(candidateId);
                                    setTimeout(
                                      () => setCopiedCandidateId(null),
                                      2000,
                                    );
                                  }}
                                  className={`px-3 py-1 rounded-md text-sm font-medium flex items-center gap-1 transition-all cursor-pointer shrink-0 ${
                                    isCopied
                                      ? "bg-[#191919] text-white shadow-xs"
                                      : "bg-white hover:bg-gray-100 text-gray-700 border border-gray-200"
                                  }`}
                                >
                                  {isCopied ? (
                                    <>
                                      <Check className="w-3 h-3" />
                                      <span>Copied</span>
                                    </>
                                  ) : (
                                    <>
                                      <Copy className="w-3 h-3 text-gray-600" />
                                      <span>Copy</span>
                                    </>
                                  )}
                                </button>

                                <a
                                  href={roomUrl}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="p-1 hover:bg-gray-100 text-gray-500 rounded transition-colors shrink-0"
                                  title="Open Room"
                                >
                                  <ExternalLink className="w-3.5 h-3.5" />
                                </a>
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  </div>

                  {/* Bottom Dual Action Buttons (Side-by-side matching Twin screenshot) */}
                  <div className=" flex items-center gap-3">
                    <button
                      type="button"
                      onClick={handleSeeDetail}
                      className="px-3 py-1.5 flex-1 bg-[white border border-gray-200 hover:bg-gray-200 text-gray-900 text-sm font-medium rounded-md transition-colors cursor-pointer flex items-center justify-center gap-1.5"
                    >
                      <span>See detail</span>
                      <ExternalLink className="w-4 h-4 text-gray-600" />
                    </button>
                    <button
                      type="button"
                      onClick={handleDone}
                      className="px-3 py-1.5 flex-1 bg-[#191919] hover:bg-black text-white text-sm font-medium rounded-md transition-colors cursor-pointer flex items-center justify-center"
                    >
                      Done
                    </button>
                  </div>
                </div>
              );
            })()}
        </div>
      </div>

      {/* Custom Scrollbar Styles for the modal content */}
      <style
        dangerouslySetInnerHTML={{
          __html: `
        .custom-scrollbar::-webkit-scrollbar {
          width: 6px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: transparent;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background-color: #E9E9E9;
          border-radius: 20px;
        }
      `,
        }}
      />
    </div>
  );
}
