# 🔎 Arch Lens AI: Project Scope Statement

**Project Name:** Arch Lens AI  
**Codename:** `arch-lens-ai`  
**Target User:** CTOs, Tech Leads, Bridge SEs, R&D Managers  
**Vision:** "The Strategic Lens for Technical Due Diligence."

---

## 1. Mục tiêu Dự án (Project Objectives)
Xây dựng một hệ điều hành R&D (R&D OS) cục bộ, giúp người dùng thẩm định tính khả thi, rủi ro và giá trị thực tiễn của các công nghệ mới (từ Research Papers & GitHub) dựa trên ngữ cảnh và ràng buộc cụ thể của doanh nghiệp.

---

## 2. Phạm vi Công việc (In-Scope) - 5 Trụ cột chính

### 2.1. Local Workspace & Business Context (Hệ quy chiếu nội bộ)
*   **Quản lý Project/Workspace:** Tạo không gian riêng cho từng dự án nghiên cứu.
*   **Ingestion đa định dạng:** Sử dụng **MarkItDown** để nạp tài liệu nội bộ (PRD, Architecture, Team Skills, Budget Constraints) dưới dạng DOCX, PPTX, XLSX, MD.
*   **Contextual Embedding:** Biến tài liệu nội bộ thành "bộ lọc" để AI đối chiếu các công nghệ bên ngoài.

### 2.2. GitHub Due Diligence Engine (Thẩm định Mã nguồn)
*   **Smart Sampling Analysis:** Phân tích nhanh repo mà không cần clone hoàn toàn (cấu trúc thư mục, README, dependencies).
*   **Chỉ số thẩm định (CTO Metrics):**
    *   *Legal & Compliance:* Rà soát License (MIT, Apache, GPL...).
    *   *Project Health:* Tần suất cập nhật, số lượng maintainer, mật độ Issue/PR.
    *   *Integration Difficulty:* Đánh giá nỗ lực cần thiết để đưa repo vào stack hiện có của công ty.

### 2.3. Feasibility & ROI Analyzer (Thẩm định Nghiên cứu khoa học)
*   **ArXiv Deep Inspection:** Phân tích bài báo dưới lăng kính thực chiến thay vì lý thuyết suông.
*   **Bóc tách tài nguyên (Resource Footprint):**
    *   Hardware Req: Ước tính GPU/RAM cần thiết để chạy model.
    *   Data Hunger: Đánh giá khối lượng dữ liệu cần để tái hiện kết quả.
    *   Business Mapping: AI đánh giá xem ý tưởng bài báo giải quyết được KPI nào trong PRD của user.

### 2.4. Cross-Verification Multi-Agent RAG (Chat đối chiếu chéo)
*   **Hệ thống Đa tác tử (PydanticAI):** Một tác tử điều phối (Router) và các tác tử chuyên gia (Specialists) cho Paper, Code và Docs.
*   **Reasoning Across Sources:** Trả lời các câu hỏi mang tính quyết định: *"Dựa trên bài báo X, mã nguồn Y có điểm yếu gì khi triển khai trên hạ tầng Z của chúng ta?"*

### 2.5. Enterprise Technology Radar (Radar quản trị xu hướng)
*   **Aggregation:** Tổng hợp xu hướng từ hàng loạt bài báo và repo liên quan đến Project.
*   **Lifecycle Categorization:** Phân loại công nghệ vào 4 nhóm: **Adopt** (Nên dùng), **Trial** (Thử nghiệm), **Assess** (Theo dõi), **Hold** (Dừng lại).

---

## 3. Phạm vi Loại biên (Out-of-Scope) - Những gì dự án KHÔNG LÀM

1.  **AI Coding (Generative):** Không viết code, không sửa lỗi cú pháp, không cạnh tranh với Cursor/Claude Code.
2.  **General Search Engine:** Không phải là công cụ tìm kiếm thông tin chung chung (General QA).
3.  **Source Code Execution:** Không tự động thực thi hoặc biên dịch mã nguồn lạ để đảm bảo an toàn hệ thống.
4.  **SaaS/Cloud Hosting:** Không lưu trữ dữ liệu Project trên Cloud. Mọi thứ phải nằm trong máy user (Privacy-First).
5.  **Model Training:** Không cung cấp tính năng huấn luyện mô hình (Training/Fine-tuning).

---

## 4. Ràng buộc Kỹ thuật (Technical Constraints)

*   **Runtime:** Python 3.11+ Sidecar tích hợp trong Tauri v2.
*   **Agent Framework:** **PydanticAI** (Strictly typed, lean dependencies).
*   **Parsing Stack:** **PyMuPDF** (PDF) + **MarkItDown** (Office formats).
*   **Size Limit:** Tổng dung lượng file thực thi Python Sidecar **< 200MB**.
*   **Database:** SQLite (SQLModel) cục bộ; không sử dụng Vector DB rời rạc nếu không thực sự cần thiết (ưu tiên ToC indexing).

---

## 5. Tiêu chí Nghiệm thu (Acceptance Criteria)

1.  Hệ thống chạy được 100% Offline (với Ollama) hoặc Hybrid (với API Key).
2.  Phân tích được một GitHub Repo và trả về báo cáo rủi ro (Risk Report) trong < 30 giây.
3.  Thực hiện được Cross-verification: Phát hiện mâu thuẫn giữa 2 nguồn tài liệu khác nhau trong cùng một Project.
4.  Giao diện hiển thị được rõ ràng các chỉ số thẩm định (Badges, Scores) thay vì chỉ có text thô.