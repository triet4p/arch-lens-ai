# 📂 Arch Lens AI: Structure & Conventions

## 1. Project Folder Structure

```text
arch-lens-ai/
├── src-tauri/                # 🦀 Rust Core (Tauri v2)
│   ├── src/
│   │   ├── main.rs           # Entry point & Sidecar orchestrator
│   │   └── lib.rs            # Rust logic (Window management, OS commands)
│   └── capabilities/         # Tauri V2 permission definitions
│
├── python-sidecar/           # 🐍 Backend AI & Persistence (Python 3.11+)
│   ├── src/
│   │   └── app/              # ← ALL Python packages live here
│   │       ├── api/          # FastAPI Layer
│   │       │   ├── v1/
│   │       │   │   ├── endpoints/    # Routers (workspaces, github, papers)
│   │       │   │   └── api.py        # Master router + app factory
│   │       │   └── deps.py           # Dependency Injection (DB sessions)
│   │       ├── agents/       # 🤖 PydanticAI Agents (The "Brain")
│   │       │   ├── models.py         # Output schemas (result_type classes)
│   │       │   ├── router.py         # Orchestrator Agent
│   │       │   ├── code_auditor.py   # Specialist: GitHub/Code analysis
│   │       │   └── paper_lens.py     # Specialist: ArXiv/Scientific analysis
│   │       ├── services/     # 🛠️ Business Logic (The "Hands")
│   │       │   ├── ingestion.py      # MarkItDown & PyMuPDF integration
│   │       │   ├── github_api.py     # Smart Sampling & Repo tree fetching
│   │       │   └── workspace.py      # Workspace/Project context management
│   │       ├── models/       # 🗄️ SQLModel Entities (Database tables)
│   │       │   ├── workspace.py      # Workspace & Artifact entities
│   │       │   └── analysis.py       # Due Diligence result entities
│   │       ├── dto/          # 📦 Data Transfer Objects (Pydantic)
│   │       │   ├── workspace.py      # WorkspaceCreate/Read/Update
│   │       │   ├── github.py         # AnalyzeRepoRequest, CodeAuditReportResponse
│   │       │   ├── analysis.py       # AnalysisResultRead
│   │       │   └── common.py         # PaginatedResponse, MessageResponse
│   │       ├── repositories/ # 🗄️ Data Access Layer
│   │       │   ├── base.py           # Generic CRUD BaseRepository
│   │       │   ├── workspace_repo.py # Workspace & Artifact queries
│   │       │   ├── artifact_repo.py  # Artifact queries
│   │       │   └── analysis_repo.py  # AnalysisResult queries
│   │       └── core/         # Config, DB, Logging
│   │           ├── config.py         # pydantic-settings (Settings class)
│   │           ├── db.py             # SQLite engine + get_session()
│   │           └── logging.py        # stdout logging for Tauri Watchdog
│   ├── main.py               # Sidecar entry point (Uvicorn, port 14201)
│   └── pyproject.toml        # uv / dependency management + pytest config
│
├── frontend/                 # ⚛️ UI Layer (React 19 + TS)
│   ├── src/
│   │   ├── assets/           # Static resources
│   │   ├── components/       # UI Components (Atomic design)
│   │   │   ├── common/       # Button, Input, Modal (Shared)
│   │   │   ├── workspace/    # Project/Workspace management UI
│   │   │   └── dashboard/    # Inspection results & Badges
│   │   ├── hooks/            # TanStack Query logic
│   │   ├── stores/           # Zustand global state (UI state)
│   │   ├── services/         # API Client (Axios)
│   │   ├── types/            # TypeScript Interfaces (Sync with Pydantic)
│   │   └── utils/            # Formatters, Helpers
│   ├── index.html
│   └── vite.config.ts
│
├── docs/                     # 📄 ADRs, Scopes, Market Analysis
├── scripts/                  # 🛠️ Automation (Build, Rebuild Sidecar)
└── .env.example              # Environment template
```

---

## 2. Coding Conventions

### 2.1. Backend (Python / PydanticAI / FastAPI)
*   **Import Root:** Tất cả import nội bộ phải bắt đầu từ `app.*` (vì `src/` được thêm vào `PYTHONPATH`).
    *   ✅ `from app.core.config import settings`
    *   ❌ `from core.config import settings`
*   **Type Hinting:** Bắt buộc sử dụng Python Type Hints cho tất cả tham số và giá trị trả về.
*   **Strict AI Schemas:** Không bao giờ để AI trả về chuỗi (string) tự do. Mọi Agent của PydanticAI phải có `result_type` là một **Pydantic Model** để đảm bảo Frontend luôn nhận được JSON chuẩn.
*   **Async-First:** Sử dụng `async/await` cho mọi tác vụ I/O (API calls, DB queries, AI inference) để không block Sidecar.
*   **Service Pattern:** Logic nghiệp vụ không được nằm trong Router. Router chỉ lo việc parse request và gọi Service.
*   **Docling/Parsing:** Luôn convert mọi tài liệu về định dạng **Markdown** trung gian trước khi nạp vào Agent.

