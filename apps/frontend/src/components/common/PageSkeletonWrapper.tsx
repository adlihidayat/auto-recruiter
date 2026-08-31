"use client";

/**
 * What: Page Skeleton Loading Wrapper component.
 * Why: Renders layout-accurate loading skeletons for Dashboard, Interview Details, Candidate Reports, & Auth pages.
 * Boundaries: Skeletons for Detail & Candidate Report pages match 1-to-1 with actual component DOM trees and operate on real data loading without artificial mock timers.
 */

import React, { useState, useEffect } from "react";
import { usePathname } from "next/navigation";

// Sidebar Skeleton (Matches exact w-[240px] width & styling of layout.tsx)
export function SidebarSkeleton() {
  return (
    <aside className="w-[240px] flex-shrink-0 bg-[#FAFAFA] border-r border-gray-200 flex flex-col h-full select-none">
      {/* Workspace Header Skeleton */}
      <div className="px-4 pt-5 pb-3 flex items-center gap-2">
        <div className="w-5 h-5 rounded bg-gray-200 animate-pulse shrink-0" />
        <div className="w-28 h-4 bg-gray-200 rounded animate-pulse flex-1" />
        <div className="w-3.5 h-3.5 bg-gray-200 rounded animate-pulse shrink-0" />
      </div>

      {/* Search / Quick Actions Button Skeleton */}
      <div className="px-2 mb-2">
        <div className="w-full h-8 bg-gray-200/80 rounded-lg animate-pulse" />
      </div>

      {/* Scrollable Nav Items Skeleton */}
      <div className="flex-1 overflow-y-auto px-2 space-y-6">
        <div className="space-y-1">
          {[1, 2, 3, 4, 5].map((i) => (
            <div
              key={i}
              className="w-full h-7 bg-gray-200/60 rounded-md animate-pulse"
            />
          ))}
        </div>

        {/* Recents Section Header & Items Skeleton */}
        <div className="space-y-1">
          <div className="w-16 h-3 bg-gray-200 rounded animate-pulse px-3 mb-2" />
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="flex items-center gap-3 px-3 py-1.5">
              <div className="w-4 h-4 rounded bg-gray-200/70 animate-pulse shrink-0" />
              <div className="w-32 h-3.5 bg-gray-200/60 rounded animate-pulse" />
            </div>
          ))}
        </div>
      </div>

      {/* Sticky Bottom Profile Footer Skeleton */}
      <div className="p-4 border-t border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-5 h-5 rounded-full bg-gray-200 animate-pulse" />
            <div className="w-20 h-3.5 bg-gray-200 rounded animate-pulse" />
          </div>
          <div className="w-12 h-6 bg-gray-200 rounded-md animate-pulse" />
        </div>
      </div>
    </aside>
  );
}

