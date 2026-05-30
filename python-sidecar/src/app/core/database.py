from typing import Any, Generator

from sqlalchemy import event, inspect, text
from sqlmodel import SQLModel, Session, create_engine

from src.app.core.config import settings

# check_same_thread=False bắt buộc cho SQLite trong FastAPI
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}
)


@event.listens_for(engine, "connect")
def _enable_sqlite_pragmas(dbapi_connection, _connection_record) -> None:
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

def init_db():
    """Tạo tất cả các bảng trong database khi khởi động"""
    SQLModel.metadata.create_all(engine)
    _ensure_analysis_result_columns()
    _cleanup_orphaned_rows()


def _ensure_analysis_result_columns() -> None:
    inspector = inspect(engine)
    if "analysis_results" not in inspector.get_table_names():
        return

    existing_columns = {column["name"] for column in inspector.get_columns("analysis_results")}
    alter_statements: list[str] = []

    if "analysis_kind" not in existing_columns:
        alter_statements.append(
            "ALTER TABLE analysis_results ADD COLUMN analysis_kind VARCHAR DEFAULT 'unknown' NOT NULL"
        )
    if "extracted_data_json" not in existing_columns:
        alter_statements.append(
            "ALTER TABLE analysis_results ADD COLUMN extracted_data_json TEXT DEFAULT '{}'"
        )

    if not alter_statements:
        return

    with engine.begin() as connection:
        for statement in alter_statements:
            connection.execute(text(statement))


def _cleanup_orphaned_rows() -> None:
    cleanup_statements = [
        """
        DELETE FROM workspace_artifact_links
        WHERE workspace_id NOT IN (SELECT id FROM workspaces)
           OR artifact_id NOT IN (SELECT id FROM artifacts)
        """,
        """
        DELETE FROM workspace_artifact_links
        WHERE EXISTS (
            SELECT 1
            FROM workspaces
            WHERE workspaces.id = workspace_artifact_links.workspace_id
              AND workspace_artifact_links.created_at < workspaces.created_at
        )
           OR EXISTS (
            SELECT 1
            FROM artifacts
            WHERE artifacts.id = workspace_artifact_links.artifact_id
              AND workspace_artifact_links.created_at < artifacts.created_at
        )
        """,
        """
        DELETE FROM analysis_results
        WHERE artifact_id NOT IN (SELECT id FROM artifacts)
           OR EXISTS (
            SELECT 1
            FROM artifacts
            WHERE artifacts.id = analysis_results.artifact_id
              AND analysis_results.analyzed_at < artifacts.created_at
        )
        """,
    ]

    with engine.begin() as connection:
        for statement in cleanup_statements:
            connection.execute(text(statement))
    
def get_session() -> Generator[Session, Any, None]:
    """Dependency Injection cho FastAPI routes"""
    with Session(engine) as session:
        yield session