#### 2.1.1. Quy ước cho Repositories (The Persistence Logic)
*   **Single Responsibility:** Mỗi Repository chỉ quản lý một thực thể chính (Aggregate Root). Ví dụ: `WorkspaceRepository` quản lý Workspace và các liên kết bên trong nó.
*   **No Business Logic:** Tuyệt đối không đưa logic AI hay logic thẩm định vào đây. Repository chỉ được phép: *Lọc, Sắp xếp, Thêm, Xóa, Sửa* dữ liệu.
*   **Session Management:** Luôn nhận `session: Session` thông qua Dependency Injection từ tầng API/Service để đảm bảo tính Atomic (Transaction).
*   **Type Safety:** Luôn trả về SQLModel objects hoặc `None`.

#### 2.1.2. Quy ước cho DTOs (The API Contract)
*   **Separation:** Phân tách rõ ràng giữa **Request DTO** (Dữ liệu user gửi lên) và **Response DTO** (Dữ liệu trả về cho UI).
    *   *Ví dụ:* `WorkspaceCreate` (chỉ cần name), `WorkspaceRead` (có thêm id, created_at, artifacts_count).
*   **Validation:** Tận dụng tối đa các validator của Pydantic (Field, EmailStr, HttpUrl) để lọc dữ liệu rác ngay tại cửa ngõ API.
*   **Conversion:** Sử dụng phương thức `.model_validate(db_obj)` của Pydantic để chuyển đổi nhanh từ Model Database (SQLModel) sang DTO Response.
*   **Consistency:** Mọi Response trả về cho Frontend phải được bọc trong một DTO, không bao giờ trả về trực tiếp Model Database (để tránh lộ các trường nhạy cảm hoặc cấu trúc DB nội bộ).

### 2.2. Frontend (React / TypeScript)
*   **Functional Components:** Sử dụng hoàn toàn React Hooks. Ưu tiên `lucide-react` cho icon.
*   **Atomic Components:** Tách nhỏ component. Nếu một khối UI được dùng ở 2 nơi (như Thẻ Repo), nó phải nằm trong `components/common/`.
*   **Zustand for UI State:** Dùng Zustand để quản lý trạng thái giao diện (Sidebar đóng/mở, Tab hiện tại, Dark mode).
*   **TanStack Query for Server State:** Toàn bộ dữ liệu từ Sidecar (List Project, Analysis Results) phải được quản lý qua Query/Mutation. Tuyệt đối không lưu data API vào `useState`.
*   **Safety:** Sử dụng Optional Chaining (`?.`) và Nullish Coalescing (`??`) khi xử lý dữ liệu từ AI để tránh crash UI khi AI trả về thiếu trường.

### 2.3. Quy ước Đặt tên (Naming)
*   **Folders:** `kebab-case` (ví dụ: `code-auditor`).
*   **Python Files/Variables:** `snake_case` (ví dụ: `analyze_repo`).
*   **TypeScript/React Files:** `PascalCase` cho Component (`RepoCard.tsx`), `camelCase` cho hooks (`useAnalyze.ts`).
*   **Database Tables:** `snake_case` số nhiều (ví dụ: `workspaces`, `artifacts`).

---

## 3. Inter-process Communication (IPC) Rules

Để đảm bảo Tauri và Sidecar giao tiếp mượt mà:
1.  **Port Stability:** Mặc định Sidecar chạy trên port `14201`.
2.  **DTO Sync:** Khi thay đổi một `BaseModel` ở Python (Backend), phải cập nhật ngay `interface` tương ứng ở `frontend/src/types/api.ts`.
3.  **Long-running Tasks:** Với các tác vụ thẩm định sâu (Deep Analysis), Backend phải sử dụng cơ chế **Polling** hoặc **Server-Sent Events (SSE)**. Frontend phải hiển thị thanh tiến trình (Progress bar) dựa trên các trạng thái này.
4.  **Graceful Shutdown:** Tauri phải gửi tín hiệu tắt Sidecar khi cửa sổ chính đóng lại (đã xử lý qua Watchdog ở bản cũ, cần giữ lại).

## 4. Luồng dữ liệu chuẩn (The Clean Flow)

Để dự án **Arch Lens AI** dễ bảo trì trong 3 tháng tới, mọi tính năng nên tuân theo luồng này:

1.  **Frontend:** Gọi API kèm theo **Interface TS** (khớp với DTO).
2.  **FastAPI Router:** Nhận dữ liệu qua **Request DTO**, thực hiện validation cơ bản.
3.  **Service Layer:** 
    *   Gọi **Repository** để lấy dữ liệu cũ (nếu cần).
    *   Đẩy dữ liệu vào **PydanticAI Agent**.
    *   Agent trả về kết quả đã được parse thành một **Schema nội bộ**.
4.  **Repository:** Lưu Schema đó vào Database.
5.  **FastAPI Router:** Chuyển đổi dữ liệu từ Database thành **Response DTO** và gửi về cho Frontend.