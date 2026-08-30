/**
 * What: Step 1 Form View for interview creation.
 * Why: Renders interview job parameters, custom duration/goals chevrons, orange range slider, candidate entries list, and emoji picker.
 * Boundaries: Emits submit event to trigger loading simulation.
 */

import React from "react";
import { Plus, Trash2, ChevronDown, ChevronUp, Globe } from "lucide-react";
import { CandidateInput, InterviewFormData } from "./types";
import { EmojiPickerPopover } from "./EmojiPickerPopover";

interface CreateInterviewFormStepProps {
  formData: InterviewFormData;
  setFormData: React.Dispatch<React.SetStateAction<InterviewFormData>>;
  candidates: CandidateInput[];
  showEmojiPicker: boolean;
  setShowEmojiPicker: (show: boolean) => void;
  emojiPickerRef: React.RefObject<HTMLDivElement | null>;
  error: string | null;
  onSubmit: (e: React.FormEvent) => void;
  onAddCandidate: () => void;
  onRemoveCandidate: (index: number) => void;
  onCandidateChange: (
    index: number,
    field: keyof CandidateInput,
    value: string
  ) => void;
}

export const CreateInterviewFormStep: React.FC<CreateInterviewFormStepProps> = ({
  formData,
  setFormData,
  candidates,
  showEmojiPicker,
  setShowEmojiPicker,
  emojiPickerRef,
  error,
  onSubmit,
  onAddCandidate,
  onRemoveCandidate,
  onCandidateChange,
}) => {
  return (
    <>
      <div className="flex justify-between items-start mb-6">
        <div>
          <h2 className="text-xl font-bold text-gray-900">Create Interview</h2>
          <p className="text-sm text-gray-500 font-medium">
            Set up role details and candidate access links.
          </p>
        </div>
      </div>

      {error && (
        <div className="mb-6 p-3 bg-red-50 border border-red-200 rounded-xl text-xs font-semibold text-red-600 animate-in fade-in duration-150">
          {error}
        </div>
      )}

      <form onSubmit={onSubmit} className="space-y-6">
        {/* Interview Icon (Notion Emoji Picker) */}
        <div className="relative group w-fit" ref={emojiPickerRef}>
          <button
            type="button"
            onClick={() => setShowEmojiPicker(!showEmojiPicker)}
            className="absolute hidden group-hover:flex items-center gap-1 bg-gray-[#FAFAFA] border border-gray-200 rounded-lg px-2 py-1 text-xs text-gray-500 font-medium z-10 cursor-pointer shadow-sm hover:bg-gray-100 transition-all top-2 left-12"
          >
            Change
          </button>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 flex items-center justify-center text-4xl">
              <span className="-translate-y-0.5">{formData.icon}</span>
            </div>
            <p className="text-sm font-semibold text-gray-900">
              Interview Icon
            </p>
          </div>
          <EmojiPickerPopover
            isOpen={showEmojiPicker}
            onSelect={(emoji) => {
              setFormData((prev) => ({ ...prev, icon: emoji }));
              setShowEmojiPicker(false);
            }}
            containerRef={emojiPickerRef}
          />
        </div>

        {/* Job Title */}
        <div>
          <label className="block text-sm font-medium text-gray-900 mb-2">
            Job Title <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            placeholder="e.g. Senior Backend Engineer"
            value={formData.job_name}
            onChange={(e) =>
              setFormData({ ...formData, job_name: e.target.value })
            }
            className="w-full px-3 py-2 bg-white border border-gray-200 rounded-xl text-sm text-gray-900 font-medium placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-900/10 focus:border-gray-900 transition-all"
            required
          />
        </div>

        {/* Job Description */}
        <div>
          <label className="block text-sm font-medium text-gray-900 mb-2">
            Job Description <span className="text-red-500">*</span>
          </label>
          <textarea
            rows={4}
            placeholder="Describe key responsibilities and expectations for this candidate..."
            value={formData.job_description}
            onChange={(e) =>
              setFormData({ ...formData, job_description: e.target.value })
            }
            className="w-full px-3 py-2 bg-white border border-gray-200 rounded-xl text-sm text-gray-900 font-medium placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-900/10 focus:border-gray-900 transition-all resize-none"
            required
          />
        </div>

        {/* Domain Hint */}
        <div>
          <label className="block text-sm font-medium text-gray-900 mb-2">
            Domain Focus Hint <span className="text-red-500">*</span>
          </label>
          <div className="relative">
            <input
              type="text"
              placeholder="e.g. Distributed Systems & High Concurrency"
              value={formData.domain_hint}
              onChange={(e) =>
                setFormData({ ...formData, domain_hint: e.target.value })
              }
              className="w-full px-3 py-2 bg-white border border-gray-200 rounded-xl text-sm text-gray-900 font-medium placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-900/10 focus:border-gray-900 transition-all"
              required
            />
            <Globe className="w-4 h-4 text-gray-400 absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none" />
          </div>
        </div>

        {/* Form Controls Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Total Duration */}
          <div>
            <label className="block text-sm font-medium text-gray-900 mb-2">
              Total Duration (mins)
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
                    total_duration_minutes: parseInt(e.target.value) || 5,
                  })
                }
                className="w-full px-3 py-2 pr-8 bg-white border border-gray-200 rounded-xl text-sm text-gray-900 font-medium placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-900/10 focus:border-gray-900 transition-all [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
              />
              <div className="absolute right-2.5 top-1/2 -translate-y-1/2 flex flex-col items-center justify-center text-gray-400 pointer-events-auto">
                <button
                  type="button"
                  onClick={() =>
                    setFormData((prev) => ({
                      ...prev,
                      total_duration_minutes: Math.min(
                        120,
                        (prev.total_duration_minutes || 0) + 5
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
                        (prev.total_duration_minutes || 5) - 5
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
                  setFormData({ ...formData, difficulty: e.target.value })
                }
                className="w-full px-3 py-2 bg-white border border-gray-200 rounded-xl text-sm text-gray-900 font-medium focus:outline-none focus:ring-2 focus:ring-gray-900/10 focus:border-gray-900 transition-all appearance-none cursor-pointer"
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
                className="w-full px-3 py-2 pr-8 bg-white border border-gray-200 rounded-xl text-sm text-gray-900 font-medium placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-900/10 focus:border-gray-900 transition-all [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
              />
              <div className="absolute right-2.5 top-1/2 -translate-y-1/2 flex flex-col items-center justify-center text-gray-400 pointer-events-auto">
                <button
                  type="button"
                  onClick={() =>
                    setFormData((prev) => ({
                      ...prev,
                      num_goals: Math.min(10, (prev.num_goals || 0) + 1),
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

        {/* Communication Weight Slider (Custom Orange Track) */}
        <div>
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
            className="w-full h-1.5 rounded-full appearance-none cursor-pointer accent-[#191919]"
          />
          <div className="flex items-center justify-between mt-1 text-xs font-semibold text-gray-500">
            <span>Knowledge Focus</span>
            <span>Communication Focus</span>
          </div>
        </div>

        {/* Candidates Section */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <label className="block text-sm font-medium text-gray-900">
              Candidates <span className="text-red-500">*</span>
            </label>
            <button
              type="button"
              onClick={onAddCandidate}
              className="px-3 py-1.5 bg-gray-100 hover:bg-gray-200 text-gray-900 rounded-lg text-xs font-bold flex items-center gap-1.5 transition-colors cursor-pointer"
            >
              <Plus className="w-3.5 h-3.5" /> Add Candidate
            </button>
          </div>

          <div className="space-y-3">
            {candidates.map((candidate, index) => (
              <div key={index} className="flex items-start gap-3 relative group">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3 w-full">
                  <input
                    type="email"
                    placeholder="Email address"
                    value={candidate.email}
                    onChange={(e) =>
                      onCandidateChange(index, "email", e.target.value)
                    }
                    className="w-full px-3 py-2 bg-white border border-gray-200 rounded-xl text-sm text-gray-900 font-medium placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-900/10 focus:border-gray-900 transition-all"
                    required
                  />
                  <input
                    type="text"
                    placeholder="First name"
                    value={candidate.first_name}
                    onChange={(e) =>
                      onCandidateChange(index, "first_name", e.target.value)
                    }
                    className="w-full px-3 py-2 bg-white border border-gray-200 rounded-xl text-sm text-gray-900 font-medium placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-900/10 focus:border-gray-900 transition-all"
                  />
                  <input
                    type="text"
                    placeholder="Last name"
                    value={candidate.last_name}
                    onChange={(e) =>
                      onCandidateChange(index, "last_name", e.target.value)
                    }
                    className="w-full px-3 py-2 bg-white border border-gray-200 rounded-xl text-sm text-gray-900 font-medium placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-900/10 focus:border-gray-900 transition-all"
                  />
                </div>
                {candidates.length > 1 && (
                  <button
                    type="button"
                    onClick={() => onRemoveCandidate(index)}
                    className="w-10 h-[42px] bg-red-500 border border-gray-200 rounded-xl flex items-center justify-center text-white hover:text-red-100 hover:border-red-200 hover:bg-red-700 transition-all cursor-pointer shrink-0"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>

        <div>
          <p className="text-[13px] text-gray-500 font-medium mb-8 leading-relaxed">
            The candidates will receive LiveKit voice access tokens. Make sure
            the difficulty and duration accurately reflect your expectations for
            this role.
          </p>

          <button
            type="submit"
            className="w-full bg-[#191919] hover:bg-black text-white rounded-xl py-2.5 text-base font-medium transition-all shadow-lg shadow-black/10 cursor-pointer flex items-center justify-center"
          >
            Continue
          </button>
        </div>
      </form>
    </>
  );
};
