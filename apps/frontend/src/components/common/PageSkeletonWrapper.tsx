"use client";

import React, { useState, useEffect } from "react";
import { usePathname } from "next/navigation";

// Navbar mock since layout wraps it
const NavbarSkeleton = () => (
  <header className="w-full py-6">
    <div className="max-w-350 mx-auto px-12 flex items-center justify-between">
      <div className="flex items-center gap-1 text-black">
        <div className="w-10 h-10 bg-gray-200 rounded-full animate-pulse" />
        <div className="w-32 h-8 bg-gray-200 rounded animate-pulse" />
      </div>
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-7 px-5 py-4 bg-white rounded-full">
          <div className="w-5.5 h-5.5 bg-gray-200 rounded-full animate-pulse" />
          <div className="w-5.5 h-5.5 bg-gray-200 rounded-full animate-pulse" />
          <div className="w-5.5 h-5.5 bg-gray-200 rounded-full animate-pulse" />
        </div>
        <div className="flex items-center gap-3 px-3 py-2.5 bg-white rounded-full">
          <div className="w-10 h-10 rounded-full bg-gray-200 animate-pulse" />
          <div className="flex flex-col gap-1 w-24">
            <div className="w-20 h-4 bg-gray-200 rounded animate-pulse" />
            <div className="w-16 h-3 bg-gray-100 rounded animate-pulse" />
          </div>
          <div className="w-6 h-6 bg-gray-200 rounded-full animate-pulse ml-2" />
        </div>
      </div>
    </div>
  </header>
);

