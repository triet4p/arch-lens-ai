import json
import os
import re
from datetime import datetime
from typing import Any, Optional

import pymupdf4llm
from markitdown import MarkItDown

from src.app.dto.analysis import AnalysisRead, AnalysisSummaryRead
from src.app.core.logger import get_logger
from src.app.models.analysis import AnalysisResult
from src.app.models.artifact import Artifact, ArtifactStatus, ArtifactType
from src.app.repositories.analysis import AnalysisRepository
from src.app.repositories.artifact import ArtifactRepository

_logger = get_logger("[Service - Analysis]")


def build_analysis_summary_dto(result: AnalysisResult) -> AnalysisSummaryRead:
    return AnalysisSummaryRead.model_validate(
        {
            "artifact_id": result.artifact_id,
            "analysis_kind": result.analysis_kind,
            "summary_markdown": result.summary_markdown,
            "extracted_data": result.extracted_data,
            "scores": result.scores_dict,
            "analyzed_at": result.analyzed_at,
        }
    )


def build_analysis_read_dto(result: AnalysisResult) -> AnalysisRead:
    return AnalysisRead.model_validate(
        {
            "artifact_id": result.artifact_id,
            "analysis_kind": result.analysis_kind,
            "summary_markdown": result.summary_markdown,
            "extracted_data": result.extracted_data,
            "scores": result.scores_dict,
            "toc": result.toc_data,
            "content_map": result.content_data,
            "analyzed_at": result.analyzed_at,
        }
    )


