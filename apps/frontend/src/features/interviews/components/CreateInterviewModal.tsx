"use client";

import React, { useState } from "react";
import {
  X,
  Plus,
  Trash2,
  Loader2,
  ChevronDown,
  Sparkles,
  CheckCircle2,
  Copy,
  Check,
  ExternalLink,
  User,
  Link as LinkIcon,
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

const AI_PROGRESS_STEPS = [
  "Analyzing Job Description & Domain Context...",
  "Extracting Core Requirements & Evaluation Goals...",
  "Configuring AI Agent & Generating Interview Plan...",
  "Generating Candidate LiveKit Access Tokens...",
];

export default function CreateInterviewModal({
  isOpen,
  onClose,
  onCampaignCreated,
}: CreateInterviewModalProps) {
  const [modalStep, setModalStep] = useState<ModalStep>("form");
  const [loadingStepIndex, setLoadingStepIndex] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const [formData, setFormData] = useState({
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
    { email: "", first_name: "", last_name: "" },
  ]);

  const [createdInterview, setCreatedInterview] =
    useState<BackendInterviewResponse | null>(null);
  const [createdCandidates, setCreatedCandidates] = useState<
    BackendCandidateResponse[]
  >([]);

  const [copiedCandidateId, setCopiedCandidateId] = useState<string | null>(
    null
  );

  const resetFormState = () => {
    setModalStep("form");
    setError(null);
    setLoadingStepIndex(0);
    setCreatedInterview(null);
    setCreatedCandidates([]);
    setCopiedCandidateId(null);
    setFormData({
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
    value: string
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
        "Please fill in all required fields (Job Name, Description, Domain Hint)."
      );
      return;
    }

    const validCandidates = candidates.filter((c) => c.email.trim() !== "");
    if (validCandidates.length === 0) {
      setError("At least one candidate with a valid email is required.");
      return;
    }

    try {
      // Transition to loading step without closing modal
      setModalStep("loading");
      setLoadingStepIndex(0);

      const rawToken = document.cookie
        .split("; ")
        .find((row) => row.startsWith("access_token="))
        ?.split("=")[1];
      const tokenCookie = rawToken ? decodeURIComponent(rawToken) : null;

      if (!tokenCookie) {
        throw new Error("You must be logged in to create an interview.");
      }

      // Start mock progress sequence interval
      const progressTimer = setInterval(() => {
        setLoadingStepIndex((prev) => (prev < 3 ? prev + 1 : prev));
      }, 650);

      const payload: CreateInterviewPayload = {
        ...formData,
        scheduled_at: formData.scheduled_at
          ? new Date(formData.scheduled_at).toISOString()
          : undefined,
        candidates: validCandidates,
      };

      // Synchronous backend creation call returns { interview, candidates }
      const creationResult = await createInterviewApi(payload, tokenCookie);
      setCreatedInterview(creationResult.interview);

      let fetchedCandidates: BackendCandidateResponse[] =
        creationResult.candidates || [];

      // If candidates list wasn't populated directly, fetch via candidates endpoint with valid interview ID
      if (fetchedCandidates.length === 0 && creationResult.interview?.id) {
        try {
          fetchedCandidates = await getCandidatesForInterviewApi(
            creationResult.interview.id,
            tokenCookie
          );
        } catch (err) {
          console.warn("Failed to fetch created candidates:", err);
        }
      }

      clearInterval(progressTimer);
      setLoadingStepIndex(3);

      // Brief pause for step completion UX before transitioning to success
      setTimeout(() => {
        setCreatedCandidates(fetchedCandidates);
        setModalStep("success");
      }, 400);
    } catch (err: unknown) {
      setModalStep("form");
      setError(
        (err as Error).message ||
          "Failed to create interview. Please try again."
      );
    }
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

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/30 backdrop-blur-sm transition-opacity"
        onClick={modalStep === "loading" ? undefined : handleClose}
      />

      {/* Modal Content Card */}
      <div className="relative w-full max-w-2xl max-h-[90vh] overflow-y-auto bg-white rounded-3xl shadow-2xl border border-[#F1F1F1] p-7 animate-in fade-in zoom-in-95 duration-150 custom-scrollbar">
        {/* Header */}
        <div className="flex items-center justify-between mb-6 border-b border-[#F1F1F1] pb-4">
          <div>
            <h2 className="text-xl font-bold text-[#272727] tracking-tight flex items-center gap-2">
              {modalStep === "loading" && (
                <>
                  <Sparkles className="w-5 h-5 text-[#FE6100] animate-pulse" />
                  Generating AI Interview Plan...
                </>
              )}
              {modalStep === "success" && (
                <>
                  <CheckCircle2 className="w-6 h-6 text-emerald-500" />
                  Interview Created Successfully!
                </>
              )}
              {modalStep === "form" && "Create Interview"}
            </h2>
            <p className="text-sm text-[#616161] mt-1 font-medium">
              {modalStep === "loading" &&
                "Please wait while our AI engine analyzes the job description and prepares candidate room tokens."}
              {modalStep === "success" &&
                "LiveKit voice access tokens have been generated for all candidates."}
              {modalStep === "form" &&
                "Configure your AI interviewer and add candidates."}
            </p>
          </div>
          {modalStep !== "loading" && (
            <button
              onClick={handleClose}
              className="p-2 text-[#B8B8B8] hover:text-[#272727] transition-colors rounded-full hover:bg-gray-50 cursor-pointer"
            >
              <X className="w-5 h-5" />
            </button>
          )}
        </div>

        {/* STEP 1: FORM INPUTS */}
        {modalStep === "form" && (
          <>
            {error && (
              <div className="mb-6 p-4 rounded-xl bg-red-50 text-sm font-medium text-red-600 border border-red-100">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Job Name */}
              <div>
                <label className="block text-sm font-semibold text-[#272727] mb-2">
                  Job Name *
                </label>
                <input
                  type="text"
                  value={formData.job_name}
                  onChange={(e) =>
                    setFormData({ ...formData, job_name: e.target.value })
                  }
                  className="w-full px-4 py-3 bg-white border border-[#E9E9E9] rounded-xl text-sm text-black font-medium placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-[#FE6100]/20 focus:border-[#FE6100] transition-all"
                  placeholder="e.g. Senior Frontend Engineer"
                />
              </div>

              {/* Job Description */}
              <div>
                <label className="block text-sm font-semibold text-[#272727] mb-2">
                  Job Description *
                </label>
                <textarea
                  value={formData.job_description}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      job_description: e.target.value,
                    })
                  }
                  className="w-full h-32 px-4 py-3 bg-white border border-[#E9E9E9] rounded-xl text-sm text-black font-medium placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-[#FE6100]/20 focus:border-[#FE6100] transition-all resize-none"
                  placeholder="Paste the job description here..."
                />
              </div>

              {/* Scheduled Date */}
              <div>
                <label className="block text-sm font-semibold text-[#272727] mb-2">
                  Scheduled Date (Optional)
                </label>
                <input
                  type="datetime-local"
                  value={formData.scheduled_at}
                  onChange={(e) =>
                    setFormData({ ...formData, scheduled_at: e.target.value })
                  }
                  className="w-full px-4 py-3 bg-white border border-[#E9E9E9] rounded-xl text-sm text-black font-medium focus:outline-none focus:ring-2 focus:ring-[#FE6100]/20 focus:border-[#FE6100] transition-all"
                />
              </div>

              <div className="grid grid-cols-2 gap-6">
                {/* Difficulty */}
                <div>
                  <label className="block text-sm font-semibold text-[#272727] mb-2">
                    Difficulty
                  </label>
                  <div className="relative">
                    <select
                      value={formData.difficulty}
                      onChange={(e) =>
                        setFormData({ ...formData, difficulty: e.target.value })
                      }
                      className="w-full px-4 py-3 bg-white border border-[#E9E9E9] rounded-xl text-sm text-black font-medium focus:outline-none focus:ring-2 focus:ring-[#FE6100]/20 focus:border-[#FE6100] transition-all appearance-none cursor-pointer"
                    >
                      <option value="junior" className="text-black bg-white">
                        Junior
                      </option>
                      <option value="mid" className="text-black bg-white">
                        Mid
                      </option>
                      <option value="senior" className="text-black bg-white">
                        Senior
                      </option>
                    </select>
                    <ChevronDown className="w-4 h-4 text-gray-500 absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none" />
                  </div>
                </div>

                {/* Domain Hint */}
                <div>
                  <label className="block text-sm font-semibold text-[#272727] mb-2">
                    Domain Hint *
                  </label>
                  <input
                    type="text"
                    value={formData.domain_hint}
                    onChange={(e) =>
                      setFormData({ ...formData, domain_hint: e.target.value })
                    }
                    className="w-full px-4 py-3 bg-white border border-[#E9E9E9] rounded-xl text-sm text-black font-medium placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-[#FE6100]/20 focus:border-[#FE6100] transition-all"
                    placeholder="e.g. React & TypeScript"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-6">
                {/* Number of Goals */}
                <div>
                  <label className="block text-sm font-semibold text-[#272727] mb-2">
                    Number of Goals
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="10"
                    value={formData.num_goals}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        num_goals: parseInt(e.target.value),
                      })
                    }
                    className="w-full px-4 py-3 bg-white border border-[#E9E9E9] rounded-xl text-sm text-black font-medium placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-[#FE6100]/20 focus:border-[#FE6100] transition-all"
                  />
                </div>

                {/* Total Duration */}
                <div>
                  <label className="block text-sm font-semibold text-[#272727] mb-2">
                    Total Duration (Minutes)
                  </label>
                  <input
                    type="number"
                    min="5"
                    max="120"
                    step="5"
                    value={formData.total_duration_minutes}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        total_duration_minutes: parseInt(e.target.value),
                      })
                    }
                    className="w-full px-4 py-3 bg-white border border-[#E9E9E9] rounded-xl text-sm text-black font-medium placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-[#FE6100]/20 focus:border-[#FE6100] transition-all"
                  />
                </div>
              </div>

              {/* Communication Weight Slider */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="block text-sm font-semibold text-[#272727]">
                    Communication vs Knowledge Weight
                  </label>
                  <span className="text-sm font-medium text-[#FE6100]">
                    {Math.round(formData.communication_weight * 100)}%
                  </span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={formData.communication_weight}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      communication_weight: parseFloat(e.target.value),
                    })
                  }
                  className="w-full h-2 bg-[#E9E9E9] rounded-lg appearance-none cursor-pointer accent-[#FE6100]"
                />
                <div className="flex items-center justify-between mt-1.5 text-xs font-medium text-[#616161]">
                  <span>More Knowledge</span>
                  <span>More Communication</span>
                </div>
              </div>

              <hr className="border-[#F1F1F1]" />

              {/* Candidates Section */}
              <div>
                <div className="flex items-center justify-between mb-4">
                  <label className="block text-sm font-semibold text-[#272727]">
                    Candidates *
                  </label>
                  <button
                    type="button"
                    onClick={handleAddCandidate}
                    className="text-xs font-semibold text-[#FE6100] hover:text-[#e05600] flex items-center gap-1 transition-colors cursor-pointer"
                  >
                    <Plus className="w-3 h-3" /> Add Another
                  </button>
                </div>

                <div className="space-y-3">
                  {candidates.map((candidate, index) => (
                    <div
                      key={index}
                      className="flex items-start gap-3 p-4 bg-gray-50 border border-[#E9E9E9] rounded-xl relative group"
                    >
                      {candidates.length > 1 && (
                        <button
                          type="button"
                          onClick={() => handleRemoveCandidate(index)}
                          className="absolute -top-2 -right-2 w-6 h-6 bg-white border border-[#E9E9E9] rounded-full flex items-center justify-center text-[#B8B8B8] hover:text-red-500 hover:border-red-200 hover:bg-red-50 transition-all opacity-0 group-hover:opacity-100 shadow-sm cursor-pointer"
                        >
                          <Trash2 className="w-3 h-3" />
                        </button>
                      )}
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-3 w-full">
                        <input
                          type="email"
                          placeholder="Email address"
                          value={candidate.email}
                          onChange={(e) =>
                            handleCandidateChange(
                              index,
                              "email",
                              e.target.value
                            )
                          }
                          className="w-full px-3 py-2 bg-white border border-[#d9d9d9] rounded-lg text-sm text-black font-medium placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-[#FE6100]/20 focus:border-[#FE6100] transition-all"
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
                              e.target.value
                            )
                          }
                          className="w-full px-3 py-2 bg-white border border-[#d9d9d9] rounded-lg text-sm text-black font-medium placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-[#FE6100]/20 focus:border-[#FE6100] transition-all"
                        />
                        <input
                          type="text"
                          placeholder="Last name"
                          value={candidate.last_name}
                          onChange={(e) =>
                            handleCandidateChange(
                              index,
                              "last_name",
                              e.target.value
                            )
                          }
                          className="w-full px-3 py-2 bg-white border border-[#d9d9d9] rounded-lg text-sm text-black font-medium placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-[#FE6100]/20 focus:border-[#FE6100] transition-all"
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="flex items-center justify-end gap-3 pt-4 border-t border-[#F1F1F1] mt-6">
                <button
                  type="button"
                  onClick={handleClose}
                  className="px-6 py-2.5 rounded-full text-sm font-semibold text-[#616161] hover:text-[#272727] hover:bg-gray-100 transition-colors cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-6 py-2.5 bg-[#FE6100] text-white rounded-full text-sm font-semibold hover:bg-[#e05600] transition-colors flex items-center gap-2 cursor-pointer shadow-md shadow-[#FE6100]/20"
                >
                  Create Interview
                </button>
              </div>
            </form>
          </>
        )}

        {/* STEP 2: LOADING / AI GENERATION SEQUENCE */}
        {modalStep === "loading" && (
          <div className="py-12 px-4 flex flex-col items-center justify-center text-center space-y-8 animate-in fade-in duration-200">
            {/* Glowing Orb Animation */}
            <div className="relative flex items-center justify-center">
              <div className="absolute w-24 h-24 rounded-full bg-[#FE6100]/20 animate-ping opacity-75" />
              <div className="w-20 h-20 rounded-full bg-gradient-to-tr from-[#FE6100] to-amber-400 p-1 shadow-lg relative z-10 flex items-center justify-center">
                <div className="w-full h-full bg-white rounded-full flex items-center justify-center">
                  <Sparkles className="w-8 h-8 text-[#FE6100] animate-spin" />
                </div>
              </div>
            </div>

            {/* Title & Active Step Subtext */}
            <div className="space-y-3 max-w-md">
              <h3 className="text-xl font-bold text-[#272727]">
                Synthesizing AI Recruiting Pipeline
              </h3>
              <p className="text-sm font-medium text-[#FE6100] animate-pulse">
                {AI_PROGRESS_STEPS[loadingStepIndex]}
              </p>
            </div>

            {/* Step Checkmarks List */}
            <div className="w-full max-w-md bg-gray-50 border border-[#E9E9E9] rounded-2xl p-5 text-left space-y-3.5">
              {AI_PROGRESS_STEPS.map((stepText, idx) => {
                const isCompleted = idx < loadingStepIndex;
                const isCurrent = idx === loadingStepIndex;

                return (
                  <div
                    key={idx}
                    className={`flex items-center gap-3 text-sm font-medium transition-all duration-300 ${
                      isCompleted
                        ? "text-emerald-700 font-semibold"
                        : isCurrent
                        ? "text-[#272727]"
                        : "text-[#B8B8B8]"
                    }`}
                  >
                    <div
                      className={`w-6 h-6 rounded-full flex items-center justify-center text-xs shrink-0 transition-colors ${
                        isCompleted
                          ? "bg-emerald-100 text-emerald-600 border border-emerald-300"
                          : isCurrent
                          ? "bg-orange-100 text-[#FE6100] border border-orange-300 animate-pulse"
                          : "bg-gray-100 text-gray-400 border border-gray-200"
                      }`}
                    >
                      {isCompleted ? (
                        <Check className="w-3.5 h-3.5 stroke-[3]" />
                      ) : isCurrent ? (
                        <Loader2 className="w-3.5 h-3.5 animate-spin" />
                      ) : (
                        <span>{idx + 1}</span>
                      )}
                    </div>
                    <span className="truncate">{stepText}</span>
                  </div>
                );
              })}
            </div>

            {/* Progress Bar */}
            <div className="w-full max-w-md h-2 bg-gray-100 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-[#FE6100] to-amber-500 transition-all duration-500 ease-out"
                style={{
                  width: `${((loadingStepIndex + 1) / AI_PROGRESS_STEPS.length) * 100}%`,
                }}
              />
            </div>
          </div>
        )}

        {/* STEP 3: SUCCESS STATE & LIVEKIT ROOM TOKENS */}
        {modalStep === "success" && (
          <div className="space-y-6 animate-in fade-in zoom-in-95 duration-200">
            {/* Summary Banner */}
            <div className="bg-emerald-50/60 border border-emerald-100 rounded-2xl p-5 flex items-start gap-4">
              <div className="w-10 h-10 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center shrink-0 mt-0.5">
                <CheckCircle2 className="w-6 h-6" />
              </div>
              <div className="space-y-1">
                <h3 className="text-base font-bold text-gray-900">
                  {createdInterview?.job_name || "Interview Campaign"} Created
                </h3>
                <p className="text-xs text-gray-600 leading-relaxed font-medium">
                  Interview position has been saved with {formData.num_goals}{" "}
                  evaluation goals ({formData.total_duration_minutes} mins).
                  Share the LiveKit room links below with your candidates to begin.
                </p>
              </div>
            </div>

            {/* Candidates & LiveKit Room Links List */}
            <div className="space-y-4">
              <h4 className="text-sm font-semibold text-[#272727] flex items-center justify-between">
                <span>Created Candidates & LiveKit Links</span>
                <span className="text-xs text-[#616161] font-normal">
                  {createdCandidates.length} candidate(s)
                </span>
              </h4>

              <div className="space-y-3.5 max-h-[340px] overflow-y-auto pr-1 custom-scrollbar">
                {createdCandidates.length === 0 ? (
                  <div className="p-6 text-center text-sm text-[#616161] bg-gray-50 rounded-2xl border border-[#E9E9E9]">
                    No candidate records retrieved.
                  </div>
                ) : (
                  createdCandidates.map((c) => {
                    const candidateName =
                      c.first_name || c.last_name
                        ? `${c.first_name || ""} ${c.last_name || ""}`.trim()
                        : "Candidate";

                    const tokenValue = c.room_token || c.id;
                    const origin =
                      typeof window !== "undefined"
                        ? window.location.origin
                        : "http://localhost:3000";
                    const roomUrl = `${origin}/interview?token=${tokenValue}`;
                    const isCopied = copiedCandidateId === c.id;

                    return (
                      <div
                        key={c.id}
                        className="bg-white border border-[#E9E9E9] rounded-2xl p-4 shadow-sm hover:border-[#d9d9d9] transition-all space-y-3"
                      >
                        {/* Candidate Info Row */}
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-3">
                            <div className="w-8 h-8 rounded-full bg-orange-50 border border-orange-100 flex items-center justify-center text-[#FE6100] shrink-0 font-semibold text-xs">
                              <User className="w-4 h-4" />
                            </div>
                            <div>
                              <p className="text-sm font-bold text-[#272727]">
                                {candidateName}
                              </p>
                              <p className="text-xs text-[#616161] font-medium">
                                {c.email}
                              </p>
                            </div>
                          </div>

                          <span className="px-2.5 py-1 bg-emerald-50 text-emerald-700 rounded-full text-[11px] font-bold border border-emerald-200">
                            Token Ready
                          </span>
                        </div>

                        {/* LiveKit Link Input Box & Copy Action */}
                        <div className="flex items-center gap-2 pt-1">
                          <div className="flex-1 bg-[#F9FAFB] border border-[#E9E9E9] rounded-xl px-3 py-2 flex items-center gap-2 overflow-hidden">
                            <LinkIcon className="w-3.5 h-3.5 text-gray-400 shrink-0" />
                            <input
                              type="text"
                              readOnly
                              value={roomUrl}
                              className="w-full bg-transparent text-xs font-mono text-[#272727] focus:outline-none truncate"
                            />
                          </div>

                          <button
                            type="button"
                            onClick={() => handleCopyLink(c)}
                            className={`px-3 py-2 rounded-xl text-xs font-semibold flex items-center gap-1.5 transition-all cursor-pointer shrink-0 ${
                              isCopied
                                ? "bg-emerald-600 text-white shadow-sm"
                                : "bg-gray-100 hover:bg-gray-200 text-[#272727] border border-gray-200"
                            }`}
                          >
                            {isCopied ? (
                              <>
                                <Check className="w-3.5 h-3.5" />
                                <span>Copied</span>
                              </>
                            ) : (
                              <>
                                <Copy className="w-3.5 h-3.5 text-gray-600" />
                                <span>Copy Link</span>
                              </>
                            )}
                          </button>

                          <a
                            href={roomUrl}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="p-2 bg-orange-50 hover:bg-orange-100 text-[#FE6100] border border-orange-200 rounded-xl transition-colors shrink-0"
                            title="Open Room in New Tab"
                          >
                            <ExternalLink className="w-4 h-4" />
                          </a>
                        </div>
                      </div>
                    );
                  })
                )}
              </div>
            </div>

            {/* Bottom Actions */}
            <div className="flex items-center justify-end pt-4 border-t border-[#F1F1F1]">
              <button
                type="button"
                onClick={handleDone}
                className="px-8 py-3 bg-[#FE6100] hover:bg-[#e05600] text-white rounded-full text-sm font-bold shadow-lg shadow-[#FE6100]/25 transition-all cursor-pointer"
              >
                Done
              </button>
            </div>
          </div>
        )}
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
