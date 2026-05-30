import React from 'react';
import { Github, FileCode, ExternalLink, PlayCircle, Trash2, Clock, BookOpen, Loader2 } from 'lucide-react';
import type { ArtifactRead } from '../../types/api';

interface Props {
    artifact: ArtifactRead;
    onAnalyze: (id: number) => void;
    onDelete: (id: number, type: any) => void;
    isAnalyzing?: boolean;
}

const statusStyles: Record<string, string> = {
    completed: 'bg-green-50 text-green-600',
    processing: 'bg-blue-50 text-blue-600',
    failed: 'bg-red-50 text-red-600',
    pending: 'bg-amber-50 text-amber-600',
};

const formatLabel = (value: string) =>
    value
        .split('_')
        .map(part => part.charAt(0).toUpperCase() + part.slice(1))
        .join(' ');

export const ArtifactCard: React.FC<Props> = ({ artifact, onAnalyze, onDelete, isAnalyzing = false }) => {
    const Icon = artifact.type === 'paper' ? BookOpen : artifact.type === 'repo' ? Github : FileCode;
    const title = artifact.metadata.title || artifact.metadata.repo_id || artifact.metadata.original_name || "Unknown Artifact";
    const canAnalyze = artifact.status === 'pending' || artifact.status === 'failed';
    const scoreEntries = Object.entries(artifact.analysis?.scores ?? {}).slice(0, 3);

    return (
        <div className="group bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800 p-5 rounded-[2rem] flex flex-col hover:border-blue-500/50 transition-all shadow-sm hover:shadow-xl hover:shadow-blue-500/5">
            <div className="flex justify-between items-start mb-4">
                <div className={`p-3 rounded-2xl ${artifact.type === 'paper' ? 'bg-orange-50 text-orange-600' : 'bg-blue-50 text-blue-600'} dark:bg-slate-800`}>
                    <Icon size={24} />
                </div>
                <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button onClick={() => onDelete(artifact.id, artifact.type)} className="p-2 text-slate-300 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-xl transition-all">
                        <Trash2 size={16} />
                    </button>
                    <a href={artifact.source_url} target="_blank" className="p-2 text-slate-300 hover:text-blue-500 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-xl transition-all">
                        <ExternalLink size={16} />
                    </a>
                </div>
            </div>

            <div className="flex-1 min-w-0 mb-4">
                <h4 className="font-bold text-sm line-clamp-2 dark:text-white" title={title}>{title}</h4>
                <div className="flex items-center gap-2 mt-2">
                    <span className="text-[9px] font-black uppercase tracking-widest px-2 py-0.5 bg-slate-100 dark:bg-slate-800 text-slate-500 rounded-md">
                        {artifact.type}
                    </span>
                    <span className={`text-[9px] font-black uppercase tracking-widest px-2 py-0.5 rounded-md ${statusStyles[artifact.status] || statusStyles.pending}`}>
                        {artifact.status}
                    </span>
                </div>
            </div>

            {artifact.analysis && (
                <div className="mb-4 space-y-3">
                    <p className="text-xs leading-5 text-slate-500 dark:text-slate-300 line-clamp-4">
                        {artifact.analysis.summary_markdown}
                    </p>
                    {scoreEntries.length > 0 && (
                        <div className="flex flex-wrap gap-2">
                            {scoreEntries.map(([label, value]) => (
                                <span
                                    key={label}
                                    className="px-2.5 py-1 rounded-full bg-slate-100 dark:bg-slate-800 text-[10px] font-black uppercase tracking-wide text-slate-500"
                                >
                                    {formatLabel(label)}: {value}
                                </span>
                            ))}
                        </div>
                    )}
                </div>
            )}

            <div className="flex items-center justify-between pt-4 border-t border-slate-50 dark:border-slate-800">
                <div className="flex items-center gap-1.5 text-[9px] font-bold text-slate-400">
                    <Clock size={12} /> {new Date(artifact.created_at).toLocaleDateString()}
                </div>
                {(isAnalyzing || artifact.status === 'processing') && (
                    <button
                        disabled
                        className="flex items-center gap-1.5 px-3 py-1.5 bg-blue-100 text-blue-600 rounded-xl text-[10px] font-black uppercase tracking-tight"
                    >
                        <Loader2 size={14} className="animate-spin" /> Analyzing
                    </button>
                )}
                {canAnalyze && !isAnalyzing && artifact.status !== 'processing' && (
                    <button
                        onClick={() => onAnalyze(artifact.id)}
                        className="flex items-center gap-1.5 px-3 py-1.5 bg-blue-600 text-white rounded-xl text-[10px] font-black uppercase tracking-tight hover:bg-blue-700 transition-all active:scale-95 shadow-lg shadow-blue-600/20"
                    >
                        <PlayCircle size={14} /> Analyze
                    </button>
                )}
            </div>
        </div>
    );
};
