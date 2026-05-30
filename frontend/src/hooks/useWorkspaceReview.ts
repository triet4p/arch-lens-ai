import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { invoke } from '@tauri-apps/api/core';

import { apiClient } from '../lib/axios';
import { useAppStore } from '../stores/useAppStore';
import type { TechRadarRead, WorkspaceReviewRead } from '../types/api';


const buildReportFileName = (workspaceId: number, workspaceName?: string) => {
    const safeName = (workspaceName || `workspace-${workspaceId}`)
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, '-')
        .replace(/^-+|-+$/g, '');
    return `${safeName || `workspace-${workspaceId}`}-review.md`;
};


export const useWorkspaceReview = (workspaceId: number | null, workspaceName?: string) => {
    const queryClient = useQueryClient();
    const pushNotification = useAppStore((state) => state.pushNotification);
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
            pushNotification({
                tone: 'success',
                title: 'Review refreshed',
                message: 'Workspace review has been recomputed from the latest evidence.',
            });
        },
        onError: (error: any) => {
            pushNotification({
                tone: 'error',
                title: 'Review failed',
                message: error?.response?.data?.detail || error?.message || 'Unable to refresh workspace review.',
            });
        }
    });

    const exportReport = useMutation({
        mutationFn: async () => (await apiClient.get<string>(`/workspaces/${workspaceId}/report.md`, { responseType: 'text' })).data,
        onSuccess: async (markdown) => {
            if (!workspaceId) return;
            const path = await invoke<string>('save_markdown_report', {
                defaultFileName: buildReportFileName(workspaceId, workspaceName),
                content: markdown,
            });
            pushNotification({
                tone: 'success',
                title: 'Report exported',
                message: `Saved markdown review to ${path}.`,
            });
        },
        onError: (error: any) => {
            const message = error?.message || error?.response?.data?.detail || 'Unable to export markdown report.';
            if (String(message).includes('Save cancelled')) {
                pushNotification({
                    tone: 'info',
                    title: 'Export cancelled',
                    message: 'Report export was cancelled before a file was selected.',
                });
                return;
            }
            pushNotification({
                tone: 'error',
                title: 'Export failed',
                message,
            });
        },
    });

    return { reviewQuery, runReview, exportReport };
};


export const useTechRadar = () => {
    return useQuery({
        queryKey: ['tech-radar'],
        queryFn: async () => (await apiClient.get<TechRadarRead>('/workspaces/radar')).data,
    });
};
