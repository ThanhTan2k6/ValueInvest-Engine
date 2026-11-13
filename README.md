# ValueInvest-Engine

> **Quantitative Financial Analysis, Multi-Agent Risk Auditing & LLMOps Platform**

[![CI Quality Gate](https://github.com/ThanhTan2k6/ValueInvest-Engine/actions/workflows/ci.yml/badge.svg)](https://github.com/ThanhTan2k6/ValueInvest-Engine/actions)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

---

## 1. Overview & Core Philosophy

**ValueInvest-Engine** giải quyết triệt để vấn đề **Math Hallucination** (ảo giác tính toán tài chính) thường gặp ở các mô hình ngôn ngữ lớn (LLM) bằng kiến trúc **Decoupled Engine**:

* **Deterministic Math Engine (100% Python/NumPy/Pandas):** Đảm nhiệm toàn bộ việc tính toán số học tài chính (DuPont 3 bước, FCFF/FCFE, WACC chuẩn CAPM, Ma trận nhạy cảm 2 chiều, Margin of Safety, và Traffic Light Red Flags) với thời gian thực thi $< 2\text{s}$.
* **Probabilistic Multi-Agent Engine (LangGraph + Pydantic v2):** Đóng vai trò Hội đồng Thẩm định Độc lập, sử dụng kỹ thuật phản biện Socrate (Socratic Devil's Advocate) để chất vấn các giả định định giá và bóc tách rủi ro từ Thuyết minh BCTC (Notes).
* **LLMOps & Anti-Hallucination Pipeline (Langfuse + DeepEval + Redis):** Đảm bảo điểm số **Faithfulness $\ge 0.95$** (mọi con số Agent nói ra phải tồn tại trong dữ liệu BCTC đã được kiểm toán).

---

## 2. System Architecture

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                   PRESENTATION LAYER                                   │
│            Streamlit Dashboard / FastAPI Web Client / Plotly Interactive Charts         │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │ (REST / WebSocket)
┌───────────────────────────────────────────▼────────────────────────────────────────────┐
│                             API GATEWAY & ORCHESTRATION                                │
│                          FastAPI Router & Request Controller                           │
└─────────────────────┬───────────────────────────────────────────┬──────────────────────┘
                      │                                           │
┌─────────────────────▼──────────────────────┐ ┌──────────────────▼──────────────────────┐
│        DETERMINISTIC MATH ENGINE           │ │          AGENTIC AI & LLMOPS ENGINE     │
│   (100% Strict Python / Pandas / NumPy)    │ │    (LangGraph / Multi-Agent / Langfuse) │
├────────────────────────────────────────────┤ ├─────────────────────────────────────────┤
│ • Module Ingestion & Data Sanitizer        │ │ • Supervisor / Dispatcher Agent         │
│ • Health Check & Dupont 3-Step Decomp      │ │ • Forensic Auditor Agent (Thuyết minh)  │
│ • Rule-based Red Flags Engine              │ │ • Socratic Devil's Advocate Agent       │
│ • DCF Multi-Scenario (Bear/Base/Bull)      │ │ • Macro & Market Research Tool Agent    │
│ • Sensitivity Heatmap Matrix (WACC vs g)   │ │ • Structured Output (Instructor/Pydantic│
│ • Margin of Safety (MoS) Calculator        │ │ • Groundedness & Faithfulness Evals     │
└─────────────────────┬──────────────────────┘ └──────────────────▲──────────────────────┘
                      │                                           │ Structured JSON
                      └───────────────── Context Pipeline ────────┘ (Anti-Hallucination)
```

---

## 3. Tech Stack

- **Core & Data:** Python 3.11+, Pydantic v2, Pandas, NumPy, OpenPyXL.
- **Agentic AI & Orchestration:** LangGraph, LangChain, Instructor, OpenAI GPT-4o.
- **LLMOps & Caching:** Langfuse, DeepEval, Redis.
- **Web & Dashboard:** Streamlit, Plotly, FastAPI.
- **DevOps & QA:** Docker, Docker Compose, GitHub Actions, Ruff, Pytest, Pytest-cov.

---

## 4. Quickstart Guide

### 4.1. Local Setup
```bash
# Clone the repository
git clone https://github.com/ThanhTan2k6/ValueInvest-Engine.git
cd ValueInvest-Engine

# Setup Virtual Environment
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install Dependencies
pip install -r requirements.txt

# Configure Environment
cp .env.example .env
# Edit .env with your OpenAI API Key and Langfuse keys
```

### 4.2. Running with Docker Compose
```bash
docker-compose up --build
```
Truy cập Streamlit UI tại: `http://localhost:8501`.

---

## 5. Development Governance & Standards

Xem chi tiết tại:
- [CLAUDE.md](CLAUDE.md) / [.cursorrules](.cursorrules): Bộ luật bất di bất dịch về ranh giới kiến trúc và kiểm toán số học.
- [.github/CONTRIBUTING.md](.github/CONTRIBUTING.md): Quy tắc GitHub Flow, Conventional Commits và Quality Gates.
- [.specs/](.specs/): Toàn bộ Data Contracts Pydantic v2, Agent Prompts và Golden Test Dataset.

---

## 6. Disclaimer

*Báo cáo và các số liệu do hệ thống này tính toán được lập cho mục đích cung cấp thông tin và kiểm toán rủi ro độc lập theo nguyên lý đầu tư giá trị. Đây không phải lời khuyên đầu tư tài chính theo quy định của Ủy ban Chứng khoán Nhà nước.*
