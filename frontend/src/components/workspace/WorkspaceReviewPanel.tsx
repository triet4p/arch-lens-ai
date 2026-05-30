import React from 'react';
import { AlertTriangle, CheckCircle2, Download, Loader2, Radar, RefreshCw, ShieldAlert } from 'lucide-react';

import type { WorkspaceReviewRead } from '../../types/api';


interface Props {
    review?: WorkspaceReviewRead;
    isLoading: boolean;
    isRefreshing: boolean;
    isExporting: boolean;
    onRefresh: () => void;
    onExport: () => void;
}


const scoreStyles: Record<string, string> = {
    technical_fit_score: 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-300',
    risk_score: 'bg-red-50 text-red-700 dark:bg-red-950/40 dark:text-red-300',
    roi_score: 'bg-blue-50 text-blue-700 dark:bg-blue-950/40 dark:text-blue-300',
    confidence_score: 'bg-violet-50 text-violet-700 dark:bg-violet-950/40 dark:text-violet-300',
    evidence_coverage_score: 'bg-amber-50 text-amber-700 dark:bg-amber-950/40 dark:text-amber-300',
};


const formatLabel = (value: string) =>
    value
        .split('_')
        .map(part => part.charAt(0).toUpperCase() + part.slice(1))
        .join(' ');


const severityStyles: Record<string, string> = {
    low: 'text-amber-600 dark:text-amber-300',
    medium: 'text-orange-600 dark:text-orange-300',
    high: 'text-red-600 dark:text-red-300',
};


