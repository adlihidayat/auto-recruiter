/**
 * What: Utility helper functions for styling class name merging and common formatters.
 * Why: Centralizes standard utility logic used across components to prevent duplicate code.
 * Boundaries: Does not handle API logic, business domain rules, or component state.
 */

import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * Combines conditional class names and resolves Tailwind CSS class conflicts cleanly.
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
