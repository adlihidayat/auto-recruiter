/**
 * What: Step 1 Form View for interview creation.
 * Why: Renders exact original interview form layout from single-file commit.
 * Boundaries: Emits submit event to trigger loading simulation.
 */

import React from "react";
import { Plus, Trash2, ChevronDown, ChevronUp, Globe, X } from "lucide-react";
import { CandidateInput, InterviewFormData } from "./types";
import { EMOJIS } from "./constants";

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
    field: "email" | "first_name" | "last_name",
    value: string,
  ) => void;
}

export const CreateInterviewFormStep: React.FC<
  CreateInterviewFormStepProps
> = ({
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
      <div className="mb-4 pb-4 border-b border-gray-200 pr-8">
        <h2 className="text-base font-semibold text-gray-900 tracking-tight mb-0">
          Create interview
        </h2>
        <p className="text-sm text-gray-500 font-medium">
          Set up a new AI interview campaign and configure evaluation goals.
        </p>
      </div>

      {error && (
        <div className="mb-6 p-4 rounded-xl bg-red-50 text-sm font-medium text-red-600 border border-red-100">
          {error}
        </div>
      )}

      <form onSubmit={onSubmit} className="space-y-6">
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
              <span className=" -translate-y-1 z-0">{formData.icon}</span>
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
                    total_duration_minutes: parseInt(e.target.value) || 5,
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

        {/* Candidates Section */}
        <div className="">
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
                      onCandidateChange(index, "email", e.target.value)
                    }
                    className="w-full px-3 py-1.5 bg-white border border-gray-200 rounded-lg text-sm text-gray-900 font-medium placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-900/10 focus:border-gray-900 transition-all"
                    required
                  />
                  <input
                    type="text"
                    placeholder="First name"
                    value={candidate.first_name}
                    onChange={(e) =>
                      onCandidateChange(index, "first_name", e.target.value)
                    }
                    className="w-full px-3 py-1.5 bg-white border border-gray-200 rounded-lg text-sm text-gray-900 font-medium placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-900/10 focus:border-gray-900 transition-all"
                  />
                  <input
                    type="text"
                    placeholder="Last name"
                    value={candidate.last_name}
                    onChange={(e) =>
                      onCandidateChange(index, "last_name", e.target.value)
                    }
                    className="w-full px-3 py-1.5 bg-white border border-gray-200 rounded-lg text-sm text-gray-900 font-medium placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-900/10 focus:border-gray-900 transition-all"
                  />
                </div>
                {candidates.length > 1 && (
                  <button
                    type="button"
                    onClick={() => onRemoveCandidate(index)}
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
            The candidates will receive LiveKit voice access tokens. Make sure
            the difficulty and duration accurately reflect your expectations for
            this role.
          </p>

          <button
            type="submit"
            className="w-full bg-[#191919] text-sm hover:bg-black text-white rounded-xl py-2.5 font-medium transition-all shadow-lg shadow-black/10 cursor-pointer flex items-center justify-center"
          >
            Continue
          </button>
        </div>
      </form>
    </>
  );
};
