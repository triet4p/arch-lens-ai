import React, { useState } from 'react';
import { useAppStore } from '../stores/useAppStore';
import { useArtifacts } from '../hooks/useArtifacts';
import { ArtifactCard } from '../components/workspace/ArtifactCard';
import { AddArtifactModal } from '../components/workspace/AddArtifactModal';
import { ChevronLeft, Plus, Cpu, HardDrive, Loader2, LayoutGrid, Info } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../lib/axios';
import type { WorkspaceDetail as WorkspaceDetailType } from '../types/api';

export const WorkspaceDetail: React.FC = () => {
    const { selectedWorkspaceId, setSelectedWorkspaceId, t } = useAppStore();
    const [isModalOpen, setIsModalOpen] = useState(false);

    const { data: ws, isLoading } = useQuery({
        queryKey: ['workspace', selectedWorkspaceId],
        queryFn: async () => (await apiClient.get<WorkspaceDetailType>(`/workspaces/${selectedWorkspaceId}`)).data,
        enabled: !!selectedWorkspaceId
    });

    const { deleteArtifact } = useArtifacts(selectedWorkspaceId!);

    if (isLoading || !ws) {
        return (
            <div className="flex flex-col items-center justify-center h-full text-slate-400">
                <Loader2 className="animate-spin mb-4 text-blue-600" size={40} />
                <p className="font-black uppercase tracking-widest text-xs">Synchronizing Project Data...</p>
            </div>
        );
    }

    const handleDeleteArtifact = (id: number, type: any) => {
        if (confirm("Remove this artifact from workspace? This will delete local files and analysis data.")) {
            deleteArtifact.mutate({ id, type });
        }
    };

    return (
        <div className="max-w-6xl mx-auto space-y-8 animate-in fade-in duration-500 pb-20">
            {/* Header Navigation */}
            <div className="flex items-center justify-between">
                <button
                    onClick={() => setSelectedWorkspaceId(null)}
                    className="flex items-center gap-2 text-slate-400 hover:text-blue-600 font-bold transition-all group"
                >
                    <div className="p-2 rounded-xl group-hover:bg-blue-50 dark:group-hover:bg-blue-900/20 transition-all">
                        <ChevronLeft size={20} />
                    </div>
                    Back to Dashboard
                </button>

                <button
                    onClick={() => setIsModalOpen(true)}
                    className="flex items-center gap-2 bg-slate-900 dark:bg-white dark:text-slate-900 text-white px-6 py-3 rounded-2xl font-black text-xs uppercase tracking-widest hover:scale-105 transition-all shadow-xl active:scale-95"
                >
                    <Plus size={18} /> Add Resource
                </button>
            </div>

            {/* Project Strategic Card */}
            <div className="relative overflow-hidden bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-10 rounded-[3rem] shadow-sm">
                <div className="absolute top-0 right-0 p-8 opacity-5">
                    <Info size={120} />
                </div>

                <div className="relative z-10">
                    <h2 className="text-4xl font-black tracking-tighter dark:text-white mb-3">{ws.name}</h2>
                    <p className="text-slate-500 font-medium max-w-2xl leading-relaxed mb-8">{ws.description || "No description provided for this strategic workspace."}</p>

                    <div className="flex flex-wrap gap-3">
                        <div className="flex items-center gap-2 px-5 py-2.5 bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 rounded-2xl text-[10px] font-black uppercase tracking-widest border border-blue-100 dark:border-blue-900/50">
                            <Cpu size={14} /> GPU: {ws.constraints.gpu_limit || "Not set"}
                        </div>
                        <div className="flex items-center gap-2 px-5 py-2.5 bg-indigo-50 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400 rounded-2xl text-[10px] font-black uppercase tracking-widest border border-indigo-100 dark:border-indigo-900/50">
                            <HardDrive size={14} /> Stack: {ws.constraints.current_stack || "Not set"}
                        </div>
                    </div>
                </div>
            </div>

            {/* Artifacts Section */}
            <div className="space-y-6">
                <div className="flex items-center justify-between px-2">
                    <div className="flex items-center gap-2">
                        <LayoutGrid size={18} className="text-slate-400" />
                        <h3 className="text-sm font-black uppercase tracking-[0.2em] text-slate-400">Project Artifacts</h3>
                    </div>
                    <span className="px-3 py-1 bg-slate-100 dark:bg-slate-800 rounded-full text-[10px] font-black text-slate-500 uppercase">
                        {ws.artifacts.length} Items
                    </span>
                </div>

                {ws.artifacts.length > 0 ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {ws.artifacts.map(art => (
                            <ArtifactCard
                                key={art.id}
                                artifact={art}
                                onAnalyze={(id) => console.log("Trigger Analysis for", id)}
                                onDelete={handleDeleteArtifact}
                            />
                        ))}
                    </div>
                ) : (
                    <div className="py-32 text-center border-2 border-dashed border-slate-200 dark:border-slate-800 rounded-[3rem] bg-slate-50/50 dark:bg-slate-900/20">
                        <div className="w-16 h-16 bg-white dark:bg-slate-800 rounded-2xl shadow-sm flex items-center justify-center mx-auto mb-4 text-slate-300">
                            <LayoutGrid size={32} />
                        </div>
                        <h4 className="text-sm font-black text-slate-400 uppercase tracking-widest">The lens is empty</h4>
                        <p className="text-[10px] text-slate-400 mt-1">Add papers, repos or docs to start due diligence.</p>
                    </div>
                )}
            </div>

            <AddArtifactModal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                workspaceId={selectedWorkspaceId!}
            />
        </div>
    );
};