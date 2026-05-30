import React, { useEffect } from 'react';
import { AlertCircle, CheckCircle2, Info, X } from 'lucide-react';

import { useAppStore } from '../../stores/useAppStore';


const toneStyles = {
    info: 'border-blue-200 bg-blue-50 text-blue-700 dark:border-blue-900/50 dark:bg-blue-950/50 dark:text-blue-200',
    success: 'border-emerald-200 bg-emerald-50 text-emerald-700 dark:border-emerald-900/50 dark:bg-emerald-950/50 dark:text-emerald-200',
    error: 'border-red-200 bg-red-50 text-red-700 dark:border-red-900/50 dark:bg-red-950/50 dark:text-red-200',
};

const toneIcons = {
    info: Info,
    success: CheckCircle2,
    error: AlertCircle,
};


export const NotificationCenter: React.FC = () => {
    const { notifications, removeNotification } = useAppStore();

    useEffect(() => {
        if (notifications.length === 0) return;

        const timers = notifications.map((notification) =>
            window.setTimeout(() => removeNotification(notification.id), notification.tone === 'error' ? 8000 : 5000)
        );
        return () => timers.forEach((timer) => window.clearTimeout(timer));
    }, [notifications, removeNotification]);

    if (notifications.length === 0) return null;

    return (
        <div className="pointer-events-none fixed right-6 top-6 z-[120] flex w-full max-w-sm flex-col gap-3">
            {notifications.map((notification) => {
                const Icon = toneIcons[notification.tone];
                return (
                    <div
                        key={notification.id}
                        className={`pointer-events-auto rounded-2xl border px-4 py-4 shadow-xl ${toneStyles[notification.tone]}`}
                    >
                        <div className="flex items-start gap-3">
                            <Icon size={18} className="mt-0.5 shrink-0" />
                            <div className="min-w-0 flex-1">
                                <div className="text-sm font-black">{notification.title}</div>
                                <p className="mt-1 text-sm leading-5 opacity-90">{notification.message}</p>
                            </div>
                            <button
                                onClick={() => removeNotification(notification.id)}
                                className="rounded-lg p-1 opacity-70 transition hover:bg-black/5 hover:opacity-100 dark:hover:bg-white/10"
                            >
                                <X size={14} />
                            </button>
                        </div>
                    </div>
                );
            })}
        </div>
    );
};
