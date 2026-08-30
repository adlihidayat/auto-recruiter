/**
 * What: Metrics Display Settings Popover styled strictly to match CompareFilterPopover theme.
 * Why: Allows toggling visual charts and metric card views.
 * Boundaries: Rendered in Dashboard table toolbar.
 */

import React from "react";

interface MetricsFilterPopoverProps {
  isOpen: boolean;
  showChart: boolean;
  onToggleChart: () => void;
  showStats: boolean;
  onToggleStats: () => void;
}

export const MetricsFilterPopover: React.FC<MetricsFilterPopoverProps> = ({
  isOpen,
  showChart,
  onToggleChart,
  showStats,
  onToggleStats,
}) => {
  if (!isOpen) return null;

  return (
    <div
      className="absolute right-0 top-10 z-50 w-64 bg-white border border-gray-200/80 rounded-xl shadow-xs p-2.5 animate-in fade-in zoom-in-95 duration-150"
      onClick={(e) => e.stopPropagation()}
    >
      <div className="text-[10px] font-semibold text-gray-600 uppercase tracking-wider px-3 py-1.5 mb-1">
        Metrics Settings
      </div>

      <div className="space-y-1">
        {/* Toggle Chart */}
        <div className="flex items-center justify-between px-3 py-2 rounded-md hover:bg-gray-50 transition-colors">
          <div>
            <div className="text-sm font-medium text-gray-900 leading-tight">
              Monthly Chart
            </div>
            <div className="text-[10px] text-gray-500 font-normal leading-none mt-0.5">
              Display bar chart overview
            </div>
          </div>
          <button
            type="button"
            onClick={onToggleChart}
            className={`w-9 h-5 rounded-full p-0.5 transition-colors flex items-center cursor-pointer shadow-inner ${
              showChart ? "bg-orange-500 justify-end" : "bg-gray-200 justify-start"
            }`}
          >
            <div className="w-4 h-4 bg-white rounded-full shadow-md" />
          </button>
        </div>

        {/* Toggle Stats Cards */}
        <div className="flex items-center justify-between px-3 py-2 rounded-md hover:bg-gray-50 transition-colors">
          <div>
            <div className="text-sm font-medium text-gray-900 leading-tight">
              Stats Cards
            </div>
            <div className="text-[10px] text-gray-500 font-normal leading-none mt-0.5">
              Show header counter metrics
            </div>
          </div>
          <button
            type="button"
            onClick={onToggleStats}
            className={`w-9 h-5 rounded-full p-0.5 transition-colors flex items-center cursor-pointer shadow-inner ${
              showStats ? "bg-orange-500 justify-end" : "bg-gray-200 justify-start"
            }`}
          >
            <div className="w-4 h-4 bg-white rounded-full shadow-md" />
          </button>
        </div>
      </div>
    </div>
  );
};
