import React from 'react';
import { FolderOpen, Layers, Clock, Trash2 } from 'lucide-react';
import type { WorkspaceRead } from '../../types/api';

interface Props {
    workspace: WorkspaceRead;
    onDelete: (id: number) => void;
    onClick: (id: number) => void;
}

export const WorkspaceCard: React.FC<Props> = ({ workspace, onDelete, onClick }) => {
    return (
        <div onClick={() => onClick(workspace.id)} className="group bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-6 rounded-[2rem] hover:shadow-xl hover:shadow-blue-500/5 transition-all cursor-pointer relative overflow-hidden">
            <div className="flex justify-between items-start mb-4">
                <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-2xl text-blue-600">
                    <FolderOpen size={24} />
                </div>
                <button 
                    onClick={(e) => { e.stopPropagation(); onDelete(workspace.id); }}
                    className="p-2 text-slate-300 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-xl transition-all opacity-0 group-hover:opacity-100"
                >
                    <Trash2 size={18} />
                </button>
            </div>

            <h3 className="text-xl font-black tracking-tight mb-2 group-hover:text-blue-600 transition-colors">{workspace.name}</h3>
            <p className="text-sm text-slate-500 line-clamp-2 mb-6 h-10">{workspace.description || "No description provided."}</p>

            <div className="flex items-center gap-4 text-[10px] font-black uppercase tracking-widest text-slate-400 border-t border-slate-100 dark:border-slate-800 pt-4">
                <div className="flex items-center gap-1.5">
                    <Layers size={14} /> {workspace.artifacts_count} Artifacts
                </div>
                <div className="flex items-center gap-1.5">
                    <Clock size={14} /> {new Date(workspace.updated_at).toLocaleDateString()}
                </div>
            </div>
        </div>
    );
};