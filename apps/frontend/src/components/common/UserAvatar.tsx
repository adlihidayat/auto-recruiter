import React from "react";

interface UserAvatarProps {
  className?: string;
}

export default function UserAvatar({
  className = "w-10 h-10",
}: UserAvatarProps) {
  return (
    <div
      className={`rounded-full bg-[#f2f2f2] flex items-center justify-center shrink-0 overflow-hidden relative ${className}`}
    >
      <svg
        viewBox="0 0 24 24"
        className="w-[105%] h-[105%] fill-[#b8b9bb] translate-y-[15%]"
      >
        <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" />
      </svg>
    </div>
  );
}
