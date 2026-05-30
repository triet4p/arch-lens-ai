import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { apiClient } from '../lib/axios';
import type { TechRadarRead, WorkspaceReviewRead } from '../types/api';


const downloadMarkdown = (workspaceId: number, markdown: string, workspaceName?: string) => {
    const safeName = (workspaceName || `workspace-${workspaceId}`)
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, '-')
        .replace(/^-+|-+$/g, '');
    const blob = new Blob([markdown], { type: 'text/markdown;charset=utf-8' });
    const url = window.URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = `${safeName || `workspace-${workspaceId}`}-review.md`;
    anchor.click();
    window.URL.revokeObjectURL(url);
};


export const useWorkspaceReview = (workspaceId: number | null, workspaceName?: string) => {
    const queryClient = useQueryClient();
    const reviewKey = ['workspace', workspaceId, 'review'];

    const reviewQuery = useQuery({
        queryKey: reviewKey,
        queryFn: async () => (await apiClient.get<WorkspaceReviewRead>(`/workspaces/${workspaceId}/review`)).data,
        enabled: !!workspaceId,
    });

    const runReview = useMutation({
        mutationFn: async () => (await apiClient.post<WorkspaceReviewRead>(`/workspaces/${workspaceId}/review`)).data,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: reviewKey });
            queryClient.invalidateQueries({ queryKey: ['tech-radar'] });
        }
    });

    const exportReport = useMutation({
        mutationFn: async () => (await apiClient.get<string>(`/workspaces/${workspaceId}/report.md`, { responseType: 'text' })).data,
        onSuccess: (markdown) => {
            if (!workspaceId) return;
            downloadMarkdown(workspaceId, markdown, workspaceName);
        }
    });

    return { reviewQuery, runReview, exportReport };
};


export const useTechRadar = () => {
    return useQuery({
        queryKey: ['tech-radar'],
        queryFn: async () => (await apiClient.get<TechRadarRead>('/workspaces/radar')).data,
    });
};
