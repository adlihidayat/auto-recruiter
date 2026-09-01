/**
 * What: Quick Action Command Palette Modal component.
 * Why: Allows users to trigger quick actions and search across all interview campaigns via "K" shortcut.
 * Boundaries: Global layout overlay component.
 */

"use client";

import React, { useState, useEffect, useRef, useMemo } from "react";
import { useRouter } from "next/navigation";
import {
  Search,
  LayersPlus,
  Home,
  Layers,
  CheckCircle2,
  ArrowRight,
  X,
  Briefcase,
} from "lucide-react";
import { useCreateModalStore } from "@/lib/store/useCreateModalStore";
import {
  getInterviewsApi,
  getRecentInterviewsApi,
  BackendInterviewResponse,
} from "@/lib/api/client";

interface QuickActionModalProps {
  isOpen: boolean;
  onClose: () => void;
}

interface ActionItem {
  id: string;
  category: "Actions" | "Recent Interviews" | "Matching Interviews";
  title: string;
  description: string;
  icon: React.ReactNode;
  perform: () => void;
}

export const QuickActionModal: React.FC<QuickActionModalProps> = ({
  isOpen,
  onClose,
}) => {
  const router = useRouter();
  const { openModal } = useCreateModalStore();
  const [query, setQuery] = useState("");
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);

  const [allInterviews, setAllInterviews] = useState<BackendInterviewResponse[]>([]);
  const [recentInterviews, setRecentInterviews] = useState<BackendInterviewResponse[]>([]);

  // Focus input & reset query on mount
  useEffect(() => {
    if (isOpen) {
      const timer = setTimeout(() => {
        setQuery("");
        setSelectedIndex(0);
        inputRef.current?.focus();
      }, 50);
      return () => clearTimeout(timer);
    }
  }, [isOpen]);

  // Fetch real interviews and recents when modal opens
  useEffect(() => {
    if (!isOpen) return;

    let isCancelled = false;
    async function loadData() {
      try {
        const rawToken = document.cookie
          .split("; ")
          .find((row) => row.startsWith("access_token="))
          ?.split("=")[1];
        const tokenCookie = rawToken ? decodeURIComponent(rawToken) : null;
        if (!tokenCookie) return;

        const [interviewsRes, recentsRes] = await Promise.all([
          getInterviewsApi(tokenCookie).catch(() => []),
          getRecentInterviewsApi(tokenCookie).catch(() => []),
        ]);

        if (!isCancelled) {
          setAllInterviews(interviewsRes || []);
          setRecentInterviews(recentsRes || []);
        }
      } catch {
        // Fallback
      }
    }

    loadData();
    return () => {
      isCancelled = true;
    };
  }, [isOpen]);

  // Core Quick Actions
  const quickActions: ActionItem[] = useMemo(
    () => [
      {
        id: "create-campaign",
        category: "Actions",
        title: "Create New Interview",
        description: "Set up a new AI interview campaign with 4 agents",
        icon: <LayersPlus className="w-4 h-4 text-orange-500" />,
        perform: () => {
          onClose();
          openModal();
        },
      },
      {
        id: "nav-home",
        category: "Actions",
        title: "Go to Home / Dashboard",
        description: "Return to main campaigns table view",
        icon: <Home className="w-4 h-4 text-blue-500" />,
        perform: () => {
          onClose();
          router.push("/");
        },
      },
      {
        id: "filter-all",
        category: "Actions",
        title: "View All Campaigns",
        description: "Show all active, finished & draft campaigns",
        icon: <Layers className="w-4 h-4 text-gray-700" />,
        perform: () => {
          onClose();
          router.push("/");
        },
      },
      {
        id: "filter-active",
        category: "Actions",
        title: "Filter Active Campaigns",
        description: "Display only campaigns with evaluating candidates",
        icon: <CheckCircle2 className="w-4 h-4 text-emerald-500" />,
        perform: () => {
          onClose();
          router.push("/");
        },
      },
    ],
    [onClose, openModal, router],
  );

  // Real recent interviews
  const recentActions: ActionItem[] = useMemo(
    () =>
      recentInterviews.map((item) => ({
        id: `recent-${item.id}`,
        category: "Recent Interviews" as const,
        title: item.job_name,
        description: `${item.domain_hint || "General"} | ${item.difficulty || "Mid"} | ${item.status.replace(/_/g, " ")}`,
        icon: <span className="text-sm">{item.icon || "💼"}</span>,
        perform: () => {
          onClose();
          router.push(`/interviews/${item.id}`);
        },
      })),
    [recentInterviews, onClose, router],
  );

  // All real interviews in database
  const allInterviewActions: ActionItem[] = useMemo(
    () =>
      allInterviews.map((item) => ({
        id: `interview-${item.id}`,
        category: "Matching Interviews" as const,
        title: item.job_name,
        description: `${item.domain_hint || "General"} | ${item.difficulty || "Mid"} | ${item.status.replace(/_/g, " ")}`,
        icon: <span className="text-sm">{item.icon || "💼"}</span>,
        perform: () => {
          onClose();
          router.push(`/interviews/${item.id}`);
        },
      })),
    [allInterviews, onClose, router],
  );

  // Determine active item set depending on query search
  const displayedActions: ActionItem[] = useMemo(() => {
    const isSearching = query.trim().length > 0;
    const q = query.toLowerCase();

    if (!isSearching) {
      return [...quickActions, ...recentActions];
    }

    const filteredQuick = quickActions.filter(
      (item) =>
        item.title.toLowerCase().includes(q) ||
        item.description.toLowerCase().includes(q),
    );

    const filteredInterviews = allInterviewActions.filter(
      (item) =>
        item.title.toLowerCase().includes(q) ||
        item.description.toLowerCase().includes(q),
    );

    return [...filteredQuick, ...filteredInterviews];
  }, [query, quickActions, recentActions, allInterviewActions]);

  // Group displayed actions by category
  const categories = useMemo(
    () => Array.from(new Set(displayedActions.map((item) => item.category))),
    [displayedActions],
  );

  // Handle keyboard navigation inside popup
  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "ArrowDown") {
        e.preventDefault();
        setSelectedIndex((prev) =>
          prev < displayedActions.length - 1 ? prev + 1 : 0,
        );
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        setSelectedIndex((prev) =>
          prev > 0 ? prev - 1 : displayedActions.length - 1,
        );
      } else if (e.key === "Enter") {
        e.preventDefault();
        if (displayedActions[selectedIndex]) {
          displayedActions[selectedIndex].perform();
        }
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, selectedIndex, displayedActions]);

  if (!isOpen) return null;

  let globalIndexCounter = 0;

  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-center pt-44 bg-black/40 backdrop-blur-xs animate-in fade-in duration-150"
      onClick={onClose}
    >
      <div
        className="w-full max-w-xl bg-white border border-gray-200/80 rounded-2xl shadow-2xl overflow-hidden animate-in zoom-in-95 duration-150"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Search Header */}
        <div className="flex items-center px-4 py-3 border-b border-gray-100 gap-3">
          <Search className="w-4 h-4 text-gray-400 shrink-0" />
          <input
            ref={inputRef}
            type="text"
            placeholder="Type to search interviews or actions..."
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              setSelectedIndex(0);
            }}
            className="w-full bg-transparent text-sm text-gray-900 font-medium placeholder:text-gray-400 outline-none"
          />
          <div className="flex items-center gap-1.5 shrink-0">
            <kbd className="px-2 py-0.5 text-[10px] font-mono font-semibold bg-gray-100 text-gray-500 rounded border border-gray-200">
              ESC
            </kbd>
            <button
              type="button"
              onClick={onClose}
              className="p-1 text-gray-400 hover:text-gray-900 rounded-md transition-colors cursor-pointer"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Actions & Interviews List */}
        <div className="max-h-96 overflow-y-auto p-2 space-y-3 custom-scrollbar">
          {displayedActions.length === 0 ? (
            <div className="py-8 text-center text-xs font-medium text-gray-400">
              No matching interviews or quick actions found.
            </div>
          ) : (
            categories.map((cat) => {
              const categoryItems = displayedActions.filter(
                (item) => item.category === cat,
              );
              if (categoryItems.length === 0) return null;

              return (
                <div key={cat} className="space-y-1">
                  <div className="text-[10px] font-semibold text-gray-500 uppercase tracking-wider px-3 py-1">
                    {cat}
                  </div>
                  {categoryItems.map((action) => {
                    const currentIndex = globalIndexCounter++;
                    const isSelected = currentIndex === selectedIndex;

                    return (
                      <div
                        key={action.id}
                        onClick={() => action.perform()}
                        onMouseEnter={() => setSelectedIndex(currentIndex)}
                        className={`flex items-center justify-between px-3 py-2 rounded-xl cursor-pointer transition-all ${
                          isSelected
                            ? "bg-gray-100/90 text-gray-900 font-semibold"
                            : "hover:bg-gray-50 text-gray-700"
                        }`}
                      >
                        <div className="flex items-center gap-3 min-w-0">
                          <div className="w-7 h-7 rounded-lg bg-gray-100 flex items-center justify-center shrink-0">
                            {action.icon}
                          </div>
                          <div className="truncate">
                            <div className="text-sm font-medium text-gray-900 leading-tight truncate">
                              {action.title}
                            </div>
                            <div className="text-xs text-gray-500 font-normal leading-none mt-0.5 truncate">
                              {action.description}
                            </div>
                          </div>
                        </div>
                        {isSelected && (
                          <ArrowRight className="w-4 h-4 text-orange-500 shrink-0" />
                        )}
                      </div>
                    );
                  })}
                </div>
              );
            })
          )}
        </div>

        {/* Footer shortcuts helper */}
        <div className="px-4 py-2.5 bg-[#FAFAFA] border-t border-gray-100 flex items-center justify-between text-[11px] text-gray-500 font-medium">
          <div className="flex items-center gap-3">
            <span className="flex items-center gap-1">
              <kbd className="px-1.5 py-0.5 bg-white border border-gray-200 rounded font-mono text-[10px]">
                ↑↓
              </kbd>{" "}
              Navigate
            </span>
            <span className="flex items-center gap-1">
              <kbd className="px-1.5 py-0.5 bg-white border border-gray-200 rounded font-mono text-[10px]">
                ↵
              </kbd>{" "}
              Open
            </span>
          </div>
          <div className="flex items-center gap-1.5 text-gray-500">
            <Briefcase className="w-3.5 h-3.5 text-orange-500" />
            <span>
              Search {allInterviews.length > 0 ? `${allInterviews.length}` : "0"} Campaigns & Actions
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
