# 📅 ARCH LENS AI: MASTER PROJECT PLAN

## PHASE 1: THE FOUNDATION (Hạ tầng Cốt lõi)
*Mục tiêu: Thiết lập xong "bộ não" (Backend) và "bộ mặt" (Frontend) cơ bản nhất, đảm bảo tính bảo mật và luồng giao tiếp.*

### Sprint 1.1: Backend Core Systems (Python)
*   **Môi trường & Config:** Khởi tạo `core/config.py` (load `.env`), `core/constants.py`.
*   **Bảo mật:** Tích hợp `KeyringManager` để lưu API Key an toàn. **[Legacy Re-use]**
*   **Lifecycle & Watchdog:** Thiết lập `SystemState`, `ArxivAPIState` (Rate limiting), và `SidecarWatchdog` để quản lý tài nguyên. **[Legacy Re-use]**
*   **Database Engine:** Cấu hình SQLite engine với SQLModel (`core/database.py`).
*   **Logging:** Setup hệ thống Logger (UTF-8) để bắn log từ Python qua Rust. **[Legacy Re-use]**

### Sprint 1.2: Frontend Shell & Global State (React)
*   **UI Architecture:** Khởi tạo cấu trúc Layout (Sidebar, Topbar, Main Content) với Tailwind v4.
*   **State Management:** Setup Zustand Store (`useAppStore`) quản lý Theme (Dark/Light), Language, và Backend Connection Status.
*   **API Client:** Cấu hình Axios (`lib/axios.ts`) và TanStack Query (`lib/queryClient.ts`) với các interceptor chuẩn. **[Legacy Re-use]**
*   **Settings UI:** Xây dựng Modal cài đặt AI Provider (Gemini, OpenAI, Ollama), cho phép nhập/lưu Key xuống OS Keyring thông qua API. **[Legacy Re-use UI logic]**

---

## PHASE 2: THE WORKSPACE ENGINE (Quản trị Ngữ cảnh)
*Mục tiêu: Chuyển đổi mô hình từ "Paper-centric" sang "Workspace-centric". Xây dựng khả năng nạp dữ liệu đa nguồn.*

### Sprint 2.1: Domain Models & Repositories (Backend)
*   Thiết kế `models/workspace.py` (Workspace, Constraints).
*   Thiết kế `models/artifact.py` (Kế thừa gộp từ `LocalPaper` và `GithubRepo` cũ).
*   Thiết kế `models/analysis.py` (Lưu kết quả thẩm định và ToC).
*   Xây dựng các Repository Layer tương ứng (CRUD cơ bản).

### Sprint 2.2: Workspace Dashboard (Frontend)
*   Tạo màn hình Home: Liệt kê các Workspaces.
*   Chức năng tạo Workspace mới: Form nhập tên, mô tả và **Business Constraints** (Ngân sách GPU, Kỹ năng team, Tech stack hiện tại).
*   Màn hình Workspace Detail: Nơi hiển thị các Artifacts thuộc về dự án này.

### Sprint 2.3: Artifact Ingestion (The Fetchers)
*   **ArXiv Fetcher:** Tích hợp lại logic search và tải PDF từ ArXiv. **[Legacy Re-use]**
*   **GitHub Fetcher:** Tích hợp lại logic lấy cây thư mục và đọc `README/dependencies` (không clone). **[Legacy Re-use]**
*   **Local Doc Ingestion (MỚI):** API sử dụng `MarkItDown` để nạp file PRD/Architecture (DOCX, MD) từ máy tính người dùng vào Workspace.

---

## PHASE 3: THE INTELLIGENCE LAYER (Thẩm định Đơn lẻ)
*Mục tiêu: Sử dụng PydanticAI để phân tích và bóc tách từng Artifact một cách độc lập.*

### Sprint 3.1: PydanticAI Routing & Tools
*   Viết lại `LMSettingService` để trả về các instance của `pydantic_ai.Agent` thay vì DSPy.
*   Định nghĩa các `Dependencies` chuẩn cho Agent (ví dụ: cấp quyền cho Agent đọc DB hoặc gọi GitHub API).

### Sprint 3.2: PDF/Doc Parsing & Indexing (Vectorless)
*   Khôi phục pipeline `pymupdf4llm` -> Markdown. **[Legacy Re-use]**
*   Khôi phục thuật toán Regex bóc tách Table of Contents (ToC). **[Legacy Re-use]**
*   Lưu cấu trúc ToC và Content Map vào `AnalysisResult` gắn với Artifact.

### Sprint 3.3: Due Diligence Agents (Thẩm định Đơn)
*   **Scientist Agent (For Papers):** Đọc ToC và Abstract, trích xuất yêu cầu phần cứng, dataset, và tóm tắt ý tưởng.
*   **Code Scout Agent (For Repos):** Đọc Metadata, trả về Tech Stack, Complexity Score, License Risk. **[Legacy Re-use Prompt Logic]**
*   **Frontend:** Hiển thị kết quả thẩm định dưới dạng Badges, Radar Charts, và Markdown Report trên UI của từng Artifact.

---

## PHASE 4: THE STRATEGIC LENS (Đối chiếu chéo & Ra quyết định)
*Mục tiêu: Hoàn thiện "Vũ khí tối thượng" của Arch Lens AI - Khả năng tìm ra sự mâu thuẫn và đánh giá độ phù hợp với doanh nghiệp.*

### Sprint 4.1: Cross-Verification Agent (The Critic)
*   Xây dựng Agent nhận đầu vào là: `Workspace Constraints` + `Paper Analysis` + `Repo Analysis`.
*   Nhiệm vụ: Tìm mâu thuẫn (Ví dụ: Paper nói cần 8GB VRAM, Code thực tế hardcode require 4x A100. Hoặc Team mạnh Python nhưng Repo viết bằng Rust).
*   Tính toán **ROI Score** và **Risk Score**.

### Sprint 4.2: Contextual Vectorless RAG Chat
*   Khôi phục tính năng Chat với tài liệu dựa trên ToC (Reasoning-based RAG). **[Legacy Re-use]**
*   **Nâng cấp:** Chat không chỉ với 1 Paper, mà chat với toàn bộ Context của Workspace ("Dựa trên PRD của công ty, bài báo này có áp dụng được không?").

### Sprint 4.3: Tech Radar & Export (Hoàn thiện)
*   Tổng hợp dữ liệu từ nhiều Workspaces để tạo Enterprise Tech Radar (Giữ lại logic Map-Reduce của TrendService cũ nhưng format lại output). **[Legacy Re-use]**
*   Tính năng xuất báo cáo thẩm định (Due Diligence Report) ra file Markdown/PDF để CTO mang đi họp.
