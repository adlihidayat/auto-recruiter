/**
 * What: Notion-style Emoji Picker Popover grid.
 * Why: Allows users to choose a icon emoji for their interview campaign.
 * Boundaries: Rendered within Step 1 form view.
 */

import React from "react";
import { EMOJIS } from "./constants";

interface EmojiPickerPopoverProps {
  isOpen: boolean;
  onSelect: (emoji: string) => void;
  containerRef: React.RefObject<HTMLDivElement | null>;
}

export const EmojiPickerPopover: React.FC<EmojiPickerPopoverProps> = ({
  isOpen,
  onSelect,
  containerRef,
}) => {
  if (!isOpen) return null;

  return (
    <div
      ref={containerRef}
      className="absolute top-14 left-0 z-50 p-2.5 bg-white border border-gray-200 rounded-2xl shadow-xl animate-in fade-in zoom-in-95 duration-150 grid grid-cols-4 gap-1.5 w-48"
    >
      {EMOJIS.map((emoji) => (
        <button
          key={emoji}
          type="button"
          onClick={() => onSelect(emoji)}
          className="w-9 h-9 flex items-center justify-center text-xl rounded-xl hover:bg-gray-100 transition-colors cursor-pointer"
        >
          {emoji}
        </button>
      ))}
    </div>
  );
};
