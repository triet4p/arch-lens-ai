import React, { useState } from 'react';
import { X, Plus, Target, Cpu, HardDrive, Send } from 'lucide-react';
import type { WorkspaceCreate } from '../../types/api';

interface Props {
    isOpen: boolean;
    onClose: () => void;
    onSubmit: (data: WorkspaceCreate) => void;
    isPending: boolean;
}

export const CreateWorkspaceModal: React.FC<Props> = ({ isOpen, onClose, onSubmit, isPending }) => {
    const [name, setName] = useState('');
    const [desc, setDesc] = useState('');
    const [gpu, setGpu] = useState('24GB VRAM');
    const [stack, setStack] = useState('Python/FastAPI');

    if (!isOpen) return null;

    const handleFormSubmit = (e: React.SyntheticEvent) => {
        e.preventDefault();
        onSubmit({
            name,
            description: desc,
            constraints: { gpu_limit: gpu, current_stack: stack }
        });
    };

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-slate-950/80 backdrop-blur-sm p-4 animate-in fade-in duration-300">
            <div className="bg-white dark:bg-slate-900 w-full max-w-2xl rounded-[2.5rem] shadow-2xl border border-slate-200 dark:border-slate-800 overflow-hidden">
                <div className="px-8 py-6 border-b border-slate-100 dark:border-slate-800 flex justify-between items-center">
                    <div className="flex items-center gap-3">
                        <Target className="text-blue-600" size={24} />
                        <h3 className="text-xl font-black uppercase tracking-tight">New Strategic Workspace</h3>
                    </div>
                    <button onClick={onClose} className="p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-xl text-slate-400"><X size={20} /></button>
                </div>

                <form onSubmit={handleFormSubmit} className="p-8 space-y-6">
                    <div className="space-y-2">
                        <label className="text-[10px] font-black uppercase tracking-widest text-slate-400 ml-1">Project Name</label>
                        <input required value={name} onChange={e => setName(e.target.value)} type="text" placeholder="e.g., Evaluating Agentic Frameworks" className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-2xl px-5 py-3 text-sm font-bold outline-none focus:border-blue-500 transition-all" />
                    </div>

                    <div className="space-y-2">
                        <label className="text-[10px] font-black uppercase tracking-widest text-slate-400 ml-1">Description</label>
                        <textarea value={desc} onChange={e => setDesc(e.target.value)} placeholder="What is the R&D goal?" className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-2xl px-5 py-3 text-sm font-bold outline-none focus:border-blue-500 transition-all h-24 resize-none" />
                    </div>

                    {/* Strategic Constraints Section */}
                    <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                            <label className="text-[10px] font-black uppercase tracking-widest text-slate-400 ml-1 flex items-center gap-1"><Cpu size={12}/> GPU Constraint</label>
                            <input value={gpu} onChange={e => setGpu(e.target.value)} type="text" className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-xl px-4 py-2 text-xs font-bold outline-none" />
                        </div>
                        <div className="space-y-2">
                            <label className="text-[10px] font-black uppercase tracking-widest text-slate-400 ml-1 flex items-center gap-1"><HardDrive size={12}/> Tech Stack</label>
                            <input value={stack} onChange={e => setStack(e.target.value)} type="text" className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-xl px-4 py-2 text-xs font-bold outline-none" />
                        </div>
                    </div>

                    <button disabled={isPending} type="submit" className="w-full py-4 bg-blue-600 hover:bg-blue-700 text-white font-black rounded-2xl shadow-lg shadow-blue-500/20 flex items-center justify-center gap-2 transition-all active:scale-95">
                        {isPending ? <Plus className="animate-spin" size={20} /> : <Send size={20} />}
                        Initialize Workspace
                    </button>
                </form>
            </div>
        </div>
    );
};