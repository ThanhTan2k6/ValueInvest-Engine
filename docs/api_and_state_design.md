# FastAPI Contract & State Management Design (`docs/api_and_state_design.md`)
> **Project:** ValueInvest-Engine  
> **Role:** Principal AI Systems Architect & Quantitative FinTech Tech Lead  
> **Target:** Sub-0.1s Sensitivity Updates, Decoupled API Services, Dual-Layer Caching

---

## 1. Kiến trúc Giao tiếp & Quản lý Trạng thái (System State Architecture)

Để đảm bảo nguyên tắc: **Khi người dùng kéo slider $WACC$ hoặc $g$, giao diện Streamlit cập nhật tức thì ($< 0.1\text{s}$) mà KHÔNG gọi lại Data Ingestion và KHÔNG gọi lại LLM Multi-Agent**, hệ thống thiết kế 3 tầng trạng thái độc lập:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                STREAMLIT SESSION STATE                                 │
│  st.session_state['ticker']           -> Mã CP hiện hành (e.g. "HPG")                 │
│  st.session_state['statements']       -> FinancialStatementSchema (Immutable Cache)  │
│  st.session_state['red_flags']        -> RedFlagReportSchema (Cached)                 │
│  st.session_state['valuation_output']  -> ValuationOutputSchema (Updated via Slider)   │
│  st.session_state['agent_critique']   -> AgentCritiqueSchema (Cached until button click)│
└───────────────────────────┬──────────────────────────────────┬─────────────────────────┘
                            │ Slider changed ($WACC, g$)       │ "Analyze" or "Challenge"
                            ▼ (Local In-Memory / Vectorized)   ▼ (REST Call)
┌───────────────────────────────────────┐  ┌─────────────────────────────────────────────┐
│ FAST VALUATION PATH (< 50ms)          │  │ FASTAPI SERVICE GATEWAY                     │
│ POST /api/v1/valuate                  │  │ POST /api/v1/analyze                        │
│ Tính toán thuần NumPy 2D Broadcasting  │  │ POST /api/v1/critique                       │
│ Bỏ qua Ingestion & Bỏ qua Multi-Agent │  └──────────────────────┬──────────────────────┘
└───────────────────────────────────────┘                         │
                                                                  ▼
                                           ┌─────────────────────────────────────────────┐
                                           │ REDIS DUAL-LAYER CACHE                      │
                                           │ 1. Raw BCTC Parquet Cache (TTL 24h)         │
                                           │ 2. Semantic Critique SHA256 Cache (TTL 24h) │
                                           └─────────────────────────────────────────────┘
