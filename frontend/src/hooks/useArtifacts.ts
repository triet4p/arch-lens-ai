import { useMutation, useQueryClient } from '@tanstack/react-query';

import { apiClient } from '../lib/axios';
import { useAppStore } from '../stores/useAppStore';
import type { AnalysisRead, ArtifactRead, ArtifactType } from '../types/api';


export const useArtifacts = (workspaceId: number | null) => {
    const queryClient = useQueryClient();
    const pushNotification = useAppStore((state) => state.pushNotification);
    const queryKey = ['workspace', workspaceId];
    const reviewKey = ['workspace', workspaceId, 'review'];

    const invalidateDerivedViews = () => {
        queryClient.invalidateQueries({ queryKey });
        queryClient.invalidateQueries({ queryKey: reviewKey });
        queryClient.invalidateQueries({ queryKey: ['tech-radar'] });
    };

    const addArxiv = useMutation({
        mutationFn: async (paperIdOrUrl: string) => {
            const { data } = await apiClient.post<ArtifactRead>(`/artifacts/arxiv/${workspaceId}`, null, {
                params: { paper_id_or_url: paperIdOrUrl }
            });
            return data;
        },
        onSuccess: invalidateDerivedViews,
        onError: (error: any) => {
            pushNotification({
                tone: 'error',
                title: 'ArXiv import failed',
                message: error?.response?.data?.detail || error?.message || 'Unable to add the ArXiv artifact.',
            });
        },
    });

    const addGithub = useMutation({
        mutationFn: async (repoUrl: string) => {
            const { data } = await apiClient.post<ArtifactRead>(`/artifacts/github/${workspaceId}`, null, {
                params: { repo_url: repoUrl }
            });
            return data;
        },
        onSuccess: invalidateDerivedViews,
        onError: (error: any) => {
            pushNotification({
                tone: 'error',
                title: 'GitHub import failed',
                message: error?.response?.data?.detail || error?.message || 'Unable to add the GitHub artifact.',
            });
        },
    });

    const uploadFile = useMutation({
        mutationFn: async (file: File) => {
            const formData = new FormData();
            formData.append('file', file);
            const { data } = await apiClient.post<ArtifactRead>(`/artifacts/upload/${workspaceId}`, formData);
            return data;
        },
        onSuccess: invalidateDerivedViews,
        onError: (error: any) => {
            pushNotification({
                tone: 'error',
                title: 'Upload failed',
                message: error?.response?.data?.detail || error?.message || 'Unable to upload the local artifact.',
            });
        },
    });

    const analyzeArtifact = useMutation({
        mutationFn: async (artifactId: number) => {
            const { data } = await apiClient.post<AnalysisRead>(`/artifacts/${artifactId}/analyze`);
            return data;
        },
        onSuccess: () => {
            invalidateDerivedViews();
            pushNotification({
                tone: 'success',
                title: 'Analysis completed',
                message: 'Artifact analysis finished and the workspace view was refreshed.',
            });
        },
        onError: (error: any) => {
            pushNotification({
                tone: 'error',
                title: 'Analysis failed',
                message: error?.response?.data?.detail || error?.message || 'Unable to analyze the selected artifact.',
            });
        },
    });

    const deleteArtifact = useMutation({
        mutationFn: async ({ id, type }: { id: number, type: ArtifactType }) => {
            const endpointMap: Record<ArtifactType, string> = {
                paper: 'arxiv',
                repo: 'github',
                internal_doc: 'upload'
            };
            await apiClient.delete(`/artifacts/${endpointMap[type]}/${workspaceId}/${id}`);
        },
        onSuccess: () => {
            invalidateDerivedViews();
            pushNotification({
                tone: 'success',
                title: 'Artifact removed',
                message: 'Artifact, local files, and related analysis data were removed from the workspace.',
            });
        },
        onError: (error: any) => {
            pushNotification({
                tone: 'error',
                title: 'Delete failed',
                message: error?.response?.data?.detail || error?.message || 'Unable to remove the selected artifact.',
            });
        },
    });

    return { addArxiv, addGithub, uploadFile, analyzeArtifact, deleteArtifact };
};
