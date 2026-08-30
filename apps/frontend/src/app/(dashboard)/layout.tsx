"use client";

import React from "react";
import {
  Search,
  Home,
  ChevronDown,
  Info,
  Settings,
  Bell,
  LayersPlus,
} from "lucide-react";
import Image from "next/image";
import Link from "next/link";
import { useRouter } from "next/navigation";
import CreateInterviewModal from "@/features/interviews/components/CreateInterviewModal";
import { useCreateModalStore } from "@/lib/store/useCreateModalStore";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const { isOpen, openModal, closeModal } = useCreateModalStore();

  const handleCampaignCreated = () => {
    router.refresh();
    if (typeof window !== "undefined") {
      window.dispatchEvent(new Event("campaignCreated"));
    }
  };

  return (
    <div className="h-screen w-screen bg-[#F4F4F5] overflow-hidden text-[#18181B] selection:bg-indigo-500 selection:text-white font-sans">
      <div className="flex h-full w-full bg-white shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-gray-200 overflow-hidden">
        {/* Sidebar */}
        <aside className="w-[240px] flex-shrink-0 bg-[#FAFAFA] border-r border-gray-200 flex flex-col">
          {/* Workspace Header */}
          <div className="px-4 pt-5 pb-3 flex items-center gap-2 cursor-pointer">
            <Image src="/logo.svg" alt="Logo" width={20} height={20} />
            <span className="text-sm font-semibold flex-1 truncate">
              Auto-Recruiter
            </span>
            <ChevronDown className="w-4 h-4 text-gray-400" />
          </div>

          {/* Search Bar */}
          <div className="px-2 mb-2">
            <div className="flex items-center gap-2 px-3 py-1.5 bg-white border border-gray-200 rounded-lg text-sm font-medium text-gray-600  cursor-text">
              <Search className="w-4 h-4" />
              <span className="flex-1">Quick actions</span>
              <kbd className="text-xs bg-gray-100 px-1.5 rounded text-gray-500 font-mono">
                K
              </kbd>
            </div>
          </div>

          {/* Scrollable Nav */}
          <div className="flex-1 overflow-y-auto px-2 space-y-6">
            <div className="space-y-0.5">
              <Link
                href="/"
                className="flex w-full items-center gap-3 px-3 py-1.5 text-sm font-medium text-gray-600 hover:text-gray-900 rounded-md hover:bg-gray-100 transition-colors"
              >
                <Home className="w-4 h-4" strokeWidth={2} /> Home
              </Link>
              <button
                onClick={openModal}
                className="flex w-full items-center gap-3 px-3 py-1.5 text-sm font-medium text-gray-600 hover:text-gray-900 rounded-md hover:bg-gray-100 transition-colors cursor-pointer"
              >
                <LayersPlus className="w-4 h-4" strokeWidth={2} /> Create
              </button>
              <button
                disabled
                className="flex w-full disabled:opacity-30 disabled:text-gray-600 disabled:bg-transparent items-center gap-3 px-3 py-1.5 text-sm font-medium text-gray-600 hover:text-gray-900 rounded-md hover:bg-gray-100 transition-colors"
              >
                <Bell className="w-4 h-4" strokeWidth={2} /> Notifications
              </button>
              <button
                disabled
                className="flex w-full disabled:opacity-30 disabled:text-gray-600 disabled:bg-transparent items-center gap-3 px-3 py-1.5 text-sm font-medium text-gray-600 hover:text-gray-900 rounded-md hover:bg-gray-100 transition-colors"
              >
                <Settings className="w-4 h-4" strokeWidth={2} /> Settings
              </button>
              <button
                disabled
                className="flex w-full disabled:opacity-30 disabled:text-gray-600 disabled:bg-transparent items-center gap-3 px-3 py-1.5 text-sm font-medium text-gray-600 hover:text-gray-900 rounded-md hover:bg-gray-100 transition-colors"
              >
                <Info className="w-4 h-4" strokeWidth={2} /> App Information
              </button>
            </div>

            <div className="space-y-0.5">
              <h3 className="px-3 text-xs font-semibold text-gray-400 mb-2">
                Recents
              </h3>
              <a
                href="#"
                className="flex capitalize items-center gap-3 px-3 py-1.5 text-sm font-medium text-gray-600 hover:text-gray-900 rounded-md hover:bg-gray-100"
              >
                <span>😀️</span>
                <span className="truncate max-w-56">
                  Retail sales associate
                </span>
              </a>
              <a
                href="#"
                className="flex capitalize items-center gap-3 px-3 py-1.5 text-sm font-medium text-gray-600 hover:text-gray-900 rounded-md hover:bg-gray-100"
              >
                <span>📈️</span>
                <span className="truncate max-w-56">
                  lead frontend engineer
                </span>
              </a>
              <a
                href="#"
                className="flex capitalize items-center gap-3 px-3 py-1.5 text-sm font-medium text-gray-600 hover:text-gray-900 rounded-md hover:bg-gray-100"
              >
                <span>🚗️</span>
                <span className="truncate max-w-56">
                  Retail sales associate
                </span>
              </a>
              <a
                href="#"
                className="flex capitalize items-center gap-3 px-3 py-1.5 text-sm font-medium text-gray-600 hover:text-gray-900 rounded-md hover:bg-gray-100"
              >
                <span>🧑‍🍳️</span>
                <span className="truncate max-w-56">
                  lead frontend engineer
                </span>
              </a>
              <a
                href="#"
                className="flex capitalize items-center gap-3 px-3 py-1.5 text-sm font-medium text-gray-600 hover:text-gray-900 rounded-md hover:bg-gray-100"
              >
                <span>🫁️</span>
                <span className="truncate max-w-56">
                  Retail sales associate
                </span>
              </a>
            </div>
          </div>

          {/* Sticky Footer */}
          <div className="p-4 border-t border-gray-200 space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-1.5 px-2">
                <Image src="/profile.svg" alt="Avatar" width={20} height={20} />
                <span className="text-xs font-bold text-gray-900">
                  Dhiya Adli
                </span>
              </div>
              <button className="bg-[#EA3536] text-white px-3 py-1 rounded-md text-xs font-semibold hover:bg-red-800 transition-colors">
                Logout
              </button>
            </div>
          </div>
        </aside>

        {/* Main Content */}
        <main className="flex-1 bg-white overflow-hidden relative flex flex-col">
          {children}
        </main>
      </div>

      {/* Global Create Interview Modal */}
      {isOpen && (
        <CreateInterviewModal
          isOpen={isOpen}
          onClose={closeModal}
          onCampaignCreated={handleCampaignCreated}
        />
      )}
    </div>
  );
}
