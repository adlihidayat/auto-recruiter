"use client";

/**
 * What: Main HR Recruiting Dashboard client component container.
 * Why: Manages active campaign state, filtering, creation modal toggles, and modal detail views.
 * Boundaries: Operates on local client state until connected to FastAPI backend OpenAPI client.
 */

import React, { useState, useEffect } from "react";
import {
  Search,
  Calendar,
  Layers,
  MoreVertical,
  ChevronDown,
  Check,
  Rows4,
  FileCheckCorner,
  SquircleDashed,
  RollerCoaster,
  TrendingUp,
  TrendingDown,
  Trash2,
} from "lucide-react";
import { InterviewCampaign } from "../types";
import {
  getInterviewsApi,
  getCandidatesForInterviewApi,
  deleteInterviewApi,
} from "@/lib/api/client";
import { mapBackendInterviewToCampaign } from "../utils";
import { useRouter } from "next/navigation";
import Image from "next/image";
import Link from "next/link";
import { RowActionPopover } from "./dashboard-popups/RowActionPopover";
import {
  StatusFilterPopover,
  StatusFilterType,
} from "./dashboard-popups/StatusFilterPopover";
import {
  ViewFilterPopover,
  ViewFilterType,
} from "./dashboard-popups/ViewFilterPopover";
import { DepartmentFilterPopover } from "./dashboard-popups/DepartmentFilterPopover";
import { CompareFilterPopover } from "./dashboard-popups/CompareFilterPopover";
import { MetricsFilterPopover } from "./dashboard-popups/MetricsFilterPopover";

const INITIAL_MOCK_CAMPAIGNS: InterviewCampaign[] = Array(12)
  .fill(null)
  .map((_, i) => ({
    id: `campaign-${i}`,
    jobTitle:
      i % 2 === 0
        ? "Marketing Lead officer"
        : i % 3 === 0
          ? "Product manager"
          : "Engineer CTO officer",
    departmentName: "Core",
    targetSeniority: "Senior",
    currentPipelineStage: "COMPLETED",
    activeCandidateCount: 23,
    evaluatedCandidateCount: 11,
    createdAtTimestamp: "11/06/2026",
    agentSummary:
      "Understanding of the following non-negotiable architectural boundaries for t...",
    questionSuite: [],
    candidatesList: [],
  }));

const MONTH_NAMES = [
  "Jan",
  "Feb",
  "Mar",
  "Apr",
  "May",
  "Jun",
  "Jul",
  "Aug",
  "Sep",
  "Oct",
  "Nov",
  "Dec",
];

function getCampaignMonthIndex(dateStr: string): number {
  if (!dateStr) return 7; // August default
  const d = new Date(dateStr);
  if (!isNaN(d.getTime())) {
    return d.getMonth();
  }
  const parts = dateStr.split("/");
  if (parts.length === 3) {
    const monthNum = parseInt(parts[1], 10) - 1;
    if (monthNum >= 0 && monthNum <= 11) return monthNum;
  }
  return 7;
}

