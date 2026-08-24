"use client";

import { useSearchParams } from "next/navigation";
import CandidateInterviewPage from "./[token]/page";
import React, { Suspense } from "react";

function InterviewQueryWrapper() {
  const searchParams = useSearchParams();
  const token = searchParams.get("token") || "mock-token";
  return <CandidateInterviewPage params={Promise.resolve({ token })} />;
}

export default function InterviewPage() {
  return (
    <Suspense fallback={<div className="p-8 text-center font-sans">Loading room...</div>}>
      <InterviewQueryWrapper />
    </Suspense>
  );
}
