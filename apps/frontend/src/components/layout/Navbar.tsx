/**
 * What: Top navigation header bar component for the Auto-Recruiter HR Dashboard.
 * Why: Provides brand identity, system status monitoring, quick search, and HR profile navigation.
 * Boundaries: Does not handle route rendering, page-level layouts, or candidate scoring logic.
 */

import React from "react";
import { Bot, Sparkles, Search, Bell, ShieldCheck } from "lucide-react";

export default function Navbar() {
  return (
    <header className="sticky top-0 z-40 w-full glass-panel border-b border-slate-800/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-4">
        {/* Brand identity */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-purple-600 to-pink-500 flex items-center justify-center shadow-lg shadow-indigo-500/20">
            <Bot className="w-6 h-6 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-lg tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
                Auto-Recruiter
              </span>
              <span className="inline-flex items-center gap-1 text-[10px] font-semibold px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                <Sparkles className="w-2.5 h-2.5" /> AI Engine v2.0
              </span>
            </div>
            <p className="text-xs text-slate-400">Autonomous Talent Acquisition Platform</p>
          </div>
        </div>

        {/* Global Search input */}
        <div className="hidden md:flex items-center flex-1 max-w-md mx-8">
          <div className="relative w-full">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input
              type="text"
              placeholder="Search interviews, candidates, or target roles..."
              className="w-full bg-slate-900/80 border border-slate-800 rounded-xl pl-9 pr-4 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/50 transition-all"
            />
          </div>
        </div>

        {/* Action items & user profile */}
        <div className="flex items-center gap-3">
          {/* Agent Pipeline Active Indicator */}
          <div className="hidden sm:flex items-center gap-2 px-3 py-1 rounded-lg bg-emerald-950/40 border border-emerald-800/40 text-emerald-400 text-xs">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
            <span className="font-medium">Agents Online</span>
          </div>

          <button className="relative p-2 rounded-lg bg-slate-900/60 border border-slate-800 text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors">
            <Bell className="w-4 h-4" />
            <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-indigo-500" />
          </button>

          <div className="h-6 w-px bg-slate-800" />

          {/* HR User Avatar */}
          <div className="flex items-center gap-2.5 pl-1 cursor-pointer">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-indigo-600 flex items-center justify-center text-xs font-bold text-white shadow-md">
              HR
            </div>
            <div className="hidden lg:block text-left">
              <div className="text-xs font-medium text-slate-200">Sarah Jenkins</div>
              <div className="text-[10px] text-slate-400">Head of Talent</div>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
