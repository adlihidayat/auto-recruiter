"use client";

import React, { useState } from "react";
import { X, Plus, Trash2, Loader2, ChevronDown } from "lucide-react";
import { CreateInterviewPayload, createInterviewApi } from "@/lib/api/client";

interface CreateInterviewModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCampaignCreated: () => void;
}

export default function CreateInterviewModal({
  isOpen,
  onClose,
  onCampaignCreated,
}: CreateInterviewModalProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    job_name: "",
    job_description: "",
    difficulty: "mid",
    num_goals: 3,
    total_duration_minutes: 30,
    domain_hint: "",
    communication_weight: 0.2,
  });

  const [candidates, setCandidates] = useState([
    { email: "", first_name: "", last_name: "" },
  ]);

  if (!isOpen) return null;

  const handleAddCandidate = () => {
    setCandidates([...candidates, { email: "", first_name: "", last_name: "" }]);
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
    if (!formData.job_name || !formData.job_description || !formData.domain_hint) {
      setError("Please fill in all required fields (Job Name, Description, Domain Hint).");
      return;
    }

    const validCandidates = candidates.filter((c) => c.email.trim() !== "");
    if (validCandidates.length === 0) {
      setError("At least one candidate with a valid email is required.");
      return;
    }

    try {
      setIsSubmitting(true);
      
      const rawToken = document.cookie
        .split("; ")
        .find((row) => row.startsWith("access_token="))
        ?.split("=")[1];
      const tokenCookie = rawToken ? decodeURIComponent(rawToken) : null;

      if (!tokenCookie) {
        throw new Error("You must be logged in to create an interview.");
      }

      const payload: CreateInterviewPayload = {
        ...formData,
        candidates: validCandidates,
      };

      await createInterviewApi(payload, tokenCookie);
      onCampaignCreated();
      onClose();
    } catch (err: unknown) {
      setError((err as Error).message || "Failed to create interview. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/20 backdrop-blur-sm transition-opacity"
        onClick={onClose}
      />

      {/* Modal Content - styled exactly like the logout popup */}
      <div className="relative w-full max-w-2xl max-h-[90vh] overflow-y-auto bg-white rounded-2xl shadow-xl border border-[#F1F1F1] p-6 animate-in fade-in zoom-in-95 duration-150 custom-scrollbar">
        <div className="flex items-center justify-between mb-6 border-b border-[#F1F1F1] pb-4">
          <div>
            <h2 className="text-xl font-bold text-[#272727] tracking-tight">Create Interview</h2>
            <p className="text-sm text-[#616161] mt-1 font-medium">Configure your AI interviewer and add candidates.</p>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-[#B8B8B8] hover:text-[#272727] transition-colors rounded-full hover:bg-gray-50 cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {error && (
          <div className="mb-6 p-4 rounded-xl bg-red-50 text-sm font-medium text-red-600 border border-red-100">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Job Name */}
          <div>
            <label className="block text-sm font-semibold text-[#272727] mb-2">Job Name *</label>
            <input
              type="text"
              value={formData.job_name}
              onChange={(e) => setFormData({ ...formData, job_name: e.target.value })}
              className="w-full px-4 py-3 bg-white border border-[#E9E9E9] rounded-xl text-sm text-[#272727] font-medium placeholder:text-[#616161] focus:outline-none focus:ring-2 focus:ring-[#FE6100]/20 focus:border-[#FE6100] transition-all"
              placeholder="e.g. Senior Frontend Engineer"
            />
          </div>

          {/* Job Description */}
          <div>
            <label className="block text-sm font-semibold text-[#272727] mb-2">Job Description *</label>
            <textarea
              value={formData.job_description}
              onChange={(e) => setFormData({ ...formData, job_description: e.target.value })}
              className="w-full h-32 px-4 py-3 bg-white border border-[#E9E9E9] rounded-xl text-sm text-[#272727] font-medium placeholder:text-[#616161] focus:outline-none focus:ring-2 focus:ring-[#FE6100]/20 focus:border-[#FE6100] transition-all resize-none"
              placeholder="Paste the job description here..."
            />
          </div>

          <div className="grid grid-cols-2 gap-6">
            {/* Difficulty */}
            <div>
              <label className="block text-sm font-semibold text-[#272727] mb-2">Difficulty</label>
              <div className="relative">
                <select
                  value={formData.difficulty}
                  onChange={(e) => setFormData({ ...formData, difficulty: e.target.value })}
                  className="w-full px-4 py-3 bg-white border border-[#E9E9E9] rounded-xl text-sm text-[#272727] font-medium focus:outline-none focus:ring-2 focus:ring-[#FE6100]/20 focus:border-[#FE6100] transition-all appearance-none cursor-pointer"
                >
                  <option value="junior" className="text-[#272727] bg-white">Junior</option>
                  <option value="mid" className="text-[#272727] bg-white">Mid</option>
                  <option value="senior" className="text-[#272727] bg-white">Senior</option>
                </select>
                <ChevronDown className="w-4 h-4 text-[#616161] absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none" />
              </div>
            </div>

            {/* Domain Hint */}
            <div>
              <label className="block text-sm font-semibold text-[#272727] mb-2">Domain Hint *</label>
              <input
                type="text"
                value={formData.domain_hint}
                onChange={(e) => setFormData({ ...formData, domain_hint: e.target.value })}
                className="w-full px-4 py-3 bg-white border border-[#E9E9E9] rounded-xl text-sm text-[#272727] font-medium placeholder:text-[#616161] focus:outline-none focus:ring-2 focus:ring-[#FE6100]/20 focus:border-[#FE6100] transition-all"
                placeholder="e.g. React & TypeScript"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-6">
            {/* Number of Goals */}
            <div>
              <label className="block text-sm font-semibold text-[#272727] mb-2">Number of Goals</label>
              <input
                type="number"
                min="1"
                max="10"
                value={formData.num_goals}
                onChange={(e) => setFormData({ ...formData, num_goals: parseInt(e.target.value) })}
                className="w-full px-4 py-3 bg-white border border-[#E9E9E9] rounded-xl text-sm text-[#272727] font-medium placeholder:text-[#616161] focus:outline-none focus:ring-2 focus:ring-[#FE6100]/20 focus:border-[#FE6100] transition-all"
              />
            </div>

            {/* Total Duration */}
            <div>
              <label className="block text-sm font-semibold text-[#272727] mb-2">Total Duration (Minutes)</label>
              <input
                type="number"
                min="5"
                max="120"
                step="5"
                value={formData.total_duration_minutes}
                onChange={(e) => setFormData({ ...formData, total_duration_minutes: parseInt(e.target.value) })}
                className="w-full px-4 py-3 bg-white border border-[#E9E9E9] rounded-xl text-sm text-[#272727] font-medium placeholder:text-[#616161] focus:outline-none focus:ring-2 focus:ring-[#FE6100]/20 focus:border-[#FE6100] transition-all"
              />
            </div>
          </div>

          {/* Communication Weight Slider */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="block text-sm font-semibold text-[#272727]">Communication vs Knowledge Weight</label>
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
              onChange={(e) => setFormData({ ...formData, communication_weight: parseFloat(e.target.value) })}
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
              <label className="block text-sm font-semibold text-[#272727]">Candidates *</label>
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
                <div key={index} className="flex items-start gap-3 p-4 bg-gray-50 border border-[#E9E9E9] rounded-xl relative group">
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
                      onChange={(e) => handleCandidateChange(index, "email", e.target.value)}
                      className="w-full px-3 py-2 bg-white border border-[#d9d9d9] rounded-lg text-sm text-[#272727] font-medium placeholder:text-[#616161] focus:outline-none focus:ring-2 focus:ring-[#FE6100]/20 focus:border-[#FE6100] transition-all"
                      required
                    />
                    <input
                      type="text"
                      placeholder="First name"
                      value={candidate.first_name}
                      onChange={(e) => handleCandidateChange(index, "first_name", e.target.value)}
                      className="w-full px-3 py-2 bg-white border border-[#d9d9d9] rounded-lg text-sm text-[#272727] font-medium placeholder:text-[#616161] focus:outline-none focus:ring-2 focus:ring-[#FE6100]/20 focus:border-[#FE6100] transition-all"
                    />
                    <input
                      type="text"
                      placeholder="Last name"
                      value={candidate.last_name}
                      onChange={(e) => handleCandidateChange(index, "last_name", e.target.value)}
                      className="w-full px-3 py-2 bg-white border border-[#d9d9d9] rounded-lg text-sm text-[#272727] font-medium placeholder:text-[#616161] focus:outline-none focus:ring-2 focus:ring-[#FE6100]/20 focus:border-[#FE6100] transition-all"
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="flex items-center justify-end gap-3 pt-4 border-t border-[#F1F1F1] mt-6">
            <button
              type="button"
              onClick={onClose}
              disabled={isSubmitting}
              className="px-6 py-2.5 rounded-full text-sm font-semibold text-[#616161] hover:text-[#272727] hover:bg-gray-100 transition-colors disabled:opacity-50 cursor-pointer"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-6 py-2.5 bg-[#FE6100] text-white rounded-full text-sm font-semibold hover:bg-[#e05600] transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 cursor-pointer"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" /> Creating...
                </>
              ) : (
                "Create Interview"
              )}
            </button>
          </div>
        </form>
      </div>
      
      {/* Custom Scrollbar Styles for the modal content */}
      <style dangerouslySetInnerHTML={{ __html: `
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
      `}} />
    </div>
  );
}
