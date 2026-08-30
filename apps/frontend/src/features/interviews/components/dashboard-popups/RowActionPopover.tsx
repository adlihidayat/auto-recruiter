/**
 * What: Row 3-dots action menu popover styled strictly to match CompareFilterPopover theme.
 * Why: Provides quick actions for individual campaign rows (View, Copy link, Archive, Delete).
 * Boundaries: Local popover component for Dashboard table rows.
 */

import React from "react";
import { ExternalLink, Copy, Archive, Trash2 } from "lucide-react";

interface RowActionPopoverProps {
  isOpen: boolean;
  onClose: () => void;
  onViewDetail: () => void;
  onCopyLink: () => void;
  onArchive: () => void;
  onDelete: () => void;
}

export const RowActionPopover: React.FC<RowActionPopoverProps> = ({
  isOpen,
  onViewDetail,
  onCopyLink,
  onArchive,
  onDelete,
}) => {
  if (!isOpen) return null;

  return (
    <div
      className="absolute right-0 top-10 z-50 w-60 bg-white border border-gray-200/80 rounded-xl shadow-xs p-2.5 animate-in fade-in zoom-in-95 duration-150 text-left"
      onClick={(e) => e.stopPropagation()}
    >
      <div className="text-[10px] font-semibold text-gray-600 uppercase tracking-wider px-3 py-1.5 mb-1">
        Actions
      </div>

      <button
        type="button"
        onClick={onViewDetail}
        className="w-full flex items-center justify-between px-3 py-2 rounded-md hover:bg-gray-50 transition-colors text-left group cursor-pointer"
      >
        <div className="flex items-center gap-2.5">
          <div className="w-6 h-6 rounded-md bg-gray-100 text-gray-700 flex items-center justify-center shrink-0">
            <ExternalLink className="w-3.5 h-3.5" />
          </div>
          <div>
            <div className="text-sm font-medium text-gray-900 leading-tight">
              View Details
            </div>
            <div className="text-[10px] text-gray-500 font-normal leading-none mt-0.5">
              Open campaign report
            </div>
          </div>
        </div>
      </button>

      <button
        type="button"
        onClick={onCopyLink}
        className="w-full flex items-center justify-between px-3 py-2 rounded-md hover:bg-gray-50 transition-colors text-left group cursor-pointer"
      >
        <div className="flex items-center gap-2.5">
          <div className="w-6 h-6 rounded-md bg-gray-100 text-gray-700 flex items-center justify-center shrink-0">
            <Copy className="w-3.5 h-3.5" />
          </div>
          <div>
            <div className="text-sm font-medium text-gray-900 leading-tight">
              Copy Room Link
            </div>
            <div className="text-[10px] text-gray-500 font-normal leading-none mt-0.5">
              Copy candidate link
            </div>
          </div>
        </div>
      </button>

      <div className="my-1.5 border-t border-gray-100" />

      <div className="text-[10px] font-semibold text-gray-600 uppercase tracking-wider px-3 py-1.5 mb-1">
        Manage
      </div>

      <button
        type="button"
        onClick={onArchive}
        className="w-full flex items-center justify-between px-3 py-2 rounded-md hover:bg-gray-50 transition-colors text-left group cursor-pointer"
      >
        <div className="flex items-center gap-2.5">
          <div className="w-6 h-6 rounded-md bg-gray-100 text-gray-700 flex items-center justify-center shrink-0">
            <Archive className="w-3.5 h-3.5" />
          </div>
          <div>
            <div className="text-sm font-medium text-gray-900 leading-tight">
              Archive Campaign
            </div>
            <div className="text-[10px] text-gray-500 font-normal leading-none mt-0.5">
              Hide from active view
            </div>
          </div>
        </div>
      </button>

      <button
        type="button"
        onClick={onDelete}
        className="w-full flex items-center justify-between px-3 py-2 rounded-md hover:bg-red-50 transition-colors text-left group cursor-pointer"
      >
        <div className="flex items-center gap-2.5">
          <div className="w-6 h-6 rounded-md bg-red-100/60 text-red-600 flex items-center justify-center shrink-0">
            <Trash2 className="w-3.5 h-3.5" />
          </div>
          <div>
            <div className="text-sm font-medium text-red-600 leading-tight">
              Delete Campaign
            </div>
            <div className="text-[10px] text-red-400 font-normal leading-none mt-0.5">
              Permanently remove
            </div>
          </div>
        </div>
      </button>
    </div>
  );
};
