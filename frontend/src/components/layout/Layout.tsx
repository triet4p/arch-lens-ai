import React from 'react';
import { useAppStore } from '../../stores/useAppStore';
import { FolderKanban, Activity, Sun, Moon, Languages, ScanSearch } from 'lucide-react';

export const Layout: React.FC<{children: React.ReactNode}> = ({ children }) => {
    const { currentView, setView, isDarkMode, toggleTheme, language, setLanguage, t } = useAppStore();

    return (
        <div className="flex h-screen overflow-hidden bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100">
            {/* Sidebar */}
            <aside className="w-64 bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800 flex flex-col">
                <div className="h-16 flex items-center gap-3 px-6 border-b border-slate-200 dark:border-slate-800">
                    <ScanSearch className="text-blue-600" size={24} />
                    <span className="text-lg font-black tracking-tighter uppercase">ARCH LENS</span>
                </div>
                
                <div className="flex-1 py-6 px-4 space-y-2">
                    <button onClick={() => setView('workspaces')} className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl font-bold text-sm transition-all ${currentView === 'workspaces' ? 'bg-blue-50 text-blue-600 dark:bg-blue-900/20 dark:text-blue-400' : 'text-slate-600 hover:bg-slate-50 dark:text-slate-400 dark:hover:bg-slate-800/50'}`}>
                        <FolderKanban size={18} /> {t.workspaces}
                    </button>
                    <button onClick={() => setView('tech_radar')} className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl font-bold text-sm transition-all ${currentView === 'tech_radar' ? 'bg-blue-50 text-blue-600 dark:bg-blue-900/20 dark:text-blue-400' : 'text-slate-600 hover:bg-slate-50 dark:text-slate-400 dark:hover:bg-slate-800/50'}`}>
                        <Activity size={18} /> {t.techRadar}
                    </button>
                </div>


            </aside>

            {/* Main Content Area */}
            <div className="flex flex-col flex-1 min-w-0">
                {/* Topbar */}
                <header className="h-16 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md border-b border-slate-200 dark:border-slate-800 flex items-center justify-end px-6 sticky top-0 z-10">
                    <div className="flex items-center gap-2">
                        <button onClick={() => setLanguage(language === 'en' ? 'vi' : 'en')} className="flex items-center gap-2 px-3 py-2 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-400 transition-all text-xs font-bold">
                            <Languages size={16} /> <span>{language.toUpperCase()}</span>
                        </button>
                        <div className="w-px h-5 bg-slate-200 dark:bg-slate-700 mx-1"></div>
                        <button onClick={toggleTheme} className="p-2 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-400 transition-all">
                            {isDarkMode ? <Sun size={18} /> : <Moon size={18} />}
                        </button>
                    </div>
                </header>

                <main className="flex-1 overflow-y-auto p-8">
                    {children}
                </main>
            </div>
        </div>
    );
};