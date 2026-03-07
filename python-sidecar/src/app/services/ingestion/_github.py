import httpx
from urllib.parse import urlparse
from typing import Dict, Any
from src.app.core.logger import get_logger
from src.app.models.artifact import ArtifactType
from src.app.dto.internal import IngestedArtifact

_logger = get_logger("[Ingestion - GitHub]")

class GithubIngestor:
    def __init__(self):
        self.http_timeout = 15.0

    def _parse_url(self, url: str) -> str:
        """Trích xuất 'owner/repo' từ URL GitHub"""
        try:
            parsed = urlparse(url)
            path_parts = [p for p in parsed.path.split('/') if p]
            if len(path_parts) >= 2:
                return f"{path_parts[0]}/{path_parts[1]}"
        except Exception:
            pass
        raise ValueError(f"Invalid GitHub URL: {url}")

    async def fetch_repo_data(self, url: str) -> IngestedArtifact:
        """Thu thập metadata và cấu trúc thư mục từ GitHub API (Smart Sampling)"""
        repo_id = self._parse_url(url)
        _logger.info(f"Fetching repo data for: {repo_id}")

        async with httpx.AsyncClient(timeout=self.http_timeout) as client:
            # 1. Fetch Metadata cơ bản
            meta_resp = await client.get(f"https://api.github.com/repos/{repo_id}")
            if meta_resp.status_code != 200:
                raise ValueError(
                    f"GitHub API Error {meta_resp.status_code}. "
                    "Repo may be private or non-existent."
                )

            meta = meta_resp.json()
            default_branch = meta.get('default_branch', 'main')

            # 2. Fetch Tree Structure (Recursive) - Smart Sampling: giới hạn 200 paths
            tree_str = "Tree structure unavailable."
            tree_resp = await client.get(
                f"https://api.github.com/repos/{repo_id}/git/trees/{default_branch}?recursive=1"
            )
            if tree_resp.status_code == 200:
                tree_data = tree_resp.json().get('tree', [])
                paths = [item['path'] for item in tree_data if item['type'] in ('blob', 'tree')]
                tree_str = "\n".join(paths[:200])

            # 3. Fetch README (Raw)
            readme_url = (
                f"https://raw.githubusercontent.com/{repo_id}/{default_branch}/README.md"
            )
            readme_resp = await client.get(readme_url, follow_redirects=True)
            readme_content = readme_resp.text if readme_resp.status_code == 200 else ""

        _logger.info(f"Successfully fetched repo data for: {repo_id}")

        return IngestedArtifact(
            type=ArtifactType.REPO,
            source_url=f"https://github.com/{repo_id}",
            raw_metadata={
                "repo_id": repo_id,
                "name": meta.get('name', ''),
                "full_name": meta.get('full_name', ''),
                "stars": meta.get('stargazers_count', 0),
                "forks": meta.get('forks_count', 0),
                "language": meta.get('language', ''),
                "description": meta.get('description', ''),
                "default_branch": default_branch,
                "tree_structure": tree_str,
                "readme_preview": readme_content,
            }
        )
