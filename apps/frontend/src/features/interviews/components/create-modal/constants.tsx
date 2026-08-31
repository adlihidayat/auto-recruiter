/**
 * What: Constants and configuration for the Agent Handoff pipeline and emoji picker.
 * Why: Keeps step data and mock simulation timelines decoupled from JSX components.
 * Boundaries: Local constants used within CreateInterviewModal components.
 */

import React from "react";
import {
  Filter,
  Binoculars,
  PenTool,
  CheckCircle2,
  ArrowRight,
} from "lucide-react";

export const AGENT_STEPS = [
  {
    name: "Context",
    role: "ANALYZER",
    color: "text-blue-500",
    bg: "bg-blue-100",
    badgeBg: "bg-blue-500",
    icon: <Filter className="w-5 h-5" />,
  },
  {
    name: "Research",
    role: "STRATEGIST",
    color: "text-purple-500",
    bg: "bg-purple-100",
    badgeBg: "bg-purple-500",
    icon: <Binoculars className="w-5 h-5" />,
  },
  {
    name: "Planning",
    role: "AGENT",
    color: "text-orange-500",
    bg: "bg-orange-100",
    badgeBg: "bg-orange-500",
    icon: <PenTool className="w-5 h-5" />,
  },
  {
    name: "Finished",
    role: "SYSTEM",
    color: "text-emerald-500",
    bg: "bg-emerald-100",
    badgeBg: "bg-emerald-500",
    icon: <CheckCircle2 className="w-5 h-5" />,
  },
];

export interface MockLogItem {
  time: number;
  dot: string;
  text: React.ReactNode;
  isPending?: boolean;
}

export const MOCK_LOGS: MockLogItem[] = [
  // Agent 0: Context (0s - 5s)
  {
    time: 1200,
    dot: "bg-blue-400",
    text: "analyzing job description & requirements",
  },
  {
    time: 2800,
    dot: "bg-blue-400",
    text: "extracting key technical skills & domain keywords",
  },
  {
    time: 4500,
    dot: "bg-blue-500",
    text: (
      <>
        <span className="font-semibold text-gray-900 mr-1">
          Context <ArrowRight className="w-3 h-3 inline -mt-0.5 mx-0.5" />{" "}
          Research
        </span>{" "}
        <span>domain context attached</span>
      </>
    ),
  },
  // Agent 1: Research (5s - 10s)
  {
    time: 6200,
    dot: "bg-purple-400",
    text: "benchmarking industry standards for seniority level",
  },
  {
    time: 7800,
    dot: "bg-purple-400",
    text: "identifying core evaluation metrics & interview depth",
  },
  {
    time: 9500,
    dot: "bg-purple-500",
    text: (
      <>
        <span className="font-semibold text-gray-900 mr-1">
          Research <ArrowRight className="w-3 h-3 inline -mt-0.5 mx-0.5" />{" "}
          Planning
        </span>{" "}
        <span>skill matrix compiled</span>
      </>
    ),
  },
  // Agent 2: Planning (10s - 15s)
  {
    time: 11200,
    dot: "bg-orange-400",
    text: "formulating goal structure & scoring criteria",
  },
  {
    time: 12800,
    dot: "bg-orange-400",
    text: "configuring dynamic interviewer agent system prompt",
  },
  {
    time: 14500,
    dot: "bg-orange-500",
    text: (
      <>
        <span className="font-semibold text-gray-900 mr-1">
          Planning <ArrowRight className="w-3 h-3 inline -mt-0.5 mx-0.5" />{" "}
          Finished
        </span>{" "}
        <span>interview campaign plan locked</span>
      </>
    ),
  },
  // Agent 3: Finished (15s - 20s)
  {
    time: 16200,
    dot: "bg-emerald-400",
    text: "provisioning LiveKit room infrastructure",
  },
  {
    time: 18000,
    dot: "bg-emerald-400",
    text: "generating candidate access tokens & invite links",
  },
  {
    time: 20000,
    dot: "bg-emerald-500",
    text: (
      <>
        <span className="font-semibold text-gray-900">
          Interview is ready!
        </span>{" "}
      </>
    ),
  },
];

export const EMOJIS = [
  "💼",
  "🚀",
  "💻",
  "🧠",
  "🔥",
  "🎯",
  "⭐",
  "🎨",
  "🛠️",
  "📈",
  "🌍",
  "⚡",
  "🤖",
  "📊",
  "🤝",
  "💡",
];
