from src.app.models.artifact import Artifact
from src.app.repositories.base import BaseRepository

class ArtifactRepository(BaseRepository[Artifact]):
    def __init__(self, session):
        super().__init__(session, Artifact)