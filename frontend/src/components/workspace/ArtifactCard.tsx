import React from 'react';
import { FileText, Github, FileCode, ExternalLink, PlayCircle, Trash2, Clock, BookOpen } from 'lucide-react';
import type { ArtifactRead } from '../../types/api';

interface Props {
    artifact: ArtifactRead;
    onAnalyze: (id: number) => void;
    onDelete: (id: number, type: any) => void;
}

export const ArtifactCard: React.FC<Props> = ({ artifact, onAnalyze, onDelete }) => {
    const Icon = artifact.type === 'paper' ? BookOpen : artifact.type === 'repo' ? Github : FileCode;
    const title = artifact.metadata.title || artifact.metadata.repo_id || artifact.metadata.original_name || "Unknown Artifact";

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
                    <span className={`text-[9px] font-black uppercase tracking-widest px-2 py-0.5 rounded-md ${artifact.status === 'completed' ? 'bg-green-50 text-green-600' : 'bg-amber-50 text-amber-600'}`}>
                        {artifact.status}
                    </span>
                </div>
            </div>

            <div className="flex items-center justify-between pt-4 border-t border-slate-50 dark:border-slate-800">
                <div className="flex items-center gap-1.5 text-[9px] font-bold text-slate-400">
                    <Clock size={12} /> {new Date(artifact.created_at).toLocaleDateString()}
                </div>
                {artifact.status === 'pending' && (
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