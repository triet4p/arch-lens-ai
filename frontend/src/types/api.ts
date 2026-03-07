// XÓA cái enum LMTask cũ đi và thay bằng dòng này:
export type LMTask = "default" | "summary" | "chat" | "trend" | "code";

export type ArtifactType = "paper" | "repo" | "internal_doc";
export type ArtifactStatus = "pending" | "processing" | "completed" | "failed";

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

export interface ArtifactRead {
    id: number;
    workspace_id: number;
    type: ArtifactType;
    status: ArtifactStatus;
    source_url: string;
    local_path?: string;
    metadata: Record<string, any>;
    created_at: string;
}

export interface WorkspaceRead {
    id: number;
    name: string;
    description?: string;
    constraints: Record<string, any>;
    artifacts_count: number;
    created_at: string;
    updated_at: string;
}

export interface WorkspaceCreate {
    name: string;
    description?: string;
    constraints: Record<string, any>;
}

export interface WorkspaceDetail extends WorkspaceRead {
    artifacts: ArtifactRead[];
}