from ._arxiv import ArxivIngestor
from ._local import LocalIngestor
from ._github import GithubIngestor

__all__ = ["ArxivIngestor", "LocalIngestor", "GithubIngestor"]