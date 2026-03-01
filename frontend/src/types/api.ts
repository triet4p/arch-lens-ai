// XÓA cái enum LMTask cũ đi và thay bằng dòng này:
export type LMTask = "default" | "summary" | "chat" | "trend" | "code";

export interface LMSettingResponse {
    active_provider: string;
    provider_configs: Record<string, Record<string, any>>;
    keys_status: Record<string, boolean>;
    task_routing: Record<LMTask, string>;
}

export interface LMSettingUpdate {
    active_provider?: string;
    config_update?: Record<string, Record<string, any>>;
    api_key_update?: Record<string, string>;
    keys_to_delete?: string[];
    task_routing_update?: Record<string, string>;
}