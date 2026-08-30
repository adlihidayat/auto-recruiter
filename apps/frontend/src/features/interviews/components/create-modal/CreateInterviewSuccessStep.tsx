/**
 * What: Step 3 Success / Publish View for created interviews.
 * Why: Displays campaign share links in Interview Detail style, featured rosette award badge, and completion actions.
 * Boundaries: Final step in Create Interview Modal.
 */

import React from "react";
import { Copy, Check, ExternalLink, Link as LinkIcon } from "lucide-react";
import { InterviewFormData } from "./types";
import { GoldenRosetteMedal } from "./GoldenRosetteMedal";

interface CreateInterviewSuccessStepProps {
  formData: InterviewFormData;
  displayCandidates: Array<{
    first_name: string;
    last_name: string;
    email: string;
    room_token: string;
  }>;
  copiedCandidateId: string | null;
  onCopyLink: (candidateId: string, token: string) => void;
  onSeeDetail: () => void;
  onDone: () => void;
}

export const CreateInterviewSuccessStep: React.FC<CreateInterviewSuccessStepProps> = ({
  formData,
  displayCandidates,
  copiedCandidateId,
  onCopyLink,
  onSeeDetail,
  onDone,
}) => {
  return (
    <div className="relative space-y-4 animate-in fade-in zoom-in-95 duration-200 w-130">
      {/* Modal Title & Subtitle */}
      <div>
        <h2 className="text-xl font-bold text-gray-900 tracking-tight">
          Interview Created
        </h2>
        <p className="text-xs text-gray-500 font-medium mt-1">
          Candidates can now access LiveKit AI voice interview rooms.
        </p>
      </div>

      {/* Featured Hero Banner Card (Twin Screenshot Style + Golden Rosette Award Badge) */}
      <div className="bg-[#F8F8F6] border border-gray-200/80 rounded-3xl p-6 relative overflow-hidden flex flex-col md:flex-row items-start md:items-center justify-between gap-6 shadow-2xs">
        <div className="space-y-4 flex-1">
          {/* Icon Badge */}
          <div className="w-10 h-10 rounded-2xl bg-white border border-gray-200/80 flex items-center justify-center text-xl shadow-2xs">
            {formData.icon}
          </div>

          <div>
            <h3 className="text-lg font-bold text-gray-900 leading-tight">
              {formData.job_name || "Senior Backend Engineer"}
            </h3>
            <p className="text-xs text-gray-500 font-medium mt-1 line-clamp-2 max-w-sm">
              {formData.job_description ||
                "AI-powered candidate evaluation campaign."}
            </p>
          </div>

          {/* Meta stats bottom left */}
          <div className="flex items-center gap-6 pt-1">
            <div>
              <span className="text-sm font-extrabold text-gray-900">
                {displayCandidates.length}
              </span>
              <span className="text-xs text-gray-500 font-medium ml-1.5">
                candidates
              </span>
            </div>
            <div>
              <span className="text-sm font-extrabold text-gray-900">
                {formData.total_duration_minutes}m
              </span>
              <span className="text-xs text-gray-500 font-medium ml-1.5">
                duration
              </span>
            </div>
          </div>
        </div>

        {/* Right Side: Golden Star Rosette Award Ribbon Medal */}
        <GoldenRosetteMedal />
      </div>

      {/* Candidate Share Section */}
      <div className="space-y-3">
        <div className="flex items-center justify-between px-1">
          <span className="text-sm font-bold text-gray-900">
            Share candidate links
          </span>
          {/* Toggle Switch */}
          <div className="w-10 h-6 bg-[#0080FF] rounded-full p-1 flex items-center justify-end cursor-pointer shadow-inner">
            <div className="w-4 h-4 bg-white rounded-full shadow-md" />
          </div>
        </div>

        {/* Candidates List (Interview Detail style) */}
        <div className="space-y-2 max-h-56 overflow-y-auto custom-scrollbar pr-1">
          {displayCandidates.map((c, i) => (
            <div
              key={i}
              className="flex items-center justify-between p-3 bg-white border border-gray-200/80 rounded-2xl shadow-2xs hover:border-gray-300 transition-all"
            >
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center text-xs font-bold text-gray-700 uppercase">
                  {c.first_name?.[0] || "C"}
                  {c.last_name?.[0] || ""}
                </div>
                <div>
                  <div className="text-xs font-bold text-gray-900">
                    {c.first_name} {c.last_name}
                  </div>
                  <div className="text-[11px] text-gray-400 font-mono">
                    {c.email}
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <div className="flex items-center gap-1 bg-gray-50 border border-gray-200 px-2.5 py-1 rounded-lg text-xs font-mono text-gray-600 max-w-[130px] truncate">
                  <LinkIcon className="w-3 h-3 text-gray-400 shrink-0" />
                  <span className="truncate">interview/{c.room_token}</span>
                </div>
                <button
                  type="button"
                  onClick={() => onCopyLink(`cand-${i}`, c.room_token)}
                  className="px-2.5 py-1.5 bg-gray-100 hover:bg-gray-200 text-gray-900 rounded-lg text-xs font-bold transition-all flex items-center gap-1 cursor-pointer shrink-0"
                >
                  {copiedCandidateId === `cand-${i}` ? (
                    <>
                      <Check className="w-3 h-3 text-emerald-600" /> Copied
                    </>
                  ) : (
                    <>
                      <Copy className="w-3 h-3 text-gray-600" /> Copy
                    </>
                  )}
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Modal Footer Actions (Equal width side-by-side) */}
      <div className="grid grid-cols-2 gap-3 pt-2">
        <button
          type="button"
          onClick={onSeeDetail}
          className="w-full bg-[#F4F4F5] hover:bg-gray-200 text-gray-900 rounded-2xl py-3 text-sm font-bold transition-all flex items-center justify-center gap-2 cursor-pointer"
        >
          See detail <ExternalLink className="w-4 h-4 text-gray-600" />
        </button>
        <button
          type="button"
          onClick={onDone}
          className="w-full bg-[#191919] hover:bg-black text-white rounded-2xl py-3 text-sm font-bold transition-all shadow-md shadow-black/10 flex items-center justify-center cursor-pointer"
        >
          Done
        </button>
      </div>
    </div>
  );
};
