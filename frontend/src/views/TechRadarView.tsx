import React from 'react';
import { Activity, Loader2, Radar } from 'lucide-react';

import { useTechRadar } from '../hooks/useWorkspaceReview';


const ringOrder = ['adopt', 'trial', 'assess', 'hold'] as const;

const ringStyles: Record<typeof ringOrder[number], string> = {
    adopt: 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-300',
    trial: 'bg-blue-50 text-blue-700 dark:bg-blue-950/40 dark:text-blue-300',
    assess: 'bg-amber-50 text-amber-700 dark:bg-amber-950/40 dark:text-amber-300',
    hold: 'bg-red-50 text-red-700 dark:bg-red-950/40 dark:text-red-300',
};


export const TechRadarView: React.FC = () => {
    const { data, isLoading } = useTechRadar();

    if (isLoading) {
        return (
            <div className="flex h-full items-center justify-center text-slate-400">
                <div className="flex items-center gap-3 text-sm font-bold">
                    <Loader2 size={18} className="animate-spin text-blue-600" />
                    Building tech radar...
                </div>
            </div>
        );
    }

    const entries = data?.entries ?? [];

    return (
        <div className="space-y-8 animate-in fade-in duration-500 pb-16">
            <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
                <div>
                    <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400">
                        <Radar size={18} />
                        <span className="text-[11px] font-black uppercase tracking-[0.24em]">Cross-Workspace Radar</span>
                    </div>
                    <h2 className="mt-2 text-3xl font-black tracking-tight">Tech Radar</h2>
                    <p className="mt-2 max-w-3xl text-sm text-slate-500 dark:text-slate-300">
                        The radar aggregates workspace reviews into a single strategic surface, grouped by recommendation ring.
                    </p>
                </div>

                <div className="flex flex-wrap gap-3">
                    <div className="rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 px-4 py-3">
                        <div className="text-[10px] font-black uppercase tracking-[0.18em] text-slate-400">Workspaces</div>
                        <div className="mt-2 text-2xl font-black tracking-tight">{data?.workspaces_covered ?? 0}</div>
                    </div>
                    <div className="rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 px-4 py-3">
                        <div className="text-[10px] font-black uppercase tracking-[0.18em] text-slate-400">Signals</div>
                        <div className="mt-2 text-2xl font-black tracking-tight">{entries.length}</div>
                    </div>
                </div>
            </div>

            {entries.length > 0 ? (
                <div className="grid grid-cols-1 gap-6 xl:grid-cols-4">
                    {ringOrder.map((ring) => {
                        const ringEntries = entries.filter(entry => entry.ring === ring);
                        return (
                            <section key={ring} className="space-y-4">
                                <div className={`rounded-2xl px-4 py-3 ${ringStyles[ring]}`}>
                                    <div className="flex items-center justify-between gap-3">
                                        <span className="text-xs font-black uppercase tracking-[0.24em]">{ring}</span>
                                        <span className="text-sm font-black">{data?.counts?.[ring] ?? 0}</span>
                                    </div>
                                </div>

                                <div className="space-y-3">
                                    {ringEntries.length > 0 ? ringEntries.map((entry) => (
                                        <article key={entry.name} className="rounded-[1.5rem] border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 px-4 py-4 shadow-sm">
                                            <div className="flex items-start justify-between gap-3">
                                                <div className="min-w-0">
                                                    <h3 className="text-sm font-black text-slate-900 dark:text-white">{entry.name}</h3>
                                                    <div className="mt-2 flex flex-wrap gap-2">
                                                        <span className="px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-[10px] font-black uppercase tracking-wide text-slate-500 dark:text-slate-300">
                                                            {entry.quadrant}
                                                        </span>
                                                        <span className="px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-[10px] font-black uppercase tracking-wide text-slate-500 dark:text-slate-300">
                                                            Score {entry.score}
                                                        </span>
                                                    </div>
                                                </div>
                                                <Activity size={16} className="text-slate-300" />
                                            </div>

                                            <p className="mt-3 text-sm leading-6 text-slate-500 dark:text-slate-300">{entry.evidence}</p>
                                            <p className="mt-3 text-[11px] font-black uppercase tracking-wide text-slate-400">
                                                {entry.workspace_ids.length} workspace{entry.workspace_ids.length === 1 ? '' : 's'}
                                            </p>
                                        </article>
                                    )) : (
                                        <div className="rounded-[1.5rem] border border-dashed border-slate-200 dark:border-slate-800 px-4 py-8 text-center text-sm text-slate-400">
                                            No signals in this ring.
                                        </div>
                                    )}
                                </div>
                            </section>
                        );
                    })}
                </div>
            ) : (
                <div className="rounded-[2rem] border-2 border-dashed border-slate-200 dark:border-slate-800 px-6 py-20 text-center text-slate-400 bg-slate-50/50 dark:bg-slate-900/20">
                    No radar signals are available yet. Analyze artifacts and refresh workspace reviews first.
                </div>
            )}
        </div>
    );
};