```

---

## 2. Đặc tả Hợp đồng REST API (FastAPI Endpoints)

### 2.1. Endpoint 1: Phân tích Toàn diện & Quét Báo cáo Tài chính (`POST /api/v1/analyze`)
- **Mục đích:** Thu thập BCTC 5 năm, làm sạch, kiểm định đẳng thức kế toán, phân rã DuPont 3 bước và quét toàn bộ Red Flags định lượng.
- **Tần suất gọi:** 1 lần duy nhất khi người dùng nhập Ticker và bấm `Analyze`.
- **SLA:** $\le 2.0\text{s}$ (Cold fetch) hoặc $\le 0.1\text{s}$ (Cache hit).

#### Request Body:
```json
{
  "ticker": "HPG",
  "lookback_years": 5,
  "exchange": "HOSE",
  "force_refresh": false
}
```

#### Response Body (HTTP 200 OK):
```json
{
  "status": "SUCCESS",
  "ticker": "HPG",
  "company_name": "CTCP Tập đoàn Hòa Phát",
  "exchange": "HOSE",
  "financial_statements": {
    "balance_sheets": [...],
    "income_statements": [...],
    "cash_flow_statements": [...]
  },
  "red_flag_report": {
    "assessment_period": "2023-FY",
    "critical_count": 1,
    "warning_count": 2,
    "safe_count": 3,
    "flags": [
      {
        "flag_id": "CRIT_REF_CLIFF",
        "severity": "CRITICAL",
        "category": "LIQUIDITY",
        "title": "Nợ vay ngắn hạn tài trợ TSCĐ dở dang",
        "metric_value": 48200.0,
        "threshold_value": 22300.0,
        "evidence": "Nợ ngắn hạn gấp 2.16 lần tiền mặt trong bối cảnh đại dự án Dung Quất 2 cần vốn."
      }
    ],
    "dupont_analysis": {
      "net_profit_margin": 0.057,
      "asset_turnover": 0.65,
      "financial_leverage": 1.85,
      "roe": 0.068
    },
    "interest_coverage_ratio": 3.8,
    "net_debt_to_equity": 0.42
  },
  "base_valuation_parameters": {
    "suggested_base_fcf": 12150.0,
    "current_market_price": 28500.0,
    "shares_outstanding": 5814785700,
    "net_debt": 25900.0,
    "capm_computed_wacc": 0.115
  }
}
```

---

### 2.2. Endpoint 2: Định giá DCF & Ma trận Độ nhạy Tức thời (`POST /api/v1/valuate`)
- **Mục đích:** Nhận các tham số tùy biến từ slider UI ($WACC, g_{stage1}, g_{terminal}$) và chạy thuật toán NumPy vectorization tính toán Intrinsic Value, MoS và Ma trận nhạy cảm 2D.
- **Tần suất gọi:** Mỗi khi người dùng thả chuột (on-change) trên các thanh trượt Streamlit.
- **SLA:** $\le 0.05\text{s}$ ($50\text{ms}$). **Tuyệt đối không gọi I/O mạng hoặc LLM**.

#### Request Body (`DCFInputParams`):
```json
{
  "ticker": "HPG",
  "current_market_price": 28500.0,
  "shares_outstanding": 5814785700,
  "base_fcf": 12150.0,
  "stage1_growth_rate": 0.08,
  "stage1_years": 5,
  "terminal_growth_rate": 0.025,
  "wacc": 0.115,
  "net_debt": 25900.0
}
```

#### Response Body (HTTP 200 OK - `ValuationOutputSchema`):
```json
{
  "ticker": "HPG",
  "current_market_price": 28500.0,
  "enterprise_value": 180420.0,
  "equity_value": 154520.0,
  "intrinsic_value_per_share": 26573.0,
  "margin_of_safety": -0.0725,
  "scenarios": [
    {
      "scenario_name": "Bear",
      "assumed_stage1_g": 0.05,
      "assumed_wacc": 0.13,
      "intrinsic_value_per_share": 20450.0,
      "margin_of_safety": -0.393,
      "verdict": "EXPENSIVE"
    },
    {
      "scenario_name": "Base",
      "assumed_stage1_g": 0.08,
      "assumed_wacc": 0.115,
      "intrinsic_value_per_share": 26573.0,
      "margin_of_safety": -0.0725,
      "verdict": "FAIR_VALUE"
    },
    {
      "scenario_name": "Bull",
      "assumed_stage1_g": 0.11,
      "assumed_wacc": 0.105,
      "intrinsic_value_per_share": 34800.0,
      "margin_of_safety": 0.181,
      "verdict": "MODERATE_BUFFER"
    }
  ],
  "sensitivity_wacc_steps": [0.10, 0.105, 0.11, 0.115, 0.12, 0.125, 0.13, 0.135, 0.14],
  "sensitivity_g_steps": [0.02, 0.025, 0.03, 0.035, 0.04],
  "sensitivity_matrix": [
    [32400.0, 34200.0, 36500.0, 39100.0, 42300.0],
    [29800.0, 31300.0, 33100.0, 35200.0, 37800.0],
    [27500.0, 28700.0, 30200.0, 32000.0, 34100.0],
    [25500.0, 26573.0, 27800.0, 29300.0, 31000.0],
    [23700.0, 24600.0, 25700.0, 27000.0, 28400.0],
    [22100.0, 22900.0, 23800.0, 24900.0, 26100.0],
    [20700.0, 21400.0, 22200.0, 23100.0, 24100.0],
    [19400.0, 20000.0, 20700.0, 21500.0, 22400.0],
    [18200.0, 18700.0, 19400.0, 20100.0, 20900.0]
  ]
}
```

---

### 2.3. Endpoint 3: Kích hoạt Hội đồng Phản biện Multi-Agent (`POST /api/v1/critique`)
- **Mục đích:** Kích hoạt luồng LangGraph StateGraph (Supervisor -> Forensic Auditor + Valuation Challenger).
- **Tần suất gọi:** Chỉ khi người dùng bấm nút `Challenge My Valuation`.
- **SLA:** $\le 0.2\text{s}$ (Redis Cache hit) hoặc $\le 6.0\text{s}$ (LangGraph cold execution).

#### Request Body:
```json
{
  "ticker": "HPG",
  "current_assumptions": {
    "stage1_growth_rate": 0.08,
    "wacc": 0.115,
    "terminal_growth_rate": 0.025
  },
  "valuation_summary": {
    "intrinsic_value": 26573.0,
    "current_price": 28500.0,
    "margin_of_safety": -0.0725
  },
  "force_refresh": false
}
```

#### Response Body (HTTP 200 OK - `AgentCritiqueSchema`):
```json
{
  "ticker": "HPG",
  "forensic_auditor_summary": "Nợ ngắn hạn chịu lãi ở mức 48.200 tỷ VND, vượt 2.16 lần lượng tiền mặt (22.300 tỷ VND). Áp lực tài trợ đại công trình Dung Quất 2 làm gia tăng rủi ro thanh khoản.",
  "valuation_challenger_points": [
    {
      "area": "GROWTH",
      "user_assumption": "Tăng trưởng dòng tiền 8.0%/năm trong 5 năm tới.",
      "counter_evidence": "Biên lợi nhuận gộp ngành thép biến động mạnh, năm 2022 từng rơi về 2.9% trong giai đoạn suy thoái.",
      "socratic_question": "Khi thị trường bất động sản nội địa chưa phục hồi và xuất khẩu gặp thuế tự vệ, động lực nào đảm bảo FCF tăng trưởng 8% liên tục mà không gặp rủi ro thừa công suất?",
      "risk_level": "HIGH"
    }
  ],
  "macro_context_evaluation": "Giá quặng sắt thế giới dao động quanh mức 110-120 USD/tấn. Biên lợi nhuận thép chịu áp lực kép từ chi phí nguyên liệu và nhu cầu tiêu thụ chậm.",
  "overall_skepticism_rating": "HIGH",
  "synthesis_memo_markdown": "### Tóm tắt Phản biện Rủi ro - HPG\n...",
  "regulatory_disclaimer": "Báo cáo này được lập cho mục đích cung cấp thông tin và kiểm toán rủi ro độc lập theo nguyên lý đầu tư giá trị. Đây không phải lời khuyên đầu tư tài chính theo quy định của Ủy ban Chứng khoán Nhà nước."
}
```

---

## 3. Thiết kế Quản lý State trên Streamlit UI (`st.session_state`)

```python
import streamlit as st
import requests
from src.valuation.sensitivity import compute_sensitivity_matrix
from src.valuation.dcf import compute_multistage_dcf

