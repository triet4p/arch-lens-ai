import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { apiClient } from '../lib/axios';
import { useAppStore } from '../stores/useAppStore';
import type { LMSettingResponse, LMSettingUpdate } from '../types/api';


export const useAISettings = () => {
    const queryClient = useQueryClient();
    const pushNotification = useAppStore((state) => state.pushNotification);

    const settingsQuery = useQuery({
        queryKey: ['ai-settings'],
        queryFn: async () => (await apiClient.get<LMSettingResponse>('/settings/ai')).data,
    });

    const updateSettings = useMutation({
        mutationFn: async (payload: LMSettingUpdate) => (await apiClient.put<LMSettingResponse>('/settings/ai', payload)).data,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['ai-settings'] });
            pushNotification({
                tone: 'success',
                title: 'Settings saved',
                message: 'AI provider configuration was updated successfully.',
            });
        },
        onError: (error: any) => {
            pushNotification({
                tone: 'error',
                title: 'Settings failed',
                message: error?.response?.data?.detail || error?.message || 'Unable to update AI settings.',
            });
        },
    });

    return { settingsQuery, updateSettings };
};
