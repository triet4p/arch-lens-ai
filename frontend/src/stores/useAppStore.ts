import { create } from 'zustand';
import { TRANSLATIONS } from '../constants/translations';

export type ViewMode = 'workspaces' | 'tech_radar';

interface AppState {
    isDarkMode: boolean;
    language: 'en' | 'vi';
    t: typeof TRANSLATIONS['en']; // Thêm dòng này
    currentView: ViewMode;
    isBackendReady: boolean;
    connectionError: string | null;
    activeOperations: Set<string>;
    minDisplayTimeReached: boolean;
    selectedWorkspaceId: number | null;

    toggleTheme: () => void;
    setLanguage: (lang: 'en' | 'vi') => void;
    setView: (view: ViewMode) => void;
    setBackendReady: (status: boolean) => void;
    setConnectionError: (error: string | null) => void;
    addOperation: (id: string) => void;
    removeOperation: (id: string) => void;
    setMinDisplayTimeReached: (status: boolean) => void;
    setSelectedWorkspaceId: (id: number | null) => void;
}

export const useAppStore = create<AppState>((set) => ({
    language: 'en',
    t: TRANSLATIONS['en'], // Thêm dòng này
    isDarkMode: true,
    currentView: 'workspaces',
    isBackendReady: false,
    connectionError: null,
    activeOperations: new Set(),
    minDisplayTimeReached: false,
    selectedWorkspaceId: null,

    toggleTheme: () => set((state) => ({ isDarkMode: !state.isDarkMode })),
    // Sửa lại hàm này để cập nhật cả object `t`
    setLanguage: (lang) => set({ language: lang, t: TRANSLATIONS[lang] }),
    setView: (view) => set({ currentView: view }),
    setBackendReady: (status) => set({ isBackendReady: status }),
    setConnectionError: (error) => set({ connectionError: error }),
    addOperation: (id) => set((state) => {
        const newOps = new Set(state.activeOperations);
        newOps.add(id);
        return { activeOperations: newOps };
    }),
    removeOperation: (id) => set((state) => {
        const newOps = new Set(state.activeOperations);
        newOps.delete(id);
        return { activeOperations: newOps };
    }),
    setMinDisplayTimeReached: (status) => set({ minDisplayTimeReached: status }),
    setSelectedWorkspaceId: (id) => set({ selectedWorkspaceId: id }),
}));

export const hasActiveOperations = (): boolean => {
    return useAppStore.getState().activeOperations.size > 0;
};