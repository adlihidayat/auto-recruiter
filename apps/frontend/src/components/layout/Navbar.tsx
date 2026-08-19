"use client";

/**
 * What: Top navigation header bar component for the Auto-Recruiter HR Dashboard.
 * Why: Provides brand identity, system status monitoring, quick search, and HR profile navigation with logout capability.
 * Boundaries: Does not handle route rendering or candidate scoring logic.
 */

import React, { useState } from "react";
import {
  Search,
  Bell,
  FileText,
  ChevronDown,
  FileCode2,
  LogOut,
  User,
} from "lucide-react";
import Image from "next/image";
import { useRouter } from "next/navigation";
import { logoutAction } from "@/features/auth/actions";

export default function Navbar() {
  const router = useRouter();
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  const handleLogout = async () => {
    // Clear document cookie on client
    document.cookie =
      "access_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT;";
    // Call server action to delete cookie
    await logoutAction();
    setIsDropdownOpen(false);
    router.push("/login");
    router.refresh();
  };

  return (
    <header className="w-full py-6">
      <div className="max-w-350 mx-auto px-12 flex items-center justify-between">
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

          {/* HR User Avatar Pill & Popup Container */}
          <div className="relative">
            <button
              onClick={() => setIsDropdownOpen(!isDropdownOpen)}
              className="flex items-center gap-3 px-3 py-2.5 bg-white rounded-full hover:bg-gray-50 transition-colors text-left cursor-pointer"
            >
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
              <ChevronDown
                className={`w-6 h-6 text-[#616161] ml-2 transition-transform duration-200 ${
                  isDropdownOpen ? "rotate-180" : ""
                }`}
              />
            </button>

            {/* Profile Dropdown Popup */}
            {isDropdownOpen && (
              <>
                {/* Backdrop to close on click outside */}
                <div
                  className="fixed inset-0 z-40"
                  onClick={() => setIsDropdownOpen(false)}
                />

                <div className="absolute right-0 top-full mt-2 w-64 bg-white rounded-2xl shadow-xl border border-[#F1F1F1] p-2 z-50 animate-in fade-in zoom-in-95 duration-150">
                  <div className="px-3 py-2.5 border-b border-[#F1F1F1]">
                    <div className="flex items-center gap-2 text-xs font-semibold text-[#272727]">
                      <User className="w-4 h-4 text-[#616161]" />
                      <span>Logged in User</span>
                    </div>
                    <p className="text-xs text-[#616161] mt-1 truncate font-medium">
                      admin@example.com
                    </p>
                  </div>

                  <div className="pt-1">
                    <button
                      onClick={handleLogout}
                      className="w-full flex items-center gap-2.5 px-3 py-2.5 rounded-xl text-sm font-semibold text-red-600 hover:bg-red-50 transition-colors cursor-pointer text-left"
                    >
                      <LogOut className="w-4 h-4" />
                      Logout
                    </button>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