// 1. Dashboard Skeleton (Header, Metrics, Grid)
function DashboardSkeleton() {
  return (
    <div className="min-h-screen bg-[#F8F9FA] text-[#272727] font-sans flex flex-col justify-between selection:bg-[#FE6100]/20 animate-in fade-in duration-150">
      <NavbarSkeleton />
      <main className="max-w-350 mx-auto px-7 pb-7 w-full">
        <div className="bg-white rounded-[36px] p-7 lg:p-7 min-h-[80vh]">
          {/* Header Section */}
          <div className="mb-7">
            <div className="flex items-center gap-4.5 mb-2">
              <div className="w-24 h-7 bg-gray-200 rounded animate-pulse" />
              <div className="w-32 h-6 bg-gray-100 rounded-full animate-pulse" />
            </div>
            <div className="w-64 h-5 bg-gray-100 rounded animate-pulse" />
          </div>

          {/* Progress & Action Section */}
          <div className="flex items-center gap-7 mb-7">
            <div className="flex items-end gap-1 h-5.5">
              {[...Array(17)].map((_, i) => (
                <div key={i} className="w-1 h-full bg-gray-200 rounded-full animate-pulse" />
              ))}
            </div>
            <div className="w-32 h-6 bg-gray-200 rounded animate-pulse" />
            <div className="ml-2 w-40 h-11 bg-gray-200 rounded-full animate-pulse" />
          </div>

          {/* Tabs Section */}
          <div className="flex items-center gap-7 border-b border-[#F1F1F1] mb-7">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="pb-4 w-24 h-5 bg-gray-200 rounded animate-pulse" />
            ))}
          </div>

          {/* Campaigns Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
            {[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
              <div key={i} className="bg-white rounded-[24px] p-6 border border-[#E9E9E9] h-[220px] shadow-sm space-y-4">
                 <div className="w-32 h-6 bg-gray-200 rounded animate-pulse" />
                 <div className="w-24 h-4 bg-gray-100 rounded animate-pulse" />
                 <div className="w-full h-12 bg-gray-100 rounded animate-pulse mt-4" />
                 <div className="w-full h-8 bg-gray-100 rounded-full animate-pulse mt-4" />
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}

// 2. Candidate Room / Lobby Skeleton (/interview/[token])
function CandidateRoomSkeleton() {
  return (
    <div className="min-h-screen bg-[#F8F9FA] text-[#272727] font-sans flex flex-col justify-between selection:bg-[#FE6100]/20 animate-in fade-in duration-150">
      <header className="h-16 border-b border-[#E9E9E9] bg-white px-6 flex items-center justify-between shadow-sm sticky top-0 z-40">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gray-200 animate-pulse" />
          <div className="flex items-center gap-2">
            <div className="w-32 h-5 bg-gray-200 rounded animate-pulse" />
            <div className="w-24 h-5 bg-gray-100 rounded-full animate-pulse" />
          </div>
        </div>
        <div className="w-32 h-7 bg-gray-100 rounded-md animate-pulse" />
      </header>

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

// 3. Login Page Skeleton (/login)
function LoginSkeleton() {
  return (
    <div className="min-h-screen bg-[#F6F6F6] flex items-center justify-center p-4 md:p-8 font-sans">
      <div className="bg-white rounded-3xl border border-[#F1F1F1] p-5 md:p-4.5 shadow-2xs max-w-325 w-full grid grid-cols-1 lg:grid-cols-12 items-stretch min-h-[600px]">
        <div className="lg:col-span-7 bg-[#F9F9F9] rounded-3xl p-8 md:p-8 flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-md bg-gray-200 animate-pulse" />
              <div className="w-24 h-6 bg-gray-200 rounded animate-pulse" />
            </div>
            <div className="flex items-center gap-4">
              <div className="w-16 h-4 bg-gray-200 rounded animate-pulse" />
              <div className="w-16 h-4 bg-gray-200 rounded animate-pulse" />
              <div className="w-16 h-4 bg-gray-200 rounded animate-pulse" />
            </div>
          </div>
          <div className="pt-16 pb-4 space-y-4">
            <div className="w-3/4 h-14 bg-gray-200 rounded-xl animate-pulse" />
            <div className="w-full h-24 bg-gray-100 rounded-lg animate-pulse mt-4" />
          </div>
        </div>

        <div className="lg:col-span-5 flex flex-col justify-center pr-4 md:pr-16 ml-8 py-6 space-y-6">
          <div className="w-10 h-10 rounded-xl bg-gray-200 animate-pulse mb-2" />
          <div className="w-48 h-8 bg-gray-200 rounded animate-pulse mb-4" />

          <div className="space-y-4 w-full">
            <div className="space-y-2">
              <div className="w-20 h-4 bg-gray-200 rounded animate-pulse" />
              <div className="w-full h-12 bg-gray-100 rounded-xl animate-pulse" />
            </div>
            <div className="space-y-2">
              <div className="w-20 h-4 bg-gray-200 rounded animate-pulse" />
              <div className="w-full h-12 bg-gray-100 rounded-xl animate-pulse" />
            </div>
            <div className="w-full h-12 bg-gray-200 rounded-xl animate-pulse mt-4" />
          </div>

          <div className="mt-8 space-y-3">
            <div className="w-24 h-4 bg-gray-200 rounded animate-pulse" />
            <div className="flex gap-2.5">
              {[1, 2, 3, 4].map(i => (
                <div key={i} className="w-9 h-9 rounded-xl bg-gray-100 animate-pulse" />
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// 4. Candidate Report Skeleton (/interviews/.../candidates/...)
function CandidateReportSkeleton() {
  return (
    <div className="min-h-screen bg-[#F8F9FA] text-[#272727] font-sans flex flex-col justify-between selection:bg-[#FE6100]/20 animate-in fade-in duration-150">
      <NavbarSkeleton />
      <main className="max-w-350 mx-auto px-6 pb-20 w-full">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 mb-6">
          <div className="lg:col-span-6 bg-white rounded-[28px] border border-[#F1F1F1] p-7 shadow-2xs flex flex-col justify-between min-h-[400px]">
            <div>
              <div className="flex items-center gap-4 pb-5 border-b border-[#F1F1F1]">
                <div className="w-10 h-10 rounded-full bg-gray-200 animate-pulse" />
                <div className="space-y-2">
                  <div className="w-32 h-5 bg-gray-200 rounded animate-pulse" />
                  <div className="w-48 h-3 bg-gray-100 rounded animate-pulse" />
                </div>
              </div>
              <div className="pt-5 mb-6 space-y-3">
                <div className="w-32 h-5 bg-gray-200 rounded animate-pulse" />
                <div className="w-full h-4 bg-gray-100 rounded animate-pulse" />
                <div className="w-full h-4 bg-gray-100 rounded animate-pulse" />
                <div className="w-3/4 h-4 bg-gray-100 rounded animate-pulse" />
              </div>
              <div className="space-y-3">
                {[1, 2, 3, 4].map((i) => (
                   <div key={i} className="flex items-center gap-3">
                     <div className="w-1 h-6 rounded-full bg-gray-200 animate-pulse" />
                     <div className="w-48 h-4 bg-gray-100 rounded animate-pulse" />
                   </div>
                ))}
              </div>
            </div>
          </div>

          <div className="lg:col-span-6 bg-white rounded-[28px] border border-[#F1F1F1] p-7 shadow-2xs flex flex-col justify-between">
            <div>
              <div className="flex items-start justify-between pb-6 border-b border-[#F1F1F1]">
                <div className="space-y-2">
                  <div className="w-16 h-4 bg-gray-200 rounded animate-pulse" />
                  <div className="flex items-center gap-2">
                    <div className="w-2.5 h-7 rounded-full bg-gray-200 animate-pulse" />
                    <div className="w-24 h-8 bg-gray-200 rounded animate-pulse" />
                  </div>
                  <div className="w-48 h-4 bg-gray-100 rounded animate-pulse" />
                </div>
                <div className="space-y-2 flex flex-col items-end">
                  <div className="w-24 h-4 bg-gray-200 rounded animate-pulse" />
                  <div className="w-16 h-8 bg-gray-200 rounded animate-pulse" />
                  <div className="w-20 h-4 bg-gray-100 rounded animate-pulse" />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-6">
                <div className="flex flex-col justify-between">
                  <div>
                    <div className="w-32 h-4 bg-gray-200 rounded animate-pulse mb-2" />
                    <div className="w-16 h-8 bg-gray-200 rounded animate-pulse mb-6" />
                    <div className="space-y-4">
                      {[1, 2, 3].map(i => <div key={i} className="w-full h-4 bg-gray-100 rounded animate-pulse" />)}
                    </div>
                  </div>
                </div>
                <div className="flex flex-col justify-between md:border-l md:border-[#F1F1F1] md:pl-6">
                  <div>
                    <div className="w-32 h-4 bg-gray-200 rounded animate-pulse mb-2" />
                    <div className="w-16 h-8 bg-gray-200 rounded animate-pulse mb-6" />
                    <div className="space-y-4">
                      {[1, 2, 3].map(i => <div key={i} className="w-full h-4 bg-gray-100 rounded animate-pulse" />)}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-[28px] border border-[#F1F1F1] p-7 shadow-2xs min-h-[300px]">
          <div className="w-48 h-6 bg-gray-200 rounded animate-pulse pb-4 mb-6" />
          <div className="space-y-6">
            {[1, 2, 3, 4].map(i => (
              <div key={i} className="flex gap-4">
                <div className="w-6 h-4 bg-gray-200 rounded animate-pulse" />
                <div className="w-2 h-2 rounded-full bg-gray-200 animate-pulse mt-1" />
                <div className="flex-1 space-y-2">
                  <div className="w-24 h-5 bg-gray-200 rounded animate-pulse" />
                  <div className="w-full h-4 bg-gray-100 rounded animate-pulse" />
                </div>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}

function InnerSkeletonLoader({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 1000);

    return () => clearTimeout(timer);
  }, []);

  if (isLoading) {
    if (pathname.startsWith("/login")) {
      return <LoginSkeleton />;
    }
    if (pathname.startsWith("/interview/")) {
      return <CandidateRoomSkeleton />;
    }
    if (pathname.includes("/candidates/")) {
      return <CandidateReportSkeleton />;
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

  return (
    <InnerSkeletonLoader key={pathname}>
      {children}
    </InnerSkeletonLoader>
  );
}
