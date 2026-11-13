# ValueInvest-Engine: Đề cương Kỹ thuật & Báo cáo Kiến trúc Toàn diện
> **Quantitative Financial Analysis, Multi-Agent Risk Auditing & LLMOps Platform**

---

## 1. Bối cảnh & Lý do Ra đời Dự án (Motivation & Problem Statement)

### 1.1. Thực trạng Thị trường & Nỗi đau của Nhà đầu tư (Pain Points)
1. **Tâm lý "Fomo" & Thiếu Phương pháp Luận:**
   * Phần lớn nhà đầu tư cá nhân trên thị trường chứng khoán Việt Nam (thị trường cận biên với hơn 80% giao dịch đến từ retail) ra quyết định dựa trên tin đồn, hội nhóm mạng xã hội (phím lệnh room Zalo/Telegram) hoặc cảm tính ngắn hạn, thay vì phân tích nền tảng doanh nghiệp.
2. **"Bẫy" Kế toán & Rủi ro Báo cáo Tài chính (Creative Accounting & Red Flags):**
   * Báo cáo tài chính (BCTC) tại Việt Nam ẩn chứa nhiều thủ thuật tài chính tinh vi: ghi nhận doanh thu ảo qua khoản phải thu, dòng tiền kinh doanh âm kéo dài ($CFO < 0$) dù lợi nhuận sau thuế vẫn tăng trưởng, dùng đòn bẩy ngắn hạn tài trợ dự án dài hạn, hoặc các giao dịch bên liên quan (Related-party transactions) phức tạp.
   * Nhà đầu tư phổ thông hầu như không đủ thời gian và kỹ năng kiểm toán để đọc hết 40–80 trang Thuyết minh BCTC nhằm bóc tách rủi ro.
3. **Sự Bất lực của các Công cụ Hiện tại:**
   * **Nền tảng tài chính truyền thống (Vietstock, FireAnt, Wichart):** Chỉ cung cấp bảng dữ liệu tĩnh (raw financial tables/charts), thiếu cơ chế tự động quét "bẫy rủi ro" có giải thích chi tiết và thiếu bộ công cụ định giá tương tác đa chiều.
   * **Các Chatbot AI phổ thông (ChatGPT, Claude web):** Thường xuyên gặp lỗi **ảo giác (Hallucination)** khi tính toán số liệu tài chính; tự "bịa" ra chỉ số P/E, ROE, FCF hoặc áp dụng công thức sai lệch, gây rủi ro đặc biệt nghiêm trọng nếu dùng vào quyết định giải ngân vốn.

