import { create } from "zustand";

/**
 * What: Global state for toggling the Create Interview modal.
 * Why: Allows sidebar button or any page component to trigger the Create Interview popup.
 * Boundaries: Client state store for modal UI visibility.
 */
interface CreateModalState {
  isOpen: boolean;
  openModal: () => void;
  closeModal: () => void;
}

export const useCreateModalStore = create<CreateModalState>((set) => ({
  isOpen: false,
  openModal: () => set({ isOpen: true }),
  closeModal: () => set({ isOpen: false }),
}));
