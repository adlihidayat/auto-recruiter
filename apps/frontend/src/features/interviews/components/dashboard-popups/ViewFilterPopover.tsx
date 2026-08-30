/**
 * What: View Filter Popover styled strictly to match CompareFilterPopover theme.
 * Why: Allows switching view modes (All campaigns, Active only, Archived).
 * Boundaries: Rendered in Dashboard table toolbar.
 */

import React from "react";
import { Layers, CheckCircle2, Archive, Check } from "lucide-react";

export type ViewFilterType = "all" | "active" | "archived";

interface ViewFilterPopoverProps {
  isOpen: boolean;
  selectedView: ViewFilterType;
  onSelect: (view: ViewFilterType) => void;
}

export const ViewFilterPopover: React.FC<ViewFilterPopoverProps> = ({
  isOpen,
  selectedView,
  onSelect,
}) => {
  if (!isOpen) return null;

  const views: Array<{
    id: ViewFilterType;
    label: string;
    desc: string;
    icon: React.ReactNode;
  }> = [
    {
      id: "all",
      label: "All Campaigns",
      desc: "View active & ongoing campaigns",
      icon: <Layers className="w-3.5 h-3.5 text-gray-700" />,
    },
    {
      id: "active",
      label: "Active Only",
      desc: "Campaigns with evaluating candidates",
      icon: <CheckCircle2 className="w-3.5 h-3.5 text-gray-700" />,
    },
    {
      id: "archived",
      label: "Archived",
      desc: "Completed & archived campaigns",
      icon: <Archive className="w-3.5 h-3.5 text-gray-700" />,
    },
  ];

  return (
    <div
      className="absolute left-0 top-10 z-50 w-64 bg-white border border-gray-200/80 rounded-xl shadow-xs p-2.5 animate-in fade-in zoom-in-95 duration-150"
      onClick={(e) => e.stopPropagation()}
    >
      <div className="text-[10px] font-semibold text-gray-600 uppercase tracking-wider px-3 py-1.5 mb-1">
        View Preset
      </div>

      <div className="space-y-1">
        {views.map((view) => {
          const isSelected = selectedView === view.id;
          return (
            <div
              key={view.id}
              onClick={() => onSelect(view.id)}
              className={`flex items-center justify-between px-3 py-2 rounded-md cursor-pointer transition-all ${
                isSelected
                  ? "bg-gray-100/90 font-bold"
                  : "hover:bg-gray-50 text-gray-700"
              }`}
            >
              <div className="flex items-center gap-2.5">
                <div className="w-6 h-6 rounded-md bg-gray-100 flex items-center justify-center shrink-0">
                  {view.icon}
                </div>
                <div>
                  <div className="text-sm font-medium text-gray-900 leading-tight">
                    {view.label}
                  </div>
                  <div className="text-[10px] text-gray-500 font-normal leading-none mt-0.5">
                    {view.desc}
                  </div>
                </div>
              </div>
              {isSelected && (
                <Check className="w-3.5 h-3.5 text-orange-500 stroke-[2.5] shrink-0" />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
