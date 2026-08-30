/**
 * What: Department Filter Popover styled strictly to match CompareFilterPopover theme.
 * Why: Allows filtering campaigns by department (Core, Engineering, Product, Design, Marketing).
 * Boundaries: Rendered in Dashboard top filter bar.
 */

import React from "react";
import { Check } from "lucide-react";

interface DepartmentFilterPopoverProps {
  isOpen: boolean;
  selectedDepartment: string;
  onSelect: (dept: string) => void;
}

export const DepartmentFilterPopover: React.FC<DepartmentFilterPopoverProps> = ({
  isOpen,
  selectedDepartment,
  onSelect,
}) => {
  if (!isOpen) return null;

  const departments = [
    "All departments",
    "Core",
    "Engineering",
    "Product",
    "Design",
    "Marketing",
  ];

  return (
    <div
      className="absolute right-0 top-10 z-50 w-52 bg-white border border-gray-200/80 rounded-xl shadow-xs p-2.5 animate-in fade-in zoom-in-95 duration-150"
      onClick={(e) => e.stopPropagation()}
    >
      <div className="text-[10px] font-semibold text-gray-600 uppercase tracking-wider px-3 py-1.5 mb-1">
        Department
      </div>

      <div className="space-y-1">
        {departments.map((dept) => {
          const isSelected = selectedDepartment === dept;
          return (
            <div
              key={dept}
              onClick={() => onSelect(dept)}
              className={`flex items-center justify-between px-3 py-2 rounded-md cursor-pointer transition-all ${
                isSelected
                  ? "bg-gray-100/90 font-bold"
                  : "hover:bg-gray-50 text-gray-700"
              }`}
            >
              <span className="text-sm font-medium text-gray-900">{dept}</span>
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
