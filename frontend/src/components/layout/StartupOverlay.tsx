import React, { useEffect, useState } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { useAppStore } from '../../stores/useAppStore';
import { AlertCircle, RefreshCw, ScanSearch, Sparkles } from 'lucide-react';

const LOADING_MESSAGES =[
    "Waking up the Evaluation Engine...",
    "Connecting to Local Knowledge Base...",
    "Loading Strategic Lens...",
    "Initializing Neural Auditors...",
];

export const StartupOverlay: React.FC<{canEnter: boolean}> = ({ canEnter }) => {
    const { connectionError, setConnectionError, pushNotification } = useAppStore();
    const [messageIndex, setMessageIndex] = useState(0);
    const[shouldRender, setShouldRender] = useState(true);
    const [retrying, setRetrying] = useState(false);

    useEffect(() => {
        if (canEnter) return;
        const interval = setInterval(() => setMessageIndex((prev) => (prev + 1) % LOADING_MESSAGES.length), 2000);
        return () => clearInterval(interval);
    }, [canEnter]);

    useEffect(() => {
        if (canEnter) {
            const timer = setTimeout(() => setShouldRender(false), 1000);
            return () => clearTimeout(timer);
        }
    }, [canEnter]);

    if (!shouldRender) return null;

    const handleRetry = async () => {
        setRetrying(true);
        setConnectionError(null);
        try {
            await invoke('start_sidecar');
            pushNotification({
                tone: 'info',
                title: 'Retry started',
                message: 'Another sidecar start attempt was issued.',
            });
        } catch (error: any) {
            const message = error?.message || 'Unable to retry the sidecar startup.';
            setConnectionError(message);
            pushNotification({
                tone: 'error',
                title: 'Retry failed',
                message,
            });
        } finally {
            setRetrying(false);
        }
    };

    return (
        <div className={`fixed inset-0 z-[9999] flex flex-col items-center justify-center bg-slate-50 dark:bg-slate-950 transition-all duration-1000 ease-in-out ${canEnter ? 'opacity-0 pointer-events-none scale-110' : 'opacity-100'}`}>
            <div className="relative flex flex-col items-center max-w-sm w-full px-8">
                <div className="mb-8 relative">
                    <div className="w-20 h-20 rounded-3xl bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center text-white shadow-2xl animate-bounce">
                        <ScanSearch size={40} />
                    </div>
                    <Sparkles className="absolute -top-2 -right-2 text-yellow-400 animate-pulse" size={24} />
                </div>

                <h1 className="text-2xl font-black tracking-tighter text-slate-900 dark:text-white mb-2 uppercase">Arch Lens AI</h1>
                <p className="text-slate-500 dark:text-slate-400 text-[10px] font-bold uppercase tracking-[0.3em] mb-12">The R&D Operating System</p>

                {connectionError ? (
                    <div className="w-full p-6 bg-red-50 dark:bg-red-900/20 border border-red-100 dark:border-red-900/30 rounded-3xl">
                        <div className="flex items-center justify-center gap-3 text-red-600 dark:text-red-400 mb-3">
                            <AlertCircle size={24} /><span className="font-bold text-sm">Connection Failed</span>
                        </div>
                        <p className="text-xs text-red-500 dark:text-red-300 mb-6 text-center">{connectionError}</p>
                        <button
                            onClick={handleRetry}
                            disabled={retrying}
                            className="w-full inline-flex items-center justify-center gap-2 rounded-2xl bg-red-600 px-4 py-3 text-xs font-black uppercase tracking-wide text-white disabled:opacity-60"
                        >
                            {retrying ? <RefreshCw size={16} className="animate-spin" /> : <RefreshCw size={16} />}
                            Retry sidecar start
                        </button>
                    </div>
                ) : (
                    <div className="w-full space-y-6">
                        <div className="flex flex-col items-center">
                            <span className="text-sm font-bold italic text-blue-600 dark:text-blue-400 mb-4 h-6 animate-pulse">{LOADING_MESSAGES[messageIndex]}</span>
                            <div className="w-full h-1.5 bg-slate-200 dark:bg-slate-800 rounded-full overflow-hidden shadow-inner">
                                <div className="h-full bg-blue-600 w-1/3 rounded-full animate-infinite-scroll"></div>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};
