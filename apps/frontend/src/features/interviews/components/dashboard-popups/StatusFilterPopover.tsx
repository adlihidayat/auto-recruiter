/**
 * What: Status Filter Popover styled strictly to match CompareFilterPopover theme.
 * Why: Allows users to filter campaign list by status (All, Finished, In-progress, Not started).
 * Boundaries: Rendered in Dashboard table toolbar.
 */

import React from "react";
import { Check } from "lucide-react";

export type StatusFilterType =
  | "ALL"
  | "FINISHED"
  | "IN_PROGRESS"
  | "NOT_STARTED";

interface StatusFilterPopoverProps {
  isOpen: boolean;
  selectedStatus: StatusFilterType;
  totalCount: number;
  finishedCount: number;
  inProgressCount: number;
  notStartedCount: number;
  onSelect: (status: StatusFilterType) => void;
}

export const StatusFilterPopover: React.FC<StatusFilterPopoverProps> = ({
  isOpen,
  selectedStatus,
  totalCount,
  finishedCount,
  inProgressCount,
  notStartedCount,
  onSelect,
}) => {
  if (!isOpen) return null;

  const items: Array<{ id: StatusFilterType; label: string; count: number }> = [
    { id: "ALL", label: "All Status", count: totalCount },
    { id: "FINISHED", label: "Finished", count: finishedCount },
    { id: "IN_PROGRESS", label: "In-progress", count: inProgressCount },
    { id: "NOT_STARTED", label: "Not started", count: notStartedCount },
  ];

  return (
    <div
      className="absolute right-0 top-10 z-50 w-56 bg-white border border-gray-200/80 rounded-xl shadow-xs p-2.5 animate-in fade-in zoom-in-95 duration-150"
      onClick={(e) => e.stopPropagation()}
    >
      <div className="text-[10px] font-semibold text-gray-600 uppercase tracking-wider px-3 py-1.5 mb-1">
        Status Filter
      </div>

      <div className="space-y-1">
        {items.map((item) => {
          const isSelected = selectedStatus === item.id;
          return (
            <div
              key={item.id}
              onClick={() => onSelect(item.id)}
              className={`flex items-center justify-between px-3 py-2 rounded-md cursor-pointer transition-all ${
                isSelected
                  ? "bg-gray-100/90 font-bold"
                  : "hover:bg-gray-50 text-gray-700"
              }`}
            >
              <span className="text-sm font-medium text-gray-900">
                {item.label}
              </span>
              <div className="flex items-center gap-2">
                <span className="text-[12px] font-mono text-gray-400">
                  {item.count}
                </span>
                {isSelected && (
                  <Check className="w-3.5 h-3.5 text-orange-500 stroke-[2.5]" />
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