export const WorkspaceReviewPanel: React.FC<Props> = ({
    review,
    isLoading,
    isRefreshing,
    isExporting,
    onRefresh,
    onExport,
}) => {
    return (
        <section className="border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 rounded-[2rem] p-6 md:p-8 space-y-6 shadow-sm">
            <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
                <div className="space-y-2">
                    <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400">
                        <Radar size={18} />
                        <span className="text-[11px] font-black uppercase tracking-[0.24em]">Workspace Review</span>
                    </div>
                    <h3 className="text-2xl font-black tracking-tight text-slate-900 dark:text-white">
                        Findings, conflicts, and decision summary
                    </h3>
                    <p className="text-sm text-slate-500 dark:text-slate-300 max-w-3xl">
                        Cross-verification is computed from workspace constraints and the persisted artifact analyses already stored in the sidecar.
                    </p>
                </div>

                <div className="flex flex-wrap gap-2">
                    <button
                        onClick={onRefresh}
                        disabled={isRefreshing}
                        className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-900 text-white dark:bg-white dark:text-slate-900 text-xs font-black uppercase tracking-wide disabled:opacity-60"
                    >
                        {isRefreshing ? <Loader2 size={14} className="animate-spin" /> : <RefreshCw size={14} />}
                        Refresh Review
                    </button>
                    <button
                        onClick={onExport}
                        disabled={isExporting || !review}
                        className="inline-flex items-center gap-2 px-4 py-2 rounded-xl border border-slate-200 dark:border-slate-700 text-xs font-black uppercase tracking-wide text-slate-600 dark:text-slate-200 disabled:opacity-60"
                    >
                        {isExporting ? <Loader2 size={14} className="animate-spin" /> : <Download size={14} />}
                        Export Markdown
                    </button>
                </div>
            </div>

            {isLoading && !review ? (
                <div className="flex min-h-48 items-center justify-center text-slate-400">
                    <div className="flex items-center gap-3 text-sm font-bold">
                        <Loader2 size={18} className="animate-spin text-blue-600" />
                        Computing workspace review...
                    </div>
                </div>
            ) : review ? (
                <div className="space-y-6">
                    <div className="flex flex-wrap items-center gap-2">
                        <span className="px-3 py-1 rounded-full bg-blue-50 text-blue-700 dark:bg-blue-950/40 dark:text-blue-300 text-[11px] font-black uppercase tracking-wide">
                            Recommendation: {review.recommendation.label}
                        </span>
                        <span className="px-3 py-1 rounded-full bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-300 text-[11px] font-black uppercase tracking-wide">
                            {review.artifact_coverage.analyzed_artifacts}/{review.artifact_coverage.total_artifacts} analyzed
                        </span>
                    </div>

                    <div className="grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-5">
                        {Object.entries(review.scores).map(([label, value]) => (
                            <div
                                key={label}
                                className={`rounded-2xl border border-transparent px-4 py-3 ${scoreStyles[label] || 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-200'}`}
                            >
                                <div className="text-[10px] font-black uppercase tracking-[0.18em]">{formatLabel(label)}</div>
                                <div className="mt-2 text-2xl font-black tracking-tight">{value}</div>
                            </div>
                        ))}
                    </div>

                    <div className="rounded-2xl border border-slate-200 dark:border-slate-800 px-5 py-4 bg-slate-50 dark:bg-slate-950/40">
                        <p className="text-sm leading-6 text-slate-700 dark:text-slate-200">{review.decision_summary}</p>
                        <p className="mt-3 text-xs leading-5 text-slate-500 dark:text-slate-400">{review.recommendation.rationale}</p>
                    </div>

                    <div className="grid grid-cols-1 gap-6 xl:grid-cols-2">
                        <div className="space-y-4">
                            <div className="flex items-center gap-2 text-sm font-black uppercase tracking-wide text-slate-500 dark:text-slate-400">
                                <CheckCircle2 size={16} className="text-emerald-500" />
                                Findings
                            </div>
                            <div className="space-y-3">
                                {review.findings.length > 0 ? review.findings.map((finding) => (
                                    <div key={finding.title} className="rounded-2xl border border-slate-200 dark:border-slate-800 px-4 py-4">
                                        <div className="text-sm font-black text-slate-900 dark:text-white">{finding.title}</div>
                                        <p className="mt-2 text-sm leading-6 text-slate-500 dark:text-slate-300">{finding.detail}</p>
                                    </div>
                                )) : (
                                    <div className="rounded-2xl border border-dashed border-slate-200 dark:border-slate-800 px-4 py-6 text-sm text-slate-400">
                                        No positive findings yet.
                                    </div>
                                )}
                            </div>
                        </div>

                        <div className="space-y-4">
                            <div className="flex items-center gap-2 text-sm font-black uppercase tracking-wide text-slate-500 dark:text-slate-400">
                                <ShieldAlert size={16} className="text-red-500" />
                                Conflicts
                            </div>
                            <div className="space-y-3">
                                {review.conflicts.length > 0 ? review.conflicts.map((conflict) => (
                                    <div key={`${conflict.severity}-${conflict.title}`} className="rounded-2xl border border-slate-200 dark:border-slate-800 px-4 py-4">
                                        <div className={`text-sm font-black ${severityStyles[conflict.severity] || 'text-slate-900 dark:text-white'}`}>
                                            {conflict.title}
                                        </div>
                                        <p className="mt-2 text-sm leading-6 text-slate-500 dark:text-slate-300">{conflict.detail}</p>
                                    </div>
                                )) : (
                                    <div className="rounded-2xl border border-dashed border-slate-200 dark:border-slate-800 px-4 py-6 text-sm text-slate-400">
                                        No material conflicts detected.
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>

                    <div className="grid grid-cols-1 gap-6 xl:grid-cols-[1.3fr_1fr]">
                        <div className="space-y-4">
                            <div className="flex items-center gap-2 text-sm font-black uppercase tracking-wide text-slate-500 dark:text-slate-400">
                                <AlertTriangle size={16} className="text-amber-500" />
                                Recommended Next Steps
                            </div>
                            <ol className="space-y-3">
                                {review.recommended_next_steps.map((step, index) => (
                                    <li key={step} className="flex gap-3 rounded-2xl border border-slate-200 dark:border-slate-800 px-4 py-4">
                                        <span className="mt-0.5 text-xs font-black text-blue-600 dark:text-blue-300">{index + 1}.</span>
                                        <span className="text-sm leading-6 text-slate-500 dark:text-slate-300">{step}</span>
                                    </li>
                                ))}
                            </ol>
                        </div>

                        <div className="space-y-4">
                            <div className="flex items-center gap-2 text-sm font-black uppercase tracking-wide text-slate-500 dark:text-slate-400">
                                <Radar size={16} className="text-blue-500" />
                                Tech Radar Signals
                            </div>
                            <div className="space-y-3">
                                {review.radar_entries.length > 0 ? review.radar_entries.map((entry) => (
                                    <div key={entry.name} className="rounded-2xl border border-slate-200 dark:border-slate-800 px-4 py-4">
                                        <div className="flex flex-wrap items-center gap-2">
                                            <div className="text-sm font-black text-slate-900 dark:text-white">{entry.name}</div>
                                            <span className="px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-[10px] font-black uppercase tracking-wide text-slate-500 dark:text-slate-300">
                                                {entry.ring}
                                            </span>
                                            <span className="px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-[10px] font-black uppercase tracking-wide text-slate-500 dark:text-slate-300">
                                                {entry.quadrant}
                                            </span>
                                        </div>
                                        <p className="mt-2 text-sm leading-6 text-slate-500 dark:text-slate-300">{entry.evidence}</p>
                                    </div>
                                )) : (
                                    <div className="rounded-2xl border border-dashed border-slate-200 dark:border-slate-800 px-4 py-6 text-sm text-slate-400">
                                        No technology signals extracted yet.
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            ) : (
                <div className="rounded-2xl border border-dashed border-slate-200 dark:border-slate-800 px-4 py-10 text-center text-sm text-slate-400">
                    Review data is not available for this workspace yet.
                </div>
            )}
        </section>
    );
};