function ChartSection({
  campaignsList,
}: {
  campaignsList: InterviewCampaign[];
}) {
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(14);
  const currentYear = new Date().getFullYear();

  // Compute monthly totals dynamically from campaignsList
  const monthlyMetrics = MONTH_NAMES.map((monthName, monthIdx) => {
    const monthCampaigns = campaignsList.filter(
      (c) => getCampaignMonthIndex(c.createdAtTimestamp) === monthIdx,
    );

    const totalCount = monthCampaigns.length;
    const finishedCount = monthCampaigns.filter(
      (c) =>
        c.currentPipelineStage === "COMPLETED" ||
        (c.activeCandidateCount > 0 &&
          c.evaluatedCandidateCount === c.activeCandidateCount),
    ).length;

    return { month: monthName, totalCount, finishedCount };
  });

  const maxVal = Math.max(
    1,
    ...monthlyMetrics.flatMap((m) => [m.totalCount, m.finishedCount]),
  );

  const chartBars = monthlyMetrics.flatMap((m) => [
    {
      value: m.totalCount,
      height:
        m.totalCount === 0
          ? 12
          : Math.max(
              16,
              Math.min(100, Math.round((m.totalCount / maxVal) * 85)),
            ),
      month: m.month,
      label: "Total Created",
    },
    {
      value: m.finishedCount,
      height:
        m.finishedCount === 0
          ? 12
          : Math.max(
              16,
              Math.min(100, Math.round((m.finishedCount / maxVal) * 85)),
            ),
      month: m.month,
      label: "Finished",
    },
  ]);

  return (
    <div className="w-full px-4 pt-10 pb-4 relative">
      {/* Dashed Grid Line */}
      <div className="absolute left-6 right-6 top-[38%] border-b border-dashed border-gray-200 pointer-events-none" />
      <div className="absolute left-6 right-6 top-[62%] border-b border-dashed border-gray-200 pointer-events-none" />
      <div className="absolute left-6 right-6 top-[12%] border-b border-dashed border-gray-200 pointer-events-none" />

      {/* 12 Month Columns Grid */}
      <div className="grid grid-cols-12 gap-3 relative z-10">
        {MONTH_NAMES.map((month, monthIdx) => {
          const bar1Idx = monthIdx * 2;
          const bar2Idx = monthIdx * 2 + 1;

          return (
            <div key={month} className="flex flex-col items-center">
              {/* Pair of 2 Bars */}
              <div className="grid grid-cols-2 gap-1.5 h-40 w-full items-end relative">
                {[bar1Idx, bar2Idx].map((barIdx) => {
                  const bar = chartBars[barIdx];
                  const isHovered = hoveredIndex === barIdx;

                  return (
                    <div
                      key={barIdx}
                      onMouseEnter={() => setHoveredIndex(barIdx)}
                      onMouseLeave={() => setHoveredIndex(null)}
                      className="relative flex flex-col justify-end h-full w-full group cursor-pointer"
                    >
                      {/* Outer Bar Container */}
                      <div
                        className={`w-full rounded-lg p-0.5 pt-3 border transition-all duration-200 relative ${
                          isHovered
                            ? "bg-[#18181B] border-[#18181B] shadow-md"
                            : "bg-[#ffffff] border-gray-200 hover:border-gray-400"
                        }`}
                        style={{ height: `${bar.height}%` }}
                      >
                        {/* Tooltip on Hover */}
                        {isHovered && (
                          <div className="absolute -top-16 left-1/2 -translate-x-1/2 z-30 flex flex-col items-center pointer-events-none">
                            <div className="bg-[#18181B] text-white px-3 py-1.5 rounded-sm shadow-xl text-center w-28 border border-gray-800">
                              <div className="text-[10px] text-gray-400 font-medium leading-none mb-1">
                                {bar.month} {currentYear}
                              </div>
                              <div className="text-xs font-bold text-white leading-none">
                                {bar.value}{" "}
                                {bar.value === 1 ? "Interview" : "Interviews"}
                              </div>
                            </div>
                            <div className="w-0 h-0 border-l-[5px] border-l-transparent border-r-[5px] border-r-transparent border-t-[5px] border-t-[#18181B] -mt-px" />
                          </div>
                        )}
                        {/* Inner Striped Fill */}
                        <div
                          className="w-full h-full rounded-lg transition-all duration-200s"
                          style={{
                            background: isHovered
                              ? "repeating-linear-gradient(-45deg, #18181B, #18181B 1px, #3F3F46 4px, #3F3F46 8px)"
                              : "repeating-linear-gradient(-45deg, transparent, transparent 1px, rgba(0, 0, 0, 0.20) 4px, rgba(0, 0, 0, 0.20) 8px)",
                          }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Month Label Centered Under Pair */}
              <span className="text-xs font-semibold text-gray-500 mt-3.5">
                {month}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default function DashboardView() {
  const [campaignsList, setCampaignsList] = useState<InterviewCampaign[]>(
    INITIAL_MOCK_CAMPAIGNS,
  );
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const router = useRouter();

  // Popovers & Filter States
  const [activeRowActionId, setActiveRowActionId] = useState<string | null>(
    null,
  );
  const [activePopup, setActivePopup] = useState<
    "status" | "view" | "dept" | "compare" | "metrics" | null
  >(null);
  const [selectedStatus, setSelectedStatus] = useState<StatusFilterType>("ALL");
  const [selectedView, setSelectedView] = useState<ViewFilterType>("all");
  const [selectedDept, setSelectedDept] = useState("All departments");
  const [selectedCompare, setSelectedCompare] = useState("This month");
  const [showChart, setShowChart] = useState(true);
  const [showStats, setShowStats] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");

  useEffect(() => {
    const handleGlobalClick = () => {
      setActiveRowActionId(null);
      setActivePopup(null);
    };
    window.addEventListener("click", handleGlobalClick);
    return () => window.removeEventListener("click", handleGlobalClick);
  }, []);

  const toggleSelectAll = () => {
    if (
      selectedIds.length === campaignsList.length &&
      campaignsList.length > 0
    ) {
      setSelectedIds([]);
    } else {
      setSelectedIds(campaignsList.map((c) => c.id));
    }
  };

  const toggleSelectRow = (id: string) => {
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id],
    );
  };

  const [isBatchDeleting, setIsBatchDeleting] = useState(false);

  const handleBatchDelete = async () => {
    if (selectedIds.length === 0) return;
    const count = selectedIds.length;
    if (
      !window.confirm(
        `Are you sure you want to delete ${count} selected interview campaign${count > 1 ? "s" : ""}?`,
      )
    ) {
      return;
    }

    setIsBatchDeleting(true);
    try {
      const rawToken = document.cookie
        .split("; ")
        .find((row) => row.startsWith("access_token="))
        ?.split("=")[1];
      const tokenCookie = rawToken ? decodeURIComponent(rawToken) : null;

      if (tokenCookie) {
        await Promise.all(
          selectedIds.map((id) =>
            deleteInterviewApi(id, tokenCookie).catch(() => null),
          ),
        );
      }

      setCampaignsList((prev) =>
        prev.filter((c) => !selectedIds.includes(c.id)),
      );
      setSelectedIds([]);
      await loadBackendInterviews();
    } catch (err) {
      console.error("Failed to delete selected interviews", err);
    } finally {
      setIsBatchDeleting(false);
    }
  };

  const loadBackendInterviews = React.useCallback(async () => {
    try {
      const rawToken = document.cookie
        .split("; ")
        .find((row) => row.startsWith("access_token="))
        ?.split("=")[1];

      const tokenCookie = rawToken ? decodeURIComponent(rawToken) : null;

      if (tokenCookie) {
        const backendInterviews = await getInterviewsApi(tokenCookie);
        if (backendInterviews) {
          const mappedCampaigns = await Promise.all(
            backendInterviews.map(async (bi) => {
              const campaign = mapBackendInterviewToCampaign(bi);
              try {
                const candidates = await getCandidatesForInterviewApi(
                  bi.id,
                  tokenCookie,
                );
                if (candidates) {
                  campaign.activeCandidateCount = candidates.length;
                  campaign.evaluatedCandidateCount = candidates.filter(
                    (c) =>
                      c.status?.toLowerCase() === "finished" ||
                      c.status?.toLowerCase() === "done" ||
                      c.status?.toLowerCase() === "evaluated" ||
                      c.status?.toLowerCase() === "completed" ||
                      c.status?.toLowerCase() === "passed" ||
                      c.status?.toLowerCase() === "rejected" ||
                      (c.composite_score !== null &&
                        c.composite_score !== undefined),
                  ).length;
                }
              } catch {
                // Candidates fetch handles empty list gracefully
              }
              return campaign;
            }),
          );
          setCampaignsList(mappedCampaigns);
        }
      }
    } catch (err) {
      console.warn("Failed to fetch backend interviews", err);
    }
  }, []);

  useEffect(() => {
    const fetchCampaigns = async () => {
      await loadBackendInterviews();
    };
    fetchCampaigns();

    const handleCreated = () => {
      loadBackendInterviews();
    };
    window.addEventListener("campaignCreated", handleCreated);
    return () => {
      window.removeEventListener("campaignCreated", handleCreated);
    };
  }, [loadBackendInterviews]);

  const getInterviewStatus = (
    c: InterviewCampaign,
  ): "FINISHED" | "NOT_STARTED" | "IN_PROGRESS" => {
    const isFinished =
      c.currentPipelineStage === "COMPLETED" ||
      (c.activeCandidateCount > 0 &&
        c.evaluatedCandidateCount === c.activeCandidateCount);
    if (isFinished) return "FINISHED";

    const isNotStarted =
      c.evaluatedCandidateCount === 0 &&
      c.currentPipelineStage !== "INTERVIEWER_LIVE" &&
      c.currentPipelineStage !== "GRADER_EVALUATING";
    if (isNotStarted) return "NOT_STARTED";

    return "IN_PROGRESS";
  };

  const totalInterviews = campaignsList.length;
  const finishedInterviews = campaignsList.filter(
    (c) => getInterviewStatus(c) === "FINISHED",
  ).length;
  const inProgressInterviews = campaignsList.filter(
    (c) => getInterviewStatus(c) === "IN_PROGRESS",
  ).length;
  const notStartedInterviews = campaignsList.filter(
    (c) => getInterviewStatus(c) === "NOT_STARTED",
  ).length;

  // Month-over-Month Calculations
  const now = new Date();
  const currentMonthIdx = now.getMonth();
  const lastMonthIdx = (currentMonthIdx + 11) % 12;

  const currentMonthCampaigns = campaignsList.filter(
    (c) => getCampaignMonthIndex(c.createdAtTimestamp) === currentMonthIdx,
  );
  const lastMonthCampaigns = campaignsList.filter(
    (c) => getCampaignMonthIndex(c.createdAtTimestamp) === lastMonthIdx,
  );

  // Total Interviews Comparison
  const currentTotal = currentMonthCampaigns.length;
  const lastTotal = lastMonthCampaigns.length;
  const totalDiff = currentTotal - lastTotal;
  const totalPercentChange =
    lastTotal === 0
      ? currentTotal > 0
        ? 100
        : 0
      : Math.round((Math.abs(totalDiff) / lastTotal) * 100);
  const isTotalUptrend = totalDiff >= 0;

  // Finished Interviews Comparison
  const currentFinished = currentMonthCampaigns.filter(
    (c) => getInterviewStatus(c) === "FINISHED",
  ).length;
  const lastFinished = lastMonthCampaigns.filter(
    (c) => getInterviewStatus(c) === "FINISHED",
  ).length;
  const finishedDiff = currentFinished - lastFinished;
  const finishedPercentChange =
    lastFinished === 0
      ? currentFinished > 0
        ? 100
        : 0
      : Math.round((Math.abs(finishedDiff) / lastFinished) * 100);
  const isFinishedUptrend = finishedDiff >= 0;

  return (
    <div className="flex flex-col h-full bg-white overflow-y-auto">
      <div className="px-8 py-8 max-w-[1400px] w-full mx-auto">
        <div className="flex justify-between mb-6">
          {/* Header Title & Actions */}
          <div className="flex items-center gap-2 text-sm font-medium text-gray-600">
            <Link href="/" className="hover:text-gray-900 transition-colors">
              Home
            </Link>
            <span>/</span>
            <span className="hover:text-gray-900 transition-colors cursor-pointer text-gray-900">
              Interview List
            </span>
          </div>

          {/* Filters Row */}
          <div className="flex items-center gap-3">
            <div className="relative">
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  setActivePopup(activePopup === "compare" ? null : "compare");
                }}
                className="flex items-center gap-2 px-2.5 py-1 border border-gray-200 rounded-lg text-sm font-medium text-gray-900 hover:bg-gray-50 transition-all cursor-pointer"
              >
                <Calendar className="w-3.5 h-3.5 text-gray-600" />{" "}
                {selectedCompare}{" "}
                <ChevronDown className="w-3.5 h-3.5 text-gray-400" />
              </button>
              <CompareFilterPopover
                isOpen={activePopup === "compare"}
                selectedRange={selectedCompare}
                onSelect={(range) => {
                  setSelectedCompare(range);
                  setActivePopup(null);
                }}
              />
            </div>

            <div className="relative">
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  setActivePopup(activePopup === "dept" ? null : "dept");
                }}
                className="flex items-center gap-2 px-2.5 py-1 border border-gray-200 rounded-lg text-sm font-medium text-gray-900 hover:bg-gray-50 transition-all cursor-pointer"
              >
                <Layers className="w-3.5 h-3.5 text-gray-600" /> {selectedDept}{" "}
                <ChevronDown className="w-3.5 h-3.5 text-gray-400" />
              </button>
              <DepartmentFilterPopover
                isOpen={activePopup === "dept"}
                selectedDepartment={selectedDept}
                onSelect={(dept) => {
                  setSelectedDept(dept);
                  setActivePopup(null);
                }}
              />
            </div>
          </div>
        </div>

        {/* Metrics Overview Card */}
        {showStats && (
          <div className="border border-gray-200 rounded-[20px] overflow-hidden mb-6 bg-white shadow-2xs">
            <div className="grid grid-cols-4 border-b border-gray-200 bg-[#FAFAFA]">
              <div className="border-r border-gray-200 p-4">
                <div className="text-xs font-medium text-gray-600 mb-3 flex items-center gap-x-2">
                  <Rows4 className="w-3 h-3" />
                  Total interviews
                </div>
                <div className="flex items-end justify-between">
                  <div className="text-xl font-medium text-gray-900">
                    {totalInterviews}
                  </div>
                  <div
                    className={`text-xs font-medium px-1.5 py-0.5 rounded flex items-center gap-x-1 ${
                      isTotalUptrend
                        ? "text-emerald-600 bg-emerald-50"
                        : "text-red-600 bg-red-50"
                    }`}
                  >
                    {isTotalUptrend ? (
                      <TrendingUp className="w-3 h-3" />
                    ) : (
                      <TrendingDown className="w-3 h-3" />
                    )}
                    {isTotalUptrend
                      ? `+${totalPercentChange}%`
                      : `-${totalPercentChange}%`}{" "}
                    this month
                  </div>
                </div>
              </div>
              <div className="border-r border-gray-200 p-4">
                <div className="text-xs font-medium text-gray-600 mb-3 flex items-center gap-x-2">
                  <FileCheckCorner className="w-3 h-3" strokeWidth={2.5} />
                  Finished
                </div>
                <div className="flex items-end justify-between">
                  <div className="text-xl font-medium text-gray-900">
                    {finishedInterviews}
                  </div>
                  <div
                    className={`text-xs font-medium px-1.5 py-0.5 rounded flex items-center gap-x-1 ${
                      isFinishedUptrend
                        ? "text-emerald-600 bg-emerald-50"
                        : "text-red-600 bg-red-50"
                    }`}
                  >
                    {isFinishedUptrend ? (
                      <TrendingUp className="w-3 h-3" />
                    ) : (
                      <TrendingDown className="w-3 h-3" />
                    )}
                    {isFinishedUptrend
                      ? `+${finishedPercentChange}%`
                      : `-${finishedPercentChange}%`}{" "}
                    this month
                  </div>
                </div>
              </div>
              <div className="border-r border-gray-200 p-4">
                <div className="text-xs font-medium text-gray-600 mb-3 flex items-center gap-x-2">
                  <RollerCoaster className="w-3 h-3" />
                  In Progress
                </div>
                <div className="flex items-end justify-between">
                  <div className="text-xl font-medium text-gray-900">
                    {inProgressInterviews}
                  </div>
                </div>
              </div>
              <div className=" p-4">
                <div className="text-xs font-medium text-gray-600 mb-3 flex items-center gap-x-2">
                  <SquircleDashed className="w-3 h-3" strokeWidth={3} />
                  Not Started
                </div>
                <div className="flex items-end justify-between">
                  <div className="text-xl font-medium text-gray-900">
                    {notStartedInterviews}
                  </div>
                </div>
              </div>
            </div>

            {/* 24-Bar Striped Chart */}
            {showChart && <ChartSection campaignsList={campaignsList} />}
          </div>
        )}

        {/* Main Data Table Card */}
        <div className="border border-gray-200 rounded-[20px] bg-white overflow-hidden shadow-2xs">
          {/* Table Toolbar */}
          <div className="flex items-center justify-between py-3 px-4 border-b border-gray-200">
            <div className="flex items-center gap-3">
              <div className="relative">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    setActivePopup(activePopup === "view" ? null : "view");
                  }}
                  className="flex items-center gap-2 px-2.5 py-1 border border-gray-200 rounded-lg text-sm font-medium text-gray-900 hover:bg-gray-50 transition-all cursor-pointer"
                >
                  <Layers className="w-4 h-4 text-gray-600 font-medium" />{" "}
                  {selectedView === "all"
                    ? "All view"
                    : selectedView === "active"
                      ? "Active view"
                      : "Archived view"}{" "}
                  <ChevronDown className="w-3.5 h-3.5 text-gray-600" />
                </button>
                <ViewFilterPopover
                  isOpen={activePopup === "view"}
                  selectedView={selectedView}
                  onSelect={(view) => {
                    setSelectedView(view);
                    setActivePopup(null);
                  }}
                />
              </div>

              <div className="relative">
                <Search className="w-4 h-4 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  placeholder="Search interviews"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-9 pr-4 py-1 border border-gray-200 rounded-lg text-sm outline-none focus:border-blue-500 w-64 transition-colors"
                />
              </div>
            </div>

            <div className="flex items-center gap-3">
              {selectedIds.length > 0 && (
                <button
                  type="button"
                  onClick={handleBatchDelete}
                  disabled={isBatchDeleting}
                  className="px-2.5 py-1 bg-red-500 text-white rounded-lg text-sm font-medium hover:bg-red-600 transition-all cursor-pointer flex items-center gap-1.5 shadow-2xs disabled:opacity-50"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                  <span>Delete ({selectedIds.length})</span>
                </button>
              )}

              <div className="relative">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    setActivePopup(activePopup === "status" ? null : "status");
                  }}
                  className="px-2.5 py-1 border border-gray-200 rounded-lg text-sm font-medium text-gray-900 hover:bg-gray-50 transition-all cursor-pointer flex items-center"
                >
                  Status{" "}
                  <ChevronDown className="w-3.5 h-3.5 inline ml-1.5 text-gray-400" />
                </button>
                <StatusFilterPopover
                  isOpen={activePopup === "status"}
                  selectedStatus={selectedStatus}
                  totalCount={totalInterviews}
                  finishedCount={finishedInterviews}
                  inProgressCount={inProgressInterviews}
                  notStartedCount={notStartedInterviews}
                  onSelect={(status) => {
                    setSelectedStatus(status);
                    setActivePopup(null);
                  }}
                />
              </div>

              <div className="relative">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    setActivePopup(
                      activePopup === "metrics" ? null : "metrics",
                    );
                  }}
                  className="px-2.5 py-1 border border-gray-200 rounded-lg text-sm font-medium text-gray-900 hover:bg-gray-50 transition-all cursor-pointer flex items-center"
                >
                  <Calendar className="w-3.5 h-3.5 inline mr-1.5 text-gray-600" />{" "}
                  Metrics
                </button>
                <MetricsFilterPopover
                  isOpen={activePopup === "metrics"}
                  showChart={showChart}
                  onToggleChart={() => setShowChart(!showChart)}
                  showStats={showStats}
                  onToggleStats={() => setShowStats(!showStats)}
                />
              </div>
            </div>
          </div>

          {/* Table */}
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-gray-200 bg-[#FAFAFA]">
                  <th className="py-2.5 px-4 w-0">
                    <div
                      onClick={toggleSelectAll}
                      className={`w-4 h-4 rounded-md border flex items-center justify-center cursor-pointer transition-all ${
                        selectedIds.length > 0 &&
                        selectedIds.length === campaignsList.length
                          ? "bg-[#18181B] border-[#18181B] text-white"
                          : "bg-white border-gray-300 hover:border-gray-400"
                      }`}
                    >
                      {selectedIds.length > 0 &&
                        selectedIds.length === campaignsList.length && (
                          <Check className="w-3 h-3 stroke-[3]" />
                        )}
                    </div>
                  </th>
                  <th className="py-2.5 px-2 text-sm font-medium text-gray-600 tracking-wider">
                    Interview Name
                  </th>
                  <th className="py-2.5 px-4 text-sm font-medium text-gray-600 tracking-wider text-right">
                    Status
                  </th>
                  <th className="py-2.5 px-4 text-sm font-medium text-gray-600 tracking-wider text-right">
                    Progress
                  </th>
                  <th className="py-2.5 px-4 text-sm font-medium text-gray-600 tracking-wider text-right">
                    Creator
                  </th>
                  <th className="py-2.5 px-4 text-sm font-medium text-gray-600 tracking-wider text-right"></th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {campaignsList
                  .filter((c) => {
                    const status = getInterviewStatus(c);
                    if (selectedStatus !== "ALL" && status !== selectedStatus)
                      return false;
                    if (
                      selectedDept !== "All departments" &&
                      c.departmentName !== selectedDept
                    )
                      return false;
                    if (
                      selectedView === "active" &&
                      c.activeCandidateCount === 0
                    )
                      return false;
                    if (searchQuery.trim().length > 0) {
                      const q = searchQuery.toLowerCase();
                      const titleMatch = c.jobTitle.toLowerCase().includes(q);
                      const deptMatch = c.departmentName
                        .toLowerCase()
                        .includes(q);
                      const senMatch = c.targetSeniority
                        .toLowerCase()
                        .includes(q);
                      if (!titleMatch && !deptMatch && !senMatch) return false;
                    }
                    return true;
                  })
                  .map((campaign) => {
                    const status = getInterviewStatus(campaign);
                    const isActionOpen = activeRowActionId === campaign.id;

                    return (
                      <tr
                        key={campaign.id}
                        className="hover:bg-gray-50 transition-colors group cursor-pointer"
                        onClick={() =>
                          router.push(`/interviews/${campaign.id}`)
                        }
                      >
                        <td
                          className="pl-4 pr-2 py-2.5"
                          onClick={(e) => e.stopPropagation()}
                        >
                          <div
                            onClick={() => toggleSelectRow(campaign.id)}
                            className={`w-4 h-4 rounded-md border flex items-center justify-center cursor-pointer transition-all ${
                              selectedIds.includes(campaign.id)
                                ? "bg-[#1857cd] border-[#00204c] text-white"
                                : "bg-white border-gray-300 hover:border-gray-400"
                            }`}
                          >
                            {selectedIds.includes(campaign.id) && (
                              <Check className="w-3 h-3 stroke-[3]" />
                            )}
                          </div>
                        </td>
                        <td className="pl-2 pr-6 py-0">
                          <div className="flex items-center gap-3">
                            <div className="w-6 rounded text-lg items-center justify-center h-8">
                              😀️
                            </div>
                            <span className="text-sm font-medium text-gray-900 truncate w-[400px]">
                              {campaign.jobTitle}{" "}
                              <span className="text-gray-600 font-normal">
                                | {campaign.departmentName} |{" "}
                                {campaign.targetSeniority}
                              </span>
                            </span>
                          </div>
                        </td>
                        <td className="px-4 py-2.5 text-right">
                          {status === "FINISHED" && (
                            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-700">
                              Finished
                            </span>
                          )}
                          {status === "IN_PROGRESS" && (
                            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-700">
                              In-progress
                            </span>
                          )}
                          {status === "NOT_STARTED" && (
                            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-700">
                              Not started
                            </span>
                          )}
                        </td>
                        <td className="px-4 py-2.5 text-right">
                          <div className="flex items-bottom gap-2 text-right justify-end">
                            <span className="text-sm text-gray-900 font-medium ">
                              {campaign.evaluatedCandidateCount} /{" "}
                              {campaign.activeCandidateCount}{" "}
                            </span>
                            {campaign.activeCandidateCount > 0 && (
                              <span className="text-xs font-medium text-gray-600 px-0.5 py-0.5 rounded">
                                (
                                {Math.round(
                                  (campaign.evaluatedCandidateCount /
                                    campaign.activeCandidateCount) *
                                    100,
                                )}
                                %)
                              </span>
                            )}
                          </div>
                        </td>
                        <td className="px-4 py-2.5 flex justify-end">
                          <div className="flex items-center justify-end bg-gray-100 w-fit px-1.5 py-1  rounded-full gap-x-1">
                            <Image
                              src="/profile.svg"
                              alt="Active"
                              width={20}
                              height={20}
                            />
                            <span className="text-xs font-medium">
                              {campaign.creatorName || "HR Manager"}
                            </span>
                          </div>
                        </td>
                        <td
                          className="px-2 py-2.5 text-right relative"
                          onClick={(e) => e.stopPropagation()}
                        >
                          <button
                            type="button"
                            onClick={() =>
                              setActiveRowActionId(
                                isActionOpen ? null : campaign.id,
                              )
                            }
                            className="p-1.5 text-gray-400 hover:text-gray-900 rounded-md hover:bg-gray-100 transition-colors cursor-pointer"
                          >
                            <MoreVertical className="w-4 h-4" />
                          </button>
                          <RowActionPopover
                            isOpen={isActionOpen}
                            onClose={() => setActiveRowActionId(null)}
                            onViewDetail={() => {
                              setActiveRowActionId(null);
                              router.push(`/interviews/${campaign.id}`);
                            }}
                            onCopyLink={() => {
                              setActiveRowActionId(null);
                              navigator.clipboard.writeText(
                                `${window.location.origin}/interview/mock_room_token_1`,
                              );
                            }}
                            onArchive={() => {
                              setActiveRowActionId(null);
                              setCampaignsList((prev) =>
                                prev.filter((item) => item.id !== campaign.id),
                              );
                            }}
                            onDelete={() => {
                              setActiveRowActionId(null);
                              setCampaignsList((prev) =>
                                prev.filter((item) => item.id !== campaign.id),
                              );
                            }}
                          />
                        </td>
                      </tr>
                    );
                  })}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
