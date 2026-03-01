# Arch Lens AI

<p align="center">
  <img src="assets/repo-banner.png" alt="Arch Lens AI Banner" width="100%"/>
</p>

<p align="center">
  <strong>The R&D Operating System for Technical Due Diligence.</strong><br/>
  Thẩm định GitHub Repos, Research Papers và đối chiếu với ngữ cảnh doanh nghiệp của bạn — 100% cục bộ.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Tauri-v2-24C8D8?logo=tauri&logoColor=white" alt="Tauri v2"/>
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=white" alt="React 19"/>
  <img src="https://img.shields.io/badge/PydanticAI-Agents-E92063?logo=pydantic&logoColor=white" alt="PydanticAI"/>
  <img src="https://img.shields.io/badge/Privacy-First-2ECC71?logo=shield&logoColor=white" alt="Privacy First"/>
  <img src="https://img.shields.io/badge/version-0.1.0-blue" alt="Version"/>
</p>

---

## 🔎 Arch Lens AI là gì?

Arch Lens AI là một **Desktop-native R&D OS** giúp CTO, Tech Lead và BrSE trả lời câu hỏi mà các công cụ AI thông thường bỏ ngỏ:

> *"Công nghệ này có thực sự chạy được, và nó có phù hợp với hạ tầng cụ thể của chúng ta không?"*

Khác với các công cụ Cloud, mọi dữ liệu nội bộ của bạn — PRD, Architecture Docs, Budget Constraints — được xử lý **hoàn toàn trên máy local**, không bao giờ rời khỏi thiết bị của bạn.

---

## ✨ Tính năng cốt lõi (5 Trụ cột)

| Trụ cột | Mô tả |
| :--- | :--- |
| 📁 **Local Workspace** | Upload tài liệu nội bộ (PDF, DOCX, PPTX, MD) làm "bộ lọc" ngữ cảnh cho AI |
| 🔬 **GitHub Due Diligence** | Smart Sampling: phân tích Repo theo License/Health/Integration mà không cần clone |
| 📄 **Feasibility & ROI Analyzer** | Thẩm định Research Papers: tách Resource Footprint, đối chiếu với PRD của bạn |
| 🧠 **Cross-Verification RAG** | Multi-Agent chat: đối chiếu đồng thời Paper + Code + Tài liệu nội bộ |
| 📡 **Enterprise Tech Radar** | Tổng hợp kết quả thẩm định thành Radar 4 vòng: Adopt / Trial / Assess / Hold |

---

## 🏗️ Kiến trúc Hệ thống (Hybrid Intelligence)

```text
┌─────────────────────────────────────────────────────────┐
│                    Tauri v2 (Rust)                      │
│           Window · IPC · Sidecar Watchdog               │
└──────────────────┬──────────────────┬───────────────────┘
                   │ IPC              │ IPC
        ┌──────────▼──────────┐  ┌───▼─────────────────┐
        │   React 19 (TS)     │  │  FastAPI Sidecar     │
        │   TanStack Query    │  │  (Python 3.11+)      │
        │   Zustand           │  │  PydanticAI Agents   │
        │   Vite              │  │  SQLite (SQLModel)   │
        └─────────────────────┘  └─────────────────────┘
```

| Layer | Tech Stack | Mục đích |
| :--- | :--- | :--- |
| **Core** | Rust / Tauri v2 | Orchestrator, OS integration, Process isolation |
| **Backend** | Python / FastAPI / PydanticAI | AI Agents, Business Logic, Persistence |
| **Frontend** | React 19 / TypeScript / Tailwind v4 | UI, Data fetching (TanStack Query), State (Zustand) |
| **Database** | SQLite / SQLModel | Local-only persistence (Privacy-First) |
| **LLM** | Ollama (offline) / OpenAI / Anthropic | Pluggable AI backend |

---

## 🚀 Hướng dẫn Cài đặt & Phát triển (Quick Start)

### Yêu cầu hệ thống (Prerequisites)
- [Node.js](https://nodejs.org/) (v18+) & `npm`
- [Rust & Cargo](https://rustup.rs/) (Yêu cầu C++ Build Tools trên Windows)
- [Python](https://www.python.org/) (v3.11+)
- [uv](https://github.com/astral-sh/uv) (Trình quản lý package Python siêu tốc)
- [PowerShell 7+](https://aka.ms/install-powershell) (`pwsh`) — dùng cho tất cả automation scripts
  ```bash
  winget install --id Microsoft.PowerShell
  ```

### Các bước khởi chạy
1. **Clone dự án:**
   ```bash
   git clone https://github.com/your-org/arch-lens-ai.git
   cd arch-lens-ai
   ```

2. **Cài đặt Dependencies:**
   ```bash
   # Cài đặt Frontend & Tauri CLI
   npm install
   cd frontend && npm install && cd ..

   # Cài đặt Backend (Python)
   cd python-sidecar
   uv sync
   cd ..
   ```

3. **Chạy môi trường Phát triển (Development Mode):**
   Arch Lens AI đi kèm script tự động quản lý vòng đời ứng dụng.
   ```bash
   # Chạy lần đầu hoặc khi có thay đổi code Python (Sẽ tự động build file sidecar .exe)
   pwsh scripts/run-dev.ps1 -RebuildSidecar

   # Chạy các lần sau (Chỉ dev Frontend/Rust)
   pwsh scripts/run-dev.ps1
   ```

4. **Cập nhật version (tất cả file cùng lúc):**
   ```bash
   pwsh scripts/bump-version.ps1 -Version 0.2.0
   ```

---

## 📂 Cấu trúc Dự án (Repository Structure)

```text
arch-lens-ai/
├── frontend/             # ⚛️ React 19, Vite, TailwindCSS v4, Zustand
├── python-sidecar/       # 🐍 FastAPI, PydanticAI, SQLModel, PyMuPDF
│   ├── src/app/          # Core Business Logic & AI Agents
│   └── scripts/          # PyInstaller build scripts
├── src-tauri/            # 🦀 Rust Core, Window Management, Capabilities
│   ├── binaries/         # Compiled Python sidecars (.exe)
│   └── src/              # IPC & Watchdog logic
├── docs/                 # Kiến trúc, ADRs, và Scope
└── scripts/              # Automation scripts (Dev & Build)
```

---

## 🗺️ Lộ trình Phát triển (Roadmap)

- [x] **Phase 1: The Foundation** (Hoàn thiện hạ tầng Rust-Python-React, Setup Watchdog & IPC).
- [ ] **Phase 2: The Workspace Engine** (Chuyển đổi sang Workspace-centric, Setup SQLModel, Ingestion file PRD/Docx).
- [ ] **Phase 3: The Intelligence Layer** (Tích hợp PydanticAI, Vectorless RAG, Code & Paper Agents).
- [ ] **Phase 4: The Strategic Lens** (Cross-verification Agent, Tech Radar, Export báo cáo Due Diligence).

---

## 📄 License

MIT © 2026 Arch Lens AI. Tự do sử dụng, sửa đổi và phân phối.