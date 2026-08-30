/**
 * What: Quick Action Command Palette Modal component.
 * Why: Allows users to trigger quick actions across the app via shortcut "K" or "Cmd+K".
 * Boundaries: Global layout overlay component.
 */

"use client";

import React, { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import {
  Search,
  LayersPlus,
  Home,
  Layers,
  CheckCircle2,
  Copy,
  ArrowRight,
  Sparkles,
  X,
} from "lucide-react";
import { useCreateModalStore } from "@/lib/store/useCreateModalStore";

interface QuickActionModalProps {
  isOpen: boolean;
  onClose: () => void;
}

interface ActionItem {
  id: string;
  category: "Actions" | "Navigation" | "Recents";
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

  const actions: ActionItem[] = [
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
      id: "copy-invite-link",
      category: "Actions",
      title: "Copy Candidate Room Link",
      description: "Copy active LiveKit candidate room token to clipboard",
      icon: <Copy className="w-4 h-4 text-purple-500" />,
      perform: () => {
        onClose();
        navigator.clipboard.writeText(
          `${window.location.origin}/interview?token=mock_room_token_1`
        );
      },
    },
    {
      id: "nav-home",
      category: "Navigation",
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
      category: "Navigation",
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
      category: "Navigation",
      title: "Filter Active Campaigns",
      description: "Display only campaigns with evaluating candidates",
      icon: <CheckCircle2 className="w-4 h-4 text-emerald-500" />,
      perform: () => {
        onClose();
        router.push("/");
      },
    },
    {
      id: "recent-1",
      category: "Recents",
      title: "Retail Sales Associate",
      description: "Core | Mid-Level | 3 Goals",
      icon: <span className="text-sm">😀️</span>,
      perform: () => {
        onClose();
        router.push("/interviews/campaign-0");
      },
    },
    {
      id: "recent-2",
      category: "Recents",
      title: "Lead Frontend Engineer",
      description: "Engineering | Senior | 4 Goals",
      icon: <span className="text-sm">📈️</span>,
      perform: () => {
        onClose();
        router.push("/interviews/campaign-1");
      },
    },
  ];

  const filteredActions = actions.filter((item) => {
    if (!query.trim()) return true;
    const q = query.toLowerCase();
    return (
      item.title.toLowerCase().includes(q) ||
      item.description.toLowerCase().includes(q) ||
      item.category.toLowerCase().includes(q)
    );
  });

  // Handle keyboard navigation inside popup
  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "ArrowDown") {
        e.preventDefault();
        setSelectedIndex((prev) =>
          prev < filteredActions.length - 1 ? prev + 1 : 0
        );
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        setSelectedIndex((prev) =>
          prev > 0 ? prev - 1 : filteredActions.length - 1
        );
      } else if (e.key === "Enter") {
        e.preventDefault();
        if (filteredActions[selectedIndex]) {
          filteredActions[selectedIndex].perform();
        }
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, selectedIndex, filteredActions]);

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-center pt-24 bg-black/40 backdrop-blur-xs animate-in fade-in duration-150"
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
            placeholder="Type a command or search quick actions..."
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
              onClick={onClose}
              className="p-1 text-gray-400 hover:text-gray-900 rounded-md transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Actions List */}
        <div className="max-h-96 overflow-y-auto p-2 space-y-1 custom-scrollbar">
          {filteredActions.length === 0 ? (
            <div className="py-8 text-center text-xs font-medium text-gray-400">
              No matching quick actions found.
            </div>
          ) : (
            filteredActions.map((action, idx) => {
              const isSelected = idx === selectedIndex;
              return (
                <div
                  key={action.id}
                  onClick={() => action.perform()}
                  onMouseEnter={() => setSelectedIndex(idx)}
                  className={`flex items-center justify-between px-3 py-2.5 rounded-xl cursor-pointer transition-all ${
                    isSelected
                      ? "bg-gray-100/90 text-gray-900 font-medium"
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
            })
          )}
        </div>

        {/* Footer shortcuts helper */}
        <div className="px-4 py-2 bg-[#FAFAFA] border-t border-gray-100 flex items-center justify-between text-[11px] text-gray-500 font-medium">
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
              Select
            </span>
          </div>
          <div className="flex items-center gap-1 text-gray-400">
            <Sparkles className="w-3 h-3 text-orange-500" />
            <span>Quick Actions Palette</span>
          </div>
        </div>
      </div>
    </div>
  );
};