def init_session_state():
    """Khởi tạo trạng thái phiên an toàn, tránh mất dữ liệu khi rerender."""
    defaults = {
        "ticker": "",
        "statement_data": None,     # FinancialStatementSchema
        "red_flag_report": None,    # RedFlagReportSchema
        "valuation_result": None,   # ValuationOutputSchema
        "agent_critique": None,     # AgentCritiqueSchema
        "wacc_slider": 0.115,
        "g_slider": 0.08,
        "terminal_g_slider": 0.025,
        "is_analyzing": False
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

def on_slider_change():
    """
    CALLBACK CỰC NHANH: Kích hoạt khi user kéo slider WACC hoặc g.
    TÍNH TOÁN CỤC BỘ BẰNG NUMPY TRONG SESSION, KHÔNG GỌI API INGESTION HOẶC LLM.
    Độ trễ: < 15ms!
    """
    if st.session_state["statement_data"] is None:
        return
        
    wacc = st.session_state["wacc_slider"]
    stage1_g = st.session_state["g_slider"]
    terminal_g = st.session_state["terminal_g_slider"]
    
    # 1. Kiểm tra guardrail toán học
    if wacc <= terminal_g:
        st.error("WACC phải lớn hơn Terminal Growth tối thiểu 0.5%!")
        return
        
    # 2. Tính lại DCF & Sensitivity bằng Math Engine thuần túy
    st.session_state["valuation_result"] = compute_multistage_dcf(
        ticker=st.session_state["ticker"],
        base_fcf=st.session_state["base_fcf"],
        stage1_growth_rate=stage1_g,
        terminal_growth_rate=terminal_g,
        wacc=wacc,
        shares_outstanding=st.session_state["shares_outstanding"],
        net_debt=st.session_state["net_debt"],
        current_market_price=st.session_state["current_market_price"]
    )
    # UI rerender Plotly Heatmap lập tức!
```
Thiết kế này cô lập hoàn toàn các tầng tải nặng, biến tương tác định giá thành trải nghiệm người dùng thời gian thực mượt mà tuyệt đối.
