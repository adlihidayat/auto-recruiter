/**
 * What: Golden Star Rosette Ribbon Medal graphic component.
 * Why: Renders award badge with radial burst rays and geometric confetti (Image 1 reference).
 * Boundaries: Rendered inside Step 3 Hero Banner card. Scaled 1.60x per user spec.
 */

import React from "react";

export const GoldenRosetteMedal: React.FC = () => {
  return (
    <div className="relative w-36 h-36 flex items-center justify-center shrink-0 overflow-visible self-center group scale-[1.60] transform origin-center">
      {/* Radial Pink Burst Lines */}
      <svg
        className="absolute w-32 h-32 text-rose-400/80 animate-pulse pointer-events-none"
        viewBox="0 0 100 100"
      >
        <line
          x1="15"
          y1="15"
          x2="26"
          y2="26"
          stroke="currentColor"
          strokeWidth="2.5"
          strokeLinecap="round"
        />
        <line
          x1="85"
          y1="15"
          x2="74"
          y2="26"
          stroke="currentColor"
          strokeWidth="2.5"
          strokeLinecap="round"
        />
        <line
          x1="10"
          y1="50"
          x2="22"
          y2="50"
          stroke="currentColor"
          strokeWidth="2.5"
          strokeLinecap="round"
        />
        <line
          x1="90"
          y1="50"
          x2="78"
          y2="50"
          stroke="currentColor"
          strokeWidth="2.5"
          strokeLinecap="round"
        />
        <line
          x1="18"
          y1="85"
          x2="28"
          y2="74"
          stroke="currentColor"
          strokeWidth="2.5"
          strokeLinecap="round"
        />
        <line
          x1="82"
          y1="85"
          x2="72"
          y2="74"
          stroke="currentColor"
          strokeWidth="2.5"
          strokeLinecap="round"
        />
        <line
          x1="50"
          y1="8"
          x2="50"
          y2="20"
          stroke="currentColor"
          strokeWidth="2.5"
          strokeLinecap="round"
        />
      </svg>

      {/* Floating Geometric Confetti */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-1 left-2 w-2.5 h-2.5 bg-pink-400 rotate-12 animate-bounce" />
        <div className="absolute top-2 left-8 text-rose-500 font-extrabold text-xs animate-pulse">
          +
        </div>
        <div className="absolute top-5 right-2 w-0 h-0 border-l-[5px] border-l-transparent border-r-[5px] border-r-transparent border-b-[8px] border-b-purple-500 rotate-45 animate-pulse" />
        <div className="absolute bottom-2 left-3 w-2.5 h-2.5 rounded-full border-2 border-orange-400 animate-ping opacity-75" />
        <div className="absolute bottom-1 right-6 w-2.5 h-2.5 bg-amber-400 -rotate-12 animate-bounce" />
        <div className="absolute bottom-8 right-1 w-2 h-2 rounded-full bg-indigo-400 animate-pulse" />
      </div>

      {/* Golden Award Medal Rosette */}
      <div className="relative z-10 flex flex-col items-center justify-center transition-transform duration-500 ease-out group-hover:scale-105">
        <div className="relative w-24 h-24 flex items-center justify-center">
          {/* Purple Ribbon Tails hanging down */}
          <div className="absolute bottom-[-10px] left-3 w-7 h-10 bg-purple-600 rounded-b-md transform -rotate-15 shadow-sm overflow-hidden">
            <div className="w-full h-full bg-gradient-to-b from-purple-500 to-indigo-700" />
          </div>
          <div className="absolute bottom-[-10px] right-3 w-7 h-10 bg-purple-600 rounded-b-md transform rotate-15 shadow-sm overflow-hidden">
            <div className="w-full h-full bg-gradient-to-b from-purple-500 to-indigo-700" />
          </div>

          {/* Outer Scalloped Golden Badge */}
          <div className="w-20 h-20 rounded-full bg-gradient-to-tr from-amber-500 via-yellow-400 to-amber-300 border-4 border-amber-200 shadow-md flex items-center justify-center relative">
            {/* Inner Golden Circle with Central Star */}
            <div className="w-14 h-14 rounded-full bg-gradient-to-tr from-amber-300 to-yellow-200 border-2 border-amber-400 flex items-center justify-center shadow-inner">
              <svg
                className="w-8 h-8 text-amber-600 drop-shadow-xs"
                fill="currentColor"
                viewBox="0 0 24 24"
              >
                <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
              </svg>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
