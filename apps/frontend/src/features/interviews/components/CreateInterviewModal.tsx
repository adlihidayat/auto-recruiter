/**
 * What: Container modal component for interview creation flow.
 * Why: Orchestrates multi-step workflow state (Form -> Agent Loading -> Publish Success).
 * Boundaries: Delegates step-specific JSX rendering to modular components under create-modal/.
 */

"use client";

import React, { useState, useRef, useEffect } from "react";
import { useRouter } from "next/navigation";
import { X } from "lucide-react";

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

  // Agent Handoff Mock Simulation State
  const [isPaused] = useState(false);
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

  // Derived mock calculation
  const mockProgressPercent = Math.min(100, (elapsedTime / 20000) * 100);
  const activeAgentIndex = Math.min(3, Math.floor((elapsedTime / 20000) * 4));
  const visibleLogs = MOCK_LOGS.filter((log) => log.time <= elapsedTime);

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
    { email: "alex.johnson@example.com", first_name: "Alex", last_name: "Johnson" },
    { email: "sarah.chen@example.com", first_name: "Sarah", last_name: "Chen" },
    { email: "michael.brown@example.com", first_name: "Michael", last_name: "Brown" },
  ]);

  const [copiedCandidateId, setCopiedCandidateId] = useState<string | null>(null);

  // Candidate management handlers
  const handleAddCandidate = () => {
    setCandidates((prev) => [...prev, { email: "", first_name: "", last_name: "" }]);
  };

  const handleRemoveCandidate = (index: number) => {
    setCandidates((prev) => prev.filter((_, i) => i !== index));
  };

  const handleCandidateChange = (
    index: number,
    field: "email" | "first_name" | "last_name",
    value: string
  ) => {
    setCandidates((prev) =>
      prev.map((c, i) => (i === index ? { ...c, [field]: value } : c))
    );
  };

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

  const handleSubmitForm = (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.job_name || !formData.job_description || !formData.domain_hint) {
      setError("Please fill in all required fields (Job Name, Description, Domain Hint).");
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
  };

  const handleCopyLink = (candidateId: string, token: string) => {
    const link = `${window.location.origin}/interview?token=${token}`;
    navigator.clipboard.writeText(link);
    setCopiedCandidateId(candidateId);
    setTimeout(() => setCopiedCandidateId(null), 2000);
  };

  const handleResetModal = () => {
    setModalStep("form");
    setElapsedTime(0);
    setIsBackendDone(false);
    setError(null);
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
    router.push(`/interviews/mock-interview-id`);
    handleResetModal();
  };

  const displayCandidates = candidates.map((c, i) => ({
    first_name:
      c.first_name || (i === 0 ? "Alex" : i === 1 ? "Sarah" : "Michael"),
    last_name:
      c.last_name || (i === 0 ? "Johnson" : i === 1 ? "Chen" : "Brown"),
    email:
      c.email ||
      (i === 0
        ? "alex.johnson@example.com"
        : i === 1
        ? "sarah.chen@example.com"
        : "michael.brown@example.com"),
    room_token: `mock_room_token_${i + 1}`,
  }));

  if (!isOpen) return null;

  return (
    <div className={`fixed inset-0 z-50 flex items-center justify-center ${modalStep === "loading" && ""}`}>
      {/* Canvas Confetti Layer */}
      <CanvasConfettiOverlay isActive={modalStep === "success"} />

      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/40 backdrop-blur-sm transition-opacity"
        onClick={modalStep === "loading" ? undefined : handleResetModal}
      />

      <div className="rounded-3xl overflow-hidden z-10">
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
              onClick={() => {
                onClose();
                handleResetModal();
              }}
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
              onReset={handleResetModal}
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
