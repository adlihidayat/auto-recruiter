/**
 * What: Container modal component for interview creation flow.
 * Why: Orchestrates multi-step workflow state, backdrop outside click, and close confirmation dialogs.
 * Boundaries: Delegates step-specific JSX rendering to modular components under create-modal/.
 */

"use client";

import React, { useState, useRef, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { X, AlertTriangle, Bot } from "lucide-react";
import { createInterviewApi, BackendCandidateResponse } from "@/lib/api/client";

import {
  ModalStep,
  CandidateInput,
  InterviewFormData,
  CreateInterviewModalProps,
} from "./create-modal/types";
import { MOCK_LOGS } from "./create-modal/constants";
import { CanvasConfettiOverlay } from "./create-modal/CanvasConfettiOverlay";
import { CreateInterviewFormStep } from "./create-modal/CreateInterviewFormStep";
import { CreateInterviewLoadingStep } from "./create-modal/CreateInterviewLoadingStep";
import { CreateInterviewSuccessStep } from "./create-modal/CreateInterviewSuccessStep";

export default function CreateInterviewModal({
  isOpen,
  onClose,
  onCampaignCreated,
}: CreateInterviewModalProps) {
  const router = useRouter();
  const [modalStep, setModalStep] = useState<ModalStep>("form");
  const [isBackendDone, setIsBackendDone] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Confirmation dialog state ('form' | 'loading' | null)
  const [showConfirmClose, setShowConfirmClose] = useState<
    "form" | "loading" | null
  >(null);

  // Agent Handoff Mock Simulation State
  const [isPaused] = useState(false);
  const [elapsedTime, setElapsedTime] = useState(0);

  const [isApiFinished, setIsApiFinished] = useState(false);
  const [createdInterviewId, setCreatedInterviewId] = useState<string | null>(null);
  const [createdCandidates, setCreatedCandidates] = useState<BackendCandidateResponse[]>([]);

  useEffect(() => {
    if (modalStep !== "loading" || isPaused || isBackendDone) return;
    const interval = setInterval(() => {
      setElapsedTime((prev) => {
        const next = prev + 100;
        if (next >= 20000 && isApiFinished) {
          setIsBackendDone(true);
        }
        return next;
      });
    }, 100);
    return () => clearInterval(interval);
  }, [modalStep, isPaused, isBackendDone, isApiFinished]);

  // Derived mock calculation
  const mockProgressPercent = Math.min(100, (elapsedTime / 20000) * 100);
  const activeAgentIndex = Math.min(3, Math.floor((elapsedTime / 20000) * 4));
  const baseLogs = MOCK_LOGS.filter((log, index) => {
    if (index < 11) return log.time <= elapsedTime;
    return false;
  });

  const visibleLogs = (() => {
    if (isBackendDone) {
      const finalLog = MOCK_LOGS[11];
      return [
        ...baseLogs,
        {
          ...finalLog,
          time: elapsedTime,
        },
      ];
    }
    if (elapsedTime > 20000) {
      return [
        ...baseLogs,
        {
          time: elapsedTime,
          dot: "bg-amber-500",
          isPending: true,
          text: (
            <span className="text-amber-600 font-medium">
              waiting the agent to process...
            </span>
          ),
        },
      ];
    }
    return baseLogs;
  })();

  // Emoji picker state
  const [showEmojiPicker, setShowEmojiPicker] = useState(false);
  const emojiPickerRef = useRef<HTMLDivElement>(null);

  // Form State
  const [formData, setFormData] = useState<InterviewFormData>({
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

  const [candidates, setCandidates] = useState<CandidateInput[]>([
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

  const [copiedCandidateId, setCopiedCandidateId] = useState<string | null>(
    null,
  );

  // Candidate management handlers
  const handleAddCandidate = () => {
    setCandidates((prev) => [
      ...prev,
      { email: "", first_name: "", last_name: "" },
    ]);
  };

  const handleRemoveCandidate = (index: number) => {
    setCandidates((prev) => prev.filter((_, i) => i !== index));
  };

  const handleCandidateChange = (
    index: number,
    field: "email" | "first_name" | "last_name",
    value: string,
  ) => {
    setCandidates((prev) =>
      prev.map((c, i) => (i === index ? { ...c, [field]: value } : c)),
    );
  };

  // Reset modal state
  const handleResetModal = useCallback(() => {
    setModalStep("form");
    setElapsedTime(0);
    setIsBackendDone(false);
    setIsApiFinished(false);
    setCreatedInterviewId(null);
    setError(null);
    setShowConfirmClose(null);
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
    setCandidates([
      {
        email: "alex.johnson@example.com",
        first_name: "Alex",
        last_name: "Johnson",
      },
      {
        email: "sarah.chen@example.com",
        first_name: "Sarah",
        last_name: "Chen",
      },
      {
        email: "michael.brown@example.com",
        first_name: "Michael",
        last_name: "Brown",
      },
    ]);
  }, []);

  // Request Close intent handler with confirmation dialog checks
  const handleRequestClose = useCallback(() => {
    if (modalStep === "form") {
      const isFormFilled =
        formData.job_name.trim().length > 0 ||
        formData.job_description.trim().length > 0 ||
        formData.domain_hint.trim().length > 0;

      if (isFormFilled) {
        setShowConfirmClose("form");
        return;
      }
    } else if (modalStep === "loading" && !isBackendDone) {
      setShowConfirmClose("loading");
      return;
    }

    onClose();
    handleResetModal();
  }, [formData, modalStep, isBackendDone, onClose, handleResetModal]);

  // Handle ESC key press
  useEffect(() => {
    if (!isOpen) return;
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape" && !showEmojiPicker && !showConfirmClose) {
        handleRequestClose();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, showEmojiPicker, showConfirmClose, handleRequestClose]);

  // Close & Outside click for Emoji Picker
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        emojiPickerRef.current &&
        !emojiPickerRef.current.contains(event.target as Node)
      ) {
        setShowEmojiPicker(false);
      }
    };

    if (showEmojiPicker) {
      document.addEventListener("mousedown", handleClickOutside);
    }
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [showEmojiPicker]);

  const handleSubmitForm = async (e: React.FormEvent) => {
    e.preventDefault();
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
    const validCandidates = candidates.filter((c) => c.email.trim().length > 0);
    if (validCandidates.length === 0) {
      setError("At least one candidate with a valid email is required.");
      return;
    }

    setError(null);
    setModalStep("loading");
    setElapsedTime(0);
    setIsBackendDone(false);
    setIsApiFinished(false);

    try {
      const rawToken = document.cookie
        .split("; ")
        .find((row) => row.startsWith("access_token="))
        ?.split("=")[1];
      const tokenCookie = rawToken ? decodeURIComponent(rawToken) : null;
      if (!tokenCookie) {
        setError("Authentication token not found.");
        setModalStep("form");
        return;
      }

      const payload = {
        job_name: formData.job_name,
        job_description: formData.job_description,
        icon: formData.icon,
        difficulty: formData.difficulty,
        num_goals: formData.num_goals,
        total_duration_minutes: formData.total_duration_minutes,
        domain_hint: formData.domain_hint,
        communication_weight: formData.communication_weight,
        scheduled_at: formData.scheduled_at
          ? new Date(formData.scheduled_at).toISOString()
          : new Date().toISOString(),
        candidates: validCandidates,
      };

      const result = await createInterviewApi(payload, tokenCookie);
      setCreatedInterviewId(result.interview.id);
      setCreatedCandidates(result.candidates);
      setIsApiFinished(true);
    } catch (err: unknown) {
      console.error("Failed to create interview", err);
      setError(err instanceof Error ? err.message : "Failed to create interview");
      setModalStep("form");
    }
  };

  const handleCopyLink = (candidateId: string, token: string) => {
    const link = `${window.location.origin}/interview?token=${token}`;
    navigator.clipboard.writeText(link);
    setCopiedCandidateId(candidateId);
    setTimeout(() => setCopiedCandidateId(null), 2000);
  };

  const handleContinueToSuccess = () => {
    if (isBackendDone) {
      setModalStep("success");
    } else {
      setElapsedTime(0);
      setIsBackendDone(false);
    }
  };

  const handleDone = () => {
    onCampaignCreated();
    onClose();
    handleResetModal();
  };

  const handleSeeDetail = () => {
    onCampaignCreated();
    onClose();
    if (createdInterviewId) {
      router.push(`/interviews/${createdInterviewId}`);
    } else {
      router.push(`/`);
    }
    handleResetModal();
  };

  const displayCandidates = createdCandidates.length > 0 
    ? createdCandidates.map((c) => ({
        id: c.id,
        first_name: c.first_name || "",
        last_name: c.last_name || "",
        email: c.email,
        room_token: c.room_token || "unavailable",
      }))
    : candidates.map((c, i) => ({
        id: `mock-${i}`,
        first_name: c.first_name || (i === 0 ? "Alex" : i === 1 ? "Sarah" : "Michael"),
        last_name: c.last_name || (i === 0 ? "Johnson" : i === 1 ? "Chen" : "Brown"),
        email: c.email || (i === 0 ? "alex.johnson@example.com" : i === 1 ? "sarah.chen@example.com" : "michael.brown@example.com"),
        room_token: `mock_room_token_${i + 1}`,
      }));

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Canvas Confetti Layer */}
      <CanvasConfettiOverlay isActive={modalStep === "success"} />

      {/* Backdrop (Clicking outside triggers request close with confirmation check) */}
      <div
        className="absolute inset-0 bg-black/40 backdrop-blur-sm transition-opacity cursor-pointer"
        onClick={handleRequestClose}
      />

      <div
        className="rounded-3xl overflow-hidden z-10"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal Content Card */}
        <div
          className={`relative w-full max-h-[90vh] overflow-y-scroll bg-white rounded-3xl shadow-2xl ${
            modalStep === "form" && "p-8 max-w-xl"
          } ${modalStep === "loading" && "p-4"} ${
            modalStep === "success" && "p-8"
          } custom-scrollbar`}
        >
          {/* Close Button */}
          {modalStep !== "loading" && (
            <button
              onClick={handleRequestClose}
              className="absolute top-6 right-6 p-2 text-gray-400 hover:text-gray-900 transition-colors rounded-full hover:bg-gray-100 cursor-pointer z-20"
            >
              <X className="w-5 h-5" />
            </button>
          )}

          {/* Modal Step Routing */}
          {modalStep === "form" && (
            <CreateInterviewFormStep
              formData={formData}
              setFormData={setFormData}
              candidates={candidates}
              showEmojiPicker={showEmojiPicker}
              setShowEmojiPicker={setShowEmojiPicker}
              emojiPickerRef={emojiPickerRef}
              error={error}
              onSubmit={handleSubmitForm}
              onAddCandidate={handleAddCandidate}
              onRemoveCandidate={handleRemoveCandidate}
              onCandidateChange={handleCandidateChange}
            />
          )}

          {modalStep === "loading" && (
            <CreateInterviewLoadingStep
              formData={formData}
              elapsedTime={elapsedTime}
              isPaused={isPaused}
              isBackendDone={isBackendDone}
              activeAgentIndex={activeAgentIndex}
              mockProgressPercent={mockProgressPercent}
              visibleLogs={visibleLogs}
              onReset={handleRequestClose}
              onContinue={handleContinueToSuccess}
            />
          )}

          {modalStep === "success" && (
            <CreateInterviewSuccessStep
              formData={formData}
              displayCandidates={displayCandidates}
              copiedCandidateId={copiedCandidateId}
              onCopyLink={handleCopyLink}
              onSeeDetail={handleSeeDetail}
              onDone={handleDone}
            />
          )}
        </div>
      </div>

      {/* Confirmation Dialog Overlay for Form Discard */}
      {showConfirmClose === "form" && (
        <div
          className="fixed inset-0 z-60 flex items-center justify-center bg-black/50 backdrop-blur-xs p-4 animate-in fade-in duration-150"
          onClick={() => setShowConfirmClose(null)}
        >
          <div
            className="bg-white border border-gray-200/80 rounded-2xl p-6 shadow-2xl max-w-sm w-full space-y-8 text-center animate-in zoom-in-95 duration-150"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="w-12 h-12 rounded-2xl bg-orange-50 border border-orange-200/60 text-orange-500 flex items-center justify-center mx-auto">
              <AlertTriangle className="w-6 h-6" />
            </div>

            <div>
              <h4 className="text-base font-semibold text-gray-900 tracking-tight">
                Discard interview creation?
              </h4>
              <p className="text-sm text-gray-600 font-normal leading-relaxed mt-1">
                Closing will cancel your progress and any un-submitted
                configuration will be lost.
              </p>
            </div>

            <div className="flex items-center gap-2 pt-2">
              <button
                type="button"
                onClick={() => setShowConfirmClose(null)}
                className="px-3.5 py-2 flex-1 border border-gray-200 text-gray-700 hover:bg-gray-100 rounded-lg text-sm font-semibold transition-colors cursor-pointer"
              >
                Continue editing
              </button>
              <button
                type="button"
                onClick={() => {
                  setShowConfirmClose(null);
                  onClose();
                  handleResetModal();
                }}
                className="px-3.5 py-2 flex-1 bg-red-600 hover:bg-red-700 text-white rounded-lg text-sm font-semibold transition-colors cursor-pointer shadow-xs"
              >
                Discard & close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Confirmation Dialog Overlay for Pipeline Loading In-Progress */}
      {showConfirmClose === "loading" && (
        <div
          className="fixed inset-0 z-60 flex items-center justify-center bg-black/50 backdrop-blur-xs p-4 animate-in fade-in duration-150"
          onClick={() => setShowConfirmClose(null)}
        >
          <div
            className="bg-white border border-gray-200/80 rounded-2xl p-6 shadow-2xl max-w-sm w-full space-y-4 text-center animate-in zoom-in-95 duration-150"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="w-12 h-12 rounded-2xl bg-blue-50 border border-blue-200/60 text-blue-600 flex items-center justify-center mx-auto">
              <Bot className="w-6 h-6" />
            </div>

            <div>
              <h4 className="text-base font-bold text-gray-900 tracking-tight">
                Agent pipeline in progress
              </h4>
              <p className="text-xs text-gray-500 font-normal leading-relaxed mt-1">
                The AI agents will continue running in the background even if
                you close this window. You can check campaign status anytime
                from your dashboard.
              </p>
            </div>

            <div className="flex items-center gap-2 pt-2">
              <button
                type="button"
                onClick={() => setShowConfirmClose(null)}
                className="px-3.5 py-2 flex-1 border border-gray-200 text-gray-700 hover:bg-gray-100 rounded-xl text-xs font-semibold transition-colors cursor-pointer"
              >
                Stay here
              </button>
              <button
                type="button"
                onClick={() => {
                  setShowConfirmClose(null);
                  onClose();
                  handleResetModal();
                }}
                className="px-3.5 py-2 flex-1 bg-[#191919] hover:bg-black text-white rounded-xl text-xs font-semibold transition-colors cursor-pointer shadow-xs"
              >
                Close window
              </button>
            </div>
          </div>
        </div>
      )}

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
