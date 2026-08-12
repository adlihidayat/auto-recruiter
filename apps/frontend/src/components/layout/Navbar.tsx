/**
 * What: Top navigation header bar component for the Auto-Recruiter HR Dashboard.
 * Why: Provides brand identity, system status monitoring, quick search, and HR profile navigation.
 * Boundaries: Does not handle route rendering, page-level layouts, or candidate scoring logic.
 */

import React from "react";
import { Search, Bell, FileText, ChevronDown, FileCode2 } from "lucide-react";
import Image from "next/image";

export default function Navbar() {
  return (
    <header className="w-full py-6">
      <div className="max-w-[1400px] mx-auto px-12 flex items-center justify-between">
        {/* Brand identity */}
        <div className="flex items-center gap-1 text-black">
          <FileCode2 className="w-8 h-8" strokeWidth={2.5} />
          <span className="font-light text-3xl tracking-tight">auto-rec</span>
        </div>

        {/* Action items & user profile */}
        <div className="flex items-center gap-4">
          {/* Icons Pill */}
          <div className="flex items-center gap-7 px-5 py-4 bg-white rounded-full">
            <button className="text-gray-800 hover:text-black transition-colors">
              <Search className="w-5.5 h-5.5" strokeWidth={2} />
            </button>
            <button className="text-gray-800 hover:text-black transition-colors relative">
              <Bell className="w-5.5 h-5.5" strokeWidth={2} />
            </button>
            <button className="text-gray-800 hover:text-black transition-colors">
              <FileText className="w-5.5 h-5.5" strokeWidth={2} />
            </button>
          </div>

          {/* HR User Avatar Pill */}
          <button className="flex items-center gap-3 px-3 py-2.5 bg-white rounded-full hover:bg-gray-50 transition-colors text-left">
            <div className="w-10 h-10 rounded-full bg-gray-200 overflow-hidden relative shrink-0">
              <Image
                src="https://i.pravatar.cc/150?u=dhiya"
                alt="User Avatar"
                fill
                className="object-cover"
                unoptimized
              />
            </div>
            <div className="flex flex-col">
              <span className="text-base font-semibold text-[#272727] leading-tight">
                Dhiya Adli Hidayat
              </span>
              <span className="text-sm text-[#616161] font-medium">
                dhiyaadli30@gmai...
              </span>
            </div>
            <ChevronDown className="w-6 h-6 text-[#616161] ml-2" />
          </button>
        </div>
      </div>
    </header>
  );
}
