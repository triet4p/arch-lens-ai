import React, { useState } from 'react';
import { X, BookOpen, Github, Upload, Send, Loader2, FileUp } from 'lucide-react';
import { useArtifacts } from '../../hooks/useArtifacts';

interface Props {
    isOpen: boolean;
    onClose: () => void;
    workspaceId: number;
}

type Tab = 'arxiv' | 'github' | 'local';

export const AddArtifactModal: React.FC<Props> = ({ isOpen, onClose, workspaceId }) => {
    const [activeTab, setActiveTab] = useState<Tab>('arxiv');
    const [inputValue, setInputValue] = useState('');
    const { addArxiv, addGithub, uploadFile } = useArtifacts(workspaceId);

    if (!isOpen) return null;

    const handleAction = async (e: React.SyntheticEvent) => {
        e.preventDefault();
        if (activeTab === 'arxiv') {
            addArxiv.mutate(inputValue, { onSuccess: onClose });
        } else if (activeTab === 'github') {
            addGithub.mutate(inputValue, { onSuccess: onClose });
        }
    };

    const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) uploadFile.mutate(file, { onSuccess: onClose });
    };

    const isPending = addArxiv.isPending || addGithub.isPending || uploadFile.isPending;

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-slate-950/80 backdrop-blur-sm p-4 animate-in fade-in duration-300">
            <div className="bg-white dark:bg-slate-900 w-full max-w-lg rounded-[2.5rem] shadow-2xl border border-slate-200 dark:border-slate-800 overflow-hidden">
                <div className="px-8 py-6 border-b border-slate-100 dark:border-slate-800 flex justify-between items-center">
                    <h3 className="text-xl font-black uppercase tracking-tight">Add Artifact</h3>
                    <button onClick={onClose} className="p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-xl text-slate-400"><X size={20} /></button>
                </div>

                <div className="p-2 bg-slate-50 dark:bg-slate-950 flex gap-1">
                    {(['arxiv', 'github', 'local'] as Tab[]).map(t => (
                        <button key={t} onClick={() => setActiveTab(t)} className={`flex-1 py-3 rounded-2xl text-[10px] font-black uppercase tracking-widest transition-all ${activeTab === t ? 'bg-white dark:bg-slate-800 shadow-sm text-blue-600' : 'text-slate-400 hover:text-slate-600'}`}>
                            {t}
                        </button>
                    ))}
                </div>

                <div className="p-8">
                    {activeTab !== 'local' ? (
                        <form onSubmit={handleAction} className="space-y-4">
                            <div className="relative group">
                                {activeTab === 'arxiv' ? <BookOpen className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" size={20} /> : <Github className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" size={20} />}
                                <input
                                    autoFocus
                                    value={inputValue}
                                    onChange={e => setInputValue(e.target.value)}
                                    placeholder={activeTab === 'arxiv' ? "ArXiv ID (e.g. 2401.00001)" : "GitHub Repo URL"}
                                    className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-2xl pl-12 pr-4 py-4 text-sm font-bold outline-none focus:border-blue-500"
                                />
                            </div>
                            <button disabled={isPending || !inputValue} className="w-full py-4 bg-blue-600 hover:bg-blue-700 text-white font-black rounded-2xl flex items-center justify-center gap-2 transition-all active:scale-95 disabled:opacity-50">
                                {isPending ? <Loader2 className="animate-spin" size={20} /> : <Send size={20} />} Ingest Resource
                            </button>
                        </form>
                    ) : (
                        <div className="space-y-4">
                            <label className="flex flex-col items-center justify-center w-full h-40 border-2 border-dashed border-slate-200 dark:border-slate-800 rounded-[2rem] cursor-pointer hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-all">
                                <div className="flex flex-col items-center justify-center pt-5 pb-6 text-slate-400">
                                    {uploadFile.isPending ? <Loader2 className="animate-spin mb-3 text-blue-600" size={32}/> : <FileUp className="mb-3" size={32}/>}
                                    <p className="text-xs font-black uppercase tracking-widest">Click to upload doc</p>
                                    <p className="text-[10px] mt-1">PDF, DOCX, MD, PPTX</p>
                                </div>
                                <input type="file" className="hidden" onChange={handleFileUpload} disabled={uploadFile.isPending} />
                            </label>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};