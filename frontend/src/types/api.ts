export type LMTask = "default" | "summary" | "chat" | "trend" | "code";

export type ArtifactType = "paper" | "repo" | "internal_doc";
export type ArtifactStatus = "pending" | "processing" | "completed" | "failed";

export interface AnalysisSummaryRead {
    artifact_id: number;
    analysis_kind: string;
    summary_markdown?: string;
    extracted_data: Record<string, any>;
    scores: Record<string, any>;
    analyzed_at: string;
}

export interface AnalysisRead extends AnalysisSummaryRead {
    toc: Array<Record<string, any>>;
    content_map: Record<string, string>;
}

export interface ReviewArtifactContext {
    artifact_id: number;
    artifact_type: ArtifactType;
    status: ArtifactStatus;
    title: string;
    analysis_kind?: string | null;
    summary_markdown?: string | null;
    extracted_data: Record<string, any>;
    scores: Record<string, any>;
}

export interface WorkspaceReviewInput {
    workspace_id: number;
    workspace_name: string;
    workspace_description?: string | null;
    constraints: Record<string, any>;
    artifacts: ReviewArtifactContext[];
}

export interface ReviewFinding {
    category: "fit" | "evidence" | "execution" | "risk";
    title: string;
    detail: string;
    related_artifact_ids: number[];
}

export interface ReviewConflict {
    severity: "low" | "medium" | "high";
    title: string;
    detail: string;
    related_artifact_ids: number[];
}

export interface ReviewRecommendation {
    label: "adopt" | "trial" | "assess" | "hold";
    rationale: string;
}

export interface TechRadarEntry {
    name: string;
    ring: "adopt" | "trial" | "assess" | "hold";
    quadrant: "platform" | "delivery" | "data-ai" | "experience" | "architecture";
    score: number;
    evidence: string;
    workspace_ids: number[];
}

export interface TechRadarRead {
    generated_at: string;
    entries: TechRadarEntry[];
    counts: Record<string, number>;
    workspaces_covered: number;
}

export interface WorkspaceReviewRead {
    workspace_id: number;
    generated_at: string;
    review_input: WorkspaceReviewInput;
    findings: ReviewFinding[];
    conflicts: ReviewConflict[];
    decision_summary: string;
    recommendation: ReviewRecommendation;
    recommended_next_steps: string[];
    scores: Record<string, number>;
    artifact_coverage: Record<string, number>;
    radar_entries: TechRadarEntry[];
}

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
    type: ArtifactType;
    status: ArtifactStatus;
    source_url: string;
    local_path?: string;
    metadata: Record<string, any>;
    created_at: string;
    analysis?: AnalysisSummaryRead | null;
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