// 1. Dashboard View Skeleton (Includes Left Sidebar & Main Content)
export function DashboardSkeleton() {
  return (
    <div className="flex h-screen bg-[#FAFAFA] overflow-hidden text-gray-900 animate-in fade-in duration-150">
      {/* Left Sidebar Skeleton */}
      <SidebarSkeleton />

      {/* Main Content Area Skeleton */}
      <main className="flex-1 bg-white overflow-hidden relative flex flex-col">
        <div className="flex flex-col h-full bg-white overflow-y-auto">
          <div className="px-8 py-8 max-w-[1400px] w-full mx-auto">
            {/* Top Header Row (Breadcrumbs & Filters) */}
            <div className="flex justify-between mb-6 items-center">
              {/* Breadcrumb Title */}
              <div className="flex items-center gap-2">
                <div className="w-10 h-4 bg-gray-200 rounded animate-pulse" />
                <span className="text-gray-300 text-xs">/</span>
                <div className="w-24 h-4 bg-gray-200 rounded animate-pulse" />
              </div>

              {/* Filters Row */}
              <div className="flex items-center gap-3">
                <div className="w-28 h-7 bg-gray-200/80 rounded-lg animate-pulse" />
                <div className="w-32 h-7 bg-gray-200/80 rounded-lg animate-pulse" />
              </div>
            </div>

            {/* Metrics Overview Card */}
            <div className="border border-gray-200 rounded-[20px] overflow-hidden mb-6 bg-white shadow-2xs">
              {/* Top 4 Metrics Grid */}
              <div className="grid grid-cols-4 border-b border-gray-200 bg-[#FAFAFA]">
                {[1, 2, 3, 4].map((i) => (
                  <div
                    key={i}
                    className={`p-4 ${i !== 4 ? "border-r border-gray-200" : ""}`}
                  >
                    <div className="w-28 h-3.5 bg-gray-200 rounded animate-pulse mb-3" />
                    <div className="flex items-end justify-between">
                      <div className="w-8 h-6 bg-gray-300 rounded animate-pulse" />
                      <div className="w-24 h-4 bg-gray-200/70 rounded animate-pulse" />
                    </div>
                  </div>
                ))}
              </div>

              {/* 24-Bar Striped Chart Section */}
              <div className="p-6 bg-white">
                <div className="flex items-center justify-between mb-4">
                  <div className="w-44 h-4 bg-gray-200 rounded animate-pulse" />
                  <div className="w-20 h-4 bg-gray-100 rounded animate-pulse" />
                </div>
                <div className="h-32 flex items-end justify-between gap-1.5 pt-4">
                  {Array.from({ length: 24 }).map((_, i) => (
                    <div
                      key={i}
                      className="flex-1 bg-gray-200/60 rounded-lg animate-pulse"
                      style={{
                        height: `${Math.max(25, Math.floor(Math.sin(i * 0.8) * 35 + 55))}%`,
                      }}
                    />
                  ))}
                </div>
              </div>
            </div>

            {/* Main Data Table Card */}
            <div className="border border-gray-200 rounded-[20px] bg-white overflow-hidden shadow-2xs">
              {/* Table Toolbar */}
              <div className="flex items-center justify-between py-3 px-4 border-b border-gray-200">
                <div className="flex items-center gap-3">
                  <div className="w-24 h-7 bg-gray-200/80 rounded-lg animate-pulse" />
                  <div className="w-64 h-7 bg-gray-200/80 rounded-lg animate-pulse" />
                </div>

                <div className="flex items-center gap-3">
                  <div className="w-20 h-7 bg-gray-200/80 rounded-lg animate-pulse" />
                  <div className="w-24 h-7 bg-gray-200/80 rounded-lg animate-pulse" />
                </div>
              </div>

              {/* Table */}
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="border-b border-gray-200 bg-[#FAFAFA]">
                      <th className="py-2.5 px-4 w-0">
                        <div className="w-4 h-4 rounded-md bg-gray-200 animate-pulse" />
                      </th>
                      <th className="py-2.5 px-2">
                        <div className="w-28 h-3.5 bg-gray-200 rounded animate-pulse" />
                      </th>
                      <th className="py-2.5 px-4 text-right">
                        <div className="w-16 h-3.5 bg-gray-200 rounded animate-pulse ml-auto" />
                      </th>
                      <th className="py-2.5 px-4 text-right">
                        <div className="w-20 h-3.5 bg-gray-200 rounded animate-pulse ml-auto" />
                      </th>
                      <th className="py-2.5 px-4 text-right">
                        <div className="w-16 h-3.5 bg-gray-200 rounded animate-pulse ml-auto" />
                      </th>
                      <th className="py-2.5 px-4 text-right"></th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
                      <tr key={i} className="hover:bg-gray-50/80 transition-all">
                        <td className="py-3.5 px-4">
                          <div className="w-4 h-4 rounded-md bg-gray-200 animate-pulse" />
                        </td>
                        <td className="py-3.5 px-2">
                          <div className="flex items-center gap-3">
                            <div className="w-7 h-7 rounded-lg bg-gray-200 animate-pulse shrink-0" />
                            <div className="space-y-1.5">
                              <div className="w-44 h-4 bg-gray-200 rounded animate-pulse" />
                              <div className="w-28 h-3 bg-gray-100 rounded animate-pulse" />
                            </div>
                          </div>
                        </td>
                        <td className="py-3.5 px-4 text-right">
                          <div className="w-20 h-6 bg-gray-200/80 rounded-md animate-pulse ml-auto" />
                        </td>
                        <td className="py-3.5 px-4 text-right">
                          <div className="w-12 h-4 bg-gray-200 rounded animate-pulse ml-auto" />
                        </td>
                        <td className="py-3.5 px-4 text-right">
                          <div className="flex items-center justify-end gap-1.5">
                            <div className="w-5 h-5 rounded-full bg-gray-200 animate-pulse shrink-0" />
                            <div className="w-16 h-3.5 bg-gray-200 rounded animate-pulse" />
                          </div>
                        </td>
                        <td className="py-3.5 px-4 text-right">
                          <div className="w-6 h-6 bg-gray-200/60 rounded-lg animate-pulse ml-auto" />
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

// 2. Interview Detail Skeleton (/interviews/[interviewId]) - Runs ONLY on actual loading
export function InterviewDetailSkeleton() {
  return (
    <div className="flex flex-col h-full bg-white overflow-y-auto animate-in fade-in duration-150">
      <div className="px-8 py-8 max-w-[900px] w-full mx-auto">
        {/* Breadcrumb Skeleton */}
        <div className="flex items-center gap-2 mb-8">
          <div className="w-12 h-4 bg-gray-200 rounded animate-pulse" />
          <span className="text-gray-300 text-xs">/</span>
          <div className="w-24 h-4 bg-gray-200 rounded animate-pulse" />
          <span className="text-gray-300 text-xs">/</span>
          <div className="w-48 h-4 bg-gray-200 rounded animate-pulse" />
        </div>

        {/* Header Section Skeleton */}
        <div className="flex flex-col gap-2 mb-8">
          <div className="w-10 h-10 rounded-xl bg-gray-200 animate-pulse shrink-0" />
          <div className="flex justify-between items-center gap-2">
            <div className="space-y-2">
              <div className="flex items-center gap-3">
                <div className="w-64 h-7 bg-gray-300 rounded animate-pulse" />
                <div className="w-16 h-5 bg-emerald-100 rounded-md animate-pulse" />
              </div>
              <div className="flex items-center gap-3">
                <div className="w-20 h-4 bg-gray-200 rounded animate-pulse" />
                <span className="text-gray-300 text-xs">/</span>
                <div className="w-16 h-4 bg-gray-200 rounded animate-pulse" />
                <span className="text-gray-300 text-xs">/</span>
                <div className="w-24 h-4 bg-gray-100 rounded animate-pulse" />
              </div>
            </div>

            <div className="flex items-center gap-3">
              <div className="w-16 h-8 bg-gray-200 rounded-lg animate-pulse" />
              <div className="w-28 h-8 bg-gray-200 rounded-lg animate-pulse" />
            </div>
          </div>
        </div>

        {/* Hero Banner Skeleton */}
        <div className="w-full h-32 rounded-2xl bg-gray-100 border border-gray-200 mb-10 flex items-center justify-center p-6 animate-pulse">
          <div className="w-60 h-9 bg-white/80 rounded-full" />
        </div>

        {/* Interview Plan Section Skeleton */}
        <div className="mb-10 space-y-3">
          <div className="w-44 h-5 bg-gray-300 rounded animate-pulse mb-3" />
          <div className="space-y-6">
            {[1, 2].map((i) => (
              <div
                key={i}
                className="border border-gray-200 rounded-xl overflow-hidden bg-white shadow-xs"
              >
                <div className="p-4 border-b border-gray-100">
                  <div className="w-full h-5 bg-gray-200 rounded animate-pulse" />
                </div>
                <div className="p-4 space-y-3 bg-[#FAFAFA]">
                  <div className="w-32 h-3 bg-gray-200 rounded animate-pulse mb-2" />
                  <div className="w-3/4 h-4 bg-gray-200/80 rounded animate-pulse" />
                  <div className="w-2/3 h-4 bg-gray-200/80 rounded animate-pulse" />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Candidates List Skeleton */}
        <div className="mb-10 space-y-3">
          <div className="w-32 h-5 bg-gray-300 rounded animate-pulse mb-3" />
          <div className="border border-gray-200 rounded-xl bg-white overflow-hidden divide-y divide-gray-100">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="flex items-center justify-between p-4">
                <div className="flex items-center gap-3">
                  <div className="w-6 h-6 rounded-full bg-gray-200 animate-pulse shrink-0" />
                  <div className="w-40 h-4 bg-gray-200 rounded animate-pulse" />
                  <div className="w-32 h-4 bg-gray-100 rounded animate-pulse" />
                </div>
                <div className="w-24 h-4 bg-gray-200/80 rounded animate-pulse" />
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

// 3. Candidate Report Skeleton (1-to-1 match for CandidateReportView.tsx: max-w-200)
export function CandidateReportSkeleton() {
  return (
    <div className="flex flex-col h-full bg-white overflow-y-auto animate-in fade-in duration-150">
      <div className="px-8 py-10 max-w-200 w-full mx-auto font-sans">
        {/* Breadcrumb Skeleton */}
        <div className="flex items-center gap-2 mb-10">
          <div className="w-10 h-4 bg-gray-200 rounded animate-pulse" />
          <span className="text-gray-300 text-xs">/</span>
          <div className="w-20 h-4 bg-gray-200 rounded animate-pulse" />
          <span className="text-gray-300 text-xs">/</span>
          <div className="w-28 h-4 bg-gray-200 rounded animate-pulse" />
          <span className="text-gray-300 text-xs">/</span>
          <div className="w-24 h-4 bg-gray-200 rounded animate-pulse" />
        </div>

        {/* Minimalist Header Skeleton */}
        <div className="mb-10 space-y-2">
          <div className="flex items-center gap-4">
            <div className="w-48 h-8 bg-gray-300 rounded animate-pulse" />
            <div className="w-20 h-6 bg-emerald-100/80 rounded-md animate-pulse" />
          </div>
          <div className="w-36 h-4 bg-gray-200 rounded animate-pulse" />
        </div>

        {/* Reasoning Paragraph Skeleton */}
        <div className="space-y-2 mb-8">
          <div className="w-full h-4 bg-gray-200/80 rounded animate-pulse" />
          <div className="w-full h-4 bg-gray-200/80 rounded animate-pulse" />
          <div className="w-3/4 h-4 bg-gray-200/80 rounded animate-pulse" />
        </div>

        {/* Core Analysis Breakdown Skeleton */}
        <div className="mb-8">
          <div className="w-40 h-4 bg-gray-200 rounded animate-pulse mb-4" />
          <div className="bg-white border border-gray-200 rounded-xl overflow-hidden divide-y divide-gray-100">
            {[1, 2, 3].map((i) => (
              <div key={i} className="py-4 px-5 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-5 h-5 bg-gray-200 rounded animate-pulse shrink-0" />
                  <div className="w-24 h-4 bg-gray-200 rounded animate-pulse" />
                  <div className="w-12 h-4 bg-emerald-100/70 rounded animate-pulse" />
                </div>
                <div className="w-12 h-4 bg-gray-200 rounded animate-pulse" />
              </div>
            ))}
          </div>
        </div>

        {/* Communication & Traits Breakdown Skeleton */}
        <div className="mb-8">
          <div className="w-52 h-4 bg-gray-200 rounded animate-pulse mb-4" />
          <div className="bg-white border border-gray-200 rounded-xl overflow-hidden divide-y divide-gray-100">
            {[1, 2].map((i) => (
              <div key={i} className="py-4 px-5 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-5 h-5 bg-gray-200 rounded animate-pulse shrink-0" />
                  <div className="w-28 h-4 bg-gray-200 rounded animate-pulse" />
                  <div className="w-12 h-4 bg-emerald-100/70 rounded animate-pulse" />
                </div>
                <div className="w-12 h-4 bg-gray-200 rounded animate-pulse" />
              </div>
            ))}
          </div>
        </div>

        {/* Full Transcript Skeleton */}
        <div>
          <div className="w-44 h-4 bg-gray-200 rounded animate-pulse mb-4" />
          <div className="bg-white border border-gray-200 rounded-xl p-5 space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="space-y-2">
                <div className="w-24 h-3 bg-gray-200 rounded animate-pulse" />
                <div className="w-full h-4 bg-gray-100 rounded animate-pulse" />
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

// 4. Candidate Room / Lobby Skeleton (/interview/[token])
export function CandidateRoomSkeleton() {
  return (
    <div className="min-h-screen bg-[#F8F9FA] text-[#272727] font-sans flex flex-col justify-between selection:bg-[#FE6100]/20 animate-in fade-in duration-150">
      <main className="flex-1 max-w-5xl w-full mx-auto p-6 flex flex-col justify-center items-center">
        <div className="w-full max-w-xl bg-white rounded-3xl border border-[#E9E9E9] shadow-xl p-8 animate-in fade-in zoom-in-95 duration-200">
          <div className="text-center mb-8 flex flex-col items-center">
            <div className="w-16 h-16 rounded-2xl bg-gray-100 mb-4 animate-pulse" />
            <div className="w-64 h-8 bg-gray-200 rounded-lg mb-2 animate-pulse" />
            <div className="w-80 h-4 bg-gray-100 rounded animate-pulse" />
          </div>

          <div className="bg-[#F9FAFB] rounded-2xl border border-[#E9E9E9] p-5 mb-8 space-y-4">
            <div className="w-24 h-4 bg-gray-200 rounded animate-pulse" />
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-gray-200 animate-pulse" />
                <div className="space-y-1">
                  <div className="w-24 h-5 bg-gray-200 rounded animate-pulse" />
                  <div className="w-32 h-3 bg-gray-100 rounded animate-pulse" />
                </div>
              </div>
              <div className="w-16 h-8 bg-gray-200 rounded-lg animate-pulse" />
            </div>
            <div className="w-full h-2.5 bg-gray-200 rounded-full animate-pulse mt-4" />
          </div>

          <div className="space-y-2 mb-8">
            <div className="w-full h-4 bg-gray-100 rounded animate-pulse" />
            <div className="w-3/4 h-4 bg-gray-100 rounded animate-pulse" />
          </div>

          <div className="w-full h-14 bg-gray-200 rounded-2xl animate-pulse" />
        </div>
      </main>
    </div>
  );
}

// 5. Login Page Skeleton (/login)
export function LoginSkeleton() {
  return (
    <div className="min-h-screen bg-[#F6F6F6] flex items-center justify-center p-4 md:p-8 font-sans">
      <div className="bg-white border border-gray-200 rounded-3xl p-6 md:py-6 md:pl-6 md:pr-10 max-w-5xl w-full flex gap-8 items-stretch min-h-[480px]">
        <div className="w-full flex-1 rounded-3xl bg-gray-200 animate-pulse min-h-[380px]" />
        <div className="py-12 max-w-110 flex-1 space-y-6">
          <div className="w-48 h-6 bg-gray-200 rounded animate-pulse" />
          <div className="w-full h-4 bg-gray-100 rounded animate-pulse" />
          <div className="space-y-4 pt-4">
            <div className="w-full h-10 bg-gray-100 rounded-md animate-pulse" />
            <div className="w-full h-10 bg-gray-100 rounded-md animate-pulse" />
            <div className="w-full h-10 bg-gray-200 rounded-lg animate-pulse mt-4" />
          </div>
        </div>
      </div>
    </div>
  );
}

function InnerSkeletonLoader({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const isDetailOrReportRoute = pathname.includes("/interviews/");
  const [isLoading, setIsLoading] = useState(!isDetailOrReportRoute);

  useEffect(() => {
    if (isDetailOrReportRoute) return;

    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 600);

    return () => clearTimeout(timer);
  }, [isDetailOrReportRoute]);

  if (isLoading) {
    if (pathname.startsWith("/login") || pathname.startsWith("/create-account")) {
      return <LoginSkeleton />;
    }
    if (pathname === "/interview" || pathname.startsWith("/interview/")) {
      return <CandidateRoomSkeleton />;
    }
    return <DashboardSkeleton />;
  }

  return <>{children}</>;
}

export default function PageSkeletonWrapper({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();

  return <InnerSkeletonLoader key={pathname}>{children}</InnerSkeletonLoader>;
}