### 1.2. Lý do Ra đời của `ValueInvest-Engine`
* **Triết lý Cốt lõi: Risk-First & Decision Support System:**
  * Hệ thống **tuyệt đối không** đưa ra các khuyến nghị mua/bán dạng "phán lệnh" hoặc một con số định giá cố định duy nhất.
  * Hệ thống đóng vai trò như một **Hội đồng Thẩm định Độc lập**, cung cấp 3 lớp phòng vệ:
    1. Tự động kiểm toán sức khỏe tài chính & phát hiện Red Flags định lượng.
    2. Mô hình hóa định giá tương tác đa kịch bản với Biên an toàn (Margin of Safety).
    3. Hệ thống Multi-Agent AI đóng vai "Biện lý phản bác" (Socratic Devil's Advocate) để chất vấn, vạch lá tìm sâu vào các giả định màu hồng của nhà đầu tư trước khi xuống tiền.
* **Nguyên tắc Thiết kế Decoupled Engine:**
  * Tách biệt 100% giữa **Tầng Tính toán Quyết định (Deterministic Math Engine)** dùng code toán thuần (Pandas/NumPy) và **Tầng Trí tuệ Nhân tạo Xác suất (Probabilistic Multi-Agent & LLMOps Engine)**. Đảm bảo tính trung thực tuyệt đối của số liệu tài chính.

---

## 2. Kiến trúc Hệ thống Tổng thể (High-Level Architecture)

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
                                            ▲
                                            │
┌───────────────────────────────────────────┴────────────────────────────────────────────┐
│                                 INFRASTRUCTURE & OPS                                   │
│  • LLMOps: Langfuse / Phoenix (Tracing, Latency, Token Cost, Eval Metric Suites)       │
│  • Caching: Redis / Disk-cache (Semantic & Raw Ingestion Caching)                      │
│  • Testing: Pytest Suite, Golden Test Cases (Vietstock/FireAnt Verified Datasets)       │
│  • Delivery: Docker Container, GitHub Actions CI/CD Pipeline                           │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Chi tiết Phân hệ Kỹ thuật (Core Engine Modules)

### 3.1. Phân hệ Tính toán Quyết định (Deterministic Math Engine - `src/engine/`)
Đảm bảo tính chính xác 100% về mặt toán học và báo cáo tài chính, không phụ thuộc vào LLM:
1. **Module Data Ingestion & Sanitizer (`src/ingestion/`):**
   * Tự động crawl/ingest BCTC 3–5 năm từ các nguồn tài chính chuẩn hóa (vnstock, Vietstock API, file Excel/JSON).
   * Chuẩn hóa danh mục tài khoản kế toán (Balance Sheet, Income Statement, Cash Flow Statement) theo Thông tư 200/BTC.
   * Xử lý dữ liệu khuyết thiếu, kiểm định tính cân bằng của Bảng cân đối kế toán: $\text{Tài sản} = \text{Nguồn vốn}$.
2. **Health Check & Dupont Decomposition:**
   * Phân tích DuPont 3 nhân tố:
     $$\text{ROE} = \left(\frac{\text{Net Income}}{\text{Revenue}}\right) \times \left(\frac{\text{Revenue}}{\text{Assets}}\right) \times \left(\frac{\text{Assets}}{\text{Equity}}\right)$$
   * Đánh giá chi tiết: ROIC, Gross Margin, Net Margin, Vòng quay hàng tồn kho, Kỳ thu tiền bình quân.
3. **Cỗ máy Phát hiện Bẫy Kế toán (Traffic Light Red Flags):**
   * 🔴 **Critical Flags:**
     * $CFO < 0$ kéo dài liên tiếp 2–3 kỳ trong khi Lợi nhuận sau thuế tăng trưởng (Dấu hiệu lợi nhuận giấy).
     * Nợ vay ngắn hạn vượt quá Tài sản ngắn hạn (Rủi ro vỡ nợ thanh khoản).
   * 🟡 **Warning Flags:**
     * Tỷ lệ $\frac{\text{Phải thu}}{\text{Doanh thu}}$ tăng đột biến qua các quý (Nguy cơ ghi nhận doanh thu non hoặc chuyển vốn lòng vòng).
     * Biên lợi nhuận gộp suy giảm 3 năm liên tiếp (Mất lợi thế cạnh tranh Moat).
   * 🟢 **Safe Checks:**
     * Hệ số phủ lãi vay ($\text{Interest Coverage Ratio} = \frac{\text{EBIT}}{\text{Lãi vay}} > 5.0x$).
     * Tỷ lệ Đòn bẩy tài chính ($\frac{\text{Debt}}{\text{Equity}}$) an toàn trong ngưỡng ngành.
4. **Mô hình Định giá Tương tác (Dynamic Valuation & Sensitivity):**
   * **DCF Đa giai đoạn (Multi-stage DCF):**
     * Chiết khấu dòng tiền tự do doanh nghiệp ($FCFF$) hoặc vốn chủ sở hữu ($FCFE$).
     * Tính toán WACC chuẩn CAPM:
       $$WACC = \frac{E}{V} \times R_e + \frac{D}{V} \times R_d \times (1 - T_c)$$
   * **Ma trận độ nhạy (Sensitivity Heatmap Matrix):**
     * Biến thiên 2 chiều giữa Discount Rate ($WACC$: 10% – 14%) và Terminal Growth ($g$: 2% – 5%), trả về ma trận giá trị nội tại tức thời (< 0.1s).
   * **Margin of Safety (MoS):**
     $$MoS = \frac{\text{Giá trị Nội tại} - \text{Thị giá}}{\text{Giá trị Nội tại}} \times 100\%$$

---

### 3.2. Phân hệ Trí tuệ Nhân tạo Đa Tác tử (Agentic AI Engine - `src/agents/`)
Thay vì sử dụng một prompt LLM đơn lẻ, hệ thống áp dụng kiến trúc **Multi-Agent Collaboration** (sử dụng LangGraph / AutoGen / Function Calling):

```
                       ┌─────────────────────────┐
                       │    Supervisor Agent     │
                       │ (Điều phối & Tổng hợp)  │
                       └────────────┬────────────┘
                                    │
           ┌────────────────────────┼────────────────────────┐
           ▼                        ▼                        ▼
┌──────────────────────┐ ┌──────────────────────┐ ┌──────────────────────┐
│   Forensic Auditor   │ │  Valuation Challenger │ │   Macro & Industry   │
│        Agent         │ │        Agent         │ │    Research Agent    │
├──────────────────────┤ ├──────────────────────┤ ├──────────────────────┤
│ • Quét Thuyết minh   │ │ • Đóng Devil's       │ │ • Tra cứu giá hàng   │
│ • Nợ tiềm tàng       │ │   Advocate           │ │   hóa (Thép, Dầu,..) │
│ • Giao dịch bên      │ │ • Bẻ gãy giả định    │ │ • Rủi ro tỷ giá, lạm │
│   liên quan          │ │   màu hồng về g, WACC│ │   phát, chu kỳ ngành │
└──────────────────────┘ └──────────────────────┘ └──────────────────────┘
```

1. **Supervisor / Orchestrator Agent:**
   * Đọc cấu trúc JSON từ Deterministic Engine, phân bổ nhiệm vụ chuyên biệt cho từng sub-agent.
   * Tổng hợp các luận điểm phản bác, loại bỏ trùng lặp và biên soạn báo cáo phản biện mạch lạc, súc tích (< 300 từ).
2. **Forensic Auditor Agent (Tác tử Kiểm toán BCTC):**
   * **Input:** Báo cáo Red Flags từ Module 2 + Text phần Thuyết minh BCTC (Notes to Financial Statements).
   * **Nhiệm vụ:** Phân tích sâu nguyên nhân gốc rễ của Red Flags (ví dụ: Phải thu tăng là từ đối tác nào? Doanh nghiệp trích lập dự phòng có đủ không? Nợ ngắn hạn đáo hạn trong vòng mấy tháng?).
3. **Valuation Challenger Agent (Tác tử Phản biện Định giá - Socratic Devil's Advocate):**
   * **Input:** Giả định DCF của người dùng ($g$, $WACC$, Target Margin) + Lịch sử biên lợi nhuận quá khứ.
   * **Nhiệm vụ:** Đặt ra 3 câu hỏi hóc búa mang tính Socratic để chất vấn nhà đầu tư:
     * *"Bạn đặt giả định tăng trưởng $g = 12\%$ trong 5 năm tới, nhưng công suất nhà máy hiện hữu đã chạy 95% và dự án mở rộng đang chậm tiến độ 1 năm. Động lực nào để đạt được con số này?"*
4. **Macro & Industry Tool Agent (Tác tử Tra cứu Ngoại cảnh):**
   * Tự động gọi tool web search / API vĩ mô để cập nhật bối cảnh ngành (ví dụ: thuế tự vệ ngành thép, biến động giá quặng sắt, chính sách tín dụng bất động sản) nhằm đối chiếu với tính khả thi của mô hình kinh doanh.

---

### 3.3. Hạ tầng MLOps / LLMOps Pipeline (`src/llmops/`)
Chuẩn hóa chất lượng, kiểm soát chi phí và bảo đảm khả năng vận hành production:

1. **Anti-Hallucination & Groundedness Evaluation (Đánh giá Không Ảo giác):**
   * Tích hợp framework kiểm thử LLM tự động (DeepEval / Ragas).
   * **Metric Faithfulness / Groundedness:** Toàn bộ số liệu tài chính mà Agent trích dẫn trong câu phản biện (ví dụ: *4.200 tỷ nợ ngắn hạn*) bắt buộc phải có mặt trong structured JSON do Deterministic Engine sinh ra. Điểm Faithfulness < 1.0 sẽ kích hoạt tự động sinh lại hoặc cảnh báo.
2. **Structured Output & Guardrails (Instructor & Pydantic):**
   * Ép toàn bộ output của Agent vào schema Pydantic chặt chẽ: `RiskLevel`, `EvidenceList`, `ChallengingQuestions`, `IdentifiedAccountingTricks`.
   * **Financial Disclaimer Guardrails:** Bộ lọc chặn triệt để các phát ngôn vi phạm pháp luật về tư vấn tài chính hoặc cam kết lợi nhuận.
3. **Observability, Tracing & Cost Monitoring (Langfuse / OpenTelemetry):**
   * Ghi nhận 100% trace của Multi-Agent: Latency từng agent, Token Cost (Input/Output tokens), Prompt Version, Error Rate.
   * Dashboard theo dõi chi phí gọi API theo từng mã cổ phiếu phân tích.
4. **Semantic Caching & Data Caching (Redis / GPTCache):**
   * Với cùng một mã cổ phiếu và cùng bộ tham số đầu vào trong một phiên giao dịch, kết quả phân tích phản biện của Agent được cache lại, giảm 90% chi phí gọi LLM và đưa thời gian phản hồi về dưới 0.2s.
5. **Prompt Versioning & CI Regression Tests:**
   * Quản lý system prompts bằng Git và Langfuse Prompt Registry.
   * CI test tự động chạy bộ 10 BCTC mẫu nổi tiếng có "bẫy kế toán" (case study thực tế trên sàn HOSE/HNX) trước mỗi lần merge code.

---

## 4. Chi tiết Input & Output (User & System Level)

### A. Input (Đầu vào)

Hệ thống tiếp nhận 2 nhóm dữ liệu:

1. **Dữ liệu Tự động (System Ingestion):**
   * **Mã cổ phiếu (Ticker):** ví dụ `VNM`, `HPG`, `FPT`, `MWG`.
   * **BCTC 3–5 năm gần nhất:** Bảng Cân đối kế toán, Báo cáo Kết quả KD, Báo cáo Lưu chuyển tiền tệ và Thuyết minh BCTC.
   * **Dữ liệu Thị trường Thời gian thực:** Giá đóng cửa hiện tại, Khối lượng cổ phiếu lưu hành, Vốn hóa thị trường.

2. **Dữ liệu Tùy biến từ Người dùng (User Parametric Sliders trên Dashboard):**
   * **Tốc độ tăng trưởng dự phóng ($g$):** Cho các giai đoạn (Stage 1: 1–5 năm, Stage 2: 5–10 năm).
   * **Chi phí vốn bình quân ($WACC$ / Discount Rate):** Mặc định tính sẵn theo CAPM, cho phép user kéo slider điều chỉnh (ví dụ: 10% – 14%).
   * **Terminal Growth Rate ($g_{terminal}$):** Tốc độ tăng trưởng vĩnh viễn (thường 2% – 3%).
   * **Kỳ vọng Margin of Safety tối thiểu:** (ví dụ: 20%, 25%, 30%).

---

### B. Output (Đầu ra)

Kết quả trả về được chia làm 3 tầng chuyên biệt:

* **Tầng 1: Health Check & Red Flags (Định lượng - Không LLM):**
  * Bảng điểm DuPont 3 bước: $\text{ROE} = \text{Profit Margin} \times \text{Asset Turnover} \times \text{Financial Leverage}$.
  * Thẻ cảnh báo Rủi ro (Traffic Light Red Flags):
    * 🔴 **Critical:** $CFO < 0$ liên tục 2 năm trong khi Lợi nhuận sau thuế vẫn tăng.
    * 🟡 **Warning:** Tỷ lệ Phải thu / Doanh thu tăng từ 15% lên 32% trong 4 quý gần nhất.
    * 🟢 **Safe:** Tỷ lệ phủ lãi vay (Interest Coverage) = 8.5x (an toàn cao).

* **Tầng 2: Dynamic Valuation & Sensitivity Matrix (Định giá):**
  * **Bảng định giá 3 kịch bản:**
    | Kịch bản | Tăng trưởng ($g$) | Chiết khấu ($WACC$) | Giá trị nội tại (VND) | Thị giá hiện tại (VND) | Biên an toàn (Margin of Safety) |
    | :--- | :--- | :--- | :--- | :--- | :--- |
    | **Bear** | 5% | 13.5% | 62,000 | 74,000 | -16.2% (Đắt) |
    | **Base** | 9% | 12.0% | 81,000 | 74,000 | +8.6% (Mép an toàn thấp) |
    | **Bull** | 14% | 10.5% | 105,000 | 74,000 | +29.5% (Hấp dẫn) |
  * **Ma trận độ nhạy (Sensitivity Heatmap):** Bảng 2 chiều cho thấy Giá trị CP biến thiên khi $WACC$ thay đổi (10% $\to$ 14%) và $g$ thay đổi (4% $\to$ 10%).

* **Tầng 3: Socratic Devil’s Advocate (Multi-Agent Output):**
  * Báo cáo phản biện ngắn (dưới 300 từ) dạng Markdown:
    * *"Bạn đang giả định biên lợi nhuận gộp giữ ở mức 28%, nhưng Thuyết minh BCTC cho thấy chi phí nguyên liệu đầu vào đang tăng 15% và doanh nghiệp không có khả năng chuyển giá cho khách hàng."*
    * *"Rủi ro nợ vay ngắn hạn sắp đáo hạn: 4.200 tỷ VND trong khi tiền mặt chỉ có 1.500 tỷ VND."*

---

## 5. Kịch bản Demo Thực tế (End-to-End User Flow)

Kịch bản demo 3 phút chuẩn phục vụ phỏng vấn tuyển dụng hoặc thuyết trình sản phẩm:

```
[BƯỚC 1: Nhập mã Cổ phiếu]
Gõ mã "HPG" -> Bấm "Analyze"
       │
       ▼
[BƯỚC 2: Tải & Quét số liệu tự động]
Dashboard tải BCTC 5 năm (< 2 giây).
Ngay lập tức hiển thị box Traffic Light Red Flags:
Cảnh báo nợ vay phình to trong chu kỳ đầu tư dự án đại công trình.
       │
       ▼
[BƯỚC 3: Tương tác Định giá DCF]
User kéo slider: FCF tăng trưởng 8%, WACC 11%.
Màn hình render tức thì biểu đồ Waterfall Cash Flow, bảng so sánh Giá trị nội tại vs Thị giá, 
và Ma trận Heatmap độ nhạy.
       │
       ▼
[BƯỚC 4: Kích hoạt Phân hệ Multi-Agent "Devil's Advocate"]
Bấm nút "Challenge My Valuation".
Supervisor kích hoạt Forensic Agent + Valuation Challenger Agent.
Langfuse ghi nhận trace. LLM trả về 3 câu hỏi phản biện sắc bén chống lại giả định của User.
       │
       ▼
[BƯỚC 5: Export One-Pager Báo cáo]
Bấm "Export Investment Memo" -> Xuất file PDF/Markdown đóng gói toàn bộ phân tích định lượng,
ma trận định giá và câu hỏi phản biện để lưu nhật ký đầu tư.
```

---

## 6. Cấu trúc Thư mục Dự án Chuẩn (Project Directory Layout)

```
ValueInvest-Engine/
├── .github/workflows/          # CI/CD: Test suite, Linting, Eval benchmark
│   └── ci.yml
├── data/                       # Dữ liệu mẫu & Cache
│   ├── raw/                    # BCTC JSON/Excel thô
│   └── golden_eval/            # 10 case test BCTC chuẩn phục vụ LLM Eval
├── src/
│   ├── ingestion/              # Thu thập & làm sạch dữ liệu BCTC
│   │   ├── vnstock_loader.py
│   │   ├── sanitizer.py
│   │   └── schemas.py          # Pydantic BCTC Data Models
│   ├── engine/                 # Deterministic Financial Engine (100% Math)
│   │   ├── dupont.py           # Dupont decomposition
│   │   ├── red_flags.py        # Rule-based accounting checks
│   │   ├── cashflow.py         # FCF & Cash conversion cycle
│   │   └── metrics.py          # Solvency, Liquidity, Coverage ratios
│   ├── valuation/              # Mô hình định giá
│   │   ├── dcf.py              # DCF model & WACC calculator
│   │   ├── sensitivity.py      # Heatmap 2 chiều (WACC vs g)
│   │   └── scenarios.py        # Bear / Base / Bull logic
│   ├── agents/                 # Multi-Agent System (LangGraph)
│   │   ├── supervisor.py       # Orchestrator & Synthesis
│   │   ├── forensic.py         # Thuyết minh BCTC Auditor Agent
│   │   ├── challenger.py       # Socratic Devil's Advocate Agent
│   │   └── tools.py            # Financial Tools & Web Search
│   ├── llmops/                 # LLMOps & Guardrails
│   │   ├── tracer.py           # Langfuse / OpenTelemetry setup
│   │   ├── evals.py            # Faithfulness & Groundedness Evals (DeepEval)
│   │   └── guardrails.py       # Pydantic Output Enforcement & Disclaimer filter
│   └── ui/                     # Presentation Layer
│       ├── app.py              # Streamlit Main App
│       ├── components/         # Metric cards, Traffic lights, Heatmaps
│       └── report_gen.py       # Export PDF/Markdown One-Pager
├── tests/                      # Pytest Unit & Integration Tests
│   ├── test_engine_math.py     # Đối chiếu số liệu với Vietstock/FireAnt
│   ├── test_red_flags.py
│   └── test_llm_faithfulness.py
├── Dockerfile
├── docker-compose.yml          # Containerize App + Redis Cache
├── requirements.txt
├── README.md
└── context.md                  # Tài liệu TRD & Architectural Blueprint
```

---

## 7. Tiêu chí Hoàn thành & Nghiệm thu (Definition of Done - DoD)

1. **Hiệu năng & Độ trễ (Performance):**
   * Tầng tính toán định lượng ($100\%$ Python/NumPy): Hoàn tất quét BCTC 5 năm, phát hiện Red Flags và vẽ Heatmap định giá trong vòng **dưới 2 giây**.
   * Toàn bộ phản hồi của Multi-Agent: Phản hồi dưới **6 giây** (với Streaming Markdown) hoặc dưới **0.2 giây** nếu kích hoạt Semantic Cache.
2. **Độ chính xác Tuyệt đối (Zero Math Hallucination):**
   * 100% các công thức ROE, ROIC, FCF, DCF, WACC được bảo chứng qua unit test đối chiếu dữ liệu với Vietstock/FireAnt.
   * Điểm đánh giá **Faithfulness của LLM $\ge 0.95$** (đo bằng DeepEval/Ragas): Tác tử AI không được phép bịa bất kỳ số liệu tài chính nào ngoài dữ liệu đã được cung cấp.
3. **Mã nguồn Chuẩn Kỹ thuật (Production-Ready Codebase):**
   * Độ phủ kiểm thử tự động (Unit Test Coverage) đạt trên **80%** cho `src/engine/` và `src/valuation/`.
   * Đóng gói Docker hoàn chỉnh, khởi chạy chỉ với một lệnh `docker-compose up`.

---

## 8. Lộ trình Triển khai Dự án (Project Implementation Roadmap)

* **Giai đoạn 1 (Tuần 1–2): Core Ingestion & Deterministic Math Engine**
  * Tích hợp Ingestion qua `vnstock` / API, chuẩn hóa schema Pydantic.
  * Hoàn thiện Dupont 3 bước, Traffic Light Red Flags và Mô hình DCF 3 kịch bản + Heatmap.
  * Viết Pytest kiểm thử đối chiếu số liệu tài chính thực tế.
* **Giai đoạn 2 (Tuần 3–4): Multi-Agent Architecture & Socratic Devil's Advocate**
  * Thiết lập LangGraph với Supervisor Agent, Forensic Auditor và Valuation Challenger.
  * Xây dựng Prompting System theo phương pháp tư duy phản biện Socratic.
  * Tích hợp Pydantic Instructor để ép chặt Structured JSON Output.
* **Giai đoạn 3 (Tuần 5–6): LLMOps Integration, UI Dashboard & Deployment**
  * Tích hợp Langfuse / Phoenix để giám sát Token, Latency và Trace Multi-Agent.
  * Thiết lập pipeline chạy Faithfulness Evals tự động.
  * Xây dựng UI Streamlit trực quan, biểu đồ tương tác Plotly và chức năng Export One-Pager.
  * Đóng gói Docker Compose và thiết lập CI/CD trên GitHub Actions.

---

## 9. Giá trị Đột phá cho CV & Phỏng vấn Kỹ thuật (Key CV Highlights)

1. **Kiến trúc Decoupled Độc đáo:**
   * Thể hiện tư duy kỹ thuật xuất sắc khi giải quyết triệt để điểm yếu lớn nhất của GenAI trong tài chính (Hallucination) bằng cách phân tách *Deterministic Math* và *Probabilistic Agent*.
2. **Áp dụng Chuẩn Mực AI Tiên Tiến (Agentic AI & LLMOps):**
   * Không đơn thuần là gọi OpenAI API, mà là xây dựng hệ thống **Multi-Agent (LangGraph)** có phân công vai trò, có công cụ (Tools), có cơ chế giám sát (Langfuse Tracing) và có hệ thống kiểm thử chất lượng LLM tự động (Evals).
3. **Sự kết hợp Chuyên sâu giữa Finance & Software Engineering:**
   * Chứng minh kiến thức tài chính doanh nghiệp thực chiến (phân tích BCTC, phát hiện gian lận kế toán, mô hình chiết khấu dòng tiền DCF) kết hợp cùng kỹ năng kỹ thuật phần mềm chuẩn chỉ (FastAPI, Streamlit, Docker, CI/CD).
