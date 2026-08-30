/**
 * What: Step 3 Publish Success View for interview creation.
 * Why: Renders exact original layout curated by user prior to component splitting.
 * Boundaries: Step 3 in the Create Interview Modal workflow.
 */

import React from "react";
import { Link as LinkIcon, ExternalLink, Check, Copy } from "lucide-react";
import { InterviewFormData } from "./types";

interface DisplayCandidate {
  first_name: string;
  last_name: string;
  email: string;
  room_token: string;
}

interface CreateInterviewSuccessStepProps {
  formData: InterviewFormData;
  displayCandidates: DisplayCandidate[];
  copiedCandidateId: string | null;
  onCopyLink: (candidateId: string, token: string) => void;
  onSeeDetail: () => void;
  onDone: () => void;
}

export const CreateInterviewSuccessStep: React.FC<
  CreateInterviewSuccessStepProps
> = ({
  displayCandidates,
  copiedCandidateId,
  onCopyLink,
  onSeeDetail,
  onDone,
}) => {
  return (
    <div className="animate-in fade-in zoom-in-95 duration-200">
      <div className=" relative rounded-3xl p-6 relative overflow-hidden flex justify-center gap-6 pt-14 pb-32">
        <div className=" absolute bottom-6 text-center">
          <h2 className="text-xl font-semibold text-gray-900 tracking-tight">
            Interview Created
          </h2>
          <p className="text-xs text-gray-500 font-medium mt-1">
            Candidates can now access LiveKit AI voice interview rooms.
          </p>
        </div>
        {/* Golden Star Rosette Award Ribbon Medal (Matching Image 1 Reference) */}
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
      <div className="space-y-3 mb-6">
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
            {displayCandidates.map((c, idx) => {
              const candidateName =
                c.first_name || c.last_name
                  ? `${c.first_name || ""} ${c.last_name || ""}`.trim()
                  : `Candidate ${idx + 1}`;

              const tokenValue = c.room_token || `token_${idx}`;
              const origin =
                typeof window !== "undefined"
                  ? window.location.origin
                  : "http://localhost:3000";
              const roomUrl = `${origin}/interview?token=${tokenValue}`;
              const candidateId = `cand-${idx}`;
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
                      onClick={() => onCopyLink(candidateId, tokenValue)}
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
          onClick={onSeeDetail}
          className="px-3 py-1.5 flex-1 bg-white border border-gray-200 hover:bg-gray-200 text-gray-900 text-sm font-medium rounded-md transition-colors cursor-pointer flex items-center justify-center gap-1.5"
        >
          <span>See detail</span>
          <ExternalLink className="w-4 h-4 text-gray-600" />
        </button>
        <button
          type="button"
          onClick={onDone}
          className="px-3 py-1.5 flex-1 bg-[#191919] hover:bg-black text-white text-sm font-medium rounded-md transition-colors cursor-pointer flex items-center justify-center"
        >
          Done
        </button>
      </div>
    </div>
  );
};
