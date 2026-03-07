import React, { useState } from 'react';
import { useWorkspaces } from '../hooks/useWorkspaces';
import { useAppStore } from '../stores/useAppStore';
import { WorkspaceCard } from '../components/workspace/WorkspaceCard';
import { CreateWorkspaceModal } from '../components/workspace/CreateWorkspaceModal';
import { Plus, Loader2, Search, FolderOpen } from 'lucide-react';

export const WorkspaceList: React.FC = () => {
    const { workspacesQuery, createMutation, deleteMutation } = useWorkspaces();
    const { setSelectedWorkspaceId } = useAppStore();
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [search, setSearch] = useState('');

    const filtered = workspacesQuery.data?.filter(ws => 
        ws.name.toLowerCase().includes(search.toLowerCase())
    ) || [];

    const handleDelete = (id: number) => {
        if (confirm("Delete this workspace and all its artifacts?")) {
            deleteMutation.mutate(id);
        }
    };

    return (
        <div className="space-y-8 animate-in fade-in duration-700">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div>
                    <h2 className="text-3xl font-black tracking-tight">Your Workspaces</h2>
                    <p className="text-slate-500 text-sm font-medium">Select a lens to begin your technical due diligence.</p>
                </div>
                <button 
                    onClick={() => setIsModalOpen(true)}
                    className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-2xl font-black text-sm shadow-lg shadow-blue-500/20 transition-all active:scale-95"
                >
                    <Plus size={20} /> New Workspace
                </button>
            </div>

            <div className="relative max-w-md">
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
                <input 
                    type="text" 
                    placeholder="Search projects..." 
                    value={search}
                    onChange={e => setSearch(e.target.value)}
                    className="w-full bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl pl-12 pr-4 py-3 text-sm font-bold outline-none focus:border-blue-500 transition-all"
                />
            </div>

            {workspacesQuery.isLoading ? (
                <div className="flex flex-col items-center justify-center py-20 text-slate-400">
                    <Loader2 size={40} className="animate-spin mb-4 text-blue-600" />
                    <p className="font-bold uppercase tracking-widest text-xs">Synchronizing Workspaces...</p>
                </div>
            ) : filtered.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {filtered.map(ws => (
                        <WorkspaceCard key={ws.id} workspace={ws} onDelete={handleDelete} onClick={setSelectedWorkspaceId} />
                    ))}
                </div>
            ) : (
                <div className="flex flex-col items-center justify-center py-32 bg-slate-100/50 dark:bg-slate-900/30 rounded-[3rem] border-2 border-dashed border-slate-200 dark:border-slate-800 text-center">
                    <div className="w-20 h-20 bg-white dark:bg-slate-800 rounded-3xl shadow-xl flex items-center justify-center mb-6 text-slate-300">
                        <FolderOpen size={40} />
                    </div>
                    <h4 className="text-xl font-black text-slate-400 uppercase tracking-widest">No Workspaces Found</h4>
                    <p className="text-slate-400 text-xs font-medium mt-2">Start by creating your first R&D project.</p>
                </div>
            )}

            <CreateWorkspaceModal 
                isOpen={isModalOpen} 
                onClose={() => setIsModalOpen(false)}
                onSubmit={(data) => createMutation.mutate(data, { onSuccess: () => setIsModalOpen(false) })}
                isPending={createMutation.isPending}
            />
        </div>
    );
};