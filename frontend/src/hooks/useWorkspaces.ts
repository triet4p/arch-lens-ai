import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../lib/axios';
import type { WorkspaceRead, WorkspaceCreate } from '../types/api';

export const useWorkspaces = () => {
    const queryClient = useQueryClient();

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
        }
    });

    const deleteMutation = useMutation({
        mutationFn: async (id: number) => {
            await apiClient.delete(`/workspaces/${id}`);
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['workspaces'] });
        }
    });

    return { workspacesQuery, createMutation, deleteMutation };
};