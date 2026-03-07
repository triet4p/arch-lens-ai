import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../lib/axios';
import type { ArtifactRead, ArtifactType } from '../types/api';

export const useArtifacts = (workspaceId: number | null) => {
    const queryClient = useQueryClient();
    const queryKey = ['workspace', workspaceId];

    // --- ADD MUTATIONS ---
    const addArxiv = useMutation({
        mutationFn: async (paperIdOrUrl: string) => {
            const { data } = await apiClient.post<ArtifactRead>(`/artifacts/arxiv/${workspaceId}`, null, {
                params: { paper_id_or_url: paperIdOrUrl }
            });
            return data;
        },
        onSuccess: () => queryClient.invalidateQueries({ queryKey })
    });

    const addGithub = useMutation({
        mutationFn: async (repoUrl: string) => {
            const { data } = await apiClient.post<ArtifactRead>(`/artifacts/github/${workspaceId}`, null, {
                params: { repo_url: repoUrl }
            });
            return data;
        },
        onSuccess: () => queryClient.invalidateQueries({ queryKey })
    });

    const uploadFile = useMutation({
        mutationFn: async (file: File) => {
            const formData = new FormData();
            formData.append('file', file);
            const { data } = await apiClient.post<ArtifactRead>(`/artifacts/upload/${workspaceId}`, formData);
            return data;
        },
        onSuccess: () => queryClient.invalidateQueries({ queryKey })
    });

    // --- DELETE MUTATIONS ---
    const deleteArtifact = useMutation({
        mutationFn: async ({ id, type }: { id: number, type: ArtifactType }) => {
            // Mapping endpoint theo type của backend
            const endpointMap: Record<ArtifactType, string> = {
                paper: 'arxiv',
                repo: 'github',
                internal_doc: 'upload'
            };
            await apiClient.delete(`/artifacts/${endpointMap[type]}/${workspaceId}/${id}`);
        },
        onSuccess: () => queryClient.invalidateQueries({ queryKey })
    });

    return { addArxiv, addGithub, uploadFile, deleteArtifact };
};