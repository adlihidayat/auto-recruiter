"use client";

import React from "react";
import { Info, FileText } from "lucide-react";

export default function CandidateReportView() {
  const candidateData = {
    name: "Dhiya Adli Hidayat",
    email: "dhiyaadlihidayat@gmai.com",
    status: "Hold",
    statusReason: "Reason here asdasdas",
    overallScore: 87.5,
    overallScoreSubtext: "placeholder word",
    shortSummaryParagraphs: [
      "We Pride Ourselves On Being The World's Leading Purveyor Of Highly Inventive (And Sometimes Explosive) Gadgets. We Are Actively Expanding Our Digital Infrastructure To Support Our Growing Catalog. We're Looking For An Innovative AI Engineer Who Can Bridge The Gap Between Complex Machine Learning Models And Intuitive Web Applications.",
      "The Role: As Our Senior AI Engineer, You Will Be The Brain Behind Our Next-Generation Product Recommendation And Customer Support Systems. You Will Build End-To-End Solutions, From Training NLP Models That Understand Customer Intent, To AI Engineer Who Can Bridge The Gap Between Complex Machine Learning Models And Intuitiv",
    ],
    highlightBars: [
      { text: "We Pride Ourselves On Being The", type: "pass" },
      {
        text: "Understand Customer Intent, To Deploying Them On High-Performance Web Interf",
        type: "pass",
      },
      {
        text: "Upport Systems. You Will Build End-To-End Solutio",
        type: "fail",
      },
      {
        text: "Ctively Expanding Our Digital Infrastructure To Support Our Gro",
        type: "fail",
      },
    ],
    knowledgeScore: {
      score: "60%",
      items: [
        { label: "Goal 1", status: "Failed", type: "fail" },
        { label: "Goal 2", status: "Pass", type: "pass" },
        { label: "Goal 3", status: "Pass", type: "pass" },
        { label: "Goal 4", status: "Pass", type: "pass" },
        { label: "Goal 5", status: "Failed", type: "fail" },
      ],
      note: "The World's Leading Purveyor Of Highly Inventive (And Sometimes Explosive) Gadget...",
    },
    communicationScore: {
      score: "75%",
      items: [
        { label: "Active Listening", status: "Failed", type: "fail" },
        { label: "Structure", status: "Pass", type: "pass" },
        { label: "Assertiveness", status: "Pass", type: "pass" },
        { label: "Clarity", status: "Pass", type: "pass" },
      ],
      note: "The World's Leading Purveyor Of Highly Inventive (And Sometimes Explosive) Gadget...",
    },
    interactions: [
      {
        turn: "[T1]",
        speaker: "Interviewer",
        role: "interviewer",
        text: "Welcome To The Interview. Hello! This Interview Is ...",
      },
      {
        turn: "[T2]",
        speaker: "Candidate",
        role: "candidate",
        text: "The Brain Behind Our Next-Generation Product Recommendation And Customer Support Systems. You Will Build End-To-End Solutions, From Training NLP Models That Understand Customer Intent, To",
      },
      {
        turn: "[T3]",
        speaker: "Interviewer",
        role: "interviewer",
        text: "Karena Selalu Ada Pro-Kontra Dalam Cerita-Cerita Yang Berkaitan Dengan Dunia Dimensional. Dalam Hal Ini Narasumber Hanya Ingin Berbagi Kisahnya Agar Kita Bisa Mengambil Banyak Pelajaran Dari Kisah-Kisah Tersebut.",
      },
    ],
  };

  return (
    <div className="max-w-350 mx-auto px-6 py-6 pb-20 font-sans">
      {/* Top 2-Column Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 mb-6">
        {/* Left Card: Candidate Info & Short Summary */}
        <div className="lg:col-span-6 bg-white rounded-[28px] border border-[#F1F1F1] p-7 shadow-2xs flex flex-col justify-between">
          <div>
            {/* Profile Header */}
            <div className="flex items-center gap-4 pb-5 border-b border-[#F1F1F1]">
              <div className="w-10 h-10 rounded-full bg-[#EFEFEF] shrink-0" />
              <div>
                <h2 className="text-base font-bold text-[#272727] leading-snug">
                  {candidateData.name}
                </h2>
                <p className="text-sm text-[#616161]">{candidateData.email}</p>
              </div>
            </div>

            {/* Short Summary Section */}
            <div className="pt-5 mb-6">
              <h3 className="text-base font-semibold text-[#272727] mb-3">
                Short Summary
              </h3>
              <div className="space-y-3 text-sm font-medium text-[#616161] leading-relaxed">
                {candidateData.shortSummaryParagraphs.map((para, idx) => (
                  <p key={idx}>{para}</p>
                ))}
              </div>
            </div>

            {/* Vertical Highlight Bars */}
            <div className="space-y-2.5">
              {candidateData.highlightBars.map((bar, idx) => (
                <div
                  key={idx}
                  className="flex items-center gap-3 text-sm text-[#616161] font-medium"
                >
                  <div
                    className={`w-1 h-6 rounded-full shrink-0 ${
                      bar.type === "pass" ? "bg-[#00C835]" : "bg-[#D30609]"
                    }`}
                  />
                  <span className="truncate">{bar.text}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Card: Status & Score Matrix */}
        <div className="lg:col-span-6 bg-white rounded-[28px] border border-[#F1F1F1] p-7 shadow-2xs flex flex-col justify-between">
          <div>
            {/* Top Status & Overall Score Header */}
            <div className="flex items-start justify-between pb-6 border-b border-[#F1F1F1]">
              {/* Left Status Block */}
              <div className="">
                <span className="text-sm font-medium text-[#272727] uppercase tracking-wider block mb-2.5">
                  Status
                </span>
                <div className="flex items-center gap-2.5 mb-2.5">
                  <div className="w-2.5 h-7 bg-[#DC2626] rounded-full shrink-0" />
                  <span className="text-2xl font-semibold text-[#272727]">
                    {candidateData.status}
                  </span>
                </div>
                <p className="text-sm font-medium text-[#616161]">
                  {candidateData.statusReason}
                </p>
              </div>

              {/* Right Overall Score Block */}
              <div className="text-right">
                <span className="text-sm font-medium text-[#272727] uppercase tracking-wider block mb-2.5">
                  Overall Score
                </span>
                <span className="text-2xl font-semibold text-[#272727] block leading-none mb-2.5">
                  {candidateData.overallScore}
                </span>
                <p className="text-sm font-medium text-[#616161]">
                  {candidateData.overallScoreSubtext}
                </p>
              </div>
            </div>

            {/* Dual Score Columns */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-6">
              {/* Column 1: Knowledge Score */}
              <div className="flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between mb-2.5">
                    <span className="text-sm font-medium text-[#272727]">
                      Knowledge Score
                    </span>
                    <Info className="w-3.5 h-3.5 text-[#616161] cursor-pointer" />
                  </div>
                  <div className="text-2xl font-bold text-[#272727] mb-4.5">
                    {candidateData.knowledgeScore.score}
                  </div>

                  {/* Goal List */}
                  <div className="space-y-2.5 mb-4.5">
                    {candidateData.knowledgeScore.items.map((item, idx) => (
                      <div
                        key={idx}
                        className="flex items-center justify-between text-sm"
                      >
                        <div className="flex items-center gap-2 text-[#272727] font-medium">
                          <div className="w-1.5 h-1.5 rounded-full bg-[#FE6100] shrink-0" />
                          <span>{item.label}</span>
                        </div>
                        <div className="flex-1 border-b border-dotted border-[#D9D9D9] mx-2" />
                        <span
                          className={`font-medium ${
                            item.type === "pass"
                              ? "text-[#22C55E]"
                              : "text-[#DC2626]"
                          }`}
                        >
                          {item.status}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <p className="text-xs font-medium text-[#FE6100] leading-snug mb-4.5">
                    {candidateData.knowledgeScore.note}
                  </p>
                  <button className="w-full flex items-center justify-end gap-1.5 text-sm font-bold text-[#272727] underline hover:text-black transition-colors cursor-pointer">
                    <FileText className="w-3.5 h-3.5" />
                    See Detail
                  </button>
                </div>
              </div>

              {/* Column 2: Communication Score */}
              <div className="flex flex-col justify-between md:border-l md:border-[#F1F1F1] md:pl-6">
                <div>
                  <div className="flex items-center justify-between mb-2.5">
                    <span className="text-sm font-medium text-[#272727]">
                      Communication Score
                    </span>
                    <Info className="w-3.5 h-3.5 text-[#616161] cursor-pointer" />
                  </div>
                  <div className="text-2xl font-bold text-[#272727] mb-4.5">
                    {candidateData.communicationScore.score}
                  </div>

                  {/* Signal List */}
                  <div className="space-y-2.5 mb-4.5">
                    {candidateData.communicationScore.items.map((item, idx) => (
                      <div
                        key={idx}
                        className="flex items-center justify-between text-sm"
                      >
                        <div className="flex items-center gap-2 text-[#272727] font-medium">
                          <div className="w-1.5 h-1.5 rounded-full bg-[#FE6100] shrink-0" />
                          <span>{item.label}</span>
                        </div>
                        <div className="flex-1 border-b border-dotted border-[#D9D9D9] mx-2" />
                        <span
                          className={`font-medium ${
                            item.type === "pass"
                              ? "text-[#22C55E]"
                              : "text-[#DC2626]"
                          }`}
                        >
                          {item.status}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <p className="text-[11px] font-medium text-[#FE6100] leading-snug mb-4.5">
                    {candidateData.communicationScore.note}
                  </p>
                  <button className="w-full flex items-center justify-end gap-1.5 text-sm font-bold text-[#272727] underline hover:text-black transition-colors cursor-pointer">
                    <FileText className="w-3.5 h-3.5" />
                    See Detail
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Card: Interview Interaction */}
      <div className="bg-white rounded-[28px] border border-[#F1F1F1] p-7 shadow-2xs">
        <h3 className="text-base font-semibold text-[#272727] pb-4 mb-6 border-b border-[#F1F1F1]">
          Interview Interaction
        </h3>

        <div className="relative pl-1">
          {/* Continuous vertical timeline line */}
          <div className="absolute top-2.5 bottom-6 left-12 w-px bg-[#D9D9D9]" />

          <div className="space-y-6">
            {candidateData.interactions.map((interaction, idx) => (
              <div key={idx} className="relative flex items-start gap-4">
                {/* Turn Label */}
                <span className="w-6 shrink-0 font-semibold text-base text-[#272727] pt-0.5">
                  {interaction.turn}
                </span>

                {/* Timeline Bullet Dot */}
                <div className="relative z-10 flex items-center justify-center pt-1 shrink-0">
                  <div
                    className={`w-2.5 h-2.5 rounded-full ${
                      interaction.role === "candidate"
                        ? "bg-[#FE6100]"
                        : "bg-[#B8B8B8]"
                    }`}
                  />
                </div>

                {/* Speaker & Transcript Content */}
                <div className="flex-1">
                  <span className="font-semibold text-base text-[#272727]">
                    {interaction.speaker}
                  </span>
                  <p className="text-sm font-medium text-[#616161] leading-relaxed mt-1">
                    {interaction.text}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
