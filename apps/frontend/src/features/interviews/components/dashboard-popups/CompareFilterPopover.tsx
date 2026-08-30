/**
 * What: Compare Range Filter Popover.
 * Why: Allows comparing campaign metrics by date preset (This month, Last month, Q3 2026, All time).
 * Boundaries: Rendered in Dashboard top filter bar.
 */

import React from "react";
import { Check } from "lucide-react";

interface CompareFilterPopoverProps {
  isOpen: boolean;
  selectedRange: string;
  onSelect: (range: string) => void;
}

export const CompareFilterPopover: React.FC<CompareFilterPopoverProps> = ({
  isOpen,
  selectedRange,
  onSelect,
}) => {
  if (!isOpen) return null;

  const ranges = ["This month", "Last month", "Q3 2026", "All time"];

  return (
    <div
      className="absolute left-0 top-10 z-50 w-52 bg-white border border-gray-200/80 rounded-xl shadow-xs p-2.5 animate-in fade-in zoom-in-95 duration-150"
      onClick={(e) => e.stopPropagation()}
    >
      <div className="text-[10px] font-semibold text-gray-600 uppercase tracking-wider px-3 py-1.5 mb-1">
        Compare Range
      </div>

      <div className="space-y-1">
        {ranges.map((range) => {
          const isSelected = selectedRange === range;
          return (
            <div
              key={range}
              onClick={() => onSelect(range)}
              className={`flex items-center justify-between px-3 py-2 rounded-md cursor-pointer transition-all ${
                isSelected
                  ? "bg-gray-100/90 font-bold"
                  : "hover:bg-gray-50 text-gray-700"
              }`}
            >
              <span className="text-sm font-medium text-gray-900">{range}</span>
              {isSelected && (
                <Check className="w-3.5 h-3.5 text-orange-500 stroke-[2.5]" />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
