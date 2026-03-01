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

## 🏗️ Kiến trúc

```
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

| Layer | Tech | Mục đích |
| :--- | :--- | :--- |
| **Core** | Rust / Tauri v2 | Orchestrator, OS integration, IPC |
| **Backend** | Python / FastAPI / PydanticAI | AI Agents, Business Logic, Persistence |
| **Frontend** | React 19 / TypeScript / Vite | UI, Data fetching (TanStack Query), State (Zustand) |
| **Database** | SQLite / SQLModel | Local-only persistence |
| **LLM** | Ollama (offline) / OpenAI / Anthropic | Pluggable AI backend |

---

## 📄 License

MIT © Arch Lens AI