class AnalysisService:
    def __init__(self, artifact_repo: ArtifactRepository, analysis_repo: AnalysisRepository):
        self.artifact_repo = artifact_repo
        self.analysis_repo = analysis_repo
        self._markdown_converter: Optional[MarkItDown] = None

    async def analyze_artifact(self, artifact_id: int) -> AnalysisRead:
        artifact = self.artifact_repo.get(artifact_id)
        if not artifact:
            raise ValueError(f"Artifact {artifact_id} not found")

        artifact.status = ArtifactStatus.PROCESSING
        self.artifact_repo.update(artifact)

        try:
            result = self._build_analysis_result(artifact)
            stored = self.analysis_repo.upsert_for_artifact(result)
            artifact.status = ArtifactStatus.COMPLETED
            self.artifact_repo.update(artifact)
            return build_analysis_read_dto(stored)
        except Exception as exc:
            artifact.status = ArtifactStatus.FAILED
            self.artifact_repo.update(artifact)
            _logger.error(f"Analysis failed for artifact {artifact_id}: {exc}", exc_info=True)
            raise

    async def get_analysis(self, artifact_id: int) -> Optional[AnalysisRead]:
        result = self.analysis_repo.get_by_artifact(artifact_id)
        if not result:
            return None
        return build_analysis_read_dto(result)

    def _build_analysis_result(self, artifact: Artifact) -> AnalysisResult:
        if artifact.type == ArtifactType.REPO:
            payload = self._analyze_repository(artifact)
        elif self._is_arxiv_artifact(artifact):
            payload = self._analyze_arxiv_paper(artifact)
        else:
            payload = self._analyze_local_document(artifact)

        return AnalysisResult(
            artifact_id=artifact.id,
            analysis_kind=payload["analysis_kind"],
            toc_json=json.dumps(payload["toc"]),
            content_map_json=json.dumps(payload["content_map"]),
            extracted_data_json=json.dumps(payload["extracted_data"]),
            summary_markdown=payload["summary_markdown"],
            due_diligence_score_json=json.dumps(payload["scores"]),
            analyzed_at=datetime.now(),
        )

    def _analyze_local_document(self, artifact: Artifact) -> dict[str, Any]:
        markdown = self._load_document_markdown(artifact)
        toc = self._extract_toc(markdown)
        content_map = self._build_content_map(markdown, toc)
        words = self._word_count(markdown)
        headings = len(toc)
        title = (
            artifact.metadata_dict.get("title")
            or artifact.metadata_dict.get("original_name")
            or self._first_heading(markdown)
            or "Local document"
        )
        excerpt = self._excerpt(markdown, 320)

        extracted_data = {
            "title": title,
            "format": artifact.metadata_dict.get("extension", os.path.splitext(artifact.local_path or "")[1].lower()),
            "word_count": words,
            "headings_count": headings,
            "section_titles": [entry["title"] for entry in toc[:8]],
        }
        scores = {
            "structure_score": min(100, 30 + headings * 12),
            "content_density": min(100, 10 + words // 20),
            "readiness_score": min(100, 20 + headings * 8 + words // 40),
        }

        summary_markdown = (
            f"{title}\n\n"
            f"Converted into normalized markdown with {words} words and {headings} detected sections.\n\n"
            f"{excerpt}"
        )

        return {
            "analysis_kind": "document",
            "summary_markdown": summary_markdown,
            "toc": toc,
            "content_map": content_map,
            "extracted_data": extracted_data,
            "scores": scores,
        }

    def _analyze_repository(self, artifact: Artifact) -> dict[str, Any]:
        metadata = artifact.metadata_dict
        tree_paths = self._split_tree(metadata.get("tree_structure", ""))
        readme = metadata.get("readme_preview", "")
        dependency_files = self._detect_dependency_files(tree_paths)
        stack = self._detect_stack(tree_paths, readme, metadata.get("language"))
        path_count = len(tree_paths)

        health_score = min(100, 20 + min(metadata.get("stars", 0), 500) // 8 + (10 if readme else 0) + (10 if path_count else 0))
        complexity_score = min(100, 15 + path_count // 4 + len(dependency_files) * 6)
        integration_risk = max(
            5,
            min(
                100,
                55
                + (15 if not readme else 0)
                + (10 if not metadata.get("language") else 0)
                + max(0, complexity_score - 50) // 2
                - min(health_score, 80) // 6,
            ),
        )

        extracted_data = {
            "repo_id": metadata.get("repo_id") or metadata.get("full_name") or metadata.get("name"),
            "primary_language": metadata.get("language"),
            "detected_stack": stack,
            "dependency_files": dependency_files,
            "tree_entry_count": path_count,
            "readme_present": bool(readme),
            "default_branch": metadata.get("default_branch"),
        }
        scores = {
            "health_score": health_score,
            "complexity_score": complexity_score,
            "integration_risk": integration_risk,
        }

        toc = [
            {"level": 1, "title": "Repository Overview", "anchor": "repository-overview"},
            {"level": 1, "title": "Dependency Signals", "anchor": "dependency-signals"},
            {"level": 1, "title": "README Excerpt", "anchor": "readme-excerpt"},
        ]
        content_map = {
            "Repository Overview": self._repo_overview_text(metadata, tree_paths, stack),
            "Dependency Signals": "\n".join(dependency_files) or "No common dependency manifest detected.",
            "README Excerpt": self._excerpt(readme, 1200) or "README preview unavailable.",
        }
        summary_markdown = (
            f"{metadata.get('full_name') or metadata.get('name') or 'Repository'}\n\n"
            f"Primary language: {metadata.get('language') or 'unknown'}.\n"
            f"Detected stack: {', '.join(stack) if stack else 'none detected'}.\n"
            f"Health score: {health_score}/100. "
            f"Complexity score: {complexity_score}/100. "
            f"Integration risk: {integration_risk}/100."
        )

        return {
            "analysis_kind": "repository",
            "summary_markdown": summary_markdown,
            "toc": toc,
            "content_map": content_map,
            "extracted_data": extracted_data,
            "scores": scores,
        }

    def _analyze_arxiv_paper(self, artifact: Artifact) -> dict[str, Any]:
        metadata = artifact.metadata_dict
        markdown = self._load_document_markdown(artifact, allow_missing=True)
        toc = self._extract_toc(markdown)
        content_map = self._build_content_map(markdown, toc)
        abstract = metadata.get("abstract", "")
        words = self._word_count(markdown or abstract)
        reproducibility_signal = self._keyword_signal(
            f"{abstract}\n{markdown}",
            ["dataset", "training", "experiment", "evaluation", "implementation", "appendix", "ablation"],
        )
        implementation_signal = self._keyword_signal(
            f"{abstract}\n{markdown}",
            ["code", "repository", "baseline", "benchmark", "inference", "latency", "gpu"],
        )

        extracted_data = {
            "paper_id": metadata.get("paper_id"),
            "title": metadata.get("title"),
            "authors": metadata.get("authors", []),
            "published": metadata.get("published"),
            "headings_count": len(toc),
            "word_count": words,
            "has_local_pdf": bool(artifact.local_path and os.path.exists(artifact.local_path)),
        }
        scores = {
            "document_structure": min(100, 25 + len(toc) * 10),
            "reproducibility_signal": reproducibility_signal,
            "implementation_signal": implementation_signal,
        }
        summary_markdown = (
            f"{metadata.get('title') or 'ArXiv paper'}\n\n"
            f"Authors: {', '.join(metadata.get('authors', [])[:4]) or 'unknown'}.\n"
            f"Published: {metadata.get('published') or 'unknown'}.\n\n"
            f"{self._excerpt(abstract or markdown, 400)}"
        )

        return {
            "analysis_kind": "paper",
            "summary_markdown": summary_markdown,
            "toc": toc,
            "content_map": content_map,
            "extracted_data": extracted_data,
            "scores": scores,
        }

    def _load_document_markdown(self, artifact: Artifact, allow_missing: bool = False) -> str:
        if not artifact.local_path or not os.path.exists(artifact.local_path):
            if allow_missing:
                return ""
            raise ValueError(f"Artifact {artifact.id} does not have a readable local file")

        extension = os.path.splitext(artifact.local_path)[1].lower()
        if extension == ".pdf":
            return pymupdf4llm.to_markdown(artifact.local_path) or ""
        if extension in {".md", ".txt"}:
            with open(artifact.local_path, "r", encoding="utf-8", errors="replace") as handle:
                return handle.read()

        result = self._get_markdown_converter().convert_local(artifact.local_path)
        return result.markdown or ""

    def _get_markdown_converter(self) -> MarkItDown:
        if self._markdown_converter is None:
            self._markdown_converter = MarkItDown()
        return self._markdown_converter

    def _extract_toc(self, markdown: str) -> list[dict[str, Any]]:
        toc: list[dict[str, Any]] = []
        for line in markdown.splitlines():
            match = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
            if not match:
                continue
            title = match.group(2).strip()
            toc.append(
                {
                    "level": len(match.group(1)),
                    "title": title,
                    "anchor": self._slugify(title),
                }
            )
        return toc

    def _build_content_map(self, markdown: str, toc: list[dict[str, Any]]) -> dict[str, str]:
        if not markdown.strip():
            return {}

        if not toc:
            return {"Document": self._excerpt(markdown, 2400)}

        content_map: dict[str, list[str]] = {}
        current_title: Optional[str] = None
        for line in markdown.splitlines():
            match = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
            if match:
                current_title = match.group(2).strip()
                content_map.setdefault(current_title, [])
                continue

            if current_title is not None:
                content_map[current_title].append(line)

        return {
            title: "\n".join(lines).strip()[:2400]
            for title, lines in content_map.items()
        }

    def _detect_dependency_files(self, tree_paths: list[str]) -> list[str]:
        filenames = {
            "package.json",
            "package-lock.json",
            "pnpm-lock.yaml",
            "yarn.lock",
            "requirements.txt",
            "pyproject.toml",
            "Cargo.toml",
            "go.mod",
            "pom.xml",
            "build.gradle",
            "build.gradle.kts",
            "Gemfile",
            "composer.json",
        }
        return [path for path in tree_paths if os.path.basename(path) in filenames][:20]

    def _detect_stack(self, tree_paths: list[str], readme: str, primary_language: Optional[str]) -> list[str]:
        stack: list[str] = []
        haystack = "\n".join(tree_paths) + "\n" + readme.lower()
        checks = [
            ("Python", [".py", "pyproject.toml", "requirements.txt"]),
            ("FastAPI", ["fastapi"]),
            ("React", ["react", "package.json", ".tsx"]),
            ("TypeScript", [".ts", ".tsx", "tsconfig.json"]),
            ("Tauri", ["tauri.conf.json", "src-tauri"]),
            ("Rust", [".rs", "cargo.toml"]),
            ("Docker", ["dockerfile", "docker-compose"]),
            ("PyTorch", ["torch", "pytorch"]),
            ("TensorFlow", ["tensorflow"]),
        ]

        if primary_language and primary_language not in stack:
            stack.append(primary_language)

        lowered = haystack.lower()
        for label, signals in checks:
            if any(signal.lower() in lowered for signal in signals) and label not in stack:
                stack.append(label)

        return stack[:8]

    def _repo_overview_text(self, metadata: dict[str, Any], tree_paths: list[str], stack: list[str]) -> str:
        sample_paths = "\n".join(tree_paths[:30]) or "No tree structure available."
        return (
            f"Repository: {metadata.get('full_name') or metadata.get('name') or 'unknown'}\n"
            f"Description: {metadata.get('description') or 'No description'}\n"
            f"Primary language: {metadata.get('language') or 'unknown'}\n"
            f"Detected stack: {', '.join(stack) if stack else 'none detected'}\n"
            f"Stars: {metadata.get('stars', 0)} | Forks: {metadata.get('forks', 0)}\n\n"
            f"Tree sample:\n{sample_paths}"
        )

    def _split_tree(self, tree_structure: str) -> list[str]:
        return [line.strip() for line in tree_structure.splitlines() if line.strip()]

    def _is_arxiv_artifact(self, artifact: Artifact) -> bool:
        metadata = artifact.metadata_dict
        return bool(metadata.get("paper_id")) and "local://" not in artifact.source_url

    def _keyword_signal(self, text: str, keywords: list[str]) -> int:
        lowered = text.lower()
        hits = sum(1 for keyword in keywords if keyword in lowered)
        return min(100, 15 + hits * 12)

    def _word_count(self, text: str) -> int:
        return len(re.findall(r"\w+", text))

    def _first_heading(self, markdown: str) -> Optional[str]:
        for line in markdown.splitlines():
            match = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
            if match:
                return match.group(2).strip()
        return None

    def _excerpt(self, text: str, limit: int) -> str:
        compact = re.sub(r"\s+", " ", text).strip()
        if len(compact) <= limit:
            return compact
        return compact[: limit - 3].rstrip() + "..."

    def _slugify(self, value: str) -> str:
        normalized = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower())
        return normalized.strip("-") or "section"
