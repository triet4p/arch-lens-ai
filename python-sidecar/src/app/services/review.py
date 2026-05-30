from __future__ import annotations

import re
from collections import defaultdict
from datetime import datetime
from typing import Any, Optional

from src.app.dto.review import (
    ReviewArtifactContext,
    ReviewConflict,
    ReviewFinding,
    ReviewRecommendation,
    TechRadarEntry,
    TechRadarRead,
    WorkspaceReviewInput,
    WorkspaceReviewRead,
)
from src.app.models.artifact import ArtifactType
from src.app.repositories.analysis import AnalysisRepository
from src.app.repositories.workspace import WorkspaceRepository
from src.app.services.analysis import build_analysis_summary_dto


class WorkspaceReviewService:
    def __init__(self, workspace_repo: WorkspaceRepository, analysis_repo: AnalysisRepository):
        self.workspace_repo = workspace_repo
        self.analysis_repo = analysis_repo

    async def get_workspace_review(self, workspace_id: int) -> WorkspaceReviewRead:
        review_input = self._build_review_input(workspace_id)
        return self._build_review(review_input)

    async def export_workspace_report(self, workspace_id: int) -> str:
        review = await self.get_workspace_review(workspace_id)
        lines = [
            f"# Workspace Review: {review.review_input.workspace_name}",
            "",
            review.decision_summary,
            "",
            "## Recommendation",
            f"- **Decision:** {review.recommendation.label.upper()}",
            f"- **Rationale:** {review.recommendation.rationale}",
            "",
            "## Scores",
        ]

        for label, value in review.scores.items():
            lines.append(f"- **{label.replace('_', ' ').title()}:** {value}/100")

        lines.extend(
            [
                "",
                "## Coverage",
                f"- Artifacts: {review.artifact_coverage.get('total_artifacts', 0)}",
                f"- Analyzed: {review.artifact_coverage.get('analyzed_artifacts', 0)}",
                f"- Pending: {review.artifact_coverage.get('pending_artifacts', 0)}",
                "",
                "## Findings",
            ]
        )

        if review.findings:
            for finding in review.findings:
                lines.append(f"- **{finding.title}:** {finding.detail}")
        else:
            lines.append("- No positive findings available yet.")

        lines.extend(["", "## Conflicts"])
        if review.conflicts:
            for conflict in review.conflicts:
                lines.append(f"- **{conflict.title} ({conflict.severity})**: {conflict.detail}")
        else:
            lines.append("- No major conflicts detected.")

        lines.extend(["", "## Recommended Next Steps"])
        for step in review.recommended_next_steps:
            lines.append(f"- {step}")

        lines.extend(["", "## Tech Radar Signals"])
        if review.radar_entries:
            for entry in review.radar_entries:
                lines.append(
                    f"- **{entry.name}** -> {entry.ring.upper()} ({entry.quadrant}) | {entry.evidence}"
                )
        else:
            lines.append("- No technology signals extracted yet.")

        return "\n".join(lines).strip() + "\n"

    async def get_tech_radar(self) -> TechRadarRead:
        workspaces = self.workspace_repo.get_all()
        grouped: dict[str, list[TechRadarEntry]] = defaultdict(list)

        for workspace in workspaces:
            if workspace.id is None:
                continue
            review = await self.get_workspace_review(workspace.id)
            for entry in review.radar_entries:
                grouped[entry.name.lower()].append(entry)

        aggregated_entries: list[TechRadarEntry] = []
        for entries in grouped.values():
            template = entries[0]
            score = round(sum(entry.score for entry in entries) / len(entries))
            ring = self._ring_from_average(score)
            workspace_ids = sorted({workspace_id for entry in entries for workspace_id in entry.workspace_ids})
            evidence = "; ".join(dict.fromkeys(entry.evidence for entry in entries))
            aggregated_entries.append(
                TechRadarEntry(
                    name=template.name,
                    ring=ring,
                    quadrant=template.quadrant,
                    score=score,
                    evidence=evidence,
                    workspace_ids=workspace_ids,
                )
            )

        aggregated_entries.sort(key=lambda entry: (-entry.score, entry.name))
        counts = {ring: sum(1 for entry in aggregated_entries if entry.ring == ring) for ring in ("adopt", "trial", "assess", "hold")}

        return TechRadarRead(
            generated_at=datetime.now(),
            entries=aggregated_entries,
            counts=counts,
            workspaces_covered=len([workspace for workspace in workspaces if workspace.id is not None]),
        )

    def _build_review_input(self, workspace_id: int) -> WorkspaceReviewInput:
        workspace = self.workspace_repo.get(workspace_id)
        if not workspace:
            raise ValueError(f"Workspace {workspace_id} not found")

        artifacts = self.workspace_repo.get_artifacts(workspace_id)
        artifact_ids = [artifact.id for artifact in artifacts if artifact.id is not None]
        analysis_by_artifact = self.analysis_repo.list_by_artifact_ids(artifact_ids)

        contexts: list[ReviewArtifactContext] = []
        for artifact in artifacts:
            if artifact.id is None:
                continue

            analysis = analysis_by_artifact.get(artifact.id)
            summary = build_analysis_summary_dto(analysis) if analysis else None
            metadata = artifact.metadata_dict
            contexts.append(
                ReviewArtifactContext(
                    artifact_id=artifact.id,
                    artifact_type=artifact.type,
                    status=artifact.status,
                    title=metadata.get("title")
                    or metadata.get("repo_id")
                    or metadata.get("full_name")
                    or metadata.get("original_name")
                    or metadata.get("paper_id")
                    or "Unnamed artifact",
                    analysis_kind=summary.analysis_kind if summary else None,
                    summary_markdown=summary.summary_markdown if summary else None,
                    extracted_data=summary.extracted_data if summary else {},
                    scores=summary.scores if summary else {},
                )
            )

        return WorkspaceReviewInput(
            workspace_id=workspace.id,
            workspace_name=workspace.name,
            workspace_description=workspace.description,
            constraints=workspace.constraints_dict,
            artifacts=contexts,
        )

    def _build_review(self, review_input: WorkspaceReviewInput) -> WorkspaceReviewRead:
        findings: list[ReviewFinding] = []
        conflicts: list[ReviewConflict] = []

        total_artifacts = len(review_input.artifacts)
        analyzed = [artifact for artifact in review_input.artifacts if artifact.analysis_kind]
        pending = [artifact for artifact in review_input.artifacts if not artifact.analysis_kind]
        repo_artifacts = [artifact for artifact in analyzed if artifact.artifact_type == ArtifactType.REPO]
        doc_artifacts = [artifact for artifact in analyzed if artifact.artifact_type == ArtifactType.INTERNAL_DOC]
        paper_artifacts = [artifact for artifact in analyzed if artifact.artifact_type == ArtifactType.PAPER]

        evidence_coverage = round((len(analyzed) / total_artifacts) * 100) if total_artifacts else 0
        coverage = {
            "total_artifacts": total_artifacts,
            "analyzed_artifacts": len(analyzed),
            "pending_artifacts": len(pending),
        }

        if total_artifacts == 0:
            findings.append(
                ReviewFinding(
                    category="evidence",
                    title="No evidence loaded",
                    detail="The workspace does not contain any artifacts yet, so review output is only a structural placeholder.",
                )
            )
        else:
            findings.append(
                ReviewFinding(
                    category="evidence",
                    title="Evidence coverage",
                    detail=f"{len(analyzed)} of {total_artifacts} artifacts already have persisted analysis records.",
                    related_artifact_ids=[artifact.artifact_id for artifact in analyzed],
                )
            )

        if pending:
            conflicts.append(
                ReviewConflict(
                    severity="medium" if analyzed else "high",
                    title="Incomplete artifact coverage",
                    detail=f"{len(pending)} artifacts still need analysis before the workspace review can be considered complete.",
                    related_artifact_ids=[artifact.artifact_id for artifact in pending],
                )
            )

        current_stack = str(review_input.constraints.get("current_stack", ""))
        current_stack_terms = self._stack_terms(current_stack)
        repo_stack_labels = self._repo_stack_labels(repo_artifacts)
        stack_overlap = {
            label
            for label in repo_stack_labels
            if self._normalize_stack_label(label) in current_stack_terms
        }

        if stack_overlap:
            findings.append(
                ReviewFinding(
                    category="fit",
                    title="Stack alignment",
                    detail=f"Repository evidence overlaps with the declared workspace stack: {', '.join(sorted(stack_overlap))}.",
                    related_artifact_ids=[artifact.artifact_id for artifact in repo_artifacts],
                )
            )
        elif repo_stack_labels and current_stack_terms:
            conflicts.append(
                ReviewConflict(
                    severity="medium",
                    title="Stack mismatch",
                    detail=(
                        f"Repository evidence suggests {', '.join(sorted(repo_stack_labels))}, which does not clearly match "
                        f"the declared stack constraint {current_stack}."
                    ),
                    related_artifact_ids=[artifact.artifact_id for artifact in repo_artifacts],
                )
            )

        doc_readiness = self._average_score(doc_artifacts, "readiness_score")
        if doc_artifacts and doc_readiness >= 60:
            findings.append(
                ReviewFinding(
                    category="execution",
                    title="Internal documentation is actionable",
                    detail=f"Internal docs show usable structure and execution detail, with an average readiness score of {doc_readiness}/100.",
                    related_artifact_ids=[artifact.artifact_id for artifact in doc_artifacts],
                )
            )

        paper_signal = self._average_score(paper_artifacts, "implementation_signal")
        repro_signal = self._average_score(paper_artifacts, "reproducibility_signal")
        if paper_artifacts and (paper_signal >= 55 or repro_signal >= 55):
            findings.append(
                ReviewFinding(
                    category="evidence",
                    title="Research inputs contain implementation signals",
                    detail=(
                        f"Paper analyses indicate implementation signal {paper_signal}/100 and reproducibility signal "
                        f"{repro_signal}/100."
                    ),
                    related_artifact_ids=[artifact.artifact_id for artifact in paper_artifacts],
                )
            )

        repo_risks = [self._int_score(artifact.scores.get("integration_risk")) for artifact in repo_artifacts]
        for artifact in repo_artifacts:
            risk = self._int_score(artifact.scores.get("integration_risk"))
            if risk >= 70:
                conflicts.append(
                    ReviewConflict(
                        severity="high",
                        title=f"Integration risk for {artifact.title}",
                        detail=f"Repository analysis reports integration risk {risk}/100. This needs a deeper implementation review before adoption.",
                        related_artifact_ids=[artifact.artifact_id],
                    )
                )

        gpu_limit_text = str(review_input.constraints.get("gpu_limit", ""))
        gpu_limit_gb = self._parse_gpu_limit(gpu_limit_text)
        if gpu_limit_gb is not None and gpu_limit_gb <= 24 and {"pytorch", "tensorflow"} & {
            self._normalize_stack_label(label) for label in repo_stack_labels
        }:
            conflicts.append(
                ReviewConflict(
                    severity="high" if gpu_limit_gb <= 16 else "medium",
                    title="GPU ceiling may limit ML adoption",
                    detail=(
                        f"The declared GPU limit {gpu_limit_text} may be tight for stacks such as "
                        f"{', '.join(sorted(label for label in repo_stack_labels if self._normalize_stack_label(label) in {'pytorch', 'tensorflow'}))}."
                    ),
                    related_artifact_ids=[artifact.artifact_id for artifact in repo_artifacts],
                )
            )

        technical_fit_score = self._technical_fit_score(repo_artifacts, doc_artifacts, paper_artifacts, bool(stack_overlap))
        risk_score = self._risk_score(repo_risks, pending_count=len(pending), conflict_count=len(conflicts))
        roi_score = self._roi_score(repo_artifacts, doc_artifacts, paper_artifacts)
        confidence_score = self._confidence_score(
            evidence_coverage=evidence_coverage,
            artifact_types={artifact.artifact_type for artifact in analyzed},
            conflict_count=len(conflicts),
        )
        scores = {
            "technical_fit_score": technical_fit_score,
            "risk_score": risk_score,
            "roi_score": roi_score,
            "confidence_score": confidence_score,
            "evidence_coverage_score": evidence_coverage,
        }

        recommendation = self._build_recommendation(scores, coverage, conflicts)
        decision_summary = self._decision_summary(review_input, recommendation, scores, conflicts)
        recommended_next_steps = self._recommended_next_steps(review_input, coverage, conflicts, repo_artifacts, paper_artifacts)
        radar_entries = self._build_radar_entries(review_input, repo_artifacts, recommendation, scores)

        return WorkspaceReviewRead(
            workspace_id=review_input.workspace_id,
            generated_at=datetime.now(),
            review_input=review_input,
            findings=findings,
            conflicts=conflicts,
            decision_summary=decision_summary,
            recommendation=recommendation,
            recommended_next_steps=recommended_next_steps,
            scores=scores,
            artifact_coverage=coverage,
            radar_entries=radar_entries,
        )

    def _repo_stack_labels(self, repo_artifacts: list[ReviewArtifactContext]) -> set[str]:
        labels: set[str] = set()
        for artifact in repo_artifacts:
            detected_stack = artifact.extracted_data.get("detected_stack", [])
            if isinstance(detected_stack, list):
                labels.update(str(item) for item in detected_stack if item)
        return labels

    def _technical_fit_score(
        self,
        repo_artifacts: list[ReviewArtifactContext],
        doc_artifacts: list[ReviewArtifactContext],
        paper_artifacts: list[ReviewArtifactContext],
        has_stack_overlap: bool,
    ) -> int:
        components: list[int] = []

        for artifact in repo_artifacts:
            health = self._int_score(artifact.scores.get("health_score"))
            integration_risk = self._int_score(artifact.scores.get("integration_risk"))
            components.append(round((health * 0.65) + ((100 - integration_risk) * 0.35)))

        for artifact in doc_artifacts:
            components.append(self._int_score(artifact.scores.get("readiness_score")))

        for artifact in paper_artifacts:
            components.append(self._int_score(artifact.scores.get("implementation_signal")))

        if not components:
            return 25

        score = round(sum(components) / len(components))
        if has_stack_overlap:
            score += 8
        return self._clamp(score)

    def _risk_score(self, repo_risks: list[int], pending_count: int, conflict_count: int) -> int:
        base_risk = round(sum(repo_risks) / len(repo_risks)) if repo_risks else 35
        base_risk += min(20, pending_count * 6)
        base_risk += min(20, conflict_count * 4)
        return self._clamp(base_risk)

    def _roi_score(
        self,
        repo_artifacts: list[ReviewArtifactContext],
        doc_artifacts: list[ReviewArtifactContext],
        paper_artifacts: list[ReviewArtifactContext],
    ) -> int:
        components: list[int] = []

        for artifact in repo_artifacts:
            components.append(self._int_score(artifact.scores.get("health_score")))
        for artifact in doc_artifacts:
            components.append(self._int_score(artifact.scores.get("readiness_score")))
        for artifact in paper_artifacts:
            components.append(
                round(
                    (
                        self._int_score(artifact.scores.get("implementation_signal"))
                        + self._int_score(artifact.scores.get("reproducibility_signal"))
                    )
                    / 2
                )
            )

        if not components:
            return 20
        return self._clamp(round(sum(components) / len(components)))

    def _confidence_score(self, evidence_coverage: int, artifact_types: set[ArtifactType], conflict_count: int) -> int:
        score = round((evidence_coverage * 0.7) + (len(artifact_types) * 12) - (conflict_count * 4))
        return self._clamp(score)

    def _build_recommendation(
        self,
        scores: dict[str, int],
        coverage: dict[str, int],
        conflicts: list[ReviewConflict],
    ) -> ReviewRecommendation:
        if coverage["analyzed_artifacts"] == 0:
            return ReviewRecommendation(
                label="assess",
                rationale="No persisted analysis records exist yet, so the workspace cannot support a stronger recommendation.",
            )

        if scores["risk_score"] >= 75 or any(conflict.severity == "high" for conflict in conflicts):
            return ReviewRecommendation(
                label="hold",
                rationale="Risk is still too high relative to the available evidence, so the workspace should not move forward unchanged.",
            )

        if (
            scores["technical_fit_score"] >= 78
            and scores["roi_score"] >= 70
            and scores["risk_score"] <= 35
            and scores["evidence_coverage_score"] >= 70
        ):
            return ReviewRecommendation(
                label="adopt",
                rationale="The evidence base is broad, the technical fit is strong, and the measured delivery risk is low enough to proceed.",
            )

        if (
            scores["technical_fit_score"] >= 60
            and scores["roi_score"] >= 55
            and scores["risk_score"] <= 55
            and scores["evidence_coverage_score"] >= 50
        ):
            return ReviewRecommendation(
                label="trial",
                rationale="The workspace has enough fit and ROI signal to justify a scoped implementation trial.",
            )

        return ReviewRecommendation(
            label="assess",
            rationale="The evidence supports continued investigation, but not yet a confident go decision.",
        )

    def _decision_summary(
        self,
        review_input: WorkspaceReviewInput,
        recommendation: ReviewRecommendation,
        scores: dict[str, int],
        conflicts: list[ReviewConflict],
    ) -> str:
        if conflicts:
            top_conflict = conflicts[0].title
            return (
                f"For workspace {review_input.workspace_name}, the current recommendation is {recommendation.label.upper()}. "
                f"Technical fit is {scores['technical_fit_score']}/100, ROI is {scores['roi_score']}/100, and risk is "
                f"{scores['risk_score']}/100. The main blocking issue is {top_conflict.lower()}."
            )

        return (
            f"For workspace {review_input.workspace_name}, the current recommendation is {recommendation.label.upper()}. "
            f"Technical fit is {scores['technical_fit_score']}/100, ROI is {scores['roi_score']}/100, and the evidence "
            f"coverage sits at {scores['evidence_coverage_score']}/100."
        )

    def _recommended_next_steps(
        self,
        review_input: WorkspaceReviewInput,
        coverage: dict[str, int],
        conflicts: list[ReviewConflict],
        repo_artifacts: list[ReviewArtifactContext],
        paper_artifacts: list[ReviewArtifactContext],
    ) -> list[str]:
        steps: list[str] = []

        if coverage["pending_artifacts"] > 0:
            steps.append("Analyze the remaining pending artifacts so the workspace review is based on the full evidence set.")

        if any(conflict.severity == "high" for conflict in conflicts):
            steps.append("Run a focused implementation review on the highest-risk repository before committing to delivery.")

        if repo_artifacts and not review_input.constraints.get("current_stack"):
            steps.append("Define the target stack constraint explicitly so repository fit can be judged against a concrete baseline.")

        if paper_artifacts:
            steps.append("Turn the strongest paper findings into a shortlist of implementation hypotheses or benchmarks.")

        if not steps:
            steps.append("Refresh the workspace review after the next artifact update to keep the decision surface current.")

        return steps[:4]

    def _build_radar_entries(
        self,
        review_input: WorkspaceReviewInput,
        repo_artifacts: list[ReviewArtifactContext],
        recommendation: ReviewRecommendation,
        scores: dict[str, int],
    ) -> list[TechRadarEntry]:
        current_stack = str(review_input.constraints.get("current_stack", ""))
        current_stack_terms = self._stack_terms(current_stack)
        entries: dict[str, TechRadarEntry] = {}

        for label in sorted(self._repo_stack_labels(repo_artifacts)):
            normalized = self._normalize_stack_label(label)
            label_risks = [
                self._int_score(artifact.scores.get("integration_risk"))
                for artifact in repo_artifacts
                if normalized in {self._normalize_stack_label(item) for item in artifact.extracted_data.get("detected_stack", [])}
            ]
            avg_risk = round(sum(label_risks) / len(label_risks)) if label_risks else scores["risk_score"]
            signal_score = self._clamp(round((scores["technical_fit_score"] * 0.55) + ((100 - avg_risk) * 0.45)))

            if avg_risk >= 70:
                ring = "hold"
            elif normalized in current_stack_terms and recommendation.label in {"adopt", "trial"}:
                ring = "adopt" if signal_score >= 75 else "trial"
            elif signal_score >= 65:
                ring = "trial"
            else:
                ring = "assess"

            entries[label] = TechRadarEntry(
                name=label,
                ring=ring,
                quadrant=self._quadrant_for_label(label),
                score=signal_score,
                evidence=(
                    f"Seen in repository analysis for workspace {review_input.workspace_name} "
                    f"with average integration risk {avg_risk}/100."
                ),
                workspace_ids=[review_input.workspace_id],
            )

        for raw_label in filter(None, re.split(r"[,/|]+", current_stack)):
            label = raw_label.strip()
            if not label or label in entries:
                continue
            entries[label] = TechRadarEntry(
                name=label,
                ring="assess",
                quadrant=self._quadrant_for_label(label),
                score=max(35, scores["technical_fit_score"] - 10),
                evidence=f"Declared as a workspace constraint in {review_input.workspace_name} but not yet supported by repository evidence.",
                workspace_ids=[review_input.workspace_id],
            )

        return sorted(entries.values(), key=lambda entry: (-entry.score, entry.name))

    def _ring_from_average(self, score: int) -> str:
        if score >= 78:
            return "adopt"
        if score >= 62:
            return "trial"
        if score >= 40:
            return "assess"
        return "hold"

    def _quadrant_for_label(self, label: str) -> str:
        normalized = self._normalize_stack_label(label)
        if normalized in {"react", "typescript", "javascript", "vite"}:
            return "experience"
        if normalized in {"docker", "kubernetes", "terraform", "githubactions"}:
            return "delivery"
        if normalized in {"pytorch", "tensorflow", "huggingface"}:
            return "data-ai"
        if normalized in {"tauri", "rust", "fastapi", "python", "postgres", "sqlite"}:
            return "platform"
        return "architecture"

    def _stack_terms(self, raw_stack: str) -> set[str]:
        return {self._normalize_stack_label(part) for part in re.split(r"[,/|+\s]+", raw_stack) if part.strip()}

    def _normalize_stack_label(self, value: str) -> str:
        return re.sub(r"[^a-z0-9]+", "", value.lower())

    def _parse_gpu_limit(self, raw_value: str) -> Optional[int]:
        match = re.search(r"(\d+)", raw_value)
        if not match:
            return None
        return int(match.group(1))

    def _average_score(self, artifacts: list[ReviewArtifactContext], key: str) -> int:
        values = [self._int_score(artifact.scores.get(key)) for artifact in artifacts if key in artifact.scores]
        if not values:
            return 0
        return round(sum(values) / len(values))

    def _int_score(self, value: Any) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return 0

    def _clamp(self, value: int, minimum: int = 0, maximum: int = 100) -> int:
        return max(minimum, min(maximum, value))
