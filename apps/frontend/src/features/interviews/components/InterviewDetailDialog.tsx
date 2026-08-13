"use client";

/**
 * What: Modal drawer displaying detailed interview campaign info and candidate list.
 * Why: Per frontend rules in GEMINI.md, interview details open as a popup driven by '?interview=<id>' search params.
 * Boundaries: Operates as a Client Component driven by URL params; does not navigate away from the current page.
 */

import React, { useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Image from "next/image";
import {
  CalendarDays,
  User,
  Info,
  TrendingUp,
  ChevronDown,
  MoreVertical,
  SlidersHorizontal,
  X,
  Share2,
  Pencil,
  Trash2,
  CircleGauge,
} from "lucide-react";
import { InterviewCampaign } from "../types";

interface InterviewDetailDialogProps {
  interviewCampaignsList: InterviewCampaign[];
}

export default function InterviewDetailDialog({
  interviewCampaignsList,
}: InterviewDetailDialogProps) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const activeInterviewId = searchParams.get("interview");

  const [isDescriptionExpanded, setIsDescriptionExpanded] = useState(true);

  useEffect(() => {
    if (activeInterviewId) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
    return () => {
      document.body.style.overflow = "";
    };
  }, [activeInterviewId]);

  if (!activeInterviewId) return null;

  const targetCampaign = interviewCampaignsList.find(
    (campaignItem) => campaignItem.id === activeInterviewId,
  );

  if (!targetCampaign) return null;

  const handleCloseDialog = () => {
    const nextSearchParams = new URLSearchParams(searchParams.toString());
    nextSearchParams.delete("interview");
    const newQueryString = nextSearchParams.toString();
    const destinationUrl = newQueryString ? `/?${newQueryString}` : "/";
    router.push(destinationUrl, { scroll: false });
  };

  const baseCandidates = [
    {
      name: "andika saputra",
      email: "andika.saputra@company.com",
      status: "Done",
      img: "https://i.pravatar.cc/150?u=1",
    },
    {
      name: "sari putri",
      email: "sari.putri@example.com",
      status: "Done",
      img: "https://i.pravatar.cc/150?u=2",
    },
    {
      name: "Fahril arrasyid",
      email: "Fahril-arrasyid@gmail.com",
      status: "On-Interview",
      img: "https://i.pravatar.cc/150?u=3",
    },
    {
      name: "rizky hadi",
      email: "rizky.hadi@mail.com",
      status: "On-Interview",
      img: "https://i.pravatar.cc/150?u=4",
    },
    {
      name: "ijal dilan",
      email: "ijaldilan@gmail.com",
      status: "Not-started",
      img: "https://i.pravatar.cc/150?u=5",
    },
    {
      name: "lina maulani",
      email: "lina.maulani@gmail.com",
      status: "Not-started",
      img: "https://i.pravatar.cc/150?u=6",
    },
  ];

  const mockCandidates = Array(4)
    .fill(baseCandidates)
    .flat()
    .map((c, i) => ({
      ...c,
      email: `${i + 1}.${c.email}`,
    }));

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-black/20 animate-in fade-in duration-200">
      {/* Clickable overlay to close */}
      <div className="absolute inset-0" onClick={handleCloseDialog} />

      {/* Drawer Container */}
      <div className="relative w-full max-w-162.5 h-full bg-white shadow-2xl flex flex-col animate-in slide-in-from-right duration-300">
        {/* Drawer Header */}
        <div className="px-7 py-4.5 flex items-center justify-between border-b border-[#F1F1F1]">
          <div className="flex items-center gap-3">
            <button
              onClick={handleCloseDialog}
              className="w-7 h-7 rounded-lg text-[#616161] hover:bg-gray-200 hover:text-[#272727] transition-colors flex items-center justify-center"
              title="Close"
            >
              <X className="w-4 h-4" />
            </button>
            <div className="h-4 w-px bg-[#F1F1F1]" />
            <span className="text-sm px-2 font-medium text-[#616161]">
              Interview Detail
            </span>
          </div>
          <div className="flex items-center gap-2">
            <button
              className="w-7 h-7 rounded-lg text-[#616161] hover:bg-gray-200 hover:text-[#272727] transition-colors flex items-center justify-center"
              title="Share"
            >
              <Share2 className="w-4 h-4" />
            </button>
            <button
              className="w-7 h-7 rounded-lg text-[#616161] hover:bg-gray-200 hover:text-[#272727] transition-colors flex items-center justify-center"
              title="Edit"
            >
              <Pencil className="w-4 h-4" />
            </button>
            <button
              className="w-7 h-7 rounded-lg text-[#616161] hover:bg-red-50 hover:text-red-600 transition-colors flex items-center justify-center"
              title="Delete"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Scrollable Content */}
        <div className="flex-1 overflow-y-auto p-7.5">
          {/* Title and Pills */}
          <div className="mb-7.5">
            <h2 className="text-xl font-semibold text-[#272727] mb-2.5">
              Machine Learning Engineer
            </h2>
            <div className="flex items-center gap-3">
              <span className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-[#F4F4F4] text-[#2563EB] text-xs font-medium">
                <CalendarDays className="w-3.5 h-3.5" /> 12/12/2026
              </span>
              <span className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#F4F4F4] text-[#DC2626] text-xs font-medium">
                <User className="w-3.5 h-3.5" /> Dhiya Adli Hidayat
              </span>
            </div>
          </div>

          {/* Status Cards */}
          <div className="grid grid-cols-2 gap-4 mb-7.5">
            <div className="border border-[#F1F1F1] rounded-2xl p-1">
              <div className="flex items-center justify-between p-2.5">
                <div className="flex items-center gap-2 text-[#616161] text-sm font-medium">
                  <User className="w-4 h-4" /> Interview Status
                </div>
                <Info className="w-4 h-4 text-[#616161]" />
              </div>
              <div className="bg-[#FBFBFB] rounded-md p-2.5">
                <div className="text-2xl font-semibold text-[#272727] mb-2.5">
                  89 / 127
                </div>

                <div className="flex items-center gap-1 text-xs font-medium text-[#059669] mb-2.5">
                  <TrendingUp className="w-3.5 h-3.5" /> +8.4%{" "}
                  <span className="text-[#616161]">Newly hired</span>
                </div>

                <div className="flex items-center gap-1 h-2">
                  <div className="h-full bg-[#FE6100] rounded-full w-[60%]" />
                  <div className="h-full bg-[#FFD3B8] rounded-full w-[15%]" />
                  <div className="h-full bg-[#E9E9E9] rounded-full w-[25%]" />
                </div>
              </div>
            </div>{" "}
            <div className="border border-[#F1F1F1] rounded-2xl p-1">
              <div className="flex items-center justify-between p-2.5">
                <div className="flex items-center gap-2 text-[#616161] text-sm font-medium">
                  <CircleGauge className="w-4 h-4" /> Passing Rate
                </div>
                <Info className="w-4 h-4 text-[#616161]" />
              </div>
              <div className="bg-[#FBFBFB] rounded-md p-2.5">
                <div className="text-2xl font-semibold text-[#272727] mb-2.5">
                  -/-
                </div>

                <div className="flex items-center gap-1 text-xs font-medium text-[#059669] mb-2.5">
                  {/* <TrendingUp className="w-3.5 h-3.5" /> +8.4%{" "} */}
                  <span className="text-[#616161]">Not finished yet</span>
                </div>

                <div className="flex items-center gap-1 h-2">
                  {/* <div className="h-full bg-[#FE6100] rounded-full w-[0%]" />
                  <div className="h-full bg-[#FFD3B8] rounded-full w-[0%]" /> */}
                  <div className="h-full bg-[#E9E9E9] rounded-full w-full" />
                </div>
              </div>
            </div>
          </div>

          {/* Description Section */}
          <div className="mb-7.5 relative">
            <button
              onClick={() => setIsDescriptionExpanded(!isDescriptionExpanded)}
              className="flex items-center gap-2 text-base font-semibold text-[#272727] mb-3"
            >
              Description{" "}
              <ChevronDown
                className={`w-4 h-4 transition-transform ${isDescriptionExpanded ? "rotate-180" : ""}`}
              />
            </button>
            <p
              className={`text-sm font-medium text-[#616161] leading-relaxed overflow-y-hidden ${isDescriptionExpanded ? "h-20" : "h-max"}`}
            >
              About ACME Corp : At ACME Corporation, We Pride Ourselves On Being
              The World&apos;s Leading Purveyor Of Highly Inventive (And
              Sometimes Explosive) Gadgets. We Are Actively Expanding Our
              Digital Infrastructure To Support Our Growing Catalog. We&apos;re
              Looking For An Innovative AI Engineer Who Can Bridge The Gap
              Between Complex Machine Learning Models And Intuitive Web
              Applications. About ACME Corp : At ACME Corporation, We Pride
              Ourselves On Being The World&apos;s Leading Purveyor Of Highly
              Inventive (And Sometimes Explosive) Gadgets. We Are Actively
              Expanding Our Digital Infrastructure To Support Our Growing
              Catalog. We&apos;re Looking For An Innovative AI Engineer Who Can
              Bridge The Gap Between Complex Machine Learning Models And
              Intuitive Web Applications. About ACME Corp : At ACME Corporation,
              We Pride Ourselves On Being The World&apos;s Leading Purveyor Of
              Highly Inventive (And Sometimes Explosive) Gadgets. We Are
              Actively Expanding Our Digital Infrastructure To Support Our
              Growing Catalog. We&apos;re Looking For An Innovative AI Engineer
              Who Can Bridge The Gap Between Complex Machine Learning Models And
              Intuitive Web Applications. ...
            </p>
            {isDescriptionExpanded && (
              <div className="absolute bottom-0 left-0 right-0 h-16 bg-linear-to-t from-white to-transparent pointer-events-none" />
            )}
          </div>

          <div className="flex items-center justify-between mb-3">
            <h3 className="text-base font-semibold text-[#272727]">
              Candidates (127)
            </h3>
            <button className="text-[#616161] hover:text-[#272727] transition-colors">
              <SlidersHorizontal className="w-4 h-4" />
            </button>
          </div>
          {/* Candidates List */}
          <div className="border border-[#F1F1F1] rounded-[14px] overflow-y-auto max-h-95 mb-8">
            {/* Candidates List Header */}
            {mockCandidates.map((candidate, idx) => (
              <div
                key={idx}
                className={`px-2.5 py-2.5 flex items-center justify-between ${idx !== mockCandidates.length - 1 ? "border-b border-[#F1F1F1]" : ""}`}
              >
                <div className="flex items-center gap-2.5">
                  <div className="w-9.5 h-9.5 rounded-full bg-gray-200 overflow-hidden shrink-0 relative">
                    <Image
                      src={candidate.img}
                      alt={candidate.name}
                      fill
                      className="object-cover"
                      unoptimized
                    />
                  </div>
                  <div>
                    <div className="text-sm font-medium text-[#272727]">
                      {candidate.name}
                    </div>
                    <div className="text-sm font-medium text-[#616161]">
                      {candidate.email}
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-4">
                  {candidate.status === "Done" && (
                    <span className="px-3 py-1 bg-[#DCFCE7] text-[#16A34A] rounded-full text-xs font-medium">
                      Done
                    </span>
                  )}
                  {candidate.status === "On-Interview" && (
                    <span className="px-3 py-1 bg-[#EFF6FF] text-[#2563EB] rounded-full text-xs font-medium">
                      On-Interview
                    </span>
                  )}
                  {candidate.status === "Not-started" && (
                    <span className="px-3 py-1 bg-[#F4F4F4] text-[#616161] rounded-full text-xs font-medium">
                      Not-started
                    </span>
                  )}

                  <button className="text-[#B8B8B8] hover:text-[#616161] transition-colors">
                    <MoreVertical className="w-5 h-5" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
