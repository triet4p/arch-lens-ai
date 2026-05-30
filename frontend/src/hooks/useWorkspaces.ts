import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../lib/axios';
import { useAppStore } from '../stores/useAppStore';
import type { WorkspaceRead, WorkspaceCreate } from '../types/api';

export const useWorkspaces = () => {
    const queryClient = useQueryClient();
    const pushNotification = useAppStore((state) => state.pushNotification);

    const workspacesQuery = useQuery({
        queryKey: ['workspaces'],
        queryFn: async () => {
            const { data } = await apiClient.get<WorkspaceRead[]>('/workspaces/');
            return data;
        }
    });

    const createMutation = useMutation({
        mutationFn: async (newWs: WorkspaceCreate) => {
            const { data } = await apiClient.post<WorkspaceRead>('/workspaces/', newWs);
            return data;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['workspaces'] });
            queryClient.invalidateQueries({ queryKey: ['tech-radar'] });
            pushNotification({
                tone: 'success',
                title: 'Workspace created',
                message: 'The workspace is ready for artifact ingestion and review.',
            });
        },
        onError: (error: any) => {
            pushNotification({
                tone: 'error',
                title: 'Workspace create failed',
                message: error?.response?.data?.detail || error?.message || 'Unable to create the workspace.',
            });
        },
    });

    const deleteMutation = useMutation({
        mutationFn: async (id: number) => {
            await apiClient.delete(`/workspaces/${id}`);
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['workspaces'] });
            queryClient.invalidateQueries({ queryKey: ['tech-radar'] });
            pushNotification({
                tone: 'success',
                title: 'Workspace deleted',
                message: 'The workspace and its private evidence set were removed successfully.',
            });
        },
        onError: (error: any) => {
            pushNotification({
                tone: 'error',
                title: 'Workspace delete failed',
                message: error?.response?.data?.detail || error?.message || 'Unable to delete the workspace.',
            });
        },
    });

    return { workspacesQuery, createMutation, deleteMutation };
};
