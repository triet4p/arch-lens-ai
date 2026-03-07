# Changelog: GitHub Ingestor & Artifact Delete Layer

> Ngày: 2026-03-03  
> Phạm vi: Hoàn tất tầng Ingestion với GitHub Ingestor và bộ API xóa Artifact.

---

## 1. `src/app/services/ingestion/_github.py` *(file mới)*

Triển khai `GithubIngestor` theo chiến lược **Smart Sampling**: thu thập metadata repo mà không cần clone, chỉ dùng GitHub REST API.

**Logic:**
1. `_parse_url(url)` — trích xuất `owner/repo` từ URL GitHub bất kỳ.
2. `fetch_repo_data(url)` — 3 API calls tuần tự trong 1 `AsyncClient`:
   - `GET /repos/{owner}/{repo}` → metadata cơ bản (`stars`, `forks`, `language`, `description`, `default_branch`).
   - `GET /repos/{owner}/{repo}/git/trees/{branch}?recursive=1` → cây thư mục, giới hạn **200 paths** đầu tiên.
   - `GET raw.githubusercontent.com/.../README.md` → preview README, giới hạn **5000 ký tự**.
3. Trả về `IngestedArtifact(type=REPO, source_url, raw_metadata={...})`.

---

## 2. `src/app/services/ingestion/__init__.py`

Thêm export `GithubIngestor`:

```python
from ._github import GithubIngestor
__all__ = ["ArxivIngestor", "LocalIngestor", "GithubIngestor"]
```

---

## 3. `src/app/api/deps.py`

**Thêm mới:**
- `get_github_ingestor() -> GithubIngestor` — provider trả về instance mới mỗi request (stateless).
- `GithubIngestorDep` — Annotated alias để inject vào `get_artifact_service`.
- `github_ingestor: GithubIngestorDep` được inject vào `ArtifactService`.

**Fix bug cũ:**  
`ArxivIngestorDep` / `LocalIngestorDep` được sử dụng trong `get_artifact_service` trước khi khai báo. Đã di chuyển tất cả alias lên trước factory function.

---

## 4. `src/app/repositories/link.py`

Thêm method `delete_link`:

```python
def delete_link(self, workspace_id: int, artifact_id: int) -> bool:
    """Xóa liên kết theo composite PK (workspace_id, artifact_id)"""
```

---

## 5. `src/app/services/artifact.py`

### 5a. GitHub Ingestor injection
- Thêm `github_ingestor: GithubIngestor` vào `__init__`.

### 5b. Refactor — Extract Private Helpers (DRY)
Gộp đoạn code lặp lại trong cả 3 `add_*` method:

| Helper | Trách nhiệm |
|---|---|
| `_create_and_link(workspace_id, ingested)` | Tạo `Artifact` record → `artifact_repo.create()` → `link_repo.create_link()` |
| `_to_artifact_read_dto(db_artifact)` | Chuyển DB object → `ArtifactRead` DTO + map `metadata` |

> `add_arxiv_artifact` vẫn giữ riêng phần download PDF + FAILED handling vì đây là logic đặc thù, không thể gộp mà không bị if-else.

### 5c. Thêm add_github_artifact
```
add_github_artifact(workspace_id, repo_url)
  → github_ingestor.fetch_repo_data()
  → _create_and_link()
  → _to_artifact_read_dto()
```

### 5d. Thêm 3 Delete Methods

| Method | Logic đặc thù |
|---|---|
| `delete_arxiv_artifact` | Xóa file PDF vật lý (`os.remove`) nếu `local_path` tồn tại |
| `delete_local_artifact` | Xóa file upload vật lý (`os.remove`) nếu `local_path` tồn tại |
| `delete_github_artifact` | Không có file vật lý, chỉ gọi `_delete_artifact_record` |

Tất cả chia sẻ private helper `_delete_artifact_record(workspace_id, artifact_id)`:
```
_delete_artifact_record
  → link_repo.delete_link()
  → artifact_repo.delete()
```

---

## 6. `src/app/api/v1/endpoints/artifact.py`

### Add Endpoints (POST)

| Method | URL | Service call |
|---|---|---|
| POST | `/artifact/github/{workspace_id}` | `add_github_artifact` |

### Delete Endpoints (DELETE → 204 No Content)

| Method | URL | Service call |
|---|---|---|
| DELETE | `/artifact/arxiv/{workspace_id}/{artifact_id}` | `delete_arxiv_artifact` |
| DELETE | `/artifact/upload/{workspace_id}/{artifact_id}` | `delete_local_artifact` |
| DELETE | `/artifact/github/{workspace_id}/{artifact_id}` | `delete_github_artifact` |

Tất cả DELETE trả `404` nếu `artifact_id` không tồn tại.

---

## Tổng quan luồng dữ liệu sau thay đổi

```
[API Endpoint]
    │
    ▼
[ArtifactService]  ←── inject: ArxivIngestor / LocalIngestor / GithubIngestor
    │
    ├── add_*    → _create_and_link() → _to_artifact_read_dto()
    │
    └── delete_* → _delete_artifact_record()
                       ├── LinkRepository.delete_link()
                       └── ArtifactRepository.delete()
```
